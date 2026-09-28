# Repository context

# API interface

POST /shipping/quote takes weight_grams, an integer from 100 through 30000 inclusive.
Booleans and all other types are rejected. Invalid values return 400 with error text.
HTTP 200 returns weight_grams, total_cents (integer), and currency AUD. The tariff is
500 cents plus 100 cents per started kilogram. Quotes do not persist state or invoke
shipment/payment services; there are no shipment or payment routes in this application.

All routes use JSON objects. Unknown routes return 404 with error text.

File: repository/app.py
```python
class Application:
    def dispatch(self, method, path, data):
        if (method, path) != ("POST", "/shipping/quote"):
            return 404, {"error": "Route not found"}
        weight = data.get("weight_grams")
        if type(weight) is not int or not 100 <= weight <= 30000:
            return 400, {"error": "Weight must be whole grams from 100 through 30000"}
        charge = 500 + 100 * ((weight + 999) // 1000)
        return 200, {"weight_grams": weight, "total_cents": charge, "currency": "AUD"}
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
cd evaluation/set3/cases/02_shipping_weight_quote/repository && python3 -B -m unittest discover -s . -p 'test_*.py' -v
```
