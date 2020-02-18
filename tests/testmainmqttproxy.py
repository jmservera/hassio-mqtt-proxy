import mqttproxy
from mqttproxy.__main__ import *
from mqttproxy.const import ALL_PROXIES_TOPIC
from mqttproxy.configuration import load_config,get_config,reset_config

from mqttproxy.blescan import scan 

import io
from time import sleep
import unittest
from unittest import mock

from paho.mqtt.client import MQTTMessage
from . common import get_fixture_path

_mock_error_msg="Mock error"

class TestMqttProxy(unittest.TestCase):
    def tearDown(self):
        reset_config()

    def test_hostname(self):
        self.assertTrue(host_uniqueid.startswith(mqttproxy.__package__))

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

    @mock.patch('mqttproxy.__main__.__main_sched.shutdown')
    def test_on_message_stop(self, shutdown):
        message=MQTTMessage(mid=0,topic="hello")
        message.payload=b"STOP"
        on_message('cli','data',message)
        self.assertTrue(shutdown.called)

    @mock.patch('mqttproxy.__main__.scan')
    def test_on_message_scan(self,scan):
        message=MQTTMessage(mid=0,topic="hello")
        message.payload=b"SCAN"
        on_message('cli','data',message)
        self.assertTrue(scan.called)

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
        deviceconfig={"device":None}
        dc=add_device(deviceconfig)
        #test they are the same object
        self.assertEqual(deviceconfig,dc)
        #test config added
        self.assertIsNotNone(dc["device"]["identifiers"])
        self.assertIsNotNone(dc["device"]["name"])
        self.assertIsNotNone(dc["device"]["manufacturer"])
        self.assertIsNotNone(dc["device"]["model"])
        self.assertIsNotNone(dc["device"]["sw_version"])

    def test_announce_success(self):
        deviceconfig={
            "name":"{}_state".format(host_uniqueid),
            "unique_id":host_uniqueid,
            "stat_t":"~state",
            "~":"test/tele/"
        }
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        announce(deviceconfig)
        self.assertTrue(mqtt_client.publish.called)
        self.assertGreater(len(mqtt_client.publish.call_args),0)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_announce_fail(self,mock_out):
        deviceconfig={
            "name":"{}_state".format(host_uniqueid),
            "unique_id":host_uniqueid,
            "stat_t":"~state",
            "~":"test/tele/"
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

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_loop(self,mock_out):
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        refresh_message()
        output=mock_out.getvalue()
        self.assertGreater(output.index("Sleeping"),0)

    def test_exit_with_mqtt_connected(self):
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        mqtt_client.disconnect=mock.Mock()
        mqtt_client.loop_stop=mock.Mock()
        mqtt_client._state=mqtt.mqtt_cs_connected
        goodbye()
        self.assertTrue(mqtt_client.publish.called)
        self.assertTrue(mqtt_client.disconnect.called)
        self.assertTrue(mqtt_client.loop_stop.called)

    def test_exit_with_mqtt_disconnected(self):
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        mqtt_client.disconnect=mock.Mock()
        mqtt_client.loop_stop=mock.Mock()
        mqtt_client._state=mqtt.mqtt_cs_new
        goodbye()
        self.assertFalse(mqtt_client.publish.called)
        self.assertFalse(mqtt_client.disconnect.called)
        self.assertFalse(mqtt_client.loop_stop.called)

    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_exit_with_mqtt_msg_failure(self, mock_out):
        mqtt_client.publish=mock.Mock(side_effect=Exception(_mock_error_msg))
        mqtt_client.disconnect=mock.Mock()
        mqtt_client.loop_stop=mock.Mock()
        mqtt_client._state=mqtt.mqtt_cs_connected
        goodbye()

        output=mock_out.getvalue()

        self.assertTrue(mqtt_client.disconnect.called)
        self.assertTrue(mqtt_client.loop_stop.called)

        self.assertTrue(output.index(_mock_error_msg)>0)
    
    @mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_exit_with_mqtt_disconnect_failure(self, mock_out):
        mqtt_client.publish=mock.Mock(return_value=(0,1))
        mqtt_client.disconnect=mock.Mock(side_effect=Exception(_mock_error_msg))
        mqtt_client.loop_stop=mock.Mock()
        mqtt_client._state=mqtt.mqtt_cs_connected
        goodbye()

        output=mock_out.getvalue()

        self.assertTrue(mqtt_client.publish.called)
        self.assertTrue(mqtt_client.loop_stop.called)

        self.assertTrue(output.index(_mock_error_msg)>0)

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
