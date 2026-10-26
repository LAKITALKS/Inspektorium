"""Python-level network guard for the offline evidence runs.

The setup tool copies this module into a virtual environment as
``evidence_netguard.py`` and adds a ``.pth`` file that imports it at
interpreter start. Every Python process started from that environment,
including the ``inspektorium`` console script run as a subprocess, then:

* writes one ``armed`` record to the log named by ``EVIDENCE_NETGUARD_LOG``;
* refuses, and records as ``refused``, every attempt to resolve a host name
  or to connect/send to a target that is not loopback.

Nothing is sent when a call is refused: the check runs before the original
socket function is called.

Reach (documented limit): only Python code that uses the ``socket`` module
is covered. Native code that opens sockets without going through Python's
``socket`` module, and programs that are not Python processes of the guarded
environment, are not covered. A measured zero applies only to the monitored
processes.
"""

from __future__ import annotations

import ipaddress
import json
import os
import socket
import sys
import time
from typing import Any

GUARD_ID = "evidence-netguard/1"
LOG_ENV = "EVIDENCE_NETGUARD_LOG"


class NetworkRefusedError(OSError):
    """Raised instead of performing a non-loopback network operation."""


def _record(event: str, **fields: Any) -> None:
    record = {
        "guard": GUARD_ID,
        "event": event,
        "pid": os.getpid(),
        "argv": [os.path.basename(a)[:80] for a in getattr(sys, "orig_argv", [])[:3]],
        "time": round(time.time(), 3),
    }
    record.update(fields)
    line = json.dumps(record, sort_keys=True, ensure_ascii=True)
    path = os.environ.get(LOG_ENV)
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    elif event != "armed":
        sys.stderr.write(f"evidence-netguard: {line}\n")


def _host_text(host: Any) -> str | None:
    if host is None:
        return None
    if isinstance(host, bytes | bytearray):
        return bytes(host).decode("ascii", errors="replace")
    return str(host)


def is_loopback_host(host: Any, *, passive_ok: bool = False) -> bool:
    """Return True only for loopback targets (or passive lookups if allowed)."""

    text = _host_text(host)
    if text is None or text == "":
        return passive_ok
    name = text.strip().lower().rstrip(".")
    if name == "localhost" or name.endswith(".localhost"):
        return True
    try:
        address = ipaddress.ip_address(name.split("%", 1)[0])
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        return address.ipv4_mapped.is_loopback
    return address.is_loopback


def _refuse(operation: str, target: Any) -> None:
    _record("refused", operation=operation, target=repr(target)[:200])
    raise NetworkRefusedError(f"{GUARD_ID} refused {operation} to {target!r}")


_original_getaddrinfo = socket.getaddrinfo
_original_gethostbyname = socket.gethostbyname
_original_gethostbyname_ex = socket.gethostbyname_ex
_original_gethostbyaddr = socket.gethostbyaddr
_original_getnameinfo = socket.getnameinfo
_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_original_sendto = socket.socket.sendto


def _guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
    if not is_loopback_host(host, passive_ok=True):
        _refuse("getaddrinfo", host)
    return _original_getaddrinfo(host, *args, **kwargs)


def _guarded_gethostbyname(host: Any) -> Any:
    if not is_loopback_host(host):
        _refuse("gethostbyname", host)
    return _original_gethostbyname(host)


def _guarded_gethostbyname_ex(host: Any) -> Any:
    if not is_loopback_host(host):
        _refuse("gethostbyname_ex", host)
    return _original_gethostbyname_ex(host)


def _guarded_gethostbyaddr(host: Any) -> Any:
    if not is_loopback_host(host):
        _refuse("gethostbyaddr", host)
    return _original_gethostbyaddr(host)


def _guarded_getnameinfo(sockaddr: Any, flags: int) -> Any:
    host = sockaddr[0] if isinstance(sockaddr, tuple) and sockaddr else sockaddr
    if not is_loopback_host(host):
        _refuse("getnameinfo", sockaddr)
    return _original_getnameinfo(sockaddr, flags)


def _is_ip_family(sock: socket.socket) -> bool:
    return sock.family in (socket.AF_INET, socket.AF_INET6)


def _address_host(address: Any) -> Any:
    if isinstance(address, tuple) and address:
        return address[0]
    return address


def _guarded_connect(self: socket.socket, address: Any) -> Any:
    if _is_ip_family(self) and not is_loopback_host(_address_host(address)):
        _refuse("connect", address)
    return _original_connect(self, address)


def _guarded_connect_ex(self: socket.socket, address: Any) -> Any:
    if _is_ip_family(self) and not is_loopback_host(_address_host(address)):
        _refuse("connect_ex", address)
    return _original_connect_ex(self, address)


def _guarded_sendto(self: socket.socket, data: Any, *args: Any) -> Any:
    address = args[-1] if args else None
    if _is_ip_family(self) and not is_loopback_host(_address_host(address)):
        _refuse("sendto", address)
    return _original_sendto(self, data, *args)


def arm() -> None:
    """Install the guarded functions (idempotent) and record an armed event."""

    if getattr(socket, "_evidence_netguard_armed", False):
        return
    socket.getaddrinfo = _guarded_getaddrinfo
    socket.gethostbyname = _guarded_gethostbyname
    socket.gethostbyname_ex = _guarded_gethostbyname_ex
    socket.gethostbyaddr = _guarded_gethostbyaddr
    socket.getnameinfo = _guarded_getnameinfo
    socket.socket.connect = _guarded_connect  # type: ignore[method-assign,assignment]
    socket.socket.connect_ex = _guarded_connect_ex  # type: ignore[method-assign,assignment]
    socket.socket.sendto = _guarded_sendto  # type: ignore[method-assign,assignment]
    socket._evidence_netguard_armed = True  # type: ignore[attr-defined]
    _record("armed")


def is_armed() -> bool:
    return bool(getattr(socket, "_evidence_netguard_armed", False)) and (
        socket.socket.connect is _guarded_connect
        and socket.getaddrinfo is _guarded_getaddrinfo
    )


arm()
