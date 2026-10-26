"""Loaded through a .pth file in a throwaway test venv: refuses and logs every non-loopback network attempt.

Covers every Python process of that venv, including test subprocesses. Loopback and Unix sockets stay usable.
"""
import json
import os
import socket

_LOG = os.environ.get("NETGUARD_LOG")
_connect, _connect_ex, _getaddrinfo = socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo


def _record(kind, target):
    if _LOG:
        with open(_LOG, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "kind": kind, "target": repr(target)}) + "\n")


def _local(host):
    host = host.decode() if isinstance(host, bytes) else str(host or "")
    return host in {"", "localhost", "::1"} or host.startswith("127.")


def _allowed(sock, address):
    return sock.family == getattr(socket, "AF_UNIX", None) or not isinstance(address, tuple) or _local(address[0])


def connect(self, address):
    if _allowed(self, address):
        return _connect(self, address)
    _record("connect", address)
    raise OSError("network refused by netguard")


def connect_ex(self, address):
    if _allowed(self, address):
        return _connect_ex(self, address)
    _record("connect_ex", address)
    return 111


def getaddrinfo(host, *args, **kwargs):
    if host is None or _local(host):
        return _getaddrinfo(host, *args, **kwargs)
    _record("getaddrinfo", host)
    raise socket.gaierror("network refused by netguard")


socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo = connect, connect_ex, getaddrinfo
