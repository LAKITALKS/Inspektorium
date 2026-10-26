"""Public entry to the existing audit engine; no analysis or report rewriting."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from importlib import import_module


def run_audit(arguments: Sequence[str]) -> int:
    """Dispatch directly to the installed engine, preserving its exit status.

    Loading is lazy so the reference checker still works on its own. The
    engine retains its package identity, controls and bundle provenance.
    """

    try:
        backend = import_module("agent_arena.phase10_cli")
    except ModuleNotFoundError as exc:
        if exc.name != "agent_arena":
            raise
        print(
            "inspektorium audit: the audit backend is not installed. "
            "From the repository root, install the full instrument with:\n"
            "  python -m pip install . ./agent-arena",
            file=sys.stderr,
        )
        return 2

    click = import_module("click")
    try:
        result: object = backend.audit.main(
            args=list(arguments), prog_name="inspektorium audit", standalone_mode=False
        )
    except click.ClickException as exc:
        exc.show()
        return int(exc.exit_code)
    except click.Abort:
        print("Aborted!", file=sys.stderr)
        return 1
    if result is None:
        return 0
    if isinstance(result, int):
        return result
    raise TypeError("The audit backend returned a non-integer exit status")
