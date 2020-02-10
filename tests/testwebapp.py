import unittest

from mqttproxy.web.app import _contextvars,process_context


class TestWebApp(unittest.TestCase):

    def test_index(self):
        self.skipTest("need to mock flask")


    def test_context(self):
        global _contextvars
        ctx=process_context({})
        self.assertDictEqual({},ctx)
        _contextvars["test"]="hello"
        ctx=process_context({})
        self.assertDictEqual(ctx,{"test":"hello"})
        ctx=process_context({"a":"b"})
        self.assertDictEqual(ctx,{"test":"hello","a":"b"})
