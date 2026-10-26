"""Existing five-refusal/loopback countercheck for the Python socket guard."""

import json
import socket
import sys

results = {}
try:
    import evidence_netguard as guard

    armed = guard.is_armed()
except Exception:
    armed = False
results["armed"] = armed
if not armed:
    print(json.dumps(results))
    sys.exit(3)


def attempt(name, func):
    try:
        func()
        results[name] = "NOT_REFUSED"
    except guard.NetworkRefusedError:
        results[name] = "refused_by_guard"
    except OSError as exc:
        results[name] = "other_oserror:" + type(exc).__name__


attempt("dns_api.anthropic.com", lambda: socket.getaddrinfo("api.anthropic.com", 443))
attempt("create_connection_1.1.1.1:443", lambda: socket.create_connection(("1.1.1.1", 443), 2))


def v4():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(2)
        s.connect(("1.1.1.1", 443))
    finally:
        s.close()


attempt("connect_1.1.1.1:443", v4)


def v6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        s.settimeout(2)
        s.connect(("2606:4700:4700::1111", 443))
    finally:
        s.close()


attempt("connect_[2606:4700:4700::1111]:443", v6)


def udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(b"x", ("1.1.1.1", 53))
    finally:
        s.close()


attempt("udp_1.1.1.1:53", udp)
server = socket.socket()
server.bind(("127.0.0.1", 0))
server.listen(1)
port = server.getsockname()[1]
try:
    client = socket.create_connection(("127.0.0.1", port), 2)
    client.close()
    results["loopback_positive_control"] = "connected"
except OSError as exc:
    results["loopback_positive_control"] = "failed:" + type(exc).__name__
server.close()
print(json.dumps(results))
