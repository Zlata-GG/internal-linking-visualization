window.onload = function() {
    setTimeout(function() {
        particlesJS('particles-js', {
    "particles": {
        "number": {
            "value": 80,
            "density": {
                "enable": true,
                "value_area": 800
            }
        },
        "color": {
            "value": "#02B875" 
        },
        "shape": {
            "type": "circle",
            "stroke": {
                "width": 3, 
                "color": "#ffffff" 
            }
        },
        "size": {
            "value": 3 
        },
        "move": {
            "enable": true,
            "speed": 6,
            "direction": "none",
            "random": false,
            "straight": false,
            "out_mode": "out",
            "bounce": false,
            "attract": {
                "enable": false,
                "rotateX": 600,
                "rotateY": 1200
            }
        }
    },
    "interactivity": {
        "detect_on": "window",
        "events": {
            "onhover": {
                "enable": true,
                "mode": "repulse"
            },
            "onmousemove": {
                "enable": true,
                "mode": "repulse"
            }
        },
        "modes": {
            "repulse": {
                "distance": 200,
                "duration": 0.4
            }
        }
    },
    "retina_detect": true
});
},1000);
};