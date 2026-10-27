"""Load agent configurations from YAML files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AgentConfig:
    provider: str
    model: str
    label: str
    temperature: float = 0.0
    extra: dict = field(default_factory=dict)


def load_agent_config(path: str | Path) -> AgentConfig:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Agent config not found: {path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    return AgentConfig(
        provider=data["provider"],
        model=data["model"],
        label=data.get("label", data["model"]),
        temperature=data.get("temperature", 0.0),
        extra={k: v for k, v in data.items() if k not in ("provider", "model", "label", "temperature")},
    )
