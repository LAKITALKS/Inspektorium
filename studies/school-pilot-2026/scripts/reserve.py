"""Tell which reserve texts a later sample may still use.

``make_reference_cases.py`` opened some reserve texts for ``fabricated`` cases.
``prereg/selection.json`` lists them under ``used_for_fabricated``. They stay in
the group ``reserve``, so that the draw and the sealed hash stay reproducible.
Every later sample must draw from ``available_reserve`` and never from the group
directly.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

USED_FOR_FABRICATED = "used_for_fabricated"


class ReserveError(ValueError):
    """The marking of the reserve cannot be trusted."""


def available_reserve(selection: Mapping[str, Any]) -> list[str]:
    """Return the reserve without the used texts, in the drawn order.

    A selection without the marking is refused: silently treating every reserve
    text as unused would let a used text back into a sample.
    """

    if USED_FOR_FABRICATED not in selection:
        raise ReserveError(f"the selection has no {USED_FOR_FABRICATED} list")
    reserve: list[str] = selection["groups"]["reserve"]
    used = set(selection[USED_FOR_FABRICATED])
    unknown = used - set(reserve)
    if unknown:
        raise ReserveError(f"marked texts are not in the reserve: {sorted(unknown)}")
    return [text_id for text_id in reserve if text_id not in used]
