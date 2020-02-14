import tempfile
import unittest
from mqttproxy.configuration import *
from mqttproxy.__main__ import create_parser

from os import path
from .common import get_fixture_path

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
        self.assertTrue(config.mqtt.retainConfig)
    
    def test_read_from_args(self):
        
        parser = create_parser()
        
        config=self.current_config

        args=parser.parse_args(["-r","true"])
        read_from_args(args)
        self.assertTrue(config.mqtt.retainConfig)

        args=parser.parse_args(["-r","false"])
        read_from_args(args)
        self.assertTrue(config.mqtt.retainConfig)

        args=parser.parse_args(["-r","true","--production"])
        read_from_args(args)
        self.assertTrue(config.mqtt.retainConfig)
        self.assertEqual(config.app.mode,"production")
        self.assertFalse(config.app.debug)

        args=parser.parse_args(["-c",get_fixture_path('config.yaml')])
        read_from_args(args)
        self.assertEqual(config.mqtt.server,"testlocalhost")
        self.assertEqual(config.mqtt.user,"testuser")
        self.assertEqual(config.mqtt.password,"testpassword")
        self.assertTrue(config.mqtt.retainConfig)

        if(args.configfile):
            args.configfile.close()
    
    def test_device_list(self):
        config=get_config()

        self.assertEqual(len(config.devices),1)
        self.assertIsNotNone(config.devices[0])
        self.assertEqual(config.devices[0].name,"back_garden_1")
        self.assertEqual(config.devices[0].address,"C4:7C:8d:66:D7:EB")

    
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
        path= get_fixture_path("config.yaml")
        config=self.current_config

        load_config(path)
        
        
        self.assertEqual(config.mqtt.user,"testuser")
        self.assertEqual(config.mqtt.password,"testpassword")

    def test_saveConfig(self):
        tempdir=tempfile.gettempdir()
        filename= path.join(tempdir, "configtest.xml")
        config=self.current_config
        config.mqtt.retainConfig=False
        config.app.mode="production"

        save_config(filename)

        reset_config()
        config2=load_config(filename)
        self.assertDictEqual(config,config2)

