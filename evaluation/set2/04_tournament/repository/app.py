def standings(entrants):
    return sorted([dict(row) for row in entrants], key=lambda row: -row["points"])

def dispatch(method, path, data):
    if (method, path) != ("POST", "/standings/preview"):
        return 404, {"error": "Unknown route"}
    entrants = data.get("entrants")
    if not isinstance(entrants, list) or any(not isinstance(row, dict) or set(row) != {"name", "points"} or not isinstance(row["name"], str) or type(row["points"]) is not int for row in entrants):
        return 400, {"error": "Provide names and integer points"}
    return 200, {"standings": standings(entrants)}
