from munch import Munch
import logging

logger=logging.getLogger()

def reset_config():
    global _config
    _config=Munch.fromYAML("""app:
    mode: development # production, test
    debug: true
mqtt:
    server: localhost
    user: ~
    password: ~
    retainConfig: true
    port: ~
ble:
    device: hc0

devices:
    - name: back_garden_1
      address: 'C4:7C:8d:66:D7:EB'
""")
    return _config

_config = None
reset_config()


def get_config():
    return _config

def __read_config(configfile):
    newconfig=Munch.fromYAML(configfile)
    copykey=False
    for key in newconfig:
        for subkey in newconfig[key]:
            if isinstance(subkey,str):
                _config[key][subkey]=newconfig[key][subkey]
            else:
                copykey=True
                break
        if copykey:
            _config[key]=newconfig[key]



def load_config(configpath="config.yaml"):
    global _config
    with open(configpath,"r") as configfile:
        __read_config(configfile)
    return _config

def save_config(configpath="config.yaml"):
    global _config
    with open(configpath,"w") as configfile:
        configfile.write(_config.toYAML())

def read_from_args(args):
    global _config
    if(args.retainConfig):
        _config.mqtt.retainConfig=args.retainConfig
    if(args.mqttserver):
        _config.mqtt.server=args.mqttserver
    if(args.mqttuser):
        _config.mqtt.user=args.mqttuser
    if(args.mqttpassword):
        _config.mqtt.password=args.mqttpassword
    if(args.production):
        _config.app.mode="production"
        _config.app.debug=False
    if(args.configfile):
        logger.debug("Loading {0}".format(args.configfile))
        __read_config(args.configfile)
