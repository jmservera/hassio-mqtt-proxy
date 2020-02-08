from flask import Flask, render_template
from flask_nav import Nav
from flask_nav.elements import Navbar, View 
from flask_bootstrap import Bootstrap

from .. configuration import get_config
from .. blescan import scan

app = Flask(__name__)
Bootstrap(app)
nav = Nav()
nav.init_app(app)

_contextvars=dict()

@app.route('/')
def index():
    config=get_config()
    return render_template('index.html',name=__name__, devices=config.devices)

@app.route('/',methods=['POST'])
def index_post():
    config=get_config()
    return render_template('index.html',name=__name__, devices=config.devices)

@app.context_processor
def inject_global_constants():
    return _contextvars


@nav.navigation()
def mynavbar():
    return Navbar(
        'MQTT Proxy',
        View('Home', 'index'),
    )

def web_app(port=8080, production=False, contextvars=None):
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
    web_app()
