import mqttproxy
from mqttproxy.__main__ import * 

import io
import unittest
import unittest.mock

from paho.mqtt.client import MQTTMessage
from . common import get_fixture_path

class TestMqttProxy(unittest.TestCase):
    def test_hostname(self):
        global hostname
        self.assertTrue(hostname.startswith(mqttproxy.__package__))

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_on_connect_success(self, mock_out):
        on_connect('client',None,None,0)
        output=mock_out.getvalue()
        self.assertTrue(output.index('MQTT connection established')>0)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_on_connect_error(self, mock_out):
        self.skipTest("Need to figure out how to test os_exit(1)")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_on_publish(self, mock_out):
        on_publish('cli','data',42)
        output=mock_out.getvalue()
        self.assertGreater(output.index("Message id=42"),0)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_on_message_success(self, mock_out):
        message=MQTTMessage(mid=0,topic="hello")
        message.payload="the message"
        on_message('cli','data',message)
        output=mock_out.getvalue()
        self.assertGreater(output.index("Received message:the message"),0)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_on_message_fail(self, mock_out):
        on_message('a','b',{})
        output=mock_out.getvalue()
        print(output)
        self.assertGreater(output.index("object has no attribute"),0)

    def test_add_device(self):
        deviceconfig={"dev":None}
        dc=add_device(deviceconfig)
        #test they are the same object
        self.assertEqual(deviceconfig,dc)
        #test config added
        self.assertIsNotNone(dc["dev"]["identifiers"])
        self.assertIsNotNone(dc["dev"]["name"])
        self.assertIsNotNone(dc["dev"]["manufacturer"])
        self.assertIsNotNone(dc["dev"]["model"])
        self.assertIsNotNone(dc["dev"]["sw_version"])

    def test_announce(self):
        self.skipTest("Should figure out how to mock mqtt_client")

    def test_create_parser(self):
        parser=create_parser()
        args=parser.parse_args(["--noWebServer"])
        self.assertTrue(args.noWebServer)
        argscommand="-p 8080 -r true -c {} -m localhost -u username -P thisisapa$$"
        inputargs=argscommand.format(get_fixture_path('config.yaml')).split(' ')
        args=parser.parse_args(inputargs)
        try:
            self.assertEqual(args.webPort,8080)
            self.assertTrue(args.retainConfig)
            self.assertTrue(args.configfile.name.endswith("config.yaml"))
            self.assertEqual(args.mqttserver,"localhost")
            self.assertEqual(args.mqttuser,"username")
            self.assertEqual(args.mqttpassword,"thisisapa$$")
        finally:
            if(args.configfile):
                args.configfile.close()

    def test_create_topic(self):
        global hostname
        onetopic=create_topic("one")
        self.assertEqual(onetopic,"homeassistant/binary_sensor/{}/one".format(hostname))
