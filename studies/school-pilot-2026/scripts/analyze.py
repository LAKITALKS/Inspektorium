"""Compute the pilot's twelve measures from imported runs.

The README defines each measure. The estimate is always the mean per text: each
text's runs are averaged first, then the texts. A rate with an empty denominator
is undefined, neither 0 nor 100 %, and is left out of those means. Failed runs
never enter the denominator of a quote measure.
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
from import_runs import DELIVERED_INVALID, DELIVERED_VALID, FAILED, ORIGINAL, USABLE

UNDEFINED = "nicht definiert"
MODES = ("strict", "normalized")
Run = Mapping[str, Any]
Annotated = Mapping[str, Mapping[str, list[str]]]
Targets = Mapping[str, Mapping[str, list[dict[str, Any]]]]
"""Text id, then version, then ``{sid, accepted_categories}`` for each error."""


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


def quote_fidelity(run: Run, mode: str, with_location: bool) -> float | None:
    """Share of delivered quotes that hold; undefined without a quote."""

    delivered = _delivered(run)
    if not delivered:
        return None
    hits: list[bool]
    if with_location:
        hits = [item[f"origin_{mode}"] == DELIVERED_VALID for item in delivered]
    else:
        hits = [item[f"text_valid_{mode}"] is True for item in delivered]
    return sum(hits) / len(hits)


def _valid_comment_sids(run: Run, mode: str) -> dict[int, set[str]]:
    sids: dict[int, set[str]] = defaultdict(set)
    for item in run["references"]:
        if item["owner"] == "comment" and item[f"origin_{mode}"] == DELIVERED_VALID:
            sids[item["owner_index"]].add(item["sid"])
    return sids


def evidence_coverage(run: Run, mode: str) -> float | None:
    """Share of all comments with at least one valid quote."""

    if not run["comments"]:
        return None
    return len(_valid_comment_sids(run, mode)) / len(run["comments"])


def criterion_fidelity(run: Run, annotated: Annotated) -> float | None:
    """Share of criteria of evidenced comments that the corpus marks there.

    Only comments with a valid quote (normalized) count, because only they
    point at a sentence the corpus annotation can confirm.
    """

    sentences = annotated.get(run["text_id"])
    if sentences is None:
        return None
    sids_by_comment = _valid_comment_sids(run, "normalized")
    confirmed: list[bool] = []
    for comment in run["comments"]:
        sids = sids_by_comment.get(comment["index"], set())
        if not sids:
            continue
        marked = {kid for sid in sids for kid in sentences.get(sid, [])}
        confirmed += [criterion in marked for criterion in comment["criteria"]]
    return sum(confirmed) / len(confirmed) if confirmed else None


def criterion_coverage(run: Run, annotated: Annotated) -> float | None:
    """Share of the criteria annotated in the text that a comment names."""

    sentences = annotated.get(run["text_id"])
    if sentences is None:
        return None
    marked = {kid for kids in sentences.values() for kid in kids}
    if not marked:
        return None
    named = {kid for comment in run["comments"] for kid in comment["criteria"]}
    return len(marked & named) / len(marked)


def _reference_of_error(run: Run, index: int) -> Mapping[str, Any]:
    return next(
        item
        for item in run["references"]
        if item["owner"] == "error" and item["owner_index"] == index
    )


def _detected(run: Run, target: Mapping[str, Any]) -> bool:
    """Right sentence, a valid quote and an accepted category."""

    return any(
        error["sid"] == target["sid"]
        and error["category"] in target["accepted_categories"]
        and _reference_of_error(run, error["index"])["origin_normalized"]
        == DELIVERED_VALID
        for error in run["errors"]
    )


def detection(run: Run, targets: list[dict[str, Any]]) -> float:
    """Share of the inserted errors this usable run found."""

    return sum(_detected(run, target) for target in targets) / len(targets)


def wrong_category_hits(run: Run, targets: list[dict[str, Any]]) -> int:
    """Error reports on a target sentence with a category it does not accept."""

    return sum(
        error["sid"] == target["sid"]
        and error["category"] not in target["accepted_categories"]
        for error in run["errors"]
        for target in targets
    )


def false_alarm(run: Run, sites: set[str]) -> float:
    """1 if an original text gets an error report at a correct target site."""

    return float(any(error["sid"] in sites for error in run["errors"]))


def _per_text(
    runs: Iterable[Run], measure: Callable[[Run], float | None]
) -> float | None:
    values: dict[str, list[float | None]] = defaultdict(list)
    for run in runs:
        values[run["text_id"]].append(measure(run))
    return mean_per_text(values)


def _grade_distribution(usable: Sequence[Run]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[int]] = defaultdict(Counter)
    for run in usable:
        counts[run["text_id"]][run["grade"]] += 1
    return {
        text_id: {str(grade): grades[grade] for grade in sorted(grades)}
        for text_id, grades in sorted(counts.items())
    }


def _targets_of(run: Run, targets: Targets) -> list[dict[str, Any]]:
    return list(targets.get(run["text_id"], {}).get(run["version"], []))


def _sites(text_id: str, targets: Targets) -> set[str]:
    return {
        target["sid"]
        for entries in targets.get(text_id, {}).values()
        for target in entries
    }


def analyze_model(
    runs: Sequence[Run], annotated: Annotated, targets: Targets
) -> dict[str, Any]:
    """Compute all measures for one model."""

    usable = [run for run in runs if run["status"] == USABLE]
    target_runs = [run for run in runs if _targets_of(run, targets)]

    def found(run: Run) -> float:
        if run["status"] == FAILED:
            return 0.0
        return detection(run, _targets_of(run, targets))

    def alarm(run: Run) -> float | None:
        sites = _sites(run["text_id"], targets)
        return false_alarm(run, sites) if sites else None

    fidelity = {
        mode: {
            "text": _per_text(
                usable, partial(quote_fidelity, mode=mode, with_location=False)
            ),
            "text_and_location": _per_text(
                usable, partial(quote_fidelity, mode=mode, with_location=True)
            ),
        }
        for mode in MODES
    }
    return {
        "attempted_runs": len(runs),
        "usable_runs": len(usable),
        "failure_rate": _per_text(runs, lambda r: float(r["status"] == FAILED)),
        "quote_fidelity": fidelity,
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
        "grade_distribution": _grade_distribution(usable),
        "detection_per_usable_run": _per_text(
            (run for run in target_runs if run["status"] == USABLE), found
        ),
        "detection_per_attempted_run": _per_text(target_runs, found),
        "wrong_category_hits": sum(
            wrong_category_hits(run, _targets_of(run, targets))
            for run in target_runs
            if run["status"] == USABLE
        ),
        "false_alarm": _per_text(
            (run for run in usable if run["version"] == ORIGINAL), alarm
        ),
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


def render(value: object) -> object:
    """Replace undefined rates by their label for the written report."""

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
    args.out.write_bytes(dump_json(render(report)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
