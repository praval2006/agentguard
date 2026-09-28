import unittest
from app import dispatch

class ApplicationTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(dispatch("POST", "/labels/preview", {"recipient": " Ada Lane ", "postal_code": " ab12 "}), (200, {"label": {"recipient": "Ada Lane", "postal_code": "AB12", "service": "standard"}}))
    def test_blank_fields(self):
        for data in ({"recipient": " ", "postal_code": "AB12"}, {"recipient": "Ada", "postal_code": ""}, {}):
            self.assertEqual(dispatch("POST", "/labels/preview", data)[0], 400)
    def test_independent_previews(self):
        data = {"recipient": "Ada", "postal_code": "AB12"}
        self.assertEqual(dispatch("POST", "/labels/preview", data), dispatch("POST", "/labels/preview", data))
