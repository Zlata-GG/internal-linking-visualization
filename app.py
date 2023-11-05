from dash import Dash, dcc, html, Input, Output, State, no_update
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash
import pandas as pd
import base64
import re
import io
from dash_iconify import DashIconify
import json
import os


app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA],
           suppress_callback_exceptions=True)
server= app.server
global df, link_counts
df = pd.DataFrame()
link_counts = pd.DataFrame()


#my functions

def generate_elements(df):
    if 'source' not in df.columns or 'destination' not in df.columns:
        return []
    unique_urls = pd.concat([df['source'], df['destination']]).drop_duplicates()
    nodes = [{"data": {"id": url, "label": url}} for url in unique_urls]
    edges = [{"data": {"source": row['source'], "target": row['destination']}} for index, row in df.iterrows()]
    return nodes + edges

#my navigation
navbar = dbc.NavbarSimple(
    brand="Internal Linking Visualization",
    brand_href="/",
    style={'zIndex': '2','backgroundColor': 'rgba(32, 201, 151, 0.6)'},
    children=[
        dbc.NavItem(dbc.NavLink("App", href="/exclude-urls")),
        dbc.NavItem(dbc.NavLink("Instructions & About", href="/instructions-about")),
        dbc.NavItem(
            dbc.NavLink(
                children=[
                    DashIconify(icon="fa6-brands:square-x-twitter", color="black", width=24,height=24)
                ],
                href="https://twitter.com/ZlataGarmendia",
                target="_blank"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                children=[
                    DashIconify(icon="devicon:linkedin", color="black", width=24,height=24)
                ],
                href="https://linkedin.com/in/zlata-garmendia",
                target="_blank"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                children=[
                    DashIconify(icon="devicon:github", color="black", width=24,height=24)
                ],
                href="https://github.com/Zlata-GG/internal-linking-visualization/tree/main",
                target="_blank"
            )
        )
    ],
    color="dark",
    dark=False
)
#Main layout
main_layout = dbc.Container([
    html.H3('Ensure your CSV contains internal links with "source" and "destination" columns.',style={'fontSize': '0.8em','marginTop':'20px', 'fontWeight': '400'}) ,
    html.H3('Scroll to zoom in and out of the graph. Click on nodes to move them around. To refine your graph, filter keywords from your URLs or apply regex patterns.',style={'fontSize': '0.8em', 'fontWeight': '400'}),
    html.H3('Use left table bellow, select rows to turn corresponding nodes and edges in red. The table on the right displays the total number of links each URL has.', style={'fontSize':'0.8em', 'fontWeight': '400'}),
    html.Hr(),
    dcc.Upload(
        id='upload-data',
        children=dbc.Button('Upload CSV File', color='primary'),
        multiple=False
    ),
    dbc.RadioItems(
        options=[
            {'label': 'Filter by Excluding URLs', 'value': 'exclude'},
            {'label': 'Filter by Including URLs', 'value': 'include'}
        ],
        value='exclude', 
        id='filter-mode',
        inline=True,  
        style={'marginTop': '10px'}
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='input-keyword',
                type='text',
                placeholder='Enter keyword or regex to filter out or add...',
                style={'marginRight': '5px', 'width': '60%'}
            ),
            dbc.Button('Apply Filter', id='apply-filter', color='secondary', style={'marginRight': '10px', 'borderRadius': '10px'}),
            dbc.Button('Reset', id='reset_filtering', color='danger', style={'borderRadius': '10px'})
        ],width=7),
        dbc.Col([
            html.H3('Choose different graph layout:', style={'fontSize': '1em', 'marginTop': '5px', 'display': 'inline-block', 'marginLeft': '15px'}),
            dcc.Dropdown(
                id='dropdown-update-layout',
                options=[
                    {'label': 'Circle', 'value': 'circle'},
                    {'label': 'Grid', 'value': 'grid'},
                    {'label': 'Random', 'value': 'random'},
                    {'label': 'Concentric', 'value': 'concentric'}
                ],
                value='circle',
                style={'display': 'inline-block', 'width': '200px', 'verticalAlign': 'middle', 'marginLeft': '10px'}
            )
        ], width=5),
    ]),  

    html.Div(id='excluded-words', children='You filtered out words: ', style={'marginTop': '5px', 'marginBottom': '5px'}),
    html.Div(id='included-words', children='You included URLs that contain words: ', style={'marginTop': '5px', 'marginBottom': '5px'}),
    dcc.Loading(
        id="loading",
        type="default",
        children=[
            cyto.Cytoscape(
                id="cytoscape-update-layout",
                layout={"name": "circle"},
                style={"width": "100%", "height": "500px"},
                elements=[],
                stylesheet=[
        {
            "selector": "node",
            "style": {
                "label": "data(id)"
            }
        }
    ]
            )
        ]
    ),
    dbc.Row([
        dbc.Col([
            dag.AgGrid(
                id='my_aggrid',
                rowData=[],
                columnDefs=[{'headerName': 'Source URL', 'field': 'source','flex':1,'sortable': True, 'filter': True},
                {'headerName': 'Destination URL', 'field': 'destination','flex':1,'sortable': True, 'filter': True}],
                style={'height': '600px', 'marginTop': '20px'},
                className='ag-theme-alpine',
                selectedRows=[],
                dashGridOptions={"rowSelection":"multiple","rowMultiSelectWithClick": True},
                ),
        
            html.Div(id='selected-row-data', style={'display': 'none'}),
        ], width=6),
    dbc.Col([
        dag.AgGrid(
            id='aggregated-aggrid',
            rowData=link_counts.to_dict('records'),
            columnDefs=[
                {'headerName': 'URL', 'field': 'URL', 'flex': 1, 'sortable': True, 'filter': True},
                {'headerName': 'Number of Links', 'field': 'Number of Links', 'flex': 1, 'sortable': True, 'filter': True}
                ],
            style={'height': '600px', 'marginTop': '20px'},
            selectedRows=[],
           
)
 ],width=6)
]),
], className="dbc", fluid=True)

 
#layout of About & Instructions page
instructions_about_layout = dbc.Container([
    html.H4('Why Visualization Matters?', style={'marginTop': '50px','marginBottom':'30px','marginLeft':'10px'}),
    html.P('Visualizing the internal linking structure of your website serves as a powerful tool for several reasons:',style={'marginLeft':'10px'}),
    html.H6("Optimizing User Experience (UX) and SEO:",style={'fontWeight': 'bold','marginLeft':'10px'}),
    html.P("Understanding how pages interlink helps in ensuring that users and search engines can easily navigate and find content on your site.",style={'marginLeft':'10px'}),           
    html.H6("Highlighting Conversion Paths",style={'fontWeight': 'bold', 'marginLeft':'10px'}),
    html.P("By understanding the flow of traffic and the interlinking structure, you can better optimize paths that lead to conversions.",style={'marginLeft':'10px'}),
    html.H6("Identifying Patterns and Potential Issues",style={'fontWeight': 'bold','marginLeft':'10px'}),
    html.P("Visualization assists in spotting areas where the linking structure may be too dense or too sparse. Dense areas might indicate over-concentration of links, while sparse areas could suggest missed opportunities for interlinking and improving the user journey. Overly dense linking areas might be diluting link equity or confusing users.",style={'marginLeft':'10px'}),
    html.H4('Instructions',style={'marginTop': '40px','marginBottom':'30px','marginLeft':'10px'}),
    html.P('This app has two main functionalities:', style={'marginLeft':'10px'}),
    html.P("Filter by Excluding words in URL Paths using Regex: Exclude specific URLs or URL patterns from visualization. Select rows in the table bellow to mark correcsponding URLs and their connections in red, to focus more on certain URLs.",style={'marginLeft':'10px'}),
    html.P('Filter by including - Choose specific URLs to just see internal linking of the page you are interested, add/include additional words or regex patterns to understand their internal linking relationships. By seeing all pages that match either keyword, you might identify opportunities to create content that bridges the two topics or to add internal links between related pages.',style={'marginLeft':'10px'}),
    html.P('Uploading Your Data',style={'fontWeight':'bold', 'marginLeft':'10px'}),
    html.P('Ensure your CSV file has two columns "source" and "destination". You can generate this file from an inlinks report from a web crawler.',style={'marginLeft':'10px'} ),
    html.P('After uploading, use scoll to zoom and navigate the graph. Click on nodes and move them. Use "Reset" button to cancel all filtering and start afresh.',style={'marginLeft':'10px'}),
    html.P('Use tables bellow the graph - you can sort and filter columns, by selecting rows in first table graph nodes and egdes turn red for better visualization. Second table shows links aggregated by URL.',style={'marginLeft':'10px'}),
    html.H4('Challenges with Complex Graphs',style={'marginTop': '30px','marginBottom':'30px','marginLeft':'10px'}),
    html.P('Complexity of graphs that represent linking structure makes it challenging to discover patterns, evaluate link equity distribution, or even identify potential problem areas.', style={'marginLeft':'10px'}),
    html.P('This tool aims to alleviate these challenges. While it\'s essential to understand the full picture, not every link or page holds equal importance. Some, like categories, external links, or informational pages (like \'Impressum\'), might not directly impact conversions. By allowing users to exclude specific parts of the website, this tool simplifies the visualization to focus on the links that matter most – that are crucial for conversions.', style={'marginLeft':'10px'}),
    html.P('Built with Dash and utilizing the power of Cytoscape, goal is to make link analysis more intuitive and actionable. As we continuously refine our tool, your feedback is always invaluable.', style={'fontStyle': 'italic','marginLeft':'10px','marginBottom':'70px'}),
], className="dbc", fluid=True)

#particles inclusion and homepage layout
particles_div = html.Div(id='particles-js', style={'width': '100vw', 'height': '100vh', 'position': 'fixed', 'zIndex': '2','backgroundColor': '#939AA1', 'display': 'block'})
home_layout = html.Div([
    html.Div([
        html.H3("Welcome to the Internal Linking Visualization App!"),
        html.P("Upload your CSV, apply filters, and explore the graph.", style={'fontFamily': 'Roboto'}),
        dcc.Link(
            dbc.Button('START', className='mt-3',style={
            'backgroundColor': '#02B875', 
            'border': 'none',
            'padding': '12px 24px',
            'fontSize': '16px', 
            'transition': 'background-color 0.3s', 
            ':hover': {
                'backgroundColor': '#17A288'
            }
        }),
            href='/exclude-urls'
        )
    ], style={
        'textAlign': 'center',
        'margin': '150px auto',
        'backgroundColor': 'rgba(255, 255, 255, 0.6)',
        'padding': '30px',
        'borderRadius': '16px',
        'maxWidth': '450px',
        'boxShadow': '0px 8px 30px rgba(0, 0, 0, 0.1)',
        'zIndex': '1'  
    })
], style={'position': 'relative'})  


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    particles_div,
    html.Div(id='page-content'),  
    html.Script(src="/assets/particles.js", defer=True),
    html.Script(src="/assets/particles_init.js",defer=True)
])

#callbacks and functions

@app.callback([Output('page-content', 'children'),
              Output('particles-js', 'style')],
              [Input('url', 'pathname')])

def display_page(pathname):
    
    if pathname == '/exclude-urls':
        return main_layout,{'display': 'none'}
    elif pathname == '/instructions-about':
        return instructions_about_layout,{'display': 'none'}
    else:  
        return home_layout, {'width': '100vw', 'height': '100vh', 'position': 'fixed', 'zIndex': '0','backgroundColor': '#939AA1'}


# callback to update the Cytoscape graph main page
@app.callback (
    [Output('cytoscape-update-layout', 'elements'),
     Output('cytoscape-update-layout', 'layout'),
     Output('excluded-words','children'),
     Output('included-words','children'),
     Output('my_aggrid', 'rowData')],
    [Input('upload-data', 'contents'),
     Input('dropdown-update-layout', 'value'),
     Input('apply-filter','n_clicks'),
     Input('reset_filtering', 'n_clicks'),
     Input('filter-mode', 'value')],
    [State('cytoscape-update-layout', 'elements'),
    State('input-keyword','value')]
)

#function for main page 
def update_graph_and_layout (contents, selected_layout, n_clicks, reset_clicks, filter_mode,elements, keyword):
    global df, excluded_words, included_words 

    if 'excluded_words' not in globals():
        excluded_words = []
    if 'included_words' not in globals():
        included_words = []
    
    def apply_all_filters(df, excluded_words):
        for keyword in excluded_words:
            df = df[df.apply(
                lambda row: re.search(keyword, row['source']) is None and
                re.search(keyword, row['destination']) is None,
                axis=1
            )]
        return df
    
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'filter-mode':
        return elements, no_update, no_update, no_update, no_update
        
    if trigger_id == 'reset_filtering':
        excluded_words = []  
        included_words = []  
        return generate_elements(df), {'name': selected_layout}, 'You filtered out words: ', 'You included URLs that contain words: ',df.to_dict('records')

    if trigger_id == 'dropdown-update-layout':
        return no_update, {'name': selected_layout}, no_update, no_update, no_update
    elif trigger_id == 'upload-data':
        if contents is None:
            return no_update, no_update, no_update, no_update, no_update
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))  
            if 'source' not in df.columns or 'destination' not in df.columns:
                return no_update, no_update, "Error: The uploaded CSV file must have 'source' and 'destination' columns.",no_update, no_update
            
            # Check for missing values
            if df['source'].isnull().any() or df['destination'].isnull().any():
                return no_update, no_update, "Error: The uploaded CSV file has missing values in 'source' or 'destination' columns.", no_update, no_update
            link_counts = df['source'].value_counts().reset_index()
            link_counts = link_counts.rename(columns={'source': 'URL', 'count': 'Number of links'})

        except Exception as e:
            return no_update, no_update, no_update, no_update, no_update
        return generate_elements(df), {'name': selected_layout}, no_update, no_update, df.to_dict('records')
     
    # Create elements for Cytoscape graph
        
    elif trigger_id == 'apply-filter':
        if keyword:
            if filter_mode == 'exclude' and keyword not in excluded_words:
                excluded_words.append(keyword)
            elif filter_mode == 'include' and keyword not in included_words:
                included_words.append(keyword)

    if filter_mode == 'exclude':
        filtered_df = apply_all_filters(df, excluded_words)
        update_excluded_words = f"You filtered out URLs containing: {', '.join(excluded_words)}"  
        return generate_elements(filtered_df), {'name': selected_layout}, update_excluded_words, no_update,filtered_df.to_dict('records')
    elif filter_mode == 'include':
        filtered_df = df[df.apply(
                lambda row: any(re.search(kw, row['source']) is not None or
                re.search(kw, row['destination']) is not None for kw in included_words),
                axis=1
            )]
        update_included_words = f"You included URLs that contain: {', '.join(included_words)}"
        return generate_elements(filtered_df), {'name': selected_layout}, no_update, update_included_words,filtered_df.to_dict('records')
    return no_update, no_update, no_update,no_update


#for reinitializing particles 
@app.callback(
    Output('particles-js', 'children'),
    Input('url', 'pathname')
)
def update_particles(pathname):
    if pathname == '/':  
        return html.Script(src="/assets/particles_init.js")
    return dash.no_update
#coloring nodes and edges by selecting aggrid
@app.callback(
   Output('selected-row-data', 'children'),
   Input('my_aggrid', 'selectedRows')
)
def update_selected_row_data(selected_rows):
    if not selected_rows:
        return dash.no_update
    return json.dumps(selected_rows)

@app.callback(
    Output('cytoscape-update-layout', 'stylesheet'),
    Input('selected-row-data', 'children')
)
def update_cytoscape_styles(selected_rows_json):
    
    if not selected_rows_json:
        return dash.no_update

    # Convert the JSON string into a list of dictionaries
    selected_rows = json.loads(selected_rows_json)

    selected_styles = []

    for selected_row in selected_rows:
        source = selected_row.get('source')
        destination = selected_row.get('destination')
        if source and destination:
            selected_styles.extend([
               {
                  "selector": f'node[id = "{source}"]',
                   "style": {
                       "background-color": "red",
                       "label": "data(id)"
                    }
               },
                {
                    "selector": f'node[id = "{destination}"]',
                    "style": {
                        "background-color": "red",
                        "label": "data(id)"
                    }
                },
                {
                    "selector": f'edge[source = "{source}"][target = "{destination}"]',
                    "style": {
                        "line-color": "red"
                    }
                }
            ])
   
    # Define the styles for the selected nodes and edge
    default_styles = [
        {
            "selector": 'node',
            "style": {
                "label": "data(id)"
            }
        },
        {
            "selector": 'edge',
            "style": {
                "line-color": "gray" 
            }
        }
    ]

    # Combine the default styles with the styles for the selected nodes and edges
    combined_styles = default_styles + selected_styles

    return combined_styles
@app.callback(
    Output('aggregated-aggrid', 'rowData'),
    [Input('upload-data', 'contents')]
)
def update_aggregated_table(contents):
    global link_counts
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))  
            if 'source' not in df.columns or 'destination' not in df.columns:
                return [],no_update
            if df['source'].isnull().any() or df['destination'].isnull().any():
                return [],no_update
            
            link_counts = df['source'].value_counts().reset_index()
            link_counts = link_counts.rename(columns={'source': 'URL', 'count': 'Number of Links'})
            
            return link_counts.to_dict('records')
        except Exception as e:
            return []
    return []



if(__name__) == '__main__':
    app.run_server(debug=True)

