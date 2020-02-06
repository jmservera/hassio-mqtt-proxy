#!/usr/bin/env python3

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
from mqttproxy.configuration import read_from_args,get_config
from mqttproxy.logger import log_info, log_error, log_debug, log_warning
from mqttproxy.web.app import web_app
from mqttproxy.const import REQUIRED_PYTHON_VER, RESTART_EXIT_CODE, __version__,__language__

hosttype="host"
hassio_topic="homeassistant"
hostname="hassmqttproxy-{:x}".format( uuid.getnode())
manufacturer="jmservera"

mqtt_client = mqtt.Client()
config=get_config()

 # Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log_info('MQTT connection established', console=True, sd_notify=True)
        print()
    else:
        log_error('Connection error with result code {} - {}'.format(str(rc), mqtt.connack_string(rc)))
        #kill main thread
        os._exit(1)

def on_publish(client, userdata, mid):
    log_info("Message id={}".format(mid))

def on_message(client, userdata, message):
    try:
        log_info('Received message:{}'.format(message.payload))
    except Exception as ex:
        log_error(ex)

def create_topic(suffix,base_topic="binary_sensor"):
    return "{}/{}/{}/{}".format(hassio_topic,base_topic,hostname,suffix)

def add_device(deviceconfig):    
    deviceconfig["dev"]={
            "identifiers":["raspi",hostname],
            "name":hostname,
            "manufacturer":manufacturer,
            "model":platform(),
            "sw_version":__version__}
    return deviceconfig

def announce(deviceconfig):
    deviceconfig=add_device(deviceconfig)
    (rc,mid)=mqtt_client.publish(create_topic("{}/config".format(hosttype)),payload=json.dumps(deviceconfig),retain=config.mqtt.retainConfig)

    if rc==mqtt.MQTT_ERR_SUCCESS:
        log_info("Sent message with mid:{}".format(mid))
    else:
        log_error("Error {} sending message".format(rc))

def refresh_loop():
    while True:
        log_info("Sleeping 30s")
        sleep(30)

refresh=None

def create_parser() -> argparse.ArgumentParser:
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
    parser=create_parser()
    
    args=parser.parse_args()

    read_from_args(args)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    try:
        log_debug(config)
        if(config.mqtt.user):
            if(config.mqtt.password):
                mqtt_client.username_pw_set(config.mqtt.user,config.mqtt.password)
            else:
                mqtt_client.username_pw_set(config.mqtt.user)

        mqtt_client.connect('localhost',port=1883,keepalive=60)
    except Exception as ex:
        log_error('MQTT connection error:{}'.format(ex))
        return 1
    else:
        mqtt_client.subscribe(create_topic("cmnd"))
        deviceconfig={
            "name":"{}-state".format(hostname),
            "unique_id":hostname,
            "stat_t":create_topic("{}/state".format(hosttype)),
        }
        announce(deviceconfig)
        mqtt_client.loop_start()
        sleep(0.1)
        mqtt_client.publish(create_topic("{}/state".format(hosttype)),payload='ON')

    if(not refresh):
        refresh=threading.Thread(target=refresh_loop,daemon=True)
        refresh.start()

    if(config.web_admin.enabled):
        from mqttproxy.web import app
        app.web_app(config.web_admin.port,config.app.mode=="production",
                    dict(__version__=__version__,__language__=__language__))
    else:
        while True:
            sleep(30)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())