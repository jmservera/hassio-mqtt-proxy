from flask import Flask, render_template
from flask_nav import Nav
from flask_nav.elements import Navbar, View 
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
nav = Nav()
nav.init_app(app)

_contextvars=dict()

@app.route('/')
def index():
    return render_template('index.html',name=__name__)

@app.context_processor
def inject_global_constants():
    return _contextvars


@nav.navigation()
def mynavbar():
    return Navbar(
        'MQTT Proxy',
        View('Home', 'index'),
    )

def webApp(port=8080, production=False, contextvars=None):
    global _contextvars
    if(contextvars):
        for key in contextvars.keys():
            _contextvars[key]=contextvars[key]

    if production:
        import waitress
        waitress.serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    webApp()
