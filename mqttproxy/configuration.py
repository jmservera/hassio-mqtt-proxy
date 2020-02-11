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
    user: mosquitto
    password: mosquitto
    retainConfig: true
ble:
    device: hc0

devices: []
""")
    return _config

_config = None
reset_config()


def get_config():
    return _config

def __read_config(configfile):
    newconfig=Munch.fromYAML(configfile)
    _config.clear()
    for key in newconfig:
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
