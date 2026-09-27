"""Controlled acceptance fixture: premium access is intentionally left enabled."""


def cancel_subscription(subscription: dict) -> dict:
    """Mark cancelled, intentionally omitting premium-access revocation."""
    subscription["status"] = "cancelled"
    return subscription
