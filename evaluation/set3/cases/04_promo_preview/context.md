# Repository context

# API interface

POST /promotions/preview takes code and subtotal_cents. The published promotion is
LOCAL10 for ten percent off. Code comparison trims surrounding whitespace and ignores
case. subtotal_cents is a nonnegative integer excluding booleans. HTTP 200 returns
canonical code, subtotal_cents, discount_cents (rounded down) and total_cents.
Invalid code/subtotal returns 400 with error text. PROMOTION in app.py is the local
published configuration. The operation calculates a preview without storing orders,
charging payments or consuming promotion state; repeat previews use the same rule.

All routes use JSON objects. Unknown routes return 404 with error text.

File: repository/app.py
```python
PROMOTION = {"code": "LOCAL10", "percent": 10}

class Application:
    def dispatch(self, method, path, data):
        if (method, path) != ("POST", "/promotions/preview"):
            return 404, {"error": "Route not found"}
        code = data.get("code")
        subtotal = data.get("subtotal_cents")
        if type(code) is not str or code.strip().upper() != PROMOTION["code"]:
            return 400, {"error": "Provide a recognized promotion code"}
        if type(subtotal) is not int or subtotal < 0:
            return 400, {"error": "Subtotal must be nonnegative integer cents"}
        discount = subtotal * PROMOTION["percent"] // 100
        return 200, {"code": PROMOTION["code"], "subtotal_cents": subtotal,
                     "discount_cents": discount, "total_cents": subtotal - discount}
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
cd evaluation/set3/cases/04_promo_preview/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```
