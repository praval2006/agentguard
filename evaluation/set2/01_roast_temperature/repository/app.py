def dispatch(method, path, data):
    if (method, path) != ("POST", "/roast/temperature"):
        return 404, {"error": "Unknown route"}
    value = data.get("temperature")
    if type(value) is not int or not 160 <= value <= 240:
        return 400, {"error": "Use a whole-number temperature from 160 to 240 C"}
    return 200, {"temperature": value, "unit": "C"}
