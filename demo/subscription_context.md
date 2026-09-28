Subscription cancellation is exposed through the controlled HTTP interface.

Endpoint:
POST /subscriptions/1/cancel

The endpoint starts with a subscription containing:
- status: "active"
- premium_access: true

A successful cancellation returns HTTP 200 with a JSON object representing the resulting subscription state.

The response contains:
- status
- premium_access

The cancellation requirement is implemented by sample_app.subscription.cancel_subscription.

The HTTP fixture starts from fresh subscription state for every request. Therefore this interface does not provide an observation of repeated cancellation on the same persisted subscription.
