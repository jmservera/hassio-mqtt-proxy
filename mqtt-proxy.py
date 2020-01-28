#!/usr/bin/env python3

__version__ ='0.0.3-alpha'

import argparse
import json
import os
import paho.mqtt.client as mqtt
from platform import platform
import sys
from time import sleep
from unidecode import unidecode
import uuid

#custom libs
from logger import logInfo,logWarning,logError
from web.app import webApp 

hosttype="host"
hassio_topic="homeassistant"
hostname="mqttproxy-{:x}".format( uuid.getnode())
manufacturer="servezas"

parser = argparse.ArgumentParser(description='A simple mqtt proxy for publishing hassio modules that could not run inside hassio.')
parser.add_argument('-w','--webServer',help="starts a web server", action="store_true")
parser.add_argument('-p','--port',type=int,help='the server port to listen')
parser.add_argument('-r','--retainConfig',help="sets the retain flag to the config messages",action="store_true")
args=parser.parse_args()

if(args.webServer):
    if(args.port):
        webApp(args.port)
    else:
        webApp()


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

def addDevice(config):
    config["dev"]={
            "identifiers":["raspi",hostname],
            "name":hostname,
            "manufacturer":manufacturer,
            "model":platform(),
            "sw_version":__version__}
    return config

def announce(config):
    config=addDevice(config)
    mqtt_client.publish(createTopic("{}/config".format(hosttype)),payload=json.dumps(config),retain=args.retainConfig)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
mqtt_client.on_message = on_message
try:
    mqtt_client.connect('localhost',port=1883,keepalive=60)
except Exception as ex:
    logError('MQTT connection error:{}'.format(ex))
    sys.exit(1)
else:
    mqtt_client.subscribe(createTopic("cmnd"))
    config={
        "name":"{}-state".format(hostname),
        "unique_id":hostname,
        "stat_t":createTopic("{}/state".format(hosttype)),
    }
    announce(config)
    mqtt_client.loop_start()
    sleep(0.1)
    mqtt_client.publish(createTopic("{}/state".format(hosttype)),payload='ON')

while True:
    logInfo("sleep 30s")
    sleep(30)
