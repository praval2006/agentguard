import unittest
from app import Application, CATALOG
from copy import deepcopy

class ApplicationTests(unittest.TestCase):
    def test_matching_order_and_fields(self):
        result = Application().dispatch("POST", "/catalog/search", {"term": " NOTEBOOK "})
        self.assertEqual(result, (200, {"items": [dict(CATALOG[1]), dict(CATALOG[0])]}))
    def test_no_matches(self):
        self.assertEqual(Application().dispatch("POST", "/catalog/search", {"term": "fountain pen"}), (200, {"items": []}))
    def test_invalid_terms(self):
        for term in ("", " ", None, True, 12, [], {}):
            self.assertEqual(Application().dispatch("POST", "/catalog/search", {"term": term})[0], 400)
    def test_catalog_preserved(self):
        app = Application(); before = deepcopy(app.catalog)
        body = app.dispatch("POST", "/catalog/search", {"term": "book"})[1]
        body["items"][0]["name"] = "Changed"
        self.assertEqual(app.catalog, before)
    def test_custom_catalog_copied(self):
        rows = [{"code": "A", "name": "Cup", "unit_price_cents": 400, "available": True}]
        app = Application(rows); rows[0]["name"] = "Changed"
        self.assertEqual(app.catalog[0]["name"], "Cup")
