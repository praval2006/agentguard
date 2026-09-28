class Application:
    def dispatch(self, method, path, data):
        if (method, path) != ("POST", "/shipping/quote"):
            return 404, {"error": "Route not found"}
        weight = data.get("weight_grams")
        if type(weight) is not int or not 100 <= weight <= 30000:
            return 400, {"error": "Weight must be whole grams from 100 through 30000"}
        charge = 500 + 100 * ((weight + 999) // 1000)
        return 200, {"weight_grams": weight, "total_cents": charge, "currency": "AUD"}
