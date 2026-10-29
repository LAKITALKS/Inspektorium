"""Locate a quotation in a canonical source text.

L1 is the first exact occurrence. If there is none, L2 is the window of the
same length with the highest difflib.SequenceMatcher(None, quote, window)
ratio; ties go to the earliest window. The quick upper bounds of
SequenceMatcher only skip windows that cannot beat the best ratio found so
far, so the result equals a full scan.
"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True)
class Location:
    method: str
    start: int
    end: int
    ratio: float


def locate(source: str, quote: str) -> Location:
    index = source.find(quote)
    if index >= 0:
        return Location("L1", index, index + len(quote), 1.0)
    width = len(quote)
    if width == 0 or width > len(source):
        raise ValueError("quote cannot be located in this source")
    best_ratio, best_start = -1.0, 0
    for start in range(len(source) - width + 1):
        matcher = SequenceMatcher(None, quote, source[start : start + width])
        if matcher.real_quick_ratio() <= best_ratio:
            continue
        if matcher.quick_ratio() <= best_ratio:
            continue
        ratio = matcher.ratio()
        if ratio > best_ratio:
            best_ratio, best_start = ratio, start
    return Location("L2", best_start, best_start + width, best_ratio)


def exact_occurrences(source: str, quote: str) -> int:
    """Count exact occurrences, overlapping ones included."""

    count, start = 0, source.find(quote)
    while start >= 0:
        count += 1
        start = source.find(quote, start + 1)
    return count
