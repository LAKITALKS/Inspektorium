"""pytest plugin (Area C evidence): refuse and count network paths for the whole session.
Writes counts to $AREAC_NETGUARD_OUT at session end. Does not touch providers (tests patch those themselves)."""
import json
import os
import socket

import httpx

COUNTS = {"socket_connect": 0, "socket_connect_ex": 0, "socket_create_connection": 0,
          "httpx_client_send": 0, "httpx_transport_handle_request": 0}
_oc, _ocx = socket.socket.connect, socket.socket.connect_ex


def _ref(kind):
    def f(*a, **k):
        COUNTS[kind] += 1
        raise RuntimeError(f"areac netguard refused {kind}")
    return f


def _connect(self, addr):
    if self.family == socket.AF_UNIX:
        return _oc(self, addr)
    COUNTS["socket_connect"] += 1
    raise RuntimeError("areac netguard refused socket connect")


def _connect_ex(self, addr):
    if self.family == socket.AF_UNIX:
        return _ocx(self, addr)
    COUNTS["socket_connect_ex"] += 1
    raise RuntimeError("areac netguard refused socket connect_ex")


socket.socket.connect = _connect
socket.socket.connect_ex = _connect_ex
socket.create_connection = _ref("socket_create_connection")
httpx.Client.send = _ref("httpx_client_send")
httpx.HTTPTransport.handle_request = _ref("httpx_transport_handle_request")


def pytest_sessionfinish(session, exitstatus):
    with open(os.environ["AREAC_NETGUARD_OUT"], "w") as fh:
        json.dump({"exitstatus": int(exitstatus), "counts": COUNTS}, fh, indent=1)
