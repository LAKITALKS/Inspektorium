"""Authenticated plan lookup stays component-relative inside a monorepo."""
from pathlib import Path
import subprocess

import pytest

from agent_arena.condition_contract import (
    ConditionContractError,
    _read_authenticated_plan_artifact,
)


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@pytest.fixture(params=[".", "agent-arena"])
def tracked_component(tmp_path, request):
    root = tmp_path / request.param
    root.mkdir(exist_ok=True)
    relative = Path("registered-plan.json")
    (root / relative).write_bytes(b'{"role":"component"}\n')
    if root != tmp_path:
        # A same-named root file must never supply the component's HEAD bytes.
        (tmp_path / relative).write_bytes(b'{"role":"parent-decoy"}\n')
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "-c", "user.name=Offline QA", "-c", "user.email=qa@example.invalid",
         "commit", "-qm", "Synthetic tracked plan")
    return root, relative


def test_authenticated_plan_reads_exact_component_head(tracked_component):
    root, relative = tracked_component
    assert _read_authenticated_plan_artifact(root, relative) == b'{"role":"component"}\n'


def test_authenticated_plan_rejects_changed_working_bytes(tracked_component):
    root, relative = tracked_component
    (root / relative).write_bytes(b'{"role":"changed"}\n')
    with pytest.raises(ConditionContractError, match="differs from authenticated HEAD"):
        _read_authenticated_plan_artifact(root, relative)


def test_authenticated_plan_rejects_untracked_input(tracked_component):
    root, _ = tracked_component
    relative = Path("untracked-plan.json")
    (root / relative).write_bytes(b'{}\n')
    with pytest.raises(ConditionContractError, match="not tracked at HEAD"):
        _read_authenticated_plan_artifact(root, relative)
