"""Area C guard wrapper: runs the agent-arena click CLI (or run_library main) in-process with every
network path and every provider construction refused and counted.

Usage: python -I guard_cli.py <counts.json> cli|run_library [args...]
Writes {"exit_code", "counts"} to <counts.json>. Requires ANTHROPIC_API_KEY / OPENAI_API_KEY unset.
"""
import json
import os
import socket
import sys

for _k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    assert _k not in os.environ, f"{_k} must be unset"

COUNTS = {
    "socket_connect": 0, "socket_connect_ex": 0, "socket_create_connection": 0,
    "httpx_client_send": 0, "httpx_transport_handle_request": 0,
    "get_provider_calls": 0, "provider_constructions": 0,
}


class Refused(RuntimeError):
    pass


def _refuse(kind):
    def f(*a, **k):
        COUNTS[kind] += 1
        raise Refused(f"area-C guard refused {kind}")
    return f


_oc, _ocx = socket.socket.connect, socket.socket.connect_ex


def _connect(self, addr):
    if self.family == socket.AF_UNIX:
        return _oc(self, addr)
    COUNTS["socket_connect"] += 1
    raise Refused(f"area-C guard refused socket connect {addr!r}")


def _connect_ex(self, addr):
    if self.family == socket.AF_UNIX:
        return _ocx(self, addr)
    COUNTS["socket_connect_ex"] += 1
    raise Refused(f"area-C guard refused socket connect_ex {addr!r}")


socket.socket.connect = _connect
socket.socket.connect_ex = _connect_ex
socket.create_connection = _refuse("socket_create_connection")

import httpx  # noqa: E402

httpx.Client.send = _refuse("httpx_client_send")
httpx.HTTPTransport.handle_request = _refuse("httpx_transport_handle_request")

# Provider construction refusal (before the CLI module binds anything).
import agent_arena.providers as _providers  # noqa: E402
import agent_arena.runner as _runner  # noqa: E402
from agent_arena.providers.anthropic import AnthropicProvider  # noqa: E402
from agent_arena.providers.ollama import OllamaProvider  # noqa: E402
from agent_arena.providers.openai import OpenAIProvider  # noqa: E402

_gp = _refuse("get_provider_calls")
_providers.get_provider = _gp
_runner.get_provider = _gp
for _cls in (AnthropicProvider, OpenAIProvider, OllamaProvider):
    _cls.__init__ = _refuse("provider_constructions")

import agent_arena.cli as _cli  # noqa: E402

_cli.get_provider = _gp  # cli keeps the name importable; patch it too


def main():
    counts_path, target, *args = sys.argv[1:]
    code = 0
    try:
        if target == "cli":
            _cli.cli.main(args=args, prog_name="agent-arena", standalone_mode=True)
        elif target == "run_library":
            from agent_arena.run_library import main as rl_main
            code = rl_main(args)
        elif target == "canary":
            # Guard self-test: each attempt must be refused and counted (expected counts 1 each).
            for fn in (lambda: _providers.get_provider("anthropic"), lambda: _runner.get_provider("openai"),
                       lambda: AnthropicProvider(), lambda: httpx.Client().get("http://127.0.0.1:9/"),
                       lambda: httpx.HTTPTransport().handle_request(httpx.Request("GET", "http://127.0.0.1:9/")),
                       lambda: socket.create_connection(("127.0.0.1", 9)),
                       lambda: socket.socket().connect(("127.0.0.1", 9)),
                       lambda: socket.socket().connect_ex(("127.0.0.1", 9))):
                try:
                    fn()
                except Refused:
                    pass
        else:
            raise SystemExit(f"unknown target {target}")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    finally:
        with open(counts_path, "w") as fh:
            json.dump({"argv": [target, *args], "exit_code": code, "counts": COUNTS}, fh, indent=1)
    sys.exit(code)


if __name__ == "__main__":
    main()
