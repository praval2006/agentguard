import unittest
from app import Application

class ApplicationTests(unittest.TestCase):
    def test_partial_update_and_read(self):
        prefs = {"email_enabled": True, "push_enabled": True, "daily_digest_hour": 17}
        app = Application(prefs)
        self.assertEqual(app.dispatch("PATCH", "/preferences", {"email_enabled": False}), (200, {"email_enabled": False, "push_enabled": True, "daily_digest_hour": 17}))
        self.assertIs(prefs["email_enabled"], False)
        self.assertEqual(app.dispatch("GET", "/preferences", {})[1], prefs)
    def test_both_channels(self):
        app = Application()
        self.assertEqual(app.dispatch("PATCH", "/preferences", {"email_enabled": False, "push_enabled": True})[1], {"email_enabled": False, "push_enabled": True, "daily_digest_hour": 9})
    def test_invalid_types_atomic(self):
        for field in ("email_enabled", "push_enabled"):
            for value in (0, 1, "false", None, 0.0, [], {}):
                app = Application(); before = dict(app.preferences)
                data = {"email_enabled": False, "push_enabled": True}; data[field] = value
                self.assertEqual(app.dispatch("PATCH", "/preferences", data)[0], 400)
                self.assertEqual(app.preferences, before)
    def test_invalid_keys_atomic(self):
        for data in ({}, {"daily_digest_hour": 10}, {"email_enabled": False, "unknown": True}):
            app = Application(); before = dict(app.preferences)
            self.assertEqual(app.dispatch("PATCH", "/preferences", data)[0], 400)
            self.assertEqual(app.preferences, before)
    def test_response_detached(self):
        app = Application(); result = app.dispatch("GET", "/preferences", {})[1]
        result["daily_digest_hour"] = 4
        self.assertEqual(app.preferences["daily_digest_hour"], 9)
