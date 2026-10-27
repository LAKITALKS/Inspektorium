"""v1 closeout, Area C: the only supported entry point is 'inspektorium audit'.

Historical commands that could call providers without AA-P10-LIVE authorization ('run') or write a Phase-7B
official package ('official-release') are rejected before any task, provider or release object is touched; every
other non-audit command is marked in the root listing. No provider is constructed and no socket is opened.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from inspektorium.audit.execution import run_library
from inspektorium.audit.cli import audit


def test_run_library_help_states_it_is_not_a_v1_audit(capsys):
    with pytest.raises(SystemExit) as exc:
        run_library.main(["--help"])
    assert exc.value.code == 0
    text = " ".join(capsys.readouterr().out.split())
    assert (
        "Historical research harness; not an AA-P10/v1 audit or release. Provider calls are not gated by an "
        "AA-P10-LIVE authorization."
    ) in text


def test_audit_run_help_names_a_current_profile():
    output = CliRunner().invoke(audit, ["run", "--help"], terminal_width=200).output
    assert "claude-haiku-5-5@3" in output and "claude-haiku-5-5@1" not in output
