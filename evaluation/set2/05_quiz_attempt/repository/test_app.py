import unittest
from app import Practice

class ApplicationTests(unittest.TestCase):
    def test_submit_and_revisit(self):
        app = Practice()
        status, created = app.dispatch("POST", "/practice/attempts", {})
        self.assertEqual(status, 201)
        path = "/practice/attempts/" + created["id"]
        self.assertEqual(app.dispatch("POST", path, {"answer": 12})[0], 200)
        result = app.dispatch("GET", path, {})[1]
        self.assertEqual(result["answer"], 12)
        self.assertIs(result["correct"], True)
    def test_separate_attempts(self):
        app = Practice()
        first = app.dispatch("POST", "/practice/attempts", {})[1]["id"]
        second = app.dispatch("POST", "/practice/attempts", {})[1]["id"]
        self.assertNotEqual(first, second)
        app.dispatch("POST", "/practice/attempts/" + first, {"answer": 10})
        self.assertIs(app.dispatch("GET", "/practice/attempts/" + first, {})[1]["correct"], False)
        self.assertIsNone(app.dispatch("GET", "/practice/attempts/" + second, {})[1]["answer"])
    def test_unknown_attempt(self):
        self.assertEqual(Practice().dispatch("GET", "/practice/attempts/42", {})[0], 404)
