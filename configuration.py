from munch import Munch
from logger import logDebug

config = Munch.fromYAML("""mqtt:
    server: localhost
    user: 
    password: 
    retainConfig: true

ble:
    device: hc0

web_admin:
    enabled: true
    port: 8080

devices: []
""")

def readConfig(configfile):
    newconfig=Munch.fromYAML(configfile)        
    config.clear()
    for key in newconfig:
        config[key]=newconfig[key]


def loadConfig(configpath="config.yaml"):
    global config
    with open(configpath,"r") as configfile:
        readConfig(configfile)
    return config

def saveConfig(configpath="config.yaml"):
    global config
    with open(configpath,"w") as configfile:
        config.toYAML(configfile)

def readFromArgs(args):
    global config
    if(args.webServer):
        config.webServer=True
    if(args.port):
        config.port=args.port
    if(args.retainConfig):
        config.mqtt.retainConfig=args.retainConfig
    if(args.mqttuser):
        config.mqtt.user=args.mqttuser
    if(args.mqttpassword):
        config.mqtt.password=args.mqttpassword
    if(args.configfile):
        logDebug("Loading {0}".format(args.configfile))
        readConfig(args.configfile)
