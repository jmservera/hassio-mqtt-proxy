from munch import Munch
from mqttproxy.logger import logDebug

def resetConfig():
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

web_admin:
    enabled: true
    port: 8080

devices: []
""")
    return _config

_config = None
resetConfig()


def getConfig():
    return _config

def readConfig(configfile):
    newconfig=Munch.fromYAML(configfile)        
    _config.clear()
    for key in newconfig:
        _config[key]=newconfig[key]


def loadConfig(configpath="config.yaml"):
    global _config
    with open(configpath,"r") as configfile:
        readConfig(configfile)
    return _config

def saveConfig(configpath="config.yaml"):
    global _config
    with open(configpath,"w") as configfile:
        _config.toYAML(configfile)

def readFromArgs(args):
    global _config
    if(args.noWebServer):
        _config.web_admin.enabled=False
    if(args.webPort):
        _config.web_admin.port=args.webPort
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
        logDebug("Loading {0}".format(args.configfile))
        readConfig(args.configfile)
