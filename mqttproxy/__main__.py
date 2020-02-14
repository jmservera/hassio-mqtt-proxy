#!/usr/bin/env python3

import atexit
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
import sdnotify

#custom libs
from mqttproxy.configuration import read_from_args,get_config
from mqttproxy.const import REQUIRED_PYTHON_VER, RESTART_EXIT_CODE, __version__,__language__,ALL_PROXIES_TOPIC
from mqttproxy.blescan import scan
import mqttproxy

hosttype="host"
hassio_topic="homeassistant"
host_sensor="binary_sensor"
host_device_class="connectivity"
hostname="{}-{:x}".format(mqttproxy.__package__,uuid.getnode())
manufacturer="jmservera"

mqtt_client = mqtt.Client()
config=get_config()
logger=logging.getLogger(__name__)
coloredlogs.install()
sdnotifier=sdnotify.SystemdNotifier()

__refresh_thread=None
__refresh_thread_semaphore=None
__refresh_interval=30

def cancel_main_loop():
    if(__refresh_thread):
        __refresh_thread_semaphore.release()
        __refresh_thread.join()

def create_topic(suffix:str,base_topic:str=host_sensor,is_general:bool=False)->str:
    """Creates a topic string for a suffix, based on the current device name and general base_topic.

    It is used to get consistent topic names for all the features.

    suffix: a string with the name of the last part of the topic
    base_topic: defines the type of sensor, it is binary_sensor by default (a generic binary_sensor)
    is_general: when True, will use the same string for all the proxies, when False it uses the hostname to differentiate the topic.

    Returns a string formed by the different values, for example:
    create_topic("cmnd") will create a topic named homeassistant/sensor/mqttproxy-[id]/cmnd

    Or 

    create_topic("activate",is_general=True) will create a topic named homeassistant/sensor/allmqttproxies/activate
    """
    name=hostname
    if(is_general):
        name=ALL_PROXIES_TOPIC
    return "{}/{}/{}/{}".format(hassio_topic,base_topic,name,suffix)

def create_host_topic(topic:str):
    return create_topic("{}/{}".format(hosttype,topic))

hoststatetopic = create_host_topic("state")
hostavailabilitytopic = create_host_topic("availability")
hostcommandtopic= create_host_topic("cmnd")

# Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info('MQTT connection established.')
    else:
        logger.error('Connection error with result code {} - {}'.format(str(rc), mqtt.connack_string(rc)))
        #kill main thread
        os._exit(1)

def on_publish(client, userdata, mid):
    logger.info("Message {} published".format(mid))

def on_message(client, userdata, message):
    try:
        logger.info('Received message:{}'.format(message.payload))
        
        def cases(payload):
            switcher={
                b'STOP': cancel_main_loop,
                b'SCAN': scan
            }
            foo=switcher.get(payload)
            if foo:
                return foo()
            else:
                logger.warning('Command unknown: {}'.format(payload))

        cases(message.payload)

    except Exception as ex:
        logger.error(ex)


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
    publish_message(create_host_topic("config"),json.dumps(deviceconfig),retain=config.mqtt.retainConfig)

def refresh_loop(timeout:float=30):
    global __refresh_interval

    __refresh_interval=timeout

    while True:
        publish_message(hoststatetopic,"ON")
        publish_message(hostavailabilitytopic,"online")
        logger.info("Sleeping {}s".format(__refresh_interval))
        if(timeout<0 or __refresh_thread_semaphore.acquire(True,__refresh_interval)):
            break


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

def start_main_loop(timeout=30):
    global __refresh_thread
    global __refresh_thread_semaphore

    if(not __refresh_thread):
        __refresh_thread_semaphore=threading.Semaphore(0)
        __refresh_thread=threading.Thread(target=refresh_loop,daemon=True,name='refresh_loop', args=[timeout])
    if(not __refresh_thread.is_alive()):
        __refresh_thread.start()
    return __refresh_thread

def main() -> int:
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
        mqtt_client.subscribe(hostcommandtopic)
        logger.info("Listening on topic: {}".format(hostcommandtopic))
        deviceconfig={
            "name":"{}-state".format(hostname),
            "unique_id":hostname,
            "stat_t":hoststatetopic,
            "availability_topic":hostavailabilitytopic,
            "expire_after": __refresh_interval*2,
            "device_class": host_device_class
        }
        mqtt_client.loop_start()
        sleep(0.1)
        announce(deviceconfig)
        start_main_loop().join()

    return 0

@atexit.register
def goodbye():
    logger.info("Trying to exit gracefully from {}".format(hostname))    
    if mqtt_client:
        publish_message(hoststatetopic,"OFF")
        publish_message(hostavailabilitytopic,"offline")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    sys.exit(main())
