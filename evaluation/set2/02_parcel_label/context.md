# Repository context: Parcel label preview

File: repository/app.py
```python
def dispatch(method, path, data):
    if (method, path) != ("POST", "/labels/preview"):
        return 404, {"error": "Unknown route"}
    recipient, postal = data.get("recipient"), data.get("postal_code")
    if not isinstance(recipient, str) or not isinstance(postal, str) or not recipient.strip() or not postal.strip():
        return 400, {"error": "Recipient and postal code required"}
    return 200, {"label": {"recipient": recipient.strip(), "postal_code": postal.strip().upper(), "service": "standard"}}
```

HTTP adapter: repository/server.py exposes application_server(), yielding an
http://127.0.0.1:<allocated-port> base URL. It uses evaluation/set2/http_server.py.
GET and POST dispatch to app.py; POST reads a JSON object, responses are JSON with
the integer status and body returned by dispatch. Invalid JSON returns 400.
Run with the repository and project root on Python's import path.
Requests use only their supplied data; the application retains no state between requests.

Implementation tests: repository/test_app.py, ApplicationTests.
Command from project root:
```sh
cd evaluation/set2/02_parcel_label/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```
