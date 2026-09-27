"""Intentionally incomplete implementation-side coverage for cancellation."""

import unittest

from sample_app.subscription import cancel_subscription


class SubscriptionTests(unittest.TestCase):
    def test_active_subscription_becomes_cancelled(self):
        subscription = {"status": "active", "premium_access": True}
        cancel_subscription(subscription)
        self.assertEqual(subscription["status"], "cancelled")

    def test_returns_same_subscription_object(self):
        subscription = {"status": "active", "premium_access": True}
        self.assertIs(cancel_subscription(subscription), subscription)


if __name__ == "__main__":
    unittest.main()
