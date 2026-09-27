# Subscription Cancellation

## Original Task

Add subscription cancellation.

When a user cancels an active subscription:

- the subscription should become cancelled;
- the user should no longer have access to premium features;
- repeated cancellation should not crash the application.

## Acceptance Intent

The implementation should leave the subscription in a consistent cancelled state and prevent a cancelled subscription from retaining premium access.
