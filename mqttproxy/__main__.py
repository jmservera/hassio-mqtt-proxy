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
import coloredlogs, logging

#custom libs
from mqttproxy.configuration import read_from_args,get_config
from mqttproxy.const import REQUIRED_PYTHON_VER, RESTART_EXIT_CODE, __version__,__language__
import mqttproxy

hosttype="host"
hassio_topic="homeassistant"
hostname="{}-{:x}".format(mqttproxy.__package__,uuid.getnode())
manufacturer="jmservera"

mqtt_client = mqtt.Client()
config=get_config()
logger=logging.getLogger(__name__)
coloredlogs.install()

 # Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info('MQTT connection established')
        print()
    else:
        logger.error('Connection error with result code {} - {}'.format(str(rc), mqtt.connack_string(rc)))
        #kill main thread
        os._exit(1)

def on_publish(client, userdata, mid):
    logger.info("Message {} published".format(mid))

def on_message(client, userdata, message):
    try:
        logger.info('Received message:{}'.format(message.payload))
    except Exception as ex:
        logger.error(ex)

def create_topic(suffix:str,base_topic:str="binary_sensor",is_general:bool=False)->str:
    """Creates a topic string for a suffix, based on the current device name and general base_topic.

    It is used to get consistent topic names for all the features.

    suffix: a string with the name of the last part of the topic
    base_topic: defines the type of sensor, it is binary_sensor by default (on/off sensor)
    is_general: when True, will use the same string for all the proxies, when False it uses the hostname to differentiate the topic.

    Returns a string formed by the different values, for example:
    create_topic("cmnd") will create a topic named homeassistant/binary_sensor/mqttproxy-[id]/cmnd

    Or 

    create_topic("activate",is_general=True) will create a topic named homeassistant/binary_sensor/allmqttproxies/activate
    """
    name=hostname
    if(is_general):
        name="allmqttproxies"
    return "{}/{}/{}/{}".format(hassio_topic,base_topic,name,suffix)

def add_device(deviceconfig:{})->{}:    
    deviceconfig["dev"]={
            "identifiers":["raspi",hostname],
            "name":hostname,
            "manufacturer":manufacturer,
            "model":platform(),
            "sw_version":__version__}
    return deviceconfig

def publish_message(topic, message, retain=False)->(int,int):
    (rc,mid)=mqtt_client.publish(topic,payload=message,retain=retain)

    if rc==mqtt.MQTT_ERR_SUCCESS:
        logger.info("Sent message to topic {} with mid:{}".format(topic, mid))
    else:
        logger.error("Error {} sending message to topic {}".format(rc, topic))
    return (rc,mid)

def announce(deviceconfig):
    deviceconfig=add_device(deviceconfig)
    publish_message(create_topic("{}/config".format(hosttype)),json.dumps(deviceconfig),retain=config.mqtt.retainConfig)

def refresh_loop():
    while True:
        logger.info("Sleeping 30s")
        sleep(30)

refresh=None

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='A simple mqtt proxy for publishing hassio modules that could not run inside hassio.')
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
        logger.debug(config)
        if(config.mqtt.user):
            if(config.mqtt.password):
                mqtt_client.username_pw_set(config.mqtt.user,config.mqtt.password)
            else:
                mqtt_client.username_pw_set(config.mqtt.user)

        mqtt_client.connect('localhost',port=1883,keepalive=60)
    except Exception as ex:
        logger.error('MQTT connection error:{}'.format(ex))
        return 1
    else:
        listen_topic=create_topic("cmnd")
        mqtt_client.subscribe(listen_topic)
        logger.info("Listening on topic: {}".format(listen_topic))
        deviceconfig={
            "name":"{}-state".format(hostname),
            "unique_id":hostname,
            "stat_t":create_topic("{}/state".format(hosttype)),
        }
        announce(deviceconfig)
        mqtt_client.loop_start()
        sleep(0.1)
        (rc,mid)=publish_message(create_topic("{}/state".format(hosttype)),'ON')

    if(not refresh):
        refresh=threading.Thread(target=refresh_loop,daemon=True)
    if(not refresh.is_alive()):
        refresh.start()

    refresh.join()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())