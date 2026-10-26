"""v1 closeout, Area C: the only supported entry point is 'agent-arena audit'.

Historical commands that could call providers without AA-P10-LIVE authorization ('run') or write a Phase-7B
official package ('official-release') are rejected before any task, provider or release object is touched; every
other non-audit command is marked in the root listing. No provider is constructed and no socket is opened.
"""

from __future__ import annotations

import re
import socket
from pathlib import Path

import pytest
from click.testing import CliRunner

import agent_arena.cli as cli_module
import agent_arena.release_boundary as release_boundary
import agent_arena.runner as runner_module
import agent_arena.task_loader as task_loader
from agent_arena import run_library


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = REPO_ROOT / "examples/phase10/positive-task.json"
MARKS = {
    "run": "[disabled in v1]",
    "official-release": "[disabled in v1]",
    **{name: "[legacy/diagnostic, not v1]" for name in (
        "report", "client-report", "forensic-report", "evaluate", "pipeline", "insights", "calibrate", "route",
        "caseforge", "disagreement-lab", "iaa", "packet-integrity",
    )},
    "phase5b-haiku-full-replication": "[registered historical experiment, not v1]",
    "phase5b-sonnet-full-replication": "[registered historical experiment, not v1]",
    "audit-log": "[legacy journal, not P9 adjudication]",
}


@pytest.fixture
def forbidden(monkeypatch):
    calls: list[str] = []

    def refuse(name):
        def _refuse(*_args, **_kwargs):
            calls.append(name)
            raise AssertionError(f"{name} reached")
        return _refuse

    monkeypatch.setattr(cli_module, "get_provider", refuse("cli.get_provider"))
    monkeypatch.setattr(runner_module, "get_provider", refuse("runner.get_provider"))
    monkeypatch.setattr(task_loader, "load_task", refuse("load_task"))
    monkeypatch.setattr(release_boundary, "load_release_object", refuse("load_release_object"))
    monkeypatch.setattr(release_boundary, "release_official_artifact", refuse("release_official_artifact"))
    monkeypatch.setattr(socket.socket, "connect", refuse("socket.connect"))
    return calls


@pytest.mark.parametrize("agents", [
    "anthropic",
    "anthropic,openai",
    str(REPO_ROOT / "agents/claude_sonnet.yaml"),
])
def test_legacy_run_is_rejected_before_task_or_provider(agents, tmp_path, monkeypatch, forbidden):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli_module.cli, ["run", "--task", str(TASK), "--agents", agents])
    assert result.exit_code == 2, result.output
    assert "historical research harness and is disabled in v1" in result.output
    assert "without AA-P10-LIVE authorization or budget ledger and sends no task context" in result.output
    assert "agent-arena audit validate --task TASK" in result.output
    assert "agent-arena audit run --offline|--live|--replay" in result.output
    assert "Task:" not in result.output and "Run saved" not in result.output
    assert forbidden == []
    assert list(tmp_path.iterdir()) == []


def test_run_keeps_its_options_and_cli_keeps_get_provider_patchable():
    assert [p.name for p in cli_module.cli.commands["run"].params] == ["task", "agents"]
    assert hasattr(cli_module, "get_provider")


def test_official_release_cli_is_rejected_before_any_release_object(tmp_path, forbidden):
    output = tmp_path / "out"
    result = CliRunner().invoke(cli_module.cli, [
        "official-release", "--input", str(tmp_path / "candidate.json"), "--output-root", str(output),
        "--repo-root", str(tmp_path),
    ])
    assert result.exit_code == 2, result.output
    assert "historical Phase-7B release path and is disabled in v1" in result.output
    assert "no AA-P8 scientific state, AA-P9 review or AA-P10 controls" in result.output
    assert "agent-arena audit release --bundle BUNDLE" in result.output
    assert forbidden == []
    assert not output.exists()


def _listing(output: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    current = None
    for line in output.split("Commands:\n", 1)[1].splitlines():
        if not line.strip():
            continue
        if not line.startswith("   "):
            name, _, rest = line.strip().partition(" ")
            current, rows[name] = name, rest.strip()
        else:
            rows[current] = (rows[current] + " " + line.strip()).strip()
    return rows


@pytest.mark.parametrize("width", [80, 200])
def test_root_help_names_the_v1_path_and_marks_every_other_command(width):
    output = CliRunner().invoke(cli_module.cli, ["--help"], terminal_width=width).output
    head = " ".join(output.split("Commands:")[0].split())
    assert "Supported v1 path: 'agent-arena audit' (validate, run, inspect, review, release)." in head
    assert "never produce a v1 release" in head
    rows = _listing(output)
    assert set(rows) == set(cli_module.cli.commands)
    assert rows["audit"].startswith("Canonical AA-P10 local audit")
    assert "[" not in rows["audit"]
    assert set(rows) - {"audit"} == set(MARKS)
    for name, mark in MARKS.items():
        assert rows[name].startswith(mark), (name, rows[name])


@pytest.mark.parametrize("name", ["run", "report", "client-report", "forensic-report", "official-release"])
def test_command_help_keeps_the_addendum_without_stray_indentation(name):
    output = CliRunner().invoke(cli_module.cli, [name, "--help"], terminal_width=80).output
    description = output.split("Options:")[0]
    assert "Not the canonical Phase10 path" in description
    assert not re.search(r"\S {3,}\S", description), description
    assert all(not line.startswith("   ") for line in description.splitlines()), description


def test_run_library_help_states_it_is_not_a_v1_audit(capsys):
    with pytest.raises(SystemExit) as exc:
        run_library.main(["--help"])
    assert exc.value.code == 0
    text = " ".join(capsys.readouterr().out.split())
    assert ("Historical research harness; not an AA-P10/v1 audit or release. Provider calls are not gated by an "
            "AA-P10-LIVE authorization.") in text


@pytest.mark.parametrize("name", ["run", "official-release"])
def test_disabled_commands_say_so_in_their_own_help(name):
    # Critic VC-5: the per-command help states the v1 status, not only the root listing.
    output = " ".join(CliRunner().invoke(cli_module.cli, [name, "--help"], terminal_width=120).output.split())
    assert "Disabled in v1:" in output


def test_audit_run_help_names_a_current_profile():
    output = CliRunner().invoke(cli_module.cli, ["audit", "run", "--help"], terminal_width=200).output
    assert "claude-haiku-5-5@3" in output and "claude-haiku-5-5@1" not in output
