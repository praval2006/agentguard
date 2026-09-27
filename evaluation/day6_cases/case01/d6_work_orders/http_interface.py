import json
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from .feature import start_order

@contextmanager
def server():
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != '/work-orders/start':
                self.reply(404, {'error': 'Unknown route'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size < 0 or size > 4096:
                    raise ValueError('Invalid request size')
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError('Use a JSON object')
                result = start_order(dict(payload['order']))
                self.reply(200, result)
            except (ValueError, KeyError, TypeError) as error:
                self.reply(400, {'error': str(error)})

        def reply(self, status, value):
            body = json.dumps(value).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{httpd.server_port}'
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()
