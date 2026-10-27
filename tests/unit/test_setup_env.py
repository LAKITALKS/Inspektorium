"""Setup target protection; installations are mocked, never downloaded here."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest

SETUP_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "evidence"
    / "v0.1.1"
    / "tools"
    / "setup_env.py"
)
VENV_COMMANDS = ("product-venv", "tools-venv", "build-venv")


@pytest.fixture
def setup_env() -> ModuleType:
    spec = importlib.util.spec_from_file_location("setup_env", SETUP_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def command_args(command: str, target: Path, tmp_path: Path) -> list[str]:
    args = [
        command,
        "--venv",
        str(target),
        "--setup-log",
        str(tmp_path / "setup.jsonl"),
    ]
    if command == "product-venv":
        args.extend(["--wheel", str(tmp_path / "synthetic.whl")])
    return args


@pytest.mark.parametrize("command", VENV_COMMANDS)
@pytest.mark.parametrize("target_kind", ("directory", "file", "symlink", "dangling"))
def test_existing_target_is_rejected_without_changes(
    setup_env: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    command: str,
    target_kind: str,
) -> None:
    target = tmp_path / "target"
    if target_kind == "directory":
        target.mkdir()
        sentinel = target / "sentinel.txt"
    elif target_kind == "file":
        sentinel = target
    elif target_kind == "symlink":
        referent = tmp_path / "foreign-directory"
        referent.mkdir()
        sentinel = referent / "sentinel.txt"
        target.symlink_to(referent, target_is_directory=True)
    else:
        target.symlink_to(tmp_path / "missing-directory", target_is_directory=True)
        sentinel = tmp_path / "sentinel.txt"
    sentinel.write_bytes(b"preserve this exact sentinel\x00\xff")
    before = sentinel.read_bytes()
    target_inode = target.lstat().st_ino
    link_destination = target.readlink() if target.is_symlink() else None
    run = Mock(side_effect=AssertionError("setup must stop before any subprocess"))
    remove = Mock(side_effect=AssertionError("setup must never remove this target"))
    monkeypatch.setattr(setup_env, "run_logged", run)
    monkeypatch.setattr(setup_env.shutil, "rmtree", remove)

    with pytest.raises(SystemExit, match="existing --venv target"):
        setup_env.main(command_args(command, target, tmp_path))

    run.assert_not_called()
    remove.assert_not_called()
    assert sentinel.read_bytes() == before
    assert target.lstat().st_ino == target_inode
    if link_destination is not None:
        assert target.is_symlink()
        assert target.readlink() == link_destination
    if target_kind == "dangling":
        assert not target.exists()
        assert not (tmp_path / "missing-directory").exists()
    assert not (tmp_path / "setup.jsonl").exists()


@pytest.mark.parametrize("command", VENV_COMMANDS)
def test_clean_target_reaches_install_and_metadata_with_mocked_installation(
    setup_env: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    command: str,
) -> None:
    target = tmp_path / "new-parent" / "new-environment"
    wheel = tmp_path / "synthetic.whl"
    wheel.write_bytes(b"synthetic wheel for mocked installation only")

    def fake_run(argv: list[str], log: Path, step: str) -> None:
        if step.endswith("-create"):
            assert not target.exists()
            assert argv == [sys.executable, "-m", "venv", str(target)]
            target.mkdir(parents=True)
        else:
            assert target.is_dir()
            assert argv[:4] == [str(target / "bin" / "python"), "-m", "pip", "install"]

    run = Mock(side_effect=fake_run)
    guard = Mock(return_value={"mocked": "guard"})
    frozen = Mock(return_value=["synthetic-package==0.0"])
    remove = Mock(side_effect=AssertionError("clean setup must not delete anything"))
    monkeypatch.setattr(setup_env, "run_logged", run)
    monkeypatch.setattr(setup_env, "install_guard", guard)
    monkeypatch.setattr(setup_env, "freeze", frozen)
    monkeypatch.setattr(setup_env.shutil, "rmtree", remove)

    assert setup_env.main(command_args(command, target, tmp_path)) == 0

    assert run.call_count == 2
    assert run.call_args_list[0].args[2] == f"{command}-create"
    assert run.call_args_list[1].args[2] == f"{command}-install (download from PyPI)"
    frozen.assert_called_once_with(target)
    remove.assert_not_called()
    info = json.loads((target / "evidence_venv.json").read_text(encoding="utf-8"))
    assert info["venv"] == str(target)
    assert info["freeze"] == ["synthetic-package==0.0"]
    if command == "build-venv":
        guard.assert_not_called()
    else:
        guard.assert_called_once_with(target)
        assert info["guard"] == {"mocked": "guard"}
    if command == "product-venv":
        assert info["wheel"] == wheel.name
        assert info["wheel_sha256"] == setup_env.sha256_file(wheel)
