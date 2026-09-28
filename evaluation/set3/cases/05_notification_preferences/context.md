# Repository context

# API interface

PATCH /preferences accepts optional email_enabled and push_enabled, each strictly
boolean; at least one is required. Other fields and other types are rejected with
400 and error text. The complete update is validated before storing changes.
HTTP 200 returns email_enabled, push_enabled and daily_digest_hour. Omitted channel
values and daily_digest_hour retain their stored values. GET /preferences returns
the stored object with 200. The caller owns the current-user preference dictionary;
the application does not resolve users from request input. Default state for a new
server is email_enabled true, push_enabled false, daily_digest_hour 9. Updates persist
for that server instance. No notification delivery is performed by this API.

All routes use JSON objects. Unknown routes return 404 with error text.

File: repository/app.py
```python
class Application:
    def __init__(self, preferences=None):
        self.preferences = preferences if preferences is not None else {
            "email_enabled": True, "push_enabled": False, "daily_digest_hour": 9}

    def dispatch(self, method, path, data):
        if (method, path) == ("GET", "/preferences"):
            return 200, dict(self.preferences)
        if (method, path) != ("PATCH", "/preferences"):
            return 404, {"error": "Route not found"}
        allowed = {"email_enabled", "push_enabled"}
        if not data or not set(data) <= allowed or any(type(value) is not bool for value in data.values()):
            return 400, {"error": "Provide one or both boolean channel preferences"}
        self.preferences.update(data)
        return 200, dict(self.preferences)
```

File: repository/server.py
```python
from contextlib import contextmanager
from app import Application
from evaluation.set3.transport import serve

@contextmanager
def application_server(application=None):
    with serve(Application() if application is None else application) as base_url:
        yield base_url
```

The shared evaluation/set3/transport.py adapter binds numeric IPv4 loopback on an
ephemeral port and yields its base URL. It passes GET/POST/PATCH/PUT/DELETE and the
origin path to dispatch, reads JSON objects up to 8192 bytes, and returns the
application status/body as JSON. Malformed/non-object requests return 400.
The context manager shuts down the server on exit. No proxies/external services.
Import with the case repository and project root on sys.path.

Implementation tests: repository/test_app.py and repository/test_transport.py.
Command from project root:
```sh
cd evaluation/set3/cases/05_notification_preferences/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```
