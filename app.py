from dash import Dash, dcc, html, Input, Output, State, no_update, callback_context
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import base64
import re
import dash
import io
from dash_iconify import DashIconify
import json
import os
os.environ['FLASK_DEBUG'] = '1'

app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA],
           suppress_callback_exceptions=True)
server= app.server
#my functions
df = pd.DataFrame()
filtered_words = []
def generate_elements(df):
    unique_urls = pd.concat([df['source'], df['destination']]).drop_duplicates()
    nodes = [{"data": {"id": url, "label": url}} for url in unique_urls]
    edges = [{"data": {"source": row['source'], "target": row['destination']}} for index, row in df.iterrows()]
    return nodes + edges
def apply_all_filters(df, filtered_words):
    for keyword in filtered_words:
        df = df[df.apply(
            lambda row: re.search(keyword, row['source']) is None and
            re.search(keyword, row['destination']) is None,
            axis=1
        )]
    return df

#my navigation
navbar = dbc.NavbarSimple(
    brand="Internal Linking Visualization",
    brand_href="/",
    style={'zIndex': '2'},
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Filter by Excluding", href="/exclude-urls")),
        dbc.NavItem(dbc.NavLink("Filter by Including", href="/include-urls")),
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
        )
    ],
    color="dark",
    dark=False
)
#Filter by excluding
main_layout = dbc.Container([
    html.H3('Upload your CSV containing internal links with "source" and "destination" columns.',style={'fontSize': '0.8em','marginTop':'30px'}) ,
    html.H3('Scroll to zoom-in the graph, to identify the nodes that you would like to filter out from graph.',style={'fontSize': '0.8em'}),
    html.H3('Uncover  unique linking opportunities or outliers. To refine your graph, input keywords from your URLs or apply regex patterns.', style={'fontSize': '0.8em'}),
    html.Hr(),
    dcc.Upload(
        id='upload-data',
        children=dbc.Button('Upload CSV File', color='primary'),
        multiple=False
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='input-keyword',
                type='text',
                placeholder='Enter keyword or regex to filter out...',
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

    html.Div(id='filtered-words', children='You filtered out words: ', style={'marginTop': '5px', 'marginBottom': '5px'}),

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
    dag.AgGrid(
    id='my_aggrid',
    rowData=df.to_dict('records'),
    columnDefs=[{'headerName': 'Source', 'field': 'source','flex':1},
                {'headerName': 'Destination', 'field': 'destination','flex':1}],
    style={'height': '600px', 'marginTop': '20px'},
    selectedRows=[],
    dashGridOptions={"rowSelection":"multiple"},
    
    ),
    html.Div(id='selected-row-data', style={'display': 'none'})



], className="dbc", fluid=True)

#second page layout
filter_by_including_layout = dbc.Container([
    html.H3('Filter by Including',style={'marginTop': '20px'}),
    html.H4('Upload your CSV containing internal links with "source" and "destination" columns.',style={'fontSize': '0.8em','marginTop':'15px'}),
    html.H4('Scroll to zoom-in the graph, to identify the nodes that you would like to see how they are linked trough website.',style={'fontSize': '0.8em','marginTop':'15px', 'marginBottom':'15px'}),
    dcc.Upload(
        id='include-upload-data', 
        children=dbc.Button('Upload CSV File', color='primary'),
        multiple=False
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='include-input-keyword',  
                type='text',
                placeholder='Enter keyword or regex to include URLs...',
                style={'marginRight': '5px', 'width': '60%'}
            ),
            dbc.Button('Apply Filter', id='include-apply-filter', color='secondary', style={'marginRight': '10px', 'borderRadius': '10px'}),
            dbc.Button('Reset', id='include-reset_filtering', color='danger', style={'borderRadius': '10px'})  
        ], width=7),
        dbc.Col([
            html.H3('Choose different graph layout:', style={'fontSize': '1em', 'marginTop': '5px', 'display': 'inline-block', 'marginLeft': '15px'}),
            dcc.Dropdown(
                id='include-dropdown-update-layout',  
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
    
    html.Div(id='include-filtered-words', children='You included URLs that contain words: ', style={'marginTop': '5px', 'marginBottom': '5px'}),  # Unique ID

    dcc.Loading(
        id="include-loading", 
        type="default",
        children=[
            cyto.Cytoscape(
                id="include-cytoscape-update-layout",  
                layout={"name": "circle"},
                style={"width": "100%", "height": "500px"},
                elements=[]
            )
        ]
    ),
    dag.AgGrid(
    id='my_aggrid1',
    rowData=df.to_dict('records'),
    columnDefs=[{'headerName': 'Source', 'field': 'source','flex':1},
                {'headerName': 'Destination', 'field': 'destination','flex':1}],
    style={'height': '600px', 'marginTop': '20px'}
),

], className="dbc", fluid=True)
 
#layout of About&Instructions page
instructions_about_layout = dbc.Container([
    html.H4('The Importance of Visualizing Internal Links', style={'marginTop': '50px','marginBottom':'30px','marginLeft':'10px'}),
    html.P('Visualizing your website\'s internal linking structure is important for:',style={'marginLeft':'10px'}),
    html.H6("Optimizing User Experience (UX) and SEO:",style={'fontWeight': 'bold','marginLeft':'10px'}),
    html.P("Understanding how pages interlink helps in ensuring that users and search engines can easily navigate and find content on your site.",style={'marginLeft':'10px'}),           
    html.H6("Highlighting Conversion Paths",style={'fontWeight': 'bold', 'marginLeft':'10px'}),
    html.P("By understanding the flow of traffic and the interlinking structure, you can better optimize paths that lead to conversions.",style={'marginLeft':'10px'}),
    html.H6("Identifying Patterns and Potential Issues",style={'fontWeight': 'bold','marginLeft':'10px'}),
    html.P("Visualization assists in spotting areas where the linking structure may be too dense or too sparse. Dense areas might indicate over-concentration of links, while sparse areas could suggest missed opportunities for interlinking and improving the user journey. Overly dense linking areas might be diluting link equity or confusing users.",style={'marginLeft':'10px'}),
    html.H4('Instructions',style={'marginTop': '40px','marginBottom':'30px','marginLeft':'10px'}),
    html.P('This app has two main functionalities:', style={'marginLeft':'10px'}),
    html.P("Excluding Words in URL Paths using Regex: filter out specific URLs or URL patterns you don't want to consider in the visualization.",style={'marginLeft':'10px'}),
    html.P('Starting From Specific URLs and Expanding: you can choose specific URLs as starting points, or to just see internal linking of the page you are interested, and add/include additional words or regex patterns to understand their internal linking relationships. You can visualize internal linking to view of all URL that contains either of words you are adding. By seeing all pages that match either keyword, you might identify opportunities to create content that bridges the two topics or to add internal links between related pages',style={'marginLeft':'10px'}),
    html.P('Uploading Your Data',style={'fontWeight':'bold', 'marginLeft':'10px'}),
    html.P('Make sure your CSV export of links has two columns "source" and "destination". To make this CSV file you can use inlinks report from a crawler.',style={'marginLeft':'10px'} ),
    html.P('Once your data is uploaded, use scoll to zoom and move in and out of the graph, and Reset button to cancel all filtering and stat from beginning.',style={'marginLeft':'10px'}),
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
        html.P("Visualize your website's internal linking structure. Upload your CSV, apply filters, and explore the graph."),
        html.P("Navigate through the tabs above to get started.")
    ], style={
        'textAlign': 'center',
        'margin': '150px auto',
        'backgroundColor': 'rgba(255, 255, 255, 0.8)',
        'padding': '30px',
        'borderRadius': '10px',
        'maxWidth': '450px',
        'zIndex': '1'  # Set a higher zIndex
    })
], style={'position': 'relative'})  # Ensure the parent div has a relative position


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
    if pathname == '/include-urls':
        return filter_by_including_layout,{'display': 'none'}
    elif pathname == '/exclude-urls':
        return main_layout,{'display': 'none'}
    elif pathname == '/instructions-about':
        return instructions_about_layout,{'display': 'none'}
    else:  # Default is home page
        return home_layout, {'width': '100vw', 'height': '100vh', 'position': 'fixed', 'zIndex': '0','backgroundColor': '#939AA1'}


# callback to update the Cytoscape graph main page
@app.callback (
    [Output('cytoscape-update-layout', 'elements'),
     Output('cytoscape-update-layout', 'layout'),
     Output('filtered-words','children'),
     Output('my_aggrid', 'rowData')],
    [Input('upload-data', 'contents'),
     Input('dropdown-update-layout', 'value'),
     Input('apply-filter','n_clicks'),
     Input('reset_filtering', 'n_clicks')],
    State('input-keyword','value')
)

#function for main page 
def update_graph_and_layout(contents, selected_layout,n_clicks,reset_clicks,keyword):
    global df, filtered_words
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'reset_filtering':
        filtered_words = []
        return generate_elements(df), {'name': selected_layout}, 'You filtered out words: ',no_update
    if trigger_id == 'dropdown-update-layout':
        return no_update, {'name': selected_layout}, no_update, no_update
    elif trigger_id == 'upload-data':
        if contents is None:
            return no_update, no_update, no_update, no_update
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))  
            if 'source' not in df.columns or 'destination' not in df.columns:
                return no_update, no_update, "Error: The uploaded CSV file must have 'source' and 'destination' columns.",no_update
            
            # Check for missing values
            if df['source'].isnull().any() or df['destination'].isnull().any():
                return no_update, no_update, "Error: The uploaded CSV file has missing values in 'source' or 'destination' columns.", no_update
            
        except Exception as e:
            return no_update, no_update, no_update, no_update
        return generate_elements(df), {'name': selected_layout}, no_update, df.to_dict('records')
     
    # Create elements for Cytoscape graph
        
    elif trigger_id=='apply-filter':
        if keyword and keyword not in filtered_words:
            filtered_words.append(keyword)
         # Apply all filters
        filtered_df = apply_all_filters(df, filtered_words)
        
        # Update the message
        update_filtered_words = f"You filtered out words: {', '.join(filtered_words)}"
        
        return generate_elements(filtered_df), {'name': selected_layout}, update_filtered_words,no_update
    
    return no_update, no_update, no_update,no_update

# callback and function for second page to include URLs
@app.callback (
    [Output('include-cytoscape-update-layout', 'elements'),
     Output('include-cytoscape-update-layout', 'layout'),
     Output('include-filtered-words','children'),
     Output('my_aggrid1', 'rowData')],
    [Input('include-upload-data', 'contents'),
     Input('include-dropdown-update-layout', 'value'),
     Input('include-apply-filter','n_clicks'),
     Input('include-reset_filtering', 'n_clicks')],
    State('include-input-keyword','value')
)
def update_include_graph_and_layout(contents, selected_layout, n_clicks, reset_clicks, keyword):
    global df, filtered_words
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'include-reset_filtering':
        filtered_words = []
        return generate_elements(df), {'name': selected_layout}, 'You included URLs that contain words: ',no_update
    
    if trigger_id == 'include-dropdown-update-layout':
        return no_update, {'name': selected_layout}, no_update,no_update
    
    elif trigger_id == 'include-upload-data':
        if contents is None:
            return no_update, no_update, no_update,no_update
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))  
            if 'source' not in df.columns or 'destination' not in df.columns:
                return no_update, no_update, "Error: The uploaded CSV file must have 'source' and 'destination' columns.",no_update
            
            # Check for missing values
            if df['source'].isnull().any() or df['destination'].isnull().any():
                return no_update, no_update, "Error: The uploaded CSV file has missing values in 'source' or 'destination' columns.",no_update
            
        except Exception as e:
            return no_update, no_update, no_update
        return generate_elements(df), {'name': selected_layout}, no_update,df.to_dict('records')
     
    elif trigger_id == 'include-apply-filter':
        if keyword:
            filtered_words = [keyword]  # Only consider the current keyword
        else:
            return no_update, no_update, 'You included URLs that contain words: ',no_update
        
        filtered_df = df[df.apply(
            lambda row: re.search(keyword, row['source']) is not None or
            re.search(keyword, row['destination']) is not None,
            axis=1
        )]
        
        update_filtered_words = f"You included URLs that contain words: {', '.join(filtered_words)}"
        
        return generate_elements(filtered_df), {'name': selected_layout}, update_filtered_words,no_update
    
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
                "line-color": "gray"  # or whatever your default edge color is
            }
        }
    ]

    # Combine the default styles with the styles for the selected nodes and edges
    combined_styles = default_styles + selected_styles

    return combined_styles



if __name__ == '__main__':
    app.run_server(debug=True)

