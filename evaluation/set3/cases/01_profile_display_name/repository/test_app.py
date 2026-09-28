import unittest
from app import Application

class ApplicationTests(unittest.TestCase):
    def test_update_and_read(self):
        profile = {"display_name": "Before", "language": "fr"}
        app = Application(profile)
        self.assertEqual(app.dispatch("PATCH", "/profile", {"display_name": "  River  "}), (200, {"display_name": "River", "language": "fr"}))
        self.assertEqual(profile["display_name"], "River")
        self.assertEqual(app.dispatch("GET", "/profile", {})[1], profile)
    def test_reject_without_mutation(self):
        app = Application(); before = dict(app.profile)
        for value in ("", " ", "\t\n", None, 3, False, [], {}):
            with self.subTest(value=value):
                self.assertEqual(app.dispatch("PATCH", "/profile", {"display_name": value})[0], 400)
                self.assertEqual(app.profile, before)
    def test_unrelated_fields(self):
        app = Application()
        app.dispatch("PATCH", "/profile", {"display_name": "Sky", "language": "fr"})
        self.assertEqual(app.profile["language"], "en")
    def test_response_detached(self):
        app = Application(); body = app.dispatch("GET", "/profile", {})[1]
        body["display_name"] = "Different"
        self.assertEqual(app.profile["display_name"], "Guest")
    def test_omitted_name(self):
        self.assertEqual(Application().dispatch("PATCH", "/profile", {})[0], 400)
