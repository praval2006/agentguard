# Repository context

# API interface

PATCH /profile accepts {"display_name": string}. display_name is arbitrary nonblank
text, with no format, enum, identity or uniqueness requirement. Surrounding whitespace
is removed before storage. HTTP 200 returns the current profile object with the stored
display_name and other existing fields. Invalid input returns 400 with error text.
GET /profile returns that same stored representation with 200.
The caller owns the current profile dictionary; updates persist in that dictionary.
application_server() without arguments starts with display_name Guest and language en.
State belongs to that server instance; requests do not reset it. Other request fields
are ignored and do not alter unrelated profile fields.

All routes use JSON objects. Unknown routes return 404 with error text.

File: repository/app.py
```python
class Application:
    def __init__(self, profile=None):
        self.profile = profile if profile is not None else {"display_name": "Guest", "language": "en"}

    def dispatch(self, method, path, data):
        if (method, path) == ("GET", "/profile"):
            return 200, dict(self.profile)
        if (method, path) != ("PATCH", "/profile"):
            return 404, {"error": "Route not found"}
        value = data.get("display_name")
        if type(value) is not str or not value.strip():
            return 400, {"error": "Display name must be nonblank text"}
        self.profile["display_name"] = value.strip()
        return 200, dict(self.profile)
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
cd evaluation/set3/cases/01_profile_display_name/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```
