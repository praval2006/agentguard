# Repository context

# API interface

POST /catalog/search takes term as nonblank text, trims it, and matches product-name
substrings case-insensitively. HTTP 200 returns items, an array of objects with code,
name, unit_price_cents and available; objects are ordered by code. No matches returns
items as an empty array. Invalid term input returns 400 with error text. The local
stationery catalog is defined in app.py; search does not update it. Each application
owns a copy of its catalog. No remote service is used.

All routes use JSON objects. Unknown routes return 404 with error text.

File: repository/app.py
```python
from copy import deepcopy

CATALOG = (
    {"code": "ST-210", "name": "Linen Notebook", "unit_price_cents": 1400, "available": True},
    {"code": "ST-110", "name": "Pocket Notebook", "unit_price_cents": 800, "available": False},
    {"code": "ST-310", "name": "Graphite Pencil", "unit_price_cents": 250, "available": True},
)

class Application:
    def __init__(self, catalog=None):
        self.catalog = deepcopy(CATALOG if catalog is None else catalog)

    def dispatch(self, method, path, data):
        if (method, path) != ("POST", "/catalog/search"):
            return 404, {"error": "Route not found"}
        term = data.get("term")
        if type(term) is not str or not term.strip():
            return 400, {"error": "Search term must be nonblank text"}
        term = term.strip().casefold()
        matches = [dict(row) for row in self.catalog if term in row["name"].casefold()]
        matches.sort(key=lambda row: row["code"])
        return 200, {"items": matches}
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
cd evaluation/set3/cases/03_catalog_lookup/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```
