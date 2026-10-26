"""Strict, unambiguous JSON decoding shared by every JSON entry point.

Inspection inputs and precomputed proposals are decoded by the same function.
It uses the standard-library decoder and rejects what that decoder would
otherwise accept silently:

- repeated object keys, compared after JSON decoding, at every nesting level
  (a later value would otherwise shadow an earlier one);
- the non-standard constants ``NaN``, ``Infinity`` and ``-Infinity``;
- strings or keys that decode to an unpaired UTF-16 surrogate, such as
  ``"\\ud800"``, which cannot be encoded as UTF-8 later;
- a leading UTF-8 byte order mark, trailing data, and any other invalid JSON;
- nesting deeper than ``MAX_NESTING_DEPTH`` arrays or objects.

Nothing is repaired, extracted from surrounding prose, or retried with a more
permissive parser. Error messages are bounded and never quote input text,
except for a short ASCII-escaped excerpt of a duplicated key.
"""

from __future__ import annotations

import json
import re

MAX_NESTING_DEPTH = 64
"""Deepest accepted array/object nesting; the public schemas need three."""

_KEY_EXCERPT_LIMIT = 40
_LONE_SURROGATE = re.compile("[\ud800-\udfff]")
_BYTE_ORDER_MARK = "\ufeff"


class StrictJSONError(ValueError):
    """Text is not exactly one unambiguous, standard JSON value."""


def display_key(key: str) -> str:
    """Return a bounded, ASCII-escaped excerpt of an untrusted key or name."""

    excerpt = ascii(key[:_KEY_EXCERPT_LIMIT])
    return f"{excerpt}..." if len(key) > _KEY_EXCERPT_LIMIT else excerpt


def _reject_nonstandard_constant(value: str) -> None:
    raise StrictJSONError(f"non-standard JSON constant {value}")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate object key {display_key(key)}")
        result[key] = value
    return result


def _too_deep() -> StrictJSONError:
    return StrictJSONError(
        f"nesting is deeper than {MAX_NESTING_DEPTH} arrays or objects"
    )


def _lone_surrogate() -> StrictJSONError:
    return StrictJSONError(
        "a string contains an unpaired UTF-16 surrogate (U+D800 to U+DFFF)"
    )


def _check_decoded_value(value: object) -> None:
    """Reject lone surrogates and excessive nesting without recursion."""

    pending: list[tuple[object, int]] = [(value, 1)]
    while pending:
        item, depth = pending.pop()
        if isinstance(item, str):
            if _LONE_SURROGATE.search(item) is not None:
                raise _lone_surrogate()
        elif isinstance(item, dict):
            if depth > MAX_NESTING_DEPTH:
                raise _too_deep()
            for key, child in item.items():
                if _LONE_SURROGATE.search(key) is not None:
                    raise _lone_surrogate()
                pending.append((child, depth + 1))
        elif isinstance(item, list):
            if depth > MAX_NESTING_DEPTH:
                raise _too_deep()
            pending.extend((child, depth + 1) for child in item)


def load_strict_json(raw: str | bytes | bytearray) -> object:
    """Decode exactly one standard JSON value or raise ``StrictJSONError``.

    Bytes are decoded as strict UTF-8 first; UTF-16, UTF-32 and byte order
    marks are not accepted.
    """

    if isinstance(raw, bytes | bytearray):
        try:
            raw = bytes(raw).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise StrictJSONError("the text is not valid UTF-8") from exc
    if not isinstance(raw, str):
        raise StrictJSONError("JSON text must be str or UTF-8 bytes")
    if raw.startswith(_BYTE_ORDER_MARK):
        raise StrictJSONError("the text starts with a byte order mark (BOM)")
    try:
        value: object = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_constant,
        )
    except StrictJSONError:
        raise
    except json.JSONDecodeError as exc:
        reason = exc.msg.removesuffix(" at")
        raise StrictJSONError(
            f"{reason} (line {exc.lineno}, column {exc.colno})"
        ) from exc
    except RecursionError:
        raise _too_deep() from None
    except ValueError as exc:
        # The decoder raises a plain ValueError only for integer literals that
        # exceed the interpreter's integer string conversion limit.
        raise StrictJSONError("an integer literal is too long") from exc
    _check_decoded_value(value)
    return value


__all__ = ["MAX_NESTING_DEPTH", "StrictJSONError", "display_key", "load_strict_json"]
