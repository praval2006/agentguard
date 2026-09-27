from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import threading
import time
import unittest
from unittest.mock import patch

from agentguard import http_execution as http
from agentguard.verifier import verify_observation


def scenario(path='/', expected=200, assertions=None, **action):
    return {'name': 'HTTP check', 'source': 'explicit', 'reason': 'Requested response',
            'action': {'type': 'http_request', 'method': 'GET', 'path': path, **action},
            'assertions': assertions or [{'type': 'status', 'equals': expected}]}


def field(value, path='item.state'):
    return [{'type': 'json_field', 'path': path, 'equals': value}]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def do_GET(self):
        self.server.requests.append(self.path)
        if self.path == '/slow': time.sleep(0.2)
        code = int(self.path[1:]) if self.path in ('/404', '/500', '/302') else 200
        body = b'{"item":{"state":"ready"}}'
        if self.path == '/large': body = b'"' + b'x' * (http.MAX_BODY_BYTES + 1) + b'"'
        if self.path == '/text': body = b'hello'
        if self.path == '/bad': body = b'{"x":'
        if self.path == '/duplicate': body = b'{"x":1,"x":2}'
        self.send_response(code)
        if code == 302: self.send_header('Location', 'http://example.invalid/never')
        self.send_header('Content-Length', str(len(body) + (10 if self.path == '/short' else 0)))
        self.end_headers()
        try: self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError): pass

    def do_POST(self):
        self.server.received = (self.command, self.headers, self.rfile.read(int(self.headers.get('Content-Length', 0))))
        self.do_GET()

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST


class HttpExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.server.daemon_threads = True
        cls.server.requests = []
        cls.thread = threading.Thread(target=cls.server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def run_http(self, s=None, **kwargs):
        return http.execute_http_scenario(s or scenario(), base_url=kwargs.get('base_url', self.url))

    def reject(self, s=None, base_url=None):
        with patch('agentguard.http_execution._DeadlineSocket') as connect:
            r = self.run_http(s, base_url=base_url or self.url)
        connect.assert_not_called()
        self.assertEqual(r['result']['verdict'], 'UNVERIFIED')
        self.assertFalse(r['execution']['established'])

    def test_get_pass_and_verifier_delegation(self):
        with patch('agentguard.http_execution.verify_observation', wraps=verify_observation) as verify:
            r = self.run_http()
        self.assertEqual(r['result']['verdict'], 'PASS')
        self.assertEqual(verify.call_args.args[1], r['observation'])

    def test_status_mismatch_delegates_fail(self):
        with patch('agentguard.http_execution.verify_observation', wraps=verify_observation) as verify:
            r = self.run_http(scenario(expected=201))
        self.assertEqual(r['result']['verdict'], 'FAIL')
        verify.assert_called_once()

    def test_json_nested_pass(self):
        self.assertEqual(self.run_http(scenario(assertions=field('ready')))['result']['verdict'], 'PASS')

    def test_json_mismatch(self):
        self.assertEqual(self.run_http(scenario(assertions=field('other')))['result']['verdict'], 'FAIL')

    def test_real_404(self):
        r = self.run_http(scenario('/404', 404))
        self.assertTrue(r['execution']['established'])
        self.assertEqual(r['result']['verdict'], 'PASS')

    def test_real_500(self):
        r = self.run_http(scenario('/500'))
        self.assertTrue(r['execution']['established'])
        self.assertEqual(r['result']['verdict'], 'FAIL')

    def test_post_json(self):
        self.run_http(scenario(method='POST', json={'value': 'hello'}))
        method, headers, body = self.server.received
        self.assertEqual(method, 'POST')
        self.assertEqual(json.loads(body), {'value': 'hello'})
        self.assertEqual(headers['Content-Type'], 'application/json')

    def test_safe_headers_and_other_methods(self):
        for method in ('PUT', 'PATCH', 'DELETE'):
            self.run_http(scenario(method=method, json={}, headers={'X-Case': 'safe', 'Content-Type': 'application/example+json'}))
            self.assertEqual(self.server.received[0], method)
            self.assertEqual(self.server.received[1]['X-Case'], 'safe')
            self.assertEqual(self.server.received[1]['Content-Type'], 'application/example+json')

    def test_host_override(self): self.reject(scenario(headers={'hOsT': 'example.invalid'}))

    def test_framing_and_hop_headers(self):
        for header in ('Content-Length', 'Transfer-Encoding', 'Connection', 'Proxy-Authorization', 'Proxy-Connection', 'TE', 'Trailer', 'Upgrade', 'Expect', 'Cookie'):
            self.reject(scenario(headers={header: 'x'}))

    def test_nonloopback(self): self.reject(base_url='http://192.0.2.1:80')

    def test_domains(self):
        for host in ('localhost', 'example.invalid', '127.0.0.1.example.invalid'):
            self.reject(base_url=f'http://{host}:80')

    def test_https(self): self.reject(base_url=self.url.replace('http:', 'https:'))

    def test_base_components_and_ports(self):
        for url in (self.url + '/', self.url + '?x=1', self.url + '#x', 'http://user@127.0.0.1:80',
                    'http://127.0.0.1:0', 'http://127.0.0.1:65536', 'http://127.0.0.1:abc', 'http://127.0.0.1', 'http://127.0.0.1:080'):
            self.reject(base_url=url)

    def test_paths_and_placeholders(self):
        for path in ('//example.invalid/x', '/\\host', '/x#y', '/{id}', '/bad\r\nHost:x'):
            self.reject(scenario(path))

    def test_redirect_not_followed(self):
        before = len(self.server.requests)
        r = self.run_http(scenario('/302', 302))
        self.assertEqual(r['result']['verdict'], 'PASS')
        self.assertEqual(len(self.server.requests), before + 1)

    def test_timeout_before_headers(self):
        with patch.object(http, 'TIMEOUT_SECONDS', 0.05):
            r = self.run_http(scenario('/slow'))
        self.assertEqual(r['result']['verdict'], 'UNVERIFIED')
        self.assertIsNone(r['observation'])

    def test_connection_failure(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            # Bound but not listening guarantees refusal while retaining the port.
            r = self.run_http(base_url=f'http://127.0.0.1:{sock.getsockname()[1]}')
        self.assertEqual(r['result']['verdict'], 'UNVERIFIED')

    def test_oversized_body(self):
        r = self.run_http(scenario('/large', assertions=[{'type': 'status', 'equals': 200}, *field('ready')]))
        self.assertTrue(r['execution']['body_truncated'])
        self.assertNotIn('json', r['observation'])
        self.assertEqual(r['result']['verdict'], 'UNVERIFIED')
        self.assertEqual(r['result']['assertions'][0]['verdict'], 'PASS')

    def test_non_json_status(self):
        self.assertEqual(self.run_http(scenario('/text'))['result']['verdict'], 'PASS')

    def test_malformed_json_and_incomplete_body(self):
        for path in ('/bad', '/short', '/duplicate'):
            r = self.run_http(scenario(path, assertions=field('ready')))
            self.assertEqual(r['result']['verdict'], 'UNVERIFIED')
            self.assertTrue(r['execution']['established'])
            self.assertNotIn('json', r['observation'])

    def test_not_mutated_or_sensitive_metadata(self):
        s = scenario(method='POST', headers={'Authorization': 'secret'}, json={'password': 'private'})
        before = deepcopy(s)
        r = self.run_http(s)
        self.assertEqual(s, before)
        self.assertNotIn('secret', str(r))
        self.assertNotIn('private', str(r))

    def test_no_dns_or_proxies(self):
        with patch('socket.getaddrinfo', side_effect=AssertionError('DNS')), patch.dict('os.environ', {'http_proxy': 'http://example.invalid:1', 'HTTP_PROXY': 'http://example.invalid:1'}):
            self.assertEqual(self.run_http()['result']['verdict'], 'PASS')

    def test_invalid_header_injection_and_request_json(self):
        self.reject(scenario(headers={'X-Test': 'safe\r\nHost: evil'}))
        self.reject(scenario(json={'v': float('nan')}))
        self.reject(scenario(json={'v': 'x' * 40000}))

    def test_non_http_and_invalid_scenario(self):
        with self.assertRaises(ValueError): http.execute_http_scenario({}, base_url=self.url)
        s = {'name': 'x', 'source': 'explicit', 'reason': 'x', 'action': {'type': 'unsupported', 'explanation': 'x'}}
        with self.assertRaises(ValueError): self.run_http(s)
