"""Controlled loopback HTTP observations; all verdicts come from the verifier."""

import http.client
import io
import json
import re
import socket
import time

from .scenarios import validate_scenario
from .verifier import verify_observation, _json_available

TIMEOUT_SECONDS = 2.0
MAX_BODY_BYTES = 32_768
MAX_REQUEST_BYTES = 32_768
MAX_PATH_CHARS = 2048
MAX_HEADER_BYTES = 8192
_BLOCKED_HEADERS = {
    "host", "content-length", "transfer-encoding", "connection", "proxy-authorization",
    "proxy-connection", "keep-alive", "te", "trailer", "upgrade", "expect",
    "accept-encoding", "cookie", "cookie2",
}
_TOKEN = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")


def _remaining(deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError()
    return remaining


class _Reader(io.RawIOBase):
    def __init__(self, sock):
        self.sock = sock

    def close(self):
        self.sock.close()
        super().close()

    def readable(self):
        return True

    def readinto(self, buffer):
        self.sock.settimeout(_remaining(self.sock.deadline))
        return self.sock.recv_into(buffer)


class _DeadlineSocket(socket.socket):
    def makefile(self, mode="r", buffering=None, **kwargs):
        # HTTPResponse asks only for a binary read stream.
        if mode != "rb":
            raise ValueError("Unsupported transport stream")
        reader_socket = self.dup()
        reader_socket.deadline = self.deadline
        return io.BufferedReader(_Reader(reader_socket))


def _request_policy(action, base_url):
    match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})", base_url) if type(base_url) is str else None
    if not match or not 1 <= int(match[1]) <= 65535:
        raise ValueError("Base URL must be http://127.0.0.1:<port> with port 1..65535")
    path = action["path"]
    if (len(path) > MAX_PATH_CHARS or path.startswith("//")
            or any(ord(c) <= 32 or ord(c) >= 127 or c in '\\#{}' for c in path)):
        raise ValueError("Path must be an ASCII origin path without fragments or unresolved placeholders")
    headers = dict(action.get("headers", {}))
    seen = set()
    size = 0
    for key, value in headers.items():
        lower = key.lower()
        if (not _TOKEN.fullmatch(key) or lower in seen or lower in _BLOCKED_HEADERS
                or lower.startswith("proxy-") or any(ord(c) < 32 or ord(c) >= 127 for c in value)):
            raise ValueError("Header violates request policy")
        size += len(key) + len(value)
        seen.add(lower)
    if size > MAX_HEADER_BYTES:
        raise ValueError("Headers exceed size limit")
    body = None
    if "json" in action:
        if not _json_available(action["json"]):
            raise ValueError("Request JSON is invalid or exceeds bounds")
        body = json.dumps(action["json"], allow_nan=False, separators=(",", ":")).encode()
        if len(body) > MAX_REQUEST_BYTES:
            raise ValueError("Request body exceeds size limit")
        if "content-type" not in seen:
            headers["Content-Type"] = "application/json"
    headers["Accept-Encoding"] = "identity"
    return int(match[1]), path, headers, body


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def execute_http_scenario(scenario: dict, *, base_url: str) -> dict:
    """Validate and execute one request against numeric IPv4 loopback only.

    No redirects, DNS, proxy lookup, cookies, substitution or recorder integration.
    A 2-second shared connect/send/header/body deadline and 32768-byte body cap
    apply. Header parsing uses http.client's line/count limits. The report envelope
    contains metadata only; observation may contain complete bounded parsed JSON
    for verification, so callers must treat it as potentially sensitive evidence.
    No raw body, request headers/body, URL query or cookies are copied to metadata.
    Assertions select the reportable evidence through the existing verifier.
    """
    validate_scenario(scenario)
    if scenario["action"]["type"] != "http_request":
        raise ValueError("execute_http_scenario requires an http_request scenario")
    evidence = {"established": False, "reason": None, "method": scenario["action"]["method"],
                "status": None, "body_truncated": False, "json_available": False}
    observation = None
    try:
        port, path, headers, body = _request_policy(scenario["action"], base_url)
    except (ValueError, TypeError, RecursionError):
        evidence["reason"] = "HTTP request rejected by loopback/request policy"
    else:
        connection = http.client.HTTPConnection("127.0.0.1", port)
        sock = None
        try:
            deadline = time.monotonic() + TIMEOUT_SECONDS
            sock = _DeadlineSocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.deadline = deadline
            sock.settimeout(_remaining(deadline))
            sock.connect(("127.0.0.1", port))
            connection.sock = sock
            sock.settimeout(_remaining(deadline))
            connection.request(scenario["action"]["method"], path, body=body, headers=headers)
            with connection.getresponse() as response:
                if type(response.status) is not int or not 100 <= response.status <= 599:
                    raise ValueError("Invalid status")
                lengths = response.headers.get_all("Content-Length", [])
                transfers = response.headers.get_all("Transfer-Encoding", [])
                if (len(lengths) > 1 or len(transfers) > 1 or (lengths and transfers)
                        or (lengths and not re.fullmatch(r"[0-9]+", lengths[0]))
                        or (transfers and transfers[0].lower() != "chunked")):
                    raise ValueError("Invalid response framing")
                observation = {"type": "http_response", "status": response.status}
                evidence.update(established=True, status=response.status)
                try:
                    raw = response.read(MAX_BODY_BYTES + 1)
                    truncated = len(raw) > MAX_BODY_BYTES
                    evidence["body_truncated"] = truncated
                    incomplete = response.length not in (None, 0)
                    if truncated or incomplete:
                        evidence["reason"] = "Response body exceeds limit or is incomplete"
                    elif response.headers.get("Content-Encoding", "identity").lower() != "identity":
                        evidence["reason"] = "Encoded response body is not supported"
                    else:
                        try:
                            parsed = json.loads(raw, object_pairs_hook=_pairs)
                            if not _json_available(parsed):
                                raise ValueError("Invalid JSON values")
                        except (ValueError, UnicodeError, RecursionError):
                            evidence["reason"] = "Complete bounded parsed JSON unavailable"
                        else:
                            observation["json"] = parsed
                            evidence["json_available"] = True
                except (OSError, http.client.HTTPException):
                    evidence["reason"] = "Response body could not be completely observed"
        except (OSError, http.client.HTTPException, ValueError):
            evidence["reason"] = "HTTP response could not be established"
        finally:
            connection.close()
            if sock is not None:
                sock.close()
    result = verify_observation(scenario, observation)
    if observation is None:
        result["reason"] = evidence["reason"]
    return {"execution": evidence, "observation": observation, "result": result}
