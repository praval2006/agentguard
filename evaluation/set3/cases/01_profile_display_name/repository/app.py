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
