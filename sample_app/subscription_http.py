"""Controlled demo HTTP fixture, not a production subscription service."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

from . import subscription


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        if self.path != "/subscriptions/1/cancel":
            self.send_error(404)
            return
        state = {"status": "active", "premium_access": True}
        result = subscription.cancel_subscription(state)
        body = json.dumps(result, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@contextmanager
def subscription_server():
    """Yield a trusted ephemeral numeric-loopback origin; always stop the server.

    Each request starts with fresh controlled state, so this fixture does not
    independently establish repeated cancellation of the same subscription.
    """
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    try:
        thread.start()
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        if thread.is_alive():
            server.shutdown()
            thread.join()
        server.server_close()
