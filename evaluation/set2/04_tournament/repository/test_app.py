import unittest
from app import dispatch

class ApplicationTests(unittest.TestCase):
    def test_points_order(self):
        rows = [{"name": "Lena", "points": 3}, {"name": "Omar", "points": 7}]
        self.assertEqual(dispatch("POST", "/standings/preview", {"entrants": rows})[1]["standings"], list(reversed(rows)))
    def test_empty(self):
        self.assertEqual(dispatch("POST", "/standings/preview", {"entrants": []}), (200, {"standings": []}))
    def test_input_preserved(self):
        rows = [{"name": "Lena", "points": 3}, {"name": "Omar", "points": 7}]
        dispatch("POST", "/standings/preview", {"entrants": rows})
        self.assertEqual(rows[0]["name"], "Lena")
