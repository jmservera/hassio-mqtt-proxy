import tempfile
import unittest
from mqttproxy.configuration import *
from mqttproxy.__main__ import create_parser

from os import path
from .common import getFixturePath

class TestConfiguration(unittest.TestCase):

    @property
    def current_config(self):
        config=get_config()
        self.assertEqual(config.app.mode, 'development')
        return config

    def tearDown(self):
        reset_config()

    def test_main_config(self):
        config=self.current_config
        self.assertTrue(config.web_admin.enabled)
        self.assertTrue(config.mqtt.retainConfig)
    
    def test_read_from_args(self):
        
        parser = create_parser()
        
        config=self.current_config
        
        args=parser.parse_args(["--noWebServer"])
        read_from_args(args)
        self.assertFalse(config.web_admin.enabled)

        args=parser.parse_args(["-p","42"])

        reset_config()
        config=self.current_config

        read_from_args(args)
        self.assertTrue(config.web_admin.enabled)
        self.assertEqual(config.web_admin.port,42)

        args=parser.parse_args(["-r","true"])
        read_from_args(args)
        self.assertTrue(config.mqtt.retainConfig)

        args=parser.parse_args(["-r","false"])
        read_from_args(args)
        self.assertTrue(config.mqtt.retainConfig)

        args=parser.parse_args(["-r","true","-p","443","--production"])
        read_from_args(args)
        self.assertTrue(config.mqtt.retainConfig)
        self.assertEqual(config.web_admin.port,443)
        self.assertEqual(config.app.mode,"production")
        self.assertFalse(config.app.debug)
    
    def test_read_mqtt_from_args(self):
        parser = create_parser()
        config= self.current_config

        args=parser.parse_args(["-u","user","-P","pwd","-m","localhost"])
        read_from_args(args)
        self.assertEqual(config.mqtt.user,"user")
        self.assertEqual(config.mqtt.password,"pwd")
        self.assertEqual(config.mqtt.server,"localhost")

        args=parser.parse_args(["--mqttuser","user","--mqttpassword","pwd","--mqttserver","localhost"])
        read_from_args(args)
        self.assertEqual(config.mqtt.user,"user")
        self.assertEqual(config.mqtt.password,"pwd")
        self.assertEqual(config.mqtt.server,"localhost")

    def test_loadConfig(self):
        path= getFixturePath("config.yaml")
        config=self.current_config

        load_config(path)
        
        
        self.assertEqual(config.mqtt.user,"testuser")
        self.assertEqual(config.mqtt.password,"testpassword")

    def test_saveConfig(self):
        tempdir=tempfile.gettempdir()
        filename= path.join(tempdir, "configtest.xml")
        config=self.current_config
        config.mqtt.retainConfig=False
        config.web_admin.port=443
        config.app.mode="production"

        save_config(filename)

        reset_config()
        config2=load_config(filename)
        self.assertDictEqual(config,config2)

