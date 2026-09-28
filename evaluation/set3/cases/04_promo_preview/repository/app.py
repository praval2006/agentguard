PROMOTION = {"code": "LOCAL10", "percent": 10}

class Application:
    def dispatch(self, method, path, data):
        if (method, path) != ("POST", "/promotions/preview"):
            return 404, {"error": "Route not found"}
        code = data.get("code")
        subtotal = data.get("subtotal_cents")
        if type(code) is not str or code.strip().upper() != PROMOTION["code"]:
            return 400, {"error": "Provide a recognized promotion code"}
        if type(subtotal) is not int or subtotal < 0:
            return 400, {"error": "Subtotal must be nonnegative integer cents"}
        discount = subtotal * PROMOTION["percent"] // 100
        return 200, {"code": PROMOTION["code"], "subtotal_cents": subtotal,
                     "discount_cents": discount, "total_cents": subtotal - discount}
