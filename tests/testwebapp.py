import unittest

from mqttproxy.web.app import inject_global_constants, _contextvars, mynavbar


class TestWebApp(unittest.TestCase):

    def test_index(self):
        self.skipTest("need to mock flask")

    def test_navigation(self):
        nav=mynavbar()
        self.assertIsNotNone(nav)
        

    def test_context(self):
        global _contextvars
        ctx=inject_global_constants()
        self.assertDictEqual({},ctx)
        _contextvars["test"]="hello"
        ctx=inject_global_constants()
        self.assertDictEqual(ctx,{"test":"hello"})
