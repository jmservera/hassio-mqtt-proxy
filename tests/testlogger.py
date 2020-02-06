from mqttproxy.logger import *

import io
import unittest
import unittest.mock

class TestConfiguration(unittest.TestCase):

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def assert_stdout(self, func, params, mock_stdout)->str:
        func(**params)
        return mock_stdout.getvalue()

    def test_log_debug(self):
        result=self.assert_stdout(log_debug,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)

    def test_log_info(self):
        result=self.assert_stdout(log_info,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)

    def test_log_warning(self):
        result=self.assert_stdout(log_warning,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)
    
    def test_log(self):
        result=self.assert_stdout(log,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)
        result=self.assert_stdout(log,{"text":"hello","sd_notify":True})
        self.assertTrue(result.find("hello")>0)
        self.assertTrue(result.find('>>> STATUS')>0)