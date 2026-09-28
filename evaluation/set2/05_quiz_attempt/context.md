# Repository context: Arithmetic practice attempts

File: repository/app.py
```python
class Practice:
    def __init__(self):
        self.attempts = {}
        self.next_id = 1

    def dispatch(self, method, path, data):
        if (method, path) == ("POST", "/practice/attempts"):
            identifier = str(self.next_id)
            self.next_id += 1
            self.attempts[identifier] = {"id": identifier, "question": "7 + 5", "answer": None, "correct": None}
            return 201, {"id": identifier, "question": "7 + 5"}
        parts = path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["practice", "attempts"] or parts[2] not in self.attempts:
            return 404, {"error": "Attempt not found"}
        attempt = self.attempts[parts[2]]
        if method == "POST":
            answer = data.get("answer")
            if type(answer) is not int:
                return 400, {"error": "Whole-number answer required"}
            attempt.update(answer=answer, correct=answer == 12)
        elif method != "GET":
            return 404, {"error": "Unknown route"}
        return 200, dict(attempt)
```

HTTP adapter: repository/server.py exposes application_server(), yielding an
http://127.0.0.1:<allocated-port> base URL. It uses evaluation/set2/http_server.py.
GET and POST dispatch to app.py; POST reads a JSON object, responses are JSON with
the integer status and body returned by dispatch. Invalid JSON returns 400.
Run with the repository and project root on Python's import path.
Each server instance owns one Practice instance. Its in-memory attempts persist across requests until the server closes. Identifiers are allocated at runtime; clients use the returned id.

Implementation tests: repository/test_app.py, ApplicationTests.
Command from project root:
```sh
cd evaluation/set2/05_quiz_attempt/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```
