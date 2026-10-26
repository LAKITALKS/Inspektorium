"""Public-entry boundaries; installed real-engine checks live in verify_instrument."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import click
import pytest

import inspektorium.audit as entry
from inspektorium.cli import main


def test_missing_engine_is_explicit_and_does_not_fall_back(monkeypatch, capsys):
    def unavailable(name):
        raise ModuleNotFoundError("missing", name="agent_arena")

    monkeypatch.setattr(entry, "import_module", unavailable)
    assert main(["audit", "run", "--offline"]) == 2
    streams = capsys.readouterr()
    assert not streams.out
    assert "python -m pip install . ./agent-arena" in streams.err


def test_broken_transitive_dependency_is_not_hidden(monkeypatch):
    def broken(name):
        raise ModuleNotFoundError("broken dependency", name="yaml")

    monkeypatch.setattr(entry, "import_module", broken)
    with pytest.raises(ModuleNotFoundError, match="broken dependency"):
        main(["audit", "--help"])


def test_top_level_help_does_not_load_engine(monkeypatch, capsys):
    def forbidden(name):
        raise AssertionError("top-level help must not load the optional engine")

    monkeypatch.setattr(entry, "import_module", forbidden)
    with pytest.raises(SystemExit) as result:
        main(["--help"])
    assert result.value.code == 0
    help_text = capsys.readouterr().out
    assert "audit" in help_text
    assert "reference checker" in help_text


def install_group(monkeypatch, group):
    def load(name):
        if name == "agent_arena.phase10_cli":
            return SimpleNamespace(audit=group)
        return importlib.import_module(name)

    monkeypatch.setattr(entry, "import_module", load)


@pytest.mark.parametrize("engine_exit", [0, 2])
def test_click_controlled_exit_is_preserved(monkeypatch, engine_exit):
    @click.group()
    def group():
        pass

    @group.command()
    def run():
        raise click.exceptions.Exit(engine_exit)

    install_group(monkeypatch, group)
    assert main(["audit", "run"]) == engine_exit


def test_engine_help_and_usage_keep_public_program_name(monkeypatch, capsys):
    @click.group()
    def group():
        pass

    @group.command()
    def run():
        pass

    install_group(monkeypatch, group)
    assert main(["audit", "--help"]) == 0
    assert "Usage: inspektorium audit" in capsys.readouterr().out
    assert main(["audit", "run", "--not-an-option"]) == 2
    assert "Usage: inspektorium audit run" in capsys.readouterr().err


def test_engine_abort_is_a_failure(monkeypatch, capsys):
    @click.command()
    def group():
        raise click.Abort()

    install_group(monkeypatch, group)
    assert main(["audit"]) == 1
    assert "Aborted!" in capsys.readouterr().err


def test_unexpected_engine_return_is_not_success(monkeypatch):
    @click.command()
    def group():
        return "unexpected status"

    install_group(monkeypatch, group)
    with pytest.raises(TypeError, match="non-integer exit status"):
        main(["audit"])
