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
