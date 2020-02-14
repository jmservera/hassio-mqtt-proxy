import mqttproxy
from mqttproxy.__main__ import *
from mqttproxy.const import ALL_PROXIES_TOPIC
from mqttproxy.configuration import load_config,get_config,reset_config

import io
from time import sleep
import unittest
from unittest import mock

from paho.mqtt.client import MQTTMessage
from . common import get_fixture_path

class TestMqttProxy(unittest.TestCase):
    def tearDown(self):
        reset_config()

    def test_hostname(self):
        self.assertTrue(hostname.startswith(mqttproxy.__package__))

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_on_connect_success(self, mock_out):
        on_connect('client',None,None,0)
        output=mock_out.getvalue()
        self.assertTrue(output.index('MQTT connection established')>0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_on_connect_error(self, mock_out):
        import os
        os._exit=mock.MagicMock()
        on_connect(None,None,None,1)
        self.assertTrue(os._exit.called)
        output=mock_out.getvalue()
        self.assertTrue(output.index('Connection error')>0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_on_publish(self, mock_out):
        on_publish('cli','data',42)
        output=mock_out.getvalue()
        self.assertGreater(output.index("Message 42 published"),0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_on_message_success(self, mock_out):
        message=MQTTMessage(mid=0,topic="hello")
        message.payload="the message"
        on_message('cli','data',message)
        output=mock_out.getvalue()
        self.assertGreater(output.index("Received message:the message"),0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
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

    def test_announce_success(self):
        deviceconfig={
            "name":"{}-state".format(hostname),
            "unique_id":hostname,
            "stat_t":create_topic("{}/state".format(hosttype)),
        }
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        announce(deviceconfig)
        self.assertTrue(mqtt_client.publish.called)
        self.assertGreater(len(mqtt_client.publish.call_args),0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_announce_fail(self,mock_out):
        deviceconfig={
            "name":"{}-state".format(hostname),
            "unique_id":hostname,
            "stat_t":create_topic("{}/state".format(hosttype)),
        }
        mqtt_client.publish=mock.Mock(return_value=(1,0))
        announce(deviceconfig)
        self.assertTrue(mqtt_client.publish.called)
        self.assertGreater(len(mqtt_client.publish.call_args),0)
        message=mock_out.getvalue()
        self.assertGreater(message.index('Error 1'),0)

    def test_create_parser(self):
        parser=create_parser()
        argscommand="-r true -c {} -m localhost -u username -P thisisapa$$"
        inputargs=argscommand.format(get_fixture_path('config.yaml')).split(' ')
        args=parser.parse_args(inputargs)
        try:
            self.assertTrue(args.retainConfig)
            self.assertTrue(args.configfile.name.endswith("config.yaml"))
            self.assertEqual(args.mqttserver,"localhost")
            self.assertEqual(args.mqttuser,"username")
            self.assertEqual(args.mqttpassword,"thisisapa$$")
        finally:
            if(args.configfile):
                args.configfile.close()

    def test_create_topic(self):
        onetopic=create_topic("one")
        self.assertEqual(onetopic,"homeassistant/binary_sensor/{}/one".format(hostname))

    def test_create_host_topic(self):
        onetopic=create_host_topic("one")
        self.assertEqual(onetopic,"homeassistant/binary_sensor/{}/{}/one".format(hostname,hosttype))

    def test_create_general_topic(self):
        onetopic=create_topic("one",is_general=True)
        self.assertEqual(onetopic,"homeassistant/binary_sensor/{}/one".format(ALL_PROXIES_TOPIC))

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_loop(self,mock_out):
        start_main_loop(0.1)
        output=mock_out.getvalue()
        sleep(0.1)
        cancel_main_loop()
        self.assertGreater(output.index("Sleeping"),0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_no_loop(self,mock_out):
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        mqtt_client.disconnect=mock.Mock()
        mqtt_client.loop_stop=mock.Mock()
        refresh_loop(-1)
        output=mock_out.getvalue()
        self.assertGreater(output.index("Sleeping"),0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_exit(self, mock_out):
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        mqtt_client.disconnect=mock.Mock()
        mqtt_client.loop_stop=mock.Mock()
        goodbye()
        self.assertTrue(mqtt_client.publish.called)
        self.assertTrue(mqtt_client.disconnect.called)
        self.assertTrue(mqtt_client.loop_stop.called)

    def test_connect_to_mqtt_user_pwd(self):
        path= get_fixture_path("config.yaml")
        load_config(path)
        config=get_config()

        mqtt_client.username_pw_set=mock.Mock()
        mqtt_client.connect=mock.Mock()
        mqtt_client.subscribe=mock.Mock()
        mqtt_client.loop_start=mock.Mock()
        mqtt_client.publish=mock.Mock(return_value=(0,1))

        connect_to_mqtt()

        self.assertTrue(mqtt_client.username_pw_set.called)
        self.assertEqual(config.mqtt.user, mqtt_client.username_pw_set.call_args[0][0])
        self.assertEqual(config.mqtt.password, mqtt_client.username_pw_set.call_args[0][1])
        self.assertTrue(mqtt_client.connect.called)
        self.assertEqual(config.mqtt.server,mqtt_client.connect.call_args[0][0])
        self.assertEqual(config.mqtt.port,mqtt_client.connect.call_args[1]['port'])
