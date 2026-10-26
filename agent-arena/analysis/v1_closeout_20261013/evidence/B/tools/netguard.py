"""Refuse every network connection and provider transport; count refused attempts.

Blocks httpx.Client.send, httpx.HTTPTransport.handle_request (plus async variants),
socket.socket.connect / connect_ex and socket.create_connection. Local AF_UNIX sockets are allowed.
Counts are appended as one JSON line to $NETGUARD_LOG at exit (expected: all zero).
"""
import atexit
import json
import os
import socket
import sys

for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    assert key not in os.environ, f"{key} present in environment"

COUNTS = {"httpx.Client.send": 0, "httpx.HTTPTransport.handle_request": 0, "httpx.AsyncClient.send": 0,
          "httpx.AsyncHTTPTransport.handle_async_request": 0, "socket.connect": 0, "socket.connect_ex": 0,
          "socket.create_connection": 0}
DETAILS = []

_orig_connect = socket.socket.connect
_orig_connect_ex = socket.socket.connect_ex


def _is_unix(sock, address):
    return isinstance(address, (str, bytes)) or getattr(sock, "family", None) == getattr(socket, "AF_UNIX", None)


def _connect(self, address, *a, **k):
    if _is_unix(self, address):
        return _orig_connect(self, address, *a, **k)
    COUNTS["socket.connect"] += 1
    DETAILS.append(("socket.connect", repr(address)))
    raise ConnectionRefusedError(f"netguard: blocked {address!r}")


def _connect_ex(self, address, *a, **k):
    if _is_unix(self, address):
        return _orig_connect_ex(self, address, *a, **k)
    COUNTS["socket.connect_ex"] += 1
    DETAILS.append(("socket.connect_ex", repr(address)))
    return 111


def _create_connection(address, *a, **k):
    COUNTS["socket.create_connection"] += 1
    DETAILS.append(("socket.create_connection", repr(address)))
    raise ConnectionRefusedError("netguard: blocked")


socket.socket.connect = _connect
socket.socket.connect_ex = _connect_ex
socket.create_connection = _create_connection

try:
    import httpx

    def _block(name):
        def refuse(self, request, *a, **k):
            COUNTS[name] += 1
            DETAILS.append((name, str(getattr(request, "url", request))))
            raise httpx.ConnectError("netguard: blocked")
        return refuse

    httpx.Client.send = _block("httpx.Client.send")
    httpx.HTTPTransport.handle_request = _block("httpx.HTTPTransport.handle_request")
    httpx.AsyncClient.send = _block("httpx.AsyncClient.send")
    httpx.AsyncHTTPTransport.handle_async_request = _block("httpx.AsyncHTTPTransport.handle_async_request")
    HTTPX_VERSION = httpx.__version__
except ImportError:  # pragma: no cover
    HTTPX_VERSION = None


def total():
    return sum(COUNTS.values())


@atexit.register
def _report():
    line = {"pid": os.getpid(), "argv": sys.argv, "counts": COUNTS, "total": total(), "details": DETAILS}
    target = os.environ.get("NETGUARD_LOG")
    if target:
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(line) + "\n")
    sys.stderr.write(f"NETGUARD total={total()}\n")
