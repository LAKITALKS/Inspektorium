"""Stable machine-readable report rendering."""

from __future__ import annotations

import json

from inspektorium.core.models import InspectionReport


def render_json(report: InspectionReport) -> str:
    """Render a report as deterministic UTF-8-compatible JSON text."""

    payload = report.model_dump(mode="json")
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


__all__ = ["render_json"]
