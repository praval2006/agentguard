# Repository context: Tournament standings

File: repository/app.py
```python
def standings(entrants):
    return sorted([dict(row) for row in entrants], key=lambda row: -row["points"])

def dispatch(method, path, data):
    if (method, path) != ("POST", "/standings/preview"):
        return 404, {"error": "Unknown route"}
    entrants = data.get("entrants")
    if not isinstance(entrants, list) or any(not isinstance(row, dict) or set(row) != {"name", "points"} or not isinstance(row["name"], str) or type(row["points"]) is not int for row in entrants):
        return 400, {"error": "Provide names and integer points"}
    return 200, {"standings": standings(entrants)}
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
cd evaluation/set2/04_tournament/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```
