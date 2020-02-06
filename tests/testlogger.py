from mqttproxy.logger import *

import io
import unittest
import unittest.mock

class TestConfiguration(unittest.TestCase):

    def run_func(self, func, params, mock_out)->str:
        func(**params)
        return mock_out.getvalue()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def capture_stdout(self, func, params, mock_stdout)->str:
        return self.run_func(func,params,mock_stdout)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def capture_stderr(self, func, params, mock_stderr)->str:
        return self.run_func(func,params,mock_stderr)

    def test_log_debug(self):
        result=self.capture_stdout(log_debug,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)

    def test_log_info(self):
        result=self.capture_stdout(log_info,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)

    def test_log_warning(self):
        result=self.capture_stdout(log_warning,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)

    def test_log_error(self):
        result=self.capture_stderr(log_error,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)
    
    def test_log(self):
        result=self.capture_stdout(log,{"text":"hello"})
        self.assertTrue(result.find("hello")>0)
        result=self.capture_stdout(log,{"text":"hello","sd_notify":True})
        self.assertTrue(result.find("hello")>0)
        self.assertTrue(result.find('>>> STATUS')>0)