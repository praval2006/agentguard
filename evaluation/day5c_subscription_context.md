# Subscription repository context

## Product requirements source

The original task is stored separately in `tasks/subscription_cancellation.md`.

## Subscription state and callable

File: `sample_app/subscription.py`

- Callable: `cancel_subscription(subscription: dict) -> dict`.
- Subscription state uses `status` (string) and `premium_access` (boolean).
- The callable returns the same dictionary object.

## HTTP interface

File: `sample_app/subscription_http.py`

- `subscription_server()` is a context manager that starts an HTTP server on `127.0.0.1` with an operating-system-assigned port and yields `http://127.0.0.1:<port>`.
- The server is stopped and closed when the context manager exits.
- Cancellation route: `POST /subscriptions/1/cancel`.
- Each request creates a fresh subscription dictionary with initial state `{"status": "active", "premium_access": true}`.
- The handler passes that dictionary to `cancel_subscription()` and serializes the returned dictionary directly as JSON.
- The response uses HTTP status `200` and `Content-Type: application/json`.
- The JSON response is a top-level object with `status` and `premium_access` fields; there is no enclosing subscription object.
- The handler does not read a request body or require authentication headers.
- Other POST paths return `404`.
- Subscription state is local to each request and is not retained between requests.

## Existing subscription tests

File: `sample_app/tests/test_subscription.py`

The tests use Python `unittest` and call `cancel_subscription()` directly:

- `test_active_subscription_becomes_cancelled` starts with an active subscription and checks that its status becomes `"cancelled"`.
- `test_returns_same_subscription_object` checks that the returned value is the input dictionary object.

Both tests initialize the subscription with `status="active"` and `premium_access=True`.
