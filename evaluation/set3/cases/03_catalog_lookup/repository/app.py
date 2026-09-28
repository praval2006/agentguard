from copy import deepcopy

CATALOG = (
    {"code": "ST-210", "name": "Linen Notebook", "unit_price_cents": 1400, "available": True},
    {"code": "ST-110", "name": "Pocket Notebook", "unit_price_cents": 800, "available": False},
    {"code": "ST-310", "name": "Graphite Pencil", "unit_price_cents": 250, "available": True},
)

class Application:
    def __init__(self, catalog=None):
        self.catalog = deepcopy(CATALOG if catalog is None else catalog)

    def dispatch(self, method, path, data):
        if (method, path) != ("POST", "/catalog/search"):
            return 404, {"error": "Route not found"}
        term = data.get("term")
        if type(term) is not str or not term.strip():
            return 400, {"error": "Search term must be nonblank text"}
        term = term.strip().casefold()
        matches = [dict(row) for row in self.catalog if term in row["name"].casefold()]
        matches.sort(key=lambda row: row["code"])
        return 200, {"items": matches}
