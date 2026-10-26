"""pytest plugin (-p): refuse real transport/sockets; MockTransport doubles in tests keep working."""
import atexit
import json
import socket
import sys

import httpx

REAL = {"httpx.HTTPTransport.handle_request": 0, "httpx.AsyncHTTPTransport.handle_async_request": 0,
        "socket.connect": 0, "socket.connect_ex": 0, "socket.create_connection": 0}


def _r(kind):
    def f(*a, **k):
        REAL[kind] += 1
        raise ConnectionRefusedError("real network refused: " + kind)
    return f


httpx.HTTPTransport.handle_request = _r("httpx.HTTPTransport.handle_request")
httpx.AsyncHTTPTransport.handle_async_request = _r("httpx.AsyncHTTPTransport.handle_async_request")
socket.socket.connect = _r("socket.connect")
socket.socket.connect_ex = _r("socket.connect_ex")
socket.create_connection = _r("socket.create_connection")
atexit.register(lambda: sys.stderr.write("[pytest_netguard] " + json.dumps(
    {"refused_real_network_attempts": sum(REAL.values()), "by_kind": REAL}) + "\n"))
