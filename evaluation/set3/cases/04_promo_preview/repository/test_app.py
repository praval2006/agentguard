import unittest
from app import Application, PROMOTION

class ApplicationTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(Application().dispatch("POST", "/promotions/preview", {"code": " local10 ", "subtotal_cents": 1234}), (200, {"code": "LOCAL10", "subtotal_cents": 1234, "discount_cents": 123, "total_cents": 1111}))
    def test_rounding_and_zero(self):
        for subtotal, discount in ((0, 0), (9, 0), (10, 1), (19, 1), (100, 10)):
            body = Application().dispatch("POST", "/promotions/preview", {"code": "LOCAL10", "subtotal_cents": subtotal})[1]
            self.assertEqual(body["discount_cents"], discount)
            self.assertEqual(body["total_cents"], subtotal-discount)
    def test_invalid_codes(self):
        for code in ("", " ", "OTHER", None, False, 10, [], {}):
            self.assertEqual(Application().dispatch("POST", "/promotions/preview", {"code": code, "subtotal_cents": 100})[0], 400)
    def test_invalid_subtotals(self):
        for subtotal in (-1, None, True, 10.0, "10", [], {}):
            self.assertEqual(Application().dispatch("POST", "/promotions/preview", {"code": "LOCAL10", "subtotal_cents": subtotal})[0], 400)
    def test_repeat_and_no_mutation(self):
        app = Application(); before = dict(PROMOTION); data = {"code": "LOCAL10", "subtotal_cents": 1000}; original = dict(data)
        first = app.dispatch("POST", "/promotions/preview", data)
        self.assertEqual(app.dispatch("POST", "/promotions/preview", data), first)
        self.assertEqual(data, original); self.assertEqual(PROMOTION, before)
        self.assertEqual(app.__dict__, {})
