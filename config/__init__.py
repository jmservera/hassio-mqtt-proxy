from munch import Munch

config = Munch.fromYAML("""mqtt:
    server: localhost
    user: 
    pwd: 
    retain_config: true

ble:
    device: hc0

web_admin:
    enabled: true
    port: 8080

devices: []
""")

def loadConfig(configpath="config.yaml"):
    global config
    with open(configpath,"r") as configfile:
        config=Munch.fromYAML(configfile)
    return config

def saveConfig(configpath="config.yaml"):
    global config
    with open(configpath,"w") as configfile:
        config.toYAML(configfile)