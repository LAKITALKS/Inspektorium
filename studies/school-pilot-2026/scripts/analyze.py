"""Compute the pilot's measures from imported runs.

The README defines each measure. The pilot is a feasibility check, so its report
gives counts such as ``2 von 9``: see ``pilot_report``. The rates and the mean
per text stay here for the main study and are not part of that report.

A rate with an empty denominator is undefined, neither 0 nor 100 %, and is left
out of the means. Failed runs never enter the denominator of a quote measure.
Protocol errors enter no measure at all.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from functools import partial
from pathlib import Path
from typing import Any

from genius_loader import dump_json
from import_runs import (
    DELIVERED_INVALID,
    DELIVERED_VALID,
    FAILED,
    ORIGINAL,
    PROTOCOL_ERROR,
    USABLE,
)

UNDEFINED = "nicht definiert"
MODES = ("strict", "normalized")
MIN_USABLE_RUNS = 3
"""A grade cell with fewer usable runs is marked."""

Run = Mapping[str, Any]
Annotated = Mapping[str, Mapping[str, list[str]]]
Targets = Mapping[str, Mapping[str, list[dict[str, Any]]]]
"""Text id, then version, then ``{sid, accepted_categories}`` for each error."""
Count = tuple[int, int]
"""How many of how many."""


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
    return [
        item
        for item in run["references"]
        if item["origin_strict"] in (DELIVERED_VALID, DELIVERED_INVALID)
    ]


def quote_count(run: Run, mode: str, with_location: bool) -> Count:
    """Delivered quotes that hold, of all delivered quotes."""

    delivered = _delivered(run)
    hits: list[bool]
    if with_location:
        hits = [item[f"origin_{mode}"] == DELIVERED_VALID for item in delivered]
    else:
        hits = [item[f"text_valid_{mode}"] is True for item in delivered]
    return sum(hits), len(hits)


def quote_fidelity(run: Run, mode: str, with_location: bool) -> float | None:
    """Share of delivered quotes that hold; undefined without a quote."""

    return _ratio(quote_count(run, mode, with_location))


def _valid_comment_sids(run: Run, mode: str) -> dict[int, set[str]]:
    sids: dict[int, set[str]] = defaultdict(set)
    for item in run["references"]:
        if item["owner"] == "comment" and item[f"origin_{mode}"] == DELIVERED_VALID:
            sids[item["owner_index"]].add(item["sid"])
    return sids


def coverage_count(run: Run, mode: str) -> Count:
    """Comments with at least one valid quote, of all comments."""

    return len(_valid_comment_sids(run, mode)), len(run["comments"])


def evidence_coverage(run: Run, mode: str) -> float | None:
    """Share of all comments with at least one valid quote."""

    return _ratio(coverage_count(run, mode))


def criterion_fidelity_count(run: Run, annotated: Annotated) -> Count:
    """Criteria of evidenced comments that the corpus marks there.

    Only comments with a valid quote (normalized) count, because only they
    point at a sentence the corpus annotation can confirm.
    """

    sentences = annotated.get(run["text_id"])
    if sentences is None:
        return 0, 0
    sids_by_comment = _valid_comment_sids(run, "normalized")
    confirmed: list[bool] = []
    for comment in run["comments"]:
        sids = sids_by_comment.get(comment["index"], set())
        if not sids:
            continue
        marked = {kid for sid in sids for kid in sentences.get(sid, [])}
        confirmed += [criterion in marked for criterion in comment["criteria"]]
    return sum(confirmed), len(confirmed)


def criterion_fidelity(run: Run, annotated: Annotated) -> float | None:
    """Share of criteria of evidenced comments that the corpus marks there."""

    return _ratio(criterion_fidelity_count(run, annotated))


def criterion_coverage_count(run: Run, annotated: Annotated) -> Count:
    """Criteria annotated in the text that a comment names."""

    sentences = annotated.get(run["text_id"])
    if sentences is None:
        return 0, 0
    marked = {kid for kids in sentences.values() for kid in kids}
    named = {kid for comment in run["comments"] for kid in comment["criteria"]}
    return len(marked & named), len(marked)


def criterion_coverage(run: Run, annotated: Annotated) -> float | None:
    """Share of the criteria annotated in the text that a comment names."""

    return _ratio(criterion_coverage_count(run, annotated))


def _reference_of_error(run: Run, index: int) -> Mapping[str, Any]:
    return next(
        item
        for item in run["references"]
        if item["owner"] == "error" and item["owner_index"] == index
    )


def _category_counts(
    error: Mapping[str, Any], target: Mapping[str, Any], counter_assumption: bool
) -> bool:
    if error["invalid_category"]:
        return counter_assumption
    return error["category"] in target["accepted_categories"]


def _detected(
    run: Run, target: Mapping[str, Any], counter_assumption: bool = False
) -> bool:
    """Right sentence, a valid quote and an accepted category.

    An unknown category is never a hit. Under the counter assumption it is.
    """

    return any(
        error["sid"] == target["sid"]
        and _category_counts(error, target, counter_assumption)
        and _reference_of_error(run, error["index"])["origin_normalized"]
        == DELIVERED_VALID
        for error in run["errors"]
    )


def detection_count(
    run: Run, targets: list[dict[str, Any]], counter_assumption: bool = False
) -> Count:
    """Inserted errors this run found; a failed run found none."""

    if run["status"] == FAILED:
        return 0, len(targets)
    found = sum(_detected(run, item, counter_assumption) for item in targets)
    return found, len(targets)


def wrong_category_hits(run: Run, targets: list[dict[str, Any]]) -> int:
    """Reports on a target sentence with a known category it does not accept."""

    return sum(
        error["sid"] == target["sid"]
        and not error["invalid_category"]
        and error["category"] not in target["accepted_categories"]
        for error in run["errors"]
        for target in targets
    )


def false_alarm_count(
    run: Run, sites: set[str], counter_assumption: bool = False
) -> Count:
    """1 of 1 if an original text gets an error report at a correct target site.

    Any category counts. Under the counter assumption, an unknown one does not.
    """

    if not sites:
        return 0, 0
    alarmed = any(
        error["sid"] in sites and not (counter_assumption and error["invalid_category"])
        for error in run["errors"]
    )
    return int(alarmed), 1


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


def _targets_of(run: Run, targets: Targets) -> list[dict[str, Any]]:
    return list(targets.get(run["text_id"], {}).get(run["version"], []))


def _sites(text_id: str, targets: Targets) -> set[str]:
    return {
        target["sid"]
        for entries in targets.get(text_id, {}).values()
        for target in entries
    }


def unknown_category_reports(usable: Sequence[Run], targets: Targets) -> dict[str, int]:
    """Count reports with an unknown category; they are unclear, by place."""

    places = {"at_target_in_original": 0, "at_target_in_modified": 0, "elsewhere": 0}
    for run in usable:
        sites = _sites(run["text_id"], targets)
        for error in run["errors"]:
            if not error["invalid_category"]:
                continue
            if error["sid"] not in sites:
                places["elsewhere"] += 1
            elif run["version"] == ORIGINAL:
                places["at_target_in_original"] += 1
            else:
                places["at_target_in_modified"] += 1
    return {"unclear_reports": sum(places.values()), **places}


def analyze_model(
    all_runs: Sequence[Run], annotated: Annotated, targets: Targets
) -> dict[str, Any]:
    """Compute all measures for one model."""

    runs = [run for run in all_runs if run["status"] != PROTOCOL_ERROR]
    usable = [run for run in runs if run["status"] == USABLE]
    originals = [run for run in usable if run["version"] == ORIGINAL]
    target_runs = [run for run in runs if _targets_of(run, targets)]
    usable_target_runs = [run for run in target_runs if run["status"] == USABLE]

    def found(run: Run, counter_assumption: bool = False) -> Count:
        return detection_count(run, _targets_of(run, targets), counter_assumption)

    def alarm(run: Run, counter_assumption: bool = False) -> Count:
        return false_alarm_count(
            run, _sites(run["text_id"], targets), counter_assumption
        )

    def counts(with_counter_assumption: bool) -> dict[str, Any]:
        find = partial(found, counter_assumption=with_counter_assumption)
        ring = partial(alarm, counter_assumption=with_counter_assumption)
        return {
            "detection_per_usable_run": _as_count(_pooled(usable_target_runs, find)),
            "detection_per_attempted_run": _as_count(_pooled(target_runs, find)),
            "false_alarm": _as_count(_pooled(originals, ring)),
        }

    failures = sum(run["status"] == FAILED for run in runs)
    return {
        "attempted_runs": len(runs),
        "usable_runs": len(usable),
        "protocol_errors": len(all_runs) - len(runs),
        "import_notes": import_notes(usable),
        "unknown_category": unknown_category_reports(usable, targets),
        "wrong_category_hits": sum(
            wrong_category_hits(run, _targets_of(run, targets))
            for run in usable_target_runs
        ),
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
            "evidence": {
                mode: _as_count(_pooled(usable, partial(coverage_count, mode=mode)))
                for mode in MODES
            },
            "criterion_fidelity": _as_count(
                _pooled(usable, partial(criterion_fidelity_count, annotated=annotated))
            ),
            "criterion_coverage": _as_count(
                _pooled(usable, partial(criterion_coverage_count, annotated=annotated))
            ),
            **counts(with_counter_assumption=False),
            "counter_assumption": counts(with_counter_assumption=True),
        },
        "rates": {
            "failure_rate": _per_text(runs, lambda r: float(r["status"] == FAILED)),
            "quote_fidelity": {
                mode: {
                    "text": _per_text(
                        usable, partial(quote_fidelity, mode=mode, with_location=False)
                    ),
                    "text_and_location": _per_text(
                        usable, partial(quote_fidelity, mode=mode, with_location=True)
                    ),
                }
                for mode in MODES
            },
            "evidence_coverage": {
                mode: _per_text(usable, partial(evidence_coverage, mode=mode))
                for mode in MODES
            },
            "criterion_fidelity": _per_text(
                usable, lambda r: criterion_fidelity(r, annotated)
            ),
            "criterion_coverage": _per_text(
                usable, lambda r: criterion_coverage(r, annotated)
            ),
            "detection_per_usable_run": _per_text(
                usable_target_runs, lambda r: _ratio(found(r))
            ),
            "detection_per_attempted_run": _per_text(
                target_runs, lambda r: _ratio(found(r))
            ),
            "false_alarm": _per_text(originals, lambda r: _ratio(alarm(r))),
        },
    }


def analyze(
    records: Sequence[Run], annotated: Annotated, targets: Targets
) -> dict[str, dict[str, Any]]:
    """Compute all measures for each model."""

    models: dict[str, list[Run]] = defaultdict(list)
    for record in records:
        models[record["model"]].append(record)
    return {
        model: analyze_model(runs, annotated, targets)
        for model, runs in sorted(models.items())
    }


def pilot_report(report: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Keep what the pilot reports: counts, never rates."""

    return {
        model: {key: value for key, value in results.items() if key != "rates"}
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
    parser.add_argument("--sentence-criteria", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    records = json.loads(args.imported.read_text(encoding="utf-8"))
    annotated = json.loads(args.sentence_criteria.read_text(encoding="utf-8"))
    targets = json.loads(args.targets.read_text(encoding="utf-8"))
    report = analyze(records, annotated, targets)
    args.out.write_bytes(dump_json(render(pilot_report(report))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
