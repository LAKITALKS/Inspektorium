"""Tell which reserve texts a later sample may still use, and what the pilot holds.

``make_reference_cases.py`` opened some reserve texts for ``fabricated`` cases.
``prereg/selection.json`` lists them under ``used_for_fabricated``. They stay in
the group ``reserve``, so that the draw and the sealed hash stay reproducible.
Every later sample must draw from ``available_reserve`` and never from the group
directly.

``replace_pilot_texts.py`` adds the marking ``pilot_replacement``. The groups stay
as drawn, so the texts the pilot uses come from ``current_pilot``, and the texts
that marking took from the reserve or passed over are out of later samples too.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

USED_FOR_FABRICATED = "used_for_fabricated"
PILOT_REPLACEMENT = "pilot_replacement"


class ReserveError(ValueError):
    """The marking of the reserve cannot be trusted."""


def _replacement_texts(selection: Mapping[str, Any]) -> set[str]:
    """Return the reserve texts the replacement took or passed over."""

    marking = selection.get(PILOT_REPLACEMENT)
    if marking is None:
        return set()
    entries = [*marking["replacements"], *marking["privacy_skips"]]
    return {entry["text_id"] for entry in entries}


def available_reserve(selection: Mapping[str, Any]) -> list[str]:
    """Return the reserve without the used texts, in the drawn order.

    A selection without the marking is refused: silently treating every reserve
    text as unused would let a used text back into a sample.
    """

    if USED_FOR_FABRICATED not in selection:
        raise ReserveError(f"the selection has no {USED_FOR_FABRICATED} list")
    reserve: list[str] = selection["groups"]["reserve"]
    used = set(selection[USED_FOR_FABRICATED]) | _replacement_texts(selection)
    unknown = used - set(reserve)
    if unknown:
        raise ReserveError(f"marked texts are not in the reserve: {sorted(unknown)}")
    return [text_id for text_id in reserve if text_id not in used]


def current_pilot(selection: Mapping[str, Any]) -> list[str]:
    """Return the pilot as it runs: a replacement stands where its text stood."""

    pilot: list[str] = selection["groups"]["pilot"]
    marking = selection.get(PILOT_REPLACEMENT)
    if marking is None:
        return list(pilot)
    swaps = {entry["replaces"]: entry["text_id"] for entry in marking["replacements"]}
    unknown = set(swaps) - set(pilot)
    if unknown:
        raise ReserveError(f"replaced texts are not in the pilot: {sorted(unknown)}")
    return [swaps.get(text_id, text_id) for text_id in pilot]
