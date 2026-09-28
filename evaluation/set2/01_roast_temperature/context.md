# Repository context: Roast temperature validation

File: repository/app.py
```python
def dispatch(method, path, data):
    if (method, path) != ("POST", "/roast/temperature"):
        return 404, {"error": "Unknown route"}
    value = data.get("temperature")
    if type(value) is not int or not 160 <= value <= 240:
        return 400, {"error": "Use a whole-number temperature from 160 to 240 C"}
    return 200, {"temperature": value, "unit": "C"}
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
cd evaluation/set2/01_roast_temperature/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```
