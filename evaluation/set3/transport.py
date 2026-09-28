"""Local JSON transport for small application dispatch objects."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread

@contextmanager
def serve(application):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            return
        def handle_request(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 0 or length > 8192:
                    raise ValueError("Request size")
                payload = json.loads(self.rfile.read(length)) if length else {}
                if type(payload) is not dict:
                    raise ValueError("JSON object required")
            except (ValueError, UnicodeError):
                status, body = 400, {"error": "Provide a JSON object of at most 8192 bytes"}
            else:
                status, body = application.dispatch(self.command, self.path, payload)
            encoded = json.dumps(body, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        do_GET = do_POST = do_PATCH = do_PUT = do_DELETE = handle_request
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
