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
