# Judge Parser Harmonization — Phase 2.5

Branch: `fix/judge-parser-harmonization` (from `v0.6.3-provider-contract`)

Goal: harden the judge output parser by reusing the robust output-contract
parsing introduced in Phase 1 — without changing judge prompts or judge scoring.

---

## What was fragile before

`judge._parse_judge_output` extracted JSON with raw `str.index` on markdown
fences:

```python
if "```json" in text:
    start = text.index("```json") + 7
    end = text.index("```", start)      # <-- ValueError if no closing fence
```

Problems:
- **Unhandled `ValueError`** on an unclosed ```` ```json ```` fence (the same
  crash class Phase 1 fixed for the agent parser). The `.index()` calls sit
  *before* the `try/except json.loads` block, so the exception escaped
  `_parse_judge_output`. `run_judge` calls it outside any try/except, so a
  truncated judge response crashed the whole judge call.
- No handling of duplicated/mismatched fences or truncated JSON.

## What changed

- **Extracted the shared core** from `output_contract`:
  `parse_structured_output` was refactored to delegate to a new public
  `extract_json_object(raw, finish_reason=None) -> (dict | None, ParseDiagnostics)`,
  which performs fence stripping (including unclosed fences), string-aware brace
  scanning, and best-effort truncation repair — and never raises.
- **`_parse_judge_output` now delegates** to `extract_json_object` and maps the
  returned dict onto `JudgeResult` exactly as before. On `None` it returns the
  same graceful `JudgeResult(enabled=True, comparative_note="Judge output not
  parseable", raw_output=raw)` as the previous fallback.
- No change to judge prompts, judge field mapping, judge scoring, agent scoring,
  providers, or report/PDF logic.

## Behavior preserved

- Valid judge JSON (plain, fenced, generic-fenced, or with surrounding prose)
  maps to the identical `JudgeResult` shape and values.
- Malformed/empty judge output → same graceful fallback string as before.
- Truncated/unclosed-fence judge output → now parsed (repaired) or gracefully
  handled, **never raises**.

## Tests added

`tests/test_judge_parser.py` (11 tests): plain JSON, fenced JSON, generic fence,
text before/after JSON, unclosed ```` ```json ```` (no raise), malformed
fallback, empty output, truncated JSON graceful, partial-fields defaults,
raw_output preserved, full field-mapping preserved.

## Remaining limitations

- **Pre-existing lint finding (not introduced here):** `judge.py:11`
  `from typing import Any` is unused (already present in `v0.6.3`). Left
  untouched to respect the strict "no unrelated refactor" scope; a one-line
  removal can be done in a separate hygiene change.
- The judge still uses the `send_prompt` path (not `generate`), so it does not
  yet capture `finish_reason`/`usage`. Wiring the judge onto `generate` is out
  of scope for Phase 2.5 (would touch judge call behavior).
- `extract_json_object` returns a dict; the judge does not use the parse
  `ParseDiagnostics` (e.g. `truncation_suspected`) yet — available for future use.

## Shared-core note

`extract_json_object` is now the single extraction path for both the agent
parser (`parse_structured_output`) and the judge parser. All 30 Phase-1
output-contract tests continue to pass unchanged, confirming the refactor is
behavior-preserving for the agent path.
