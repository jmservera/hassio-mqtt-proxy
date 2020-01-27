#!/usr/bin/env python3

import argparse
import json
import paho.mqtt.client as mqtt
import os
import sys
from time import sleep
from unidecode import unidecode

from web.app import webApp 
from logger import log,LogLevel

def main():
    log("Start!")

hassio_topic="homeassistant"
hostname="mqttproxy"

parser = argparse.ArgumentParser(description='A simple mqtt proxy for publishing hassio modules that could not run inside hassio.')
parser.add_argument('-w','--webServer',help="starts a web server", action="store_true")
parser.add_argument('-p','--port',type=int,help='the server port to listen')
args=parser.parse_args()
main()
if(args.webServer):
    if(args.port):
        webApp(args.port)
    else:
        webApp()


# Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log('MQTT connection established', console=True, sd_notify=True)
        print()
    else:
        log('Connection error with result code {} - {}'.format(str(rc), mqtt.connack_string(rc)), level=LogLevel.ERROR)
        #kill main thread
        os._exit(1)

def on_publish(client, userdata, mid):
    log("Message id={}".format(mid))

def on_message(client, userdata, message):
    try:
        log('Received message:{}'.format(message.payload))
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
        log(ex, level=LogLevel.ERROR)

def createTopic(suffix,base_topic="binary_sensor"):
    return "{}/{}/{}/{}".format(hassio_topic,base_topic,hostname,suffix)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
mqtt_client.on_message = on_message
try:
    mqtt_client.connect('localhost',port=1883,keepalive=60)
except:
    log('MQTT connection error',level=LogLevel.ERROR)
    sys.exit(1)
else:
    mqtt_client.subscribe(createTopic("cmnd"))
    mqtt_client.publish(createTopic("host2/state"),payload='{"power":"ON"}')
    mqtt_client.loop_start()
    sleep(0.1)
    config={
        "name":"mqttproxy-host2-state",
        "unique_id":"mqttproxy-host567",
        "stat_t":createTopic("host2/state"),
        "dev":{
            "identifiers":["raspi2","mqttproxy2"],
            "name":"mqttproxy-host2",
            "sw_version":"0.2-alpha"}
    }
    mqtt_client.publish(createTopic("host2/config"),payload=json.dumps(config),retain=True)
    mqtt_client.publish(createTopic("host2/state"),payload='ON')

while True:
    log("sleep 30s")
    sleep(30)

