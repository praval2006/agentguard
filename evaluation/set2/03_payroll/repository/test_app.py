import unittest
from app import gross_pay

class ApplicationTests(unittest.TestCase):
    def test_regular_hours(self):
        self.assertEqual(gross_pay(0, 2000), 0)
        self.assertEqual(gross_pay(40, 2000), 80000)
    def test_overtime(self):
        self.assertEqual(gross_pay(42, 2000), 86000)
    def test_invalid_inputs(self):
        for hours, rate in ((-1, 2000), (True, 2000), (2.5, 2000), (1, 0), (1, 2001)):
            with self.assertRaises(ValueError):
                gross_pay(hours, rate)
