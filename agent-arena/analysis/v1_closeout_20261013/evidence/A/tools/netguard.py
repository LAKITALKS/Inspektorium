"""Evidence-A network guard. Import before agent_arena: refuses and counts every real network attempt.

Blocked with refusing counters: httpx.Client.send, httpx.AsyncClient.send, httpx.HTTPTransport.handle_request,
httpx.AsyncHTTPTransport.handle_async_request, socket.socket.connect/connect_ex, socket.create_connection.
Only when allow_mock_transport(True) is called may httpx.Client.send pass to an in-process httpx.MockTransport
(those sends are counted separately as mock_sends; they never leave the process).
"""
import atexit
import json
import os
import socket
import sys

for _k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    assert _k not in os.environ, f"{_k} must be removed from the environment"
COUNT = {"httpx.Client.send": 0, "httpx.AsyncClient.send": 0, "httpx.HTTPTransport.handle_request": 0,
         "httpx.AsyncHTTPTransport.handle_async_request": 0, "socket.connect": 0, "socket.connect_ex": 0,
         "socket.create_connection": 0}
MOCK = {"allowed": False, "mock_sends": 0}

import httpx  # noqa: E402

_orig_send = httpx.Client.send


def _refuse(name):
    def inner(*a, **k):
        COUNT[name] += 1
        raise ConnectionRefusedError(f"evidence-A netguard: {name} refused")
    return inner


def _client_send(self, request, *a, **k):
    if MOCK["allowed"] and isinstance(getattr(self, "_transport", None), httpx.MockTransport):
        MOCK["mock_sends"] += 1
        return _orig_send(self, request, *a, **k)
    COUNT["httpx.Client.send"] += 1
    raise ConnectionRefusedError("evidence-A netguard: httpx.Client.send refused")


httpx.Client.send = _client_send
httpx.AsyncClient.send = _refuse("httpx.AsyncClient.send")
httpx.HTTPTransport.handle_request = _refuse("httpx.HTTPTransport.handle_request")
httpx.AsyncHTTPTransport.handle_async_request = _refuse("httpx.AsyncHTTPTransport.handle_async_request")
socket.socket.connect = _refuse("socket.connect")
socket.socket.connect_ex = _refuse("socket.connect_ex")
socket.create_connection = _refuse("socket.create_connection")


def allow_mock_transport(on=True):
    MOCK["allowed"] = on


def total():
    return sum(COUNT.values())


@atexit.register
def _report():
    sys.stderr.write("[netguard] " + json.dumps({"refused_real_network_attempts": total(), "by_kind": COUNT,
                                                 "mock_transport_sends": MOCK["mock_sends"]}) + "\n")
