"""Used reserve texts are out of every later sample."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import reserve as rs


@pytest.fixture(scope="module")
def selection(study_root: Path) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(
        (study_root / "prereg/selection.json").read_text("utf-8")
    )
    return loaded


def test_the_marked_texts_are_the_opened_ones(
    selection: dict[str, Any], study_root: Path
) -> None:
    summary = json.loads(
        (study_root / "prereg/reference_cases_summary.json").read_text("utf-8")
    )
    opened = summary["reserve_texts_opened_for_fabricated"]
    assert len(opened) == 8
    assert selection[rs.USED_FOR_FABRICATED] == sorted(opened)


def test_the_committed_reserve_loses_the_marked_texts(
    selection: dict[str, Any],
) -> None:
    available = rs.available_reserve(selection)
    assert len(available) == len(selection["groups"]["reserve"]) - 8
    assert set(available).isdisjoint(selection[rs.USED_FOR_FABRICATED])


def test_the_group_itself_keeps_the_marked_texts(selection: dict[str, Any]) -> None:
    assert set(selection[rs.USED_FOR_FABRICATED]) <= set(selection["groups"]["reserve"])


def test_the_drawn_order_is_kept() -> None:
    selection = {"groups": {"reserve": ["c", "a", "b"]}, rs.USED_FOR_FABRICATED: ["a"]}
    assert rs.available_reserve(selection) == ["c", "b"]


def test_a_selection_without_the_marking_is_refused() -> None:
    with pytest.raises(rs.ReserveError, match="no used_for_fabricated"):
        rs.available_reserve({"groups": {"reserve": ["a"]}})


def test_a_marked_text_outside_the_reserve_is_refused() -> None:
    selection = {"groups": {"reserve": ["a"]}, rs.USED_FOR_FABRICATED: ["x"]}
    with pytest.raises(rs.ReserveError, match="not in the reserve"):
        rs.available_reserve(selection)
