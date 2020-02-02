import unittest
from mqttproxy.configuration import *
from common import getFixturePath

class TestConfiguration(unittest.TestCase):

    def getCurrentConfig(self):
        config=getConfig()
        self.assertEqual(config.app.mode, 'development')
        return config

    def tearDown(self):
        resetConfig()

    def test_main_config(self):
        config=self.getCurrentConfig()
        self.assertTrue(config.web_admin.enabled)
        self.assertTrue(config.mqtt.retainConfig)
    
    def test_read_from_args(self):
        from mqttproxy.__main__ import createParser
        parser = createParser()
        
        config=self.getCurrentConfig()
        
        args=parser.parse_args(["--noWebServer"])
        readFromArgs(args)
        self.assertFalse(config.web_admin.enabled)

        args=parser.parse_args(["-p 42"])

        resetConfig()
        config=self.getCurrentConfig()

        readFromArgs(args)
        self.assertTrue(config.web_admin.enabled)
        self.assertEqual(config.web_admin.port,42)

        args=parser.parse_args(["-r true"])
        readFromArgs(args)
        self.assertTrue(config.mqtt.retainConfig)

        args=parser.parse_args(["-r false"])
        readFromArgs(args)
        self.assertTrue(config.mqtt.retainConfig)

        args=parser.parse_args(["-r true","-p 443","--production"])
        readFromArgs(args)
        self.assertTrue(config.mqtt.retainConfig)
        self.assertEqual(config.web_admin.port,443)
        self.assertEqual(config.app.mode,"production")
        self.assertFalse(config.app.debug)

    def test_read_config(self):
        path= getFixturePath("config.yaml")
        config=self.getCurrentConfig()

        loadConfig(path)
        
        
        self.assertEqual(config.mqtt.user,"testuser")
        self.assertEqual(config.mqtt.password,"testpassword")



    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()