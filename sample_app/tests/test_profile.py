import unittest

from sample_app.profile import PROFILE, display_name


class ProfileTests(unittest.TestCase):
    def test_displays_name_from_actual_schema(self):
        self.assertEqual(display_name(PROFILE), "Pratik")

    def test_accepts_another_profile(self):
        self.assertEqual(display_name({"user_name": "Alex"}), "Alex")


if __name__ == "__main__":
    unittest.main()
