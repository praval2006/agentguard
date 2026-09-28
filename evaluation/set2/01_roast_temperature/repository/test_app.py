import unittest
from app import dispatch

class ApplicationTests(unittest.TestCase):
    def test_temperatures(self):
        for value in (160, 200, 240):
            with self.subTest(value=value):
                self.assertEqual(dispatch("POST", "/roast/temperature", {"temperature": value}), (200, {"temperature": value, "unit": "C"}))
    def test_invalid_settings(self):
        for value in (159, 241, 180.5, True, "200", None):
            with self.subTest(value=value):
                status, body = dispatch("POST", "/roast/temperature", {"temperature": value})
                self.assertEqual(status, 400)
                self.assertTrue(body["error"])
    def test_unknown_route(self):
        self.assertEqual(dispatch("GET", "/roast/temperature", {})[0], 404)
