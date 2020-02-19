#!/usr/bin/env python3

import atexit
import argparse
import json
import os
import paho.mqtt.client as mqtt
from platform import platform
import sys
import threading
from time import time,sleep
from unidecode import unidecode
import uuid
import coloredlogs, logging
import sdnotify
from apscheduler.schedulers import blocking

#custom libs
from mqttproxy.configuration import read_from_args,get_config
from mqttproxy.const import REQUIRED_PYTHON_VER, RESTART_EXIT_CODE, __version__,__language__,ALL_PROXIES_TOPIC
from mqttproxy.blescan import scan
import mqttproxy
import socket


hosttype="host"
hassio_topic="homeassistant"
host_sensor="sensor"
host_device_class="connectivity"
hostname=socket.gethostname()
host_uniqueid="{}_{:x}".format(mqttproxy.__package__,uuid.getnode())
host_status_uniqueid="{}_status".format(host_uniqueid)
manufacturer="jmservera"

mqtt_client = mqtt.Client()
config=get_config()
logger=logging.getLogger(__package__)
coloredlogs.install()
sdnotifier=sdnotify.SystemdNotifier()

__refresh_interval=30
__main_sched=blocking.BlockingScheduler()
__exit= threading.Event()


basetopic= "{}/{}/".format(hostname,"tele")
hoststatetopic = "{}state".format(basetopic)
hostavailabilitytopic = "{}LWT".format(basetopic)
hostcommandtopic= "{}/cmnd".format(hostname)
hostconfigtopic="{}/{}/{}/config".format(hassio_topic,host_sensor,host_status_uniqueid)

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
                b'STOP': __main_sched.shutdown,
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
    deviceconfig["device"]={
            "identifiers":[host_uniqueid],
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
    publish_message(hostconfigtopic,json.dumps(deviceconfig),retain=config.mqtt.retainConfig)

def refresh_message():
    publish_message(hoststatetopic,"ON")
    publish_message(hostavailabilitytopic,"online")
    logger.info("Sleeping {}s".format(__refresh_interval))


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

def connect_to_mqtt():
    global config

    config=get_config()

    logger.debug(config)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message

    if(config.mqtt.user):
        if(config.mqtt.password):
            mqtt_client.username_pw_set(config.mqtt.user,config.mqtt.password)
        else:
            mqtt_client.username_pw_set(config.mqtt.user)

    mqtt_client.connect(config.mqtt.server,port=config.mqtt.port or 1883,keepalive=60)
    mqtt_client.subscribe(hostcommandtopic)
    logger.info("Listening on topic: {}".format(hostcommandtopic))
    mqtt_client.loop_start()
    sleep(0.1)
    deviceconfig={
        "name":hostname,
        "unique_id":host_status_uniqueid,
        "stat_t":"~state",
        "availability_topic":"~LWT",
        "expire_after": __refresh_interval*2,
        "~":basetopic
    }
    announce(deviceconfig)

def load_modules()->{}:
    from os import listdir
    from os.path import join, isdir
    import importlib
    modules={}
    basepath=os.path.dirname(__file__)
    devicespath=join(basepath,'devices')
    logger.info("Loading modules from {}".format(devicespath))
    for f in listdir(devicespath):
        if isdir(join(devicespath, f)) and not f.startswith('.'):
            module=importlib.import_module('.devices.{}'.format(f),__package__)
            logger.info("Loaded module {}".format(module.__name__))
            modules[f]=module

    return modules

def main() -> int:
    global config
    global __refresh_interval

    parser=create_parser()
    args=parser.parse_args()

    read_from_args(args)

    try:
        connect_to_mqtt()
    except Exception as ex:
        logger.error('MQTT connection error:{}'.format(ex))
        return 1

    __refresh_interval=30
    __main_sched.add_job(refresh_message,'interval',seconds=__refresh_interval)
    refresh_message()

    modules=load_modules()
    for key in modules:
        modules[key].start_module()

    __main_sched.start()

    return 0

@atexit.register
def goodbye():
    logger.info("Trying to exit gracefully from {}".format(host_uniqueid))    
    if mqtt_client and mqtt_client._state==mqtt.mqtt_cs_connected:
        try:
            publish_message(hoststatetopic,"OFF")
            publish_message(hostavailabilitytopic,"offline")
        except Exception as mex:
            logger.error('Exception trying to publish messages:{}'.format(mex))
        try:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        except Exception as dex:
            logger.error('Exception trying to close mqtt client:{}'.format(dex))

if __name__ == "__main__":
    sys.exit(main())
