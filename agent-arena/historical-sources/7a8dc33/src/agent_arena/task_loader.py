"""Load tasks from YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from agent_arena.schemas import Task


def load_task(path: str | Path) -> Task:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Task file not found: {path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    return Task(**data)
