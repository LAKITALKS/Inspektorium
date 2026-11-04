"""Compute the pilot's measures from imported runs and the filled coding sheet.

The README defines each measure. The pilot is a feasibility check, so its report
gives counts such as ``2 von 9``: see ``pilot_report``. The rates and the mean
per text stay here for the main study and are not part of that report.

A measure with an empty denominator is undefined, neither 0 nor 100 %. Failed
runs never enter the denominator of a quote measure. Protocol errors enter no
measure at all.

A trap is one inserted error per text: ``{version, type, sids, description}``.
Stage 1 is mechanical: a report names a target sentence and exactly the target
type. Stage 2 is the coder's answer from the filled sheet.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from functools import partial
from pathlib import Path
from typing import Any

from export_for_coding import (
    ANSWER_NO,
    ANSWER_UNCLEAR,
    Code,
    CodingError,
    RunKey,
    read_codes,
    run_key,
)
from genius_loader import dump_json
from import_runs import (
    DELIVERED_INVALID,
    DELIVERED_VALID,
    DELIVERED_WITHOUT_SID,
    FAILED,
    ORIGINAL,
    PROTOCOL_ERROR,
    USABLE,
)

UNDEFINED = "nicht definiert"
MODES = ("strict", "normalized")
MIN_USABLE_RUNS = 3
"""A grade cell with fewer usable runs is marked."""
TRAP_TYPES = ("Zahl", "Faktum", "Widerspruch", "Unsinn")
_SID = re.compile(r"S[1-9][0-9]*")

CONFIRMED = "confirmed"
"""Stage 1 and ``ja`` for the same report."""
UNKNOWN_CATEGORY = "unknown_category"
"""``ja`` for a report at the target sentence with an unknown category."""
MISPLACED = "misplaced"
"""``ja`` without stage 1: a hit under a wrong category or sentence."""
UNCLEAR = "unclear"
NOT_DESCRIBED = "not_described"

Run = Mapping[str, Any]
Trap = Mapping[str, Any]
Traps = Mapping[str, Trap]
Codes = Mapping[RunKey, Code]
Annotated = Mapping[str, Mapping[str, list[str]]]
Count = tuple[int, int]
"""How many of how many."""


class TrapError(ValueError):
    """A trap definition breaks the agreed form."""


def validate_traps(traps: Traps) -> None:
    """Refuse a trap that does not have exactly one type and a clear place.

    Only a contradiction may span two sentences.
    """

    for text_id, trap in traps.items():
        sids = trap.get("sids")
        if trap.get("type") not in TRAP_TYPES:
            raise TrapError(f"{text_id}: type must be one of {TRAP_TYPES}")
        if not isinstance(sids, list) or not all(
            isinstance(sid, str) and _SID.fullmatch(sid) for sid in sids
        ):
            raise TrapError(f"{text_id}: sids must be a list of sentence numbers")
        allowed = 2 if trap["type"] == "Widerspruch" else 1
        if not 1 <= len(sids) <= allowed:
            raise TrapError(f"{text_id}: {trap['type']} allows {allowed} sentence(s)")
        version = trap.get("version")
        if not isinstance(version, str) or not version or version == ORIGINAL:
            raise TrapError(f"{text_id}: version must name the modified version")
        description = trap.get("description")
        if not isinstance(description, str) or not description.strip():
            raise TrapError(f"{text_id}: the description is missing")


def _ratio(count: Count) -> float | None:
    hits, total = count
    return hits / total if total else None


def _mean(values: Iterable[float | None]) -> float | None:
    defined = [value for value in values if value is not None]
    return sum(defined) / len(defined) if defined else None


def mean_per_text(values: Mapping[str, list[float | None]]) -> float | None:
    """Average within each text, then across the texts that have a value."""

    return _mean(_mean(runs) for runs in values.values())


def _delivered(run: Run) -> list[Mapping[str, Any]]:
    delivered = (DELIVERED_VALID, DELIVERED_INVALID, DELIVERED_WITHOUT_SID)
    return [item for item in run["references"] if item["origin_strict"] in delivered]


def quote_count(run: Run, mode: str, with_location: bool) -> Count:
    """Measures 2 and 3: delivered quotes that hold.

    A quote without a sentence number counts in measure 2 only.
    """

    delivered = _delivered(run)
    if not with_location:
        return sum(item[f"text_valid_{mode}"] is True for item in delivered), len(
            delivered
        )
    located = [item for item in delivered if item["sid"] is not None]
    return sum(item[f"origin_{mode}"] == DELIVERED_VALID for item in located), len(
        located
    )


def _quote_rate(run: Run, mode: str, with_location: bool) -> float | None:
    return _ratio(quote_count(run, mode, with_location))


def _holds(item: Mapping[str, Any], mode: str) -> bool:
    if item["sid"] is None:
        return bool(item[f"text_valid_{mode}"])
    return bool(item[f"origin_{mode}"] == DELIVERED_VALID)


def invalid_quotes(usable: Sequence[Run]) -> list[dict[str, Any]]:
    """List every quote that fails in at least one mode, one by one."""

    listed: list[dict[str, Any]] = []
    for run in usable:
        for item in _delivered(run):
            strict, normalized = _holds(item, "strict"), _holds(item, "normalized")
            if strict and normalized:
                continue
            listed.append(
                {
                    "text_id": run["text_id"],
                    "version": run["version"],
                    "repetition": run["repetition"],
                    "owner": item["owner"],
                    "owner_index": item["owner_index"],
                    "sid": item["sid"],
                    "quote": item["quote"],
                    "valid_strict": strict,
                    "valid_normalized": normalized,
                }
            )
    return listed


def coverage_count(run: Run) -> Count:
    """Measure 4: comments with at least one delivered quote, of all comments."""

    with_quote = {
        item["owner_index"] for item in _delivered(run) if item["owner"] == "comment"
    }
    return len(with_quote), len(run["comments"])


def global_comment_count(run: Run) -> Count:
    """Comments the chatbot itself marks as global; descriptive only."""

    marked = sum(comment["scope"] == "global" for comment in run["comments"])
    return marked, len(run["comments"])


def criterion_grid_count(run: Run) -> Count:
    """Measure 6: criterion references inside the grid, of all references."""

    references = [ref for comment in run["comments"] for ref in comment["criteria"]]
    return sum(ref["id"] is not None for ref in references), len(references)


def criterion_reference_count(run: Run) -> Count:
    """Measure 7: comments with at least one criterion reference, of all comments."""

    return sum(bool(comment["criteria"]) for comment in run["comments"]), len(
        run["comments"]
    )


def annotation_agreement_count(run: Run, annotated: Annotated) -> Count:
    """Exploratory, not reported: references the corpus annotation confirms.

    Only comments with a valid quote (normalized) count, because only they point
    at a sentence the annotation can confirm.
    """

    sentences = annotated.get(run["text_id"])
    if sentences is None:
        return 0, 0
    sids: dict[int, set[str]] = defaultdict(set)
    for item in run["references"]:
        if item["owner"] == "comment" and item["origin_normalized"] == DELIVERED_VALID:
            sids[item["owner_index"]].add(item["sid"])
    confirmed: list[bool] = []
    for comment in run["comments"]:
        quoted = sids.get(comment["index"], set())
        if quoted:
            marked = {kid for sid in quoted for kid in sentences.get(sid, [])}
            confirmed += [ref["id"] in marked for ref in comment["criteria"]]
    return sum(confirmed), len(confirmed)


def passes_stage_1(error: Mapping[str, Any], trap: Trap) -> bool:
    """A report at a target sentence with exactly the target type."""

    return bool(error["sid"] in trap["sids"] and error["category"] == trap["type"])


def coded_outcome(run: Run, trap: Trap, code: Code) -> str:
    """Combine stage 1 and the coder's answer for one usable run."""

    if code.answer == ANSWER_NO:
        return NOT_DESCRIBED
    if code.answer == ANSWER_UNCLEAR:
        return UNCLEAR
    assert code.report is not None
    error = run["errors"][code.report - 1]
    if passes_stage_1(error, trap):
        return CONFIRMED
    if error["invalid_category"] and error["sid"] in trap["sids"]:
        return UNKNOWN_CATEGORY
    return MISPLACED


def is_hit(outcome: str, counter_assumption: bool = False) -> bool:
    """Measures 9 and 10. Unclear cases count only under the counter assumption."""

    return outcome == CONFIRMED or (
        counter_assumption and outcome in (UNCLEAR, UNKNOWN_CATEGORY)
    )


def is_false_alarm(outcome: str, counter_assumption: bool = False) -> bool:
    """Measure 11. Unclear cases count unless the counter assumption holds."""

    return outcome == CONFIRMED or (
        not counter_assumption and outcome in (UNCLEAR, UNKNOWN_CATEGORY)
    )


def _per_text(
    runs: Iterable[Run], measure: Callable[[Run], float | None]
) -> float | None:
    values: dict[str, list[float | None]] = defaultdict(list)
    for run in runs:
        values[run["text_id"]].append(measure(run))
    return mean_per_text(values)


def _pooled(runs: Iterable[Run], measure: Callable[[Run], Count]) -> Count:
    counts = [measure(run) for run in runs]
    return sum(hits for hits, _ in counts), sum(total for _, total in counts)


def _as_count(count: Count) -> dict[str, Any]:
    hits, total = count
    label = f"{hits} von {total}" if total else UNDEFINED
    return {"count": hits, "of": total, "label": label}


def grade_cell(runs: Sequence[Run]) -> dict[str, Any]:
    """Describe one cell of grades."""

    grades = [run["grade"] for run in runs if run["status"] == USABLE]
    counts = Counter(grades)
    top = max(counts.values(), default=0)
    return {
        "usable_runs": len(grades),
        "marked": len(grades) < MIN_USABLE_RUNS,
        "distribution": {str(grade): counts[grade] for grade in sorted(counts)},
        "range": [min(grades), max(grades)] if grades else None,
        "most_common": sorted(grade for grade in counts if counts[grade] == top),
        "most_common_count": top,
    }


def grade_variation(runs: Sequence[Run]) -> dict[str, dict[str, Any]]:
    """Measure 8: one cell per text, from the runs of the original only."""

    texts: dict[str, list[Run]] = defaultdict(list)
    for run in runs:
        if run["version"] == ORIGINAL:
            texts[run["text_id"]].append(run)
    return {text_id: grade_cell(texts[text_id]) for text_id in sorted(texts)}


def grades_modified(runs: Sequence[Run]) -> dict[str, dict[str, dict[str, Any]]]:
    """Grades of the modified versions, reported apart from measure 8."""

    cells: dict[str, dict[str, list[Run]]] = defaultdict(lambda: defaultdict(list))
    for run in runs:
        if run["version"] != ORIGINAL:
            cells[run["text_id"]][run["version"]].append(run)
    return {
        text_id: {
            version: grade_cell(group) for version, group in sorted(versions.items())
        }
        for text_id, versions in sorted(cells.items())
    }


def import_notes(usable: Sequence[Run]) -> dict[str, int]:
    """Count what the importer tolerated, so that it stays visible."""

    return {
        "code_fences_removed": sum(run["code_fence_removed"] for run in usable),
        "invalid_category_entries": sum(
            error["invalid_category"] for run in usable for error in run["errors"]
        ),
    }


def unknown_category_reports(usable: Sequence[Run], traps: Traps) -> dict[str, int]:
    """Count reports with an unknown category, by place."""

    places = {"at_target_in_original": 0, "at_target_in_modified": 0, "elsewhere": 0}
    for run in usable:
        trap = traps.get(run["text_id"])
        sids = trap["sids"] if trap else []
        for error in run["errors"]:
            if not error["invalid_category"]:
                continue
            if error["sid"] not in sids:
                places["elsewhere"] += 1
            elif run["version"] == ORIGINAL:
                places["at_target_in_original"] += 1
            else:
                places["at_target_in_modified"] += 1
    return {"reports": sum(places.values()), **places}


def _outcomes(usable: Sequence[Run], traps: Traps, codes: Codes) -> dict[RunKey, str]:
    """Combine both stages for every usable run of a text with a trap."""

    outcomes: dict[RunKey, str] = {}
    missing: list[str] = []
    for run in usable:
        trap = traps.get(run["text_id"])
        if trap is None:
            continue
        code = codes.get(run_key(run))
        if code is None:
            missing.append("/".join(run_key(run)))
        else:
            outcomes[run_key(run)] = coded_outcome(run, trap, code)
    if missing:
        raise CodingError([f"{name}: run has no code" for name in missing])
    return outcomes


def analyze_model(
    all_runs: Sequence[Run],
    traps: Traps,
    codes: Codes,
    annotated: Annotated | None = None,
) -> dict[str, Any]:
    """Compute all measures for one model."""

    runs = [run for run in all_runs if run["status"] != PROTOCOL_ERROR]
    usable = [run for run in runs if run["status"] == USABLE]
    outcomes = _outcomes(usable, traps, codes)

    def has_trap(run: Run) -> bool:
        return run["text_id"] in traps

    def is_modified(run: Run) -> bool:
        return has_trap(run) and run["version"] == traps[run["text_id"]]["version"]

    modified_attempted = [run for run in runs if is_modified(run)]
    modified_usable = [run for run in usable if is_modified(run)]
    originals = [run for run in usable if has_trap(run) and run["version"] == ORIGINAL]
    coded = [run for run in usable if run_key(run) in outcomes]

    def hits(selection: Sequence[Run], counter_assumption: bool) -> Count:
        found = sum(
            run_key(run) in outcomes
            and is_hit(outcomes[run_key(run)], counter_assumption)
            for run in selection
        )
        return found, len(selection)

    def alarms(counter_assumption: bool) -> Count:
        rung = sum(
            is_false_alarm(outcomes[run_key(run)], counter_assumption)
            for run in originals
        )
        return rung, len(originals)

    def trap_counts(counter_assumption: bool) -> dict[str, Any]:
        return {
            "detection_per_usable_run": _as_count(
                hits(modified_usable, counter_assumption)
            ),
            "detection_per_attempted_run": _as_count(
                hits(modified_attempted, counter_assumption)
            ),
            "false_alarm": _as_count(alarms(counter_assumption)),
        }

    def outcome_count(kind: str, selection: Iterable[Run]) -> int:
        return sum(outcomes.get(run_key(run)) == kind for run in selection)

    delivered = [item for run in usable for item in _delivered(run)]
    failures = sum(run["status"] == FAILED for run in runs)
    report: dict[str, Any] = {
        "attempted_runs": len(runs),
        "usable_runs": len(usable),
        "protocol_errors": len(all_runs) - len(runs),
        "import_notes": import_notes(usable),
        "unknown_category": unknown_category_reports(usable, traps),
        "misplaced_hits": {
            "in_modified": outcome_count(MISPLACED, modified_usable),
            "in_original": outcome_count(MISPLACED, originals),
        },
        "invalid_quotes": invalid_quotes(usable),
        "grade_variation": grade_variation(runs),
        "grades_modified": grades_modified(runs),
        "counts": {
            "failures": _as_count((failures, len(runs))),
            "quotes": {
                mode: {
                    "text": _as_count(
                        _pooled(
                            usable,
                            partial(quote_count, mode=mode, with_location=False),
                        )
                    ),
                    "text_and_location": _as_count(
                        _pooled(
                            usable,
                            partial(quote_count, mode=mode, with_location=True),
                        )
                    ),
                }
                for mode in MODES
            },
            "quotes_without_sid": sum(item["sid"] is None for item in delivered),
            "ambiguous_quotes": sum(item["ambiguous"] for item in delivered),
            "evidence": _as_count(_pooled(usable, coverage_count)),
            "self_marked_global": _as_count(_pooled(usable, global_comment_count)),
            "criterion_fidelity": _as_count(_pooled(usable, criterion_grid_count)),
            "criterion_coverage": _as_count(_pooled(usable, criterion_reference_count)),
            **trap_counts(counter_assumption=False),
            "unclear": _as_count((outcome_count(UNCLEAR, coded), len(coded))),
            "counter_assumption": trap_counts(counter_assumption=True),
        },
        "rates": {
            "failure_rate": _per_text(runs, lambda r: float(r["status"] == FAILED)),
            "quote_fidelity": {
                mode: {
                    "text": _per_text(
                        usable, partial(_quote_rate, mode=mode, with_location=False)
                    ),
                    "text_and_location": _per_text(
                        usable, partial(_quote_rate, mode=mode, with_location=True)
                    ),
                }
                for mode in MODES
            },
            "evidence_coverage": _per_text(usable, lambda r: _ratio(coverage_count(r))),
            "criterion_fidelity": _per_text(
                usable, lambda r: _ratio(criterion_grid_count(r))
            ),
            "criterion_coverage": _per_text(
                usable, lambda r: _ratio(criterion_reference_count(r))
            ),
        },
    }
    if annotated is not None:
        report["exploratory"] = {
            "annotation_agreement": _as_count(
                _pooled(
                    usable, partial(annotation_agreement_count, annotated=annotated)
                )
            )
        }
    return report


def analyze(
    records: Sequence[Run],
    traps: Traps,
    codes: Codes,
    annotated: Annotated | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute all measures for each model."""

    validate_traps(traps)
    models: dict[str, list[Run]] = defaultdict(list)
    for record in records:
        models[record["model"]].append(record)
    return {
        model: analyze_model(runs, traps, codes, annotated)
        for model, runs in sorted(models.items())
    }


def pilot_report(report: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Keep what the pilot reports: counts, no rates, nothing exploratory."""

    hidden = ("rates", "exploratory")
    return {
        model: {key: value for key, value in results.items() if key not in hidden}
        for model, results in report.items()
    }


def render(value: object) -> object:
    """Replace undefined values by their label for the written report."""

    if value is None:
        return UNDEFINED
    if isinstance(value, dict):
        return {key: render(item) for key, item in value.items()}
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imported", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--coding-sheet", type=Path, required=True)
    parser.add_argument("--coding-key", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    records = json.loads(args.imported.read_text(encoding="utf-8"))
    traps = json.loads(args.targets.read_text(encoding="utf-8"))
    key = json.loads(args.coding_key.read_text(encoding="utf-8"))
    codes = read_codes(args.coding_sheet.read_bytes(), key, records)
    args.out.write_bytes(
        dump_json(render(pilot_report(analyze(records, traps, codes))))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
