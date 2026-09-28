import unittest
from app import gross_pay

class WeeklyPayCheck(unittest.TestCase):
    def test_weekly_gross(self):
        for hours, rate, cents in ((0, 1800, 0), (10, 1800, 18000), (40, 1800, 72000), (41, 1800, 74700), (45, 2400, 114000)):
            with self.subTest(hours=hours, rate=rate):
                self.assertEqual(gross_pay(hours, rate), cents)
