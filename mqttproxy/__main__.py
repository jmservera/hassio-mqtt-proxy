#!/usr/bin/env python3

__version__ ='0.0.3-alpha'

import argparse
import json
import os
import paho.mqtt.client as mqtt
from platform import platform
import sys
import threading
from time import sleep
from unidecode import unidecode
import uuid

#custom libs
from mqttproxy.configuration import readFromArgs,getConfig
from mqttproxy.logger import logInfo, logError, logDebug, logWarning
from mqttproxy.web.app import webApp
from mqttproxy.const import REQUIRED_PYTHON_VER, RESTART_EXIT_CODE, __version__

hosttype="host"
hassio_topic="homeassistant"
hostname="hassmqttproxy-{:x}".format( uuid.getnode())
manufacturer="jmservera"

mqtt_client = mqtt.Client()
config=getConfig()

 # Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logInfo('MQTT connection established', console=True, sd_notify=True)
        print()
    else:
        logError('Connection error with result code {} - {}'.format(str(rc), mqtt.connack_string(rc)))
        #kill main thread
        os._exit(1)

def on_publish(client, userdata, mid):
    logInfo("Message id={}".format(mid))

def on_message(client, userdata, message):
    try:
        logInfo('Received message:{}'.format(message.payload))
        # value= json.loads(message.payload)
        # returnMessage={"received_message": value}
        # returnPayload=json.dumps(returnMessage)
        # log(returnPayload)
        # (rc,mid)=mqtt_client.publish('{}/RESULT'.format(base_topic), payload=returnPayload)
        # if rc==mqtt.MQTT_ERR_SUCCESS:
        #     log("Sent message with mid:{}".format(mid))
        # else:
        #     log("Error {} sending message".format(rc), level=LogLevel.ERROR)
    except Exception as ex:
        logError(ex)

def createTopic(suffix,base_topic="binary_sensor"):
    return "{}/{}/{}/{}".format(hassio_topic,base_topic,hostname,suffix)

def addDevice(deviceconfig):    
    deviceconfig["dev"]={
            "identifiers":["raspi",hostname],
            "name":hostname,
            "manufacturer":manufacturer,
            "model":platform(),
            "sw_version":__version__}
    return deviceconfig

def announce(deviceconfig):
    deviceconfig=addDevice(deviceconfig)
    mqtt_client.publish(createTopic("{}/config".format(hosttype)),payload=json.dumps(deviceconfig),retain=config.mqtt.retainConfig)

def refreshLoop():
    while True:
        logInfo("Sleeping 30s")
        sleep(30)

refresh=None

def createParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='A simple mqtt proxy for publishing hassio modules that could not run inside hassio.')
    parser.add_argument('--noWebServer',help="does not start the web server", action="store_true")
    parser.add_argument('--production',help="sets the server in production mode", action="store_true")
    parser.add_argument('-p','--webPort',type=int,help='the server port to listen')
    parser.add_argument('-r','--retainConfig', type=bool,help="sets the retain flag to the config messages")
    parser.add_argument('-c','--configfile', type=argparse.FileType('r'), help="the config.yaml file" )
    parser.add_argument('-m','--mqttserver', help="mqtt connection server",default="localhost")
    parser.add_argument('-u','--mqttuser', help="username for mqtt connection")
    parser.add_argument('-P','--mqttpassword',help="password for the mqtt connection")
    parser.add_argument("--version", action="version", version=__version__)
    return parser
    
def main() -> int:
    global refresh
    parser=createParser()
    
    args=parser.parse_args()

    readFromArgs(args)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    try:
        logDebug(config)
        if(config.mqtt.user):
            if(config.mqtt.password):
                mqtt_client.username_pw_set(config.mqtt.user,config.mqtt.password)
            else:
                mqtt_client.username_pw_set(config.mqtt.user)

        mqtt_client.connect('localhost',port=1883,keepalive=60)
    except Exception as ex:
        logError('MQTT connection error:{}'.format(ex))
        return 1
    else:
        mqtt_client.subscribe(createTopic("cmnd"))
        deviceconfig={
            "name":"{}-state".format(hostname),
            "unique_id":hostname,
            "stat_t":createTopic("{}/state".format(hosttype)),
        }
        announce(deviceconfig)
        mqtt_client.loop_start()
        sleep(0.1)
        mqtt_client.publish(createTopic("{}/state".format(hosttype)),payload='ON')

    if(not refresh):
        refresh=threading.Thread(target=refreshLoop,daemon=True)
        refresh.start()

    if(config.web_admin.enabled):
        from mqttproxy.web import app
        app.webApp(config.web_admin.port,config.app.mode=="production")
    else:
        while True:
            sleep(30)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())