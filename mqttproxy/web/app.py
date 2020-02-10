from sanic import Sanic
from sanic.response import json
from sanic_jinja2 import SanicJinja2

from .. configuration import get_config
from .. blescan import scan_async


def process_context(context:dict)->dict:
    context={**context,**_contextvars}
    print(context)
    return context

app = Sanic(__name__)
jinja= SanicJinja2(app)

_contextvars=dict()

@app.route('/')
@jinja.template('index.html')
def index(request):
    config=get_config()
    return process_context({"devices":config.devices})

@app.route('/',methods=['POST'])
@jinja.template('index.html')
async def index_post(request):   
    devices=await scan_async()
    if(not devices):
        devices=get_config().devices
    return process_context({"devices":devices})

def web_app(port=8080, production=False, contextvars=None):
    global _contextvars
    if(contextvars):
        _contextvars={**_contextvars,**contextvars}

    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    web_app()
