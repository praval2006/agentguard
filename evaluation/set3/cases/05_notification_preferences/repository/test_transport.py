import http.client
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from server import application_server

class TransportTests(unittest.TestCase):
    def test_json_interface(self):
        with application_server() as base_url:
            connection = http.client.HTTPConnection("127.0.0.1", int(base_url.rsplit(":", 1)[1]))
            try:
                connection.request('PATCH', '/preferences', body=json.dumps({'push_enabled': True}), headers={"Content-Type": "application/json"})
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIsInstance(json.loads(response.read()), dict)
                connection.request("GET", "/not-a-route")
                response = connection.getresponse(); self.assertEqual(response.status, 404); response.read()
                connection.request('PATCH', '/preferences', body="[]", headers={"Content-Type": "application/json"})
                response = connection.getresponse(); self.assertEqual(response.status, 400); response.read()
            finally:
                connection.close()
