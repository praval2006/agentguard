import unittest
from app import Application

class ApplicationTests(unittest.TestCase):
    def test_inclusive_limits(self):
        app = Application()
        for weight, total in ((100, 600), (30000, 3500)):
            self.assertEqual(app.dispatch("POST", "/shipping/quote", {"weight_grams": weight}), (200, {"weight_grams": weight, "total_cents": total, "currency": "AUD"}))
    def test_started_kilograms(self):
        for weight, total in ((999, 600), (1000, 600), (1001, 700), (2000, 700)):
            self.assertEqual(Application().dispatch("POST", "/shipping/quote", {"weight_grams": weight})[1]["total_cents"], total)
    def test_reject_invalid(self):
        for value in (99, 30001, -1, 100.0, 100.5, True, "100", None, [], {}):
            status, body = Application().dispatch("POST", "/shipping/quote", {"weight_grams": value})
            self.assertEqual(status, 400); self.assertTrue(body["error"])
    def test_repeat_quote(self):
        app = Application(); data = {"weight_grams": 1500}
        self.assertEqual(app.dispatch("POST", "/shipping/quote", data), app.dispatch("POST", "/shipping/quote", data))
    def test_no_weight(self):
        self.assertEqual(Application().dispatch("POST", "/shipping/quote", {})[0], 400)
