"""Case-library run harness + multi-run stability surface (Phase 4).

Runs the ``study_forensics`` case library in batch, optionally repeating each
case, stores structured per-run results, and produces a basic stability
summary. This is a *measurement harness* — it does not change scoring, prompts,
providers, the parser, the judge, or report/PDF logic. Scores/labels come from
the existing evaluator; truncation is read (read-only) from the existing
Phase-1 parser diagnostics.

Usage (module CLI):

    python -m agent_arena.run_library --task-family study_forensics --all --fake
    python -m agent_arena.run_library --case-id study-forensics-043 --fake
    python -m agent_arena.run_library --task-family study_forensics --limit 5 --runs-per-case 3 --fake
    python -m agent_arena.run_library --limit 3 --runs-per-case 1 --provider anthropic --model claude-opus-4-5

``--fake`` uses a deterministic in-process provider (no network) — the mode
used by the test suite. Real runs require the relevant provider API key in the
environment; keys are never printed, logged, or written to artifacts.
"""

from __future__ import annotations

import json
import statistics
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from agent_arena.confidence_validity import (
    INVALID,
    MISSING,
    VALID,
    classify_confidence,
    confidence_value_if_valid,
)
from agent_arena.evaluator import evaluate_result
from agent_arena.output_contract import parse_structured_output
from agent_arena.providers import BaseProvider
from agent_arena.runner import STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL, run_agent
from agent_arena.schemas import Task, TaskType
from agent_arena.task_loader import load_task

TASK_DIR = Path("tasks/study_forensics")
LIBRARY_RUNS_DIR = Path("runs/library")

# --- Documented stability thresholds (configurable constants) ---------------
# score range (on the 0–100 total scale) above which a case is flagged as
# high_score_variance across repeated runs.
HIGH_SCORE_VARIANCE_THRESHOLD = 15.0


# ---------------------------------------------------------------------------
# Deterministic fake provider (tests + dry runs; never touches the network)
# ---------------------------------------------------------------------------

class FakeLibraryProvider(BaseProvider):
    """Deterministic provider that echoes each task's gold_label as valid JSON.

    Produces schema-valid, label-correct output so the harness can be exercised
    offline. Tests may subclass or supply their own fakes for malformed /
    truncated / error behavior.
    """

    name = "fake"

    def __init__(self, model: str = "fake-model", label: str = "Fake", **_):
        self.model = model
        self.label = label

    def send_prompt(self, task: Task, system_prompt: str) -> str:
        gold = getattr(task, "gold_label", "") or "solid"
        payload = {
            "final_answer": gold,
            "steps": [f"Deterministic fake analysis for {task.id}."],
            "key_claims": [f"Detected {gold}."],
            "confidence": 0.75,
        }
        return json.dumps(payload)


# ---------------------------------------------------------------------------
# Case discovery
# ---------------------------------------------------------------------------

def is_retired(task: Task) -> bool:
    """A case is retired (excluded from active metrics) if flagged as such.

    See docs/case_intake_policy.md. Retired cases remain loadable and are still
    discoverable when explicitly requested by ``case_id`` or in bulk via
    ``include_retired``.
    """
    return bool(getattr(task, "excluded_from_active_metrics", False)
                or getattr(task, "status", None) == "retired")


def discover_cases(
    task_family: str = "study_forensics",
    case_id: str | None = None,
    limit: int | None = None,
    synthetic_only: bool = False,
    label: str | None = None,
    task_dir: Path | None = None,
    include_retired: bool = False,
) -> list[tuple[Path, Task]]:
    """Discover study_forensics cases, filtered and ordered by filename.

    ``task_family`` matches the task_type (the library is selected with
    ``study_forensics``); ``label`` filters by gold_label (overclaim/solid/...).
    Retired cases (``status: retired`` / ``excluded_from_active_metrics: true``)
    are excluded by default from active discovery, unless ``include_retired`` is
    set or the case is explicitly requested by ``case_id``.
    """
    d = task_dir or TASK_DIR
    out: list[tuple[Path, Task]] = []
    for f in sorted(d.glob("*.yaml")):
        t = load_task(f)
        if t.task_type != TaskType.STUDY_FORENSICS:
            continue
        if task_family and t.task_type.value != task_family:
            continue
        if case_id and t.id != case_id:
            continue
        # Skip retired cases by default, but honour an explicit case_id request.
        if is_retired(t) and not include_retired and case_id != t.id:
            continue
        if synthetic_only and t.origin != "synthetic_fixture":
            continue
        if label and t.gold_label != label:
            continue
        out.append((f, t))
    if limit is not None:
        out = out[:limit]
    return out


# ---------------------------------------------------------------------------
# Per-run execution → flat record
# ---------------------------------------------------------------------------

def run_single(
    provider: BaseProvider,
    case_file: Path,
    task: Task,
    run_index: int,
    library_run_id: str,
    *,
    prompt_version: str = STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL,
) -> dict:
    """Run one case once and return a flat, JSON-serializable result record."""
    result = run_agent(provider, task, prompt_version=prompt_version)

    # Score/label via the existing evaluator (no scoring change).
    evaluated = evaluate_result(task, result)
    sf = evaluated.study_forensics or {}
    detected_label = sf.get("detected_label")
    label_correct = sf.get("label_correct")
    score = round(evaluated.scores.total, 1) if result.parse_ok else None
    confidence = result.parsed.confidence if result.parsed else None
    confidence_state = (
        result.parsed.confidence_state if result.parsed else None
    )
    if confidence_state not in (VALID, MISSING, INVALID):
        confidence_state = classify_confidence(confidence)

    # truncation_suspected read (read-only) from the Phase-1 parser diagnostics.
    truncation_suspected = False
    if result.raw_output:
        _, diag = parse_structured_output(result.raw_output, result.finish_reason)
        truncation_suspected = diag.truncation_suspected
    elif result.finish_reason == "length":
        truncation_suspected = True

    return {
        "library_run_id": library_run_id,
        "case_id": task.id,
        "case_file": case_file.name,
        "gold_label": task.gold_label,
        "run_index": run_index,
        "provider": result.provider,
        "model": result.model,
        "label": detected_label,
        "label_correct": label_correct,
        "score": score,
        "confidence": confidence,
        "confidence_state": confidence_state,
        "parse_ok": result.parse_ok,
        "finish_reason": result.finish_reason,
        "truncation_suspected": truncation_suspected,
        "error": result.error,
        "error_type": result.error_type,
        "latency_ms": result.latency_ms,
        "usage": result.usage,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_result_ref": None,
    }


# ---------------------------------------------------------------------------
# Stability summary
# ---------------------------------------------------------------------------

@dataclass
class CaseStability:
    case_id: str
    case_file: str
    gold_label: str | None
    n_runs: int
    successful_runs: int
    failed_runs: int
    parse_failures: int
    truncation_count: int
    unique_labels: list[str]
    label_consistency_rate: float
    score_mean: float | None
    score_min: float | None
    score_max: float | None
    score_range: float | None
    confidence_mean: float | None
    n_confidence_observations: int
    n_confidence_eligible: int
    n_confidence_ineligible: int
    error_types: list[str]
    flags: dict[str, bool] = field(default_factory=dict)

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        return d


def _case_stability(case_id: str, records: list[dict]) -> CaseStability:
    n = len(records)
    successful = [r for r in records if not r["error"]]
    failed = [r for r in records if r["error"]]
    parse_failures = sum(1 for r in records if not r["parse_ok"])
    truncation = sum(1 for r in records if r["truncation_suspected"])

    labels = [r["label"] for r in successful if r["label"] is not None]
    unique_labels = sorted(set(labels))
    if labels:
        top = Counter(labels).most_common(1)[0][1]
        consistency = round(top / len(labels), 3)
    else:
        consistency = 0.0

    scores = [r["score"] for r in records if isinstance(r["score"], (int, float))]
    score_mean = round(statistics.mean(scores), 2) if scores else None
    score_min = round(min(scores), 1) if scores else None
    score_max = round(max(scores), 1) if scores else None
    score_range = round(score_max - score_min, 1) if scores else None

    confidence_values = [
        confidence_value_if_valid(r.get("confidence"), r.get("confidence_state"))
        for r in records
    ]
    confs = [v for v in confidence_values if v is not None]
    conf_mean = round(statistics.mean(confs), 3) if confs else None

    error_types = sorted({r["error_type"] for r in records if r["error_type"]})

    flags = {
        # stable only if >=1 successful labelled run and exactly one unique label
        "stable_label": len(unique_labels) == 1 and len(labels) == n,
        "unstable_label": len(unique_labels) > 1,
        "parse_fragile": parse_failures > 0,
        "truncation_risk": truncation > 0,
        "provider_error_seen": len(failed) > 0,
        "high_score_variance": bool(score_range is not None
                                    and score_range > HIGH_SCORE_VARIANCE_THRESHOLD),
    }

    return CaseStability(
        case_id=case_id,
        case_file=records[0]["case_file"],
        gold_label=records[0]["gold_label"],
        n_runs=n,
        successful_runs=len(successful),
        failed_runs=len(failed),
        parse_failures=parse_failures,
        truncation_count=truncation,
        unique_labels=unique_labels,
        label_consistency_rate=consistency,
        score_mean=score_mean,
        score_min=score_min,
        score_max=score_max,
        score_range=score_range,
        confidence_mean=conf_mean,
        n_confidence_observations=n,
        n_confidence_eligible=len(confs),
        n_confidence_ineligible=n - len(confs),
        error_types=error_types,
        flags=flags,
    )


@dataclass
class LibrarySummary:
    library_run_id: str
    timestamp: str
    provider: str
    model: str
    runs_per_case: int
    total_cases: int
    total_runs: int
    records: list[dict]
    case_stability: list[CaseStability]

    def summary_dict(self) -> dict:
        total = self.total_runs
        successful = sum(1 for r in self.records if not r["error"])
        failed = total - successful
        parse_failures = sum(1 for r in self.records if not r["parse_ok"])
        truncation = sum(1 for r in self.records if r["truncation_suspected"])
        label_dist = dict(Counter(r["label"] for r in self.records if r["label"]))
        error_dist = dict(Counter(r["error_type"] for r in self.records if r["error_type"]))
        unstable = [c.case_id for c in self.case_stability if c.flags["unstable_label"]]
        parse_fragile = [c.case_id for c in self.case_stability if c.flags["parse_fragile"]]
        truncation_cases = [c.case_id for c in self.case_stability if c.flags["truncation_risk"]]
        error_cases = [c.case_id for c in self.case_stability if c.flags["provider_error_seen"]]
        high_var = [c.case_id for c in self.case_stability if c.flags["high_score_variance"]]
        confidence_eligible = sum(c.n_confidence_eligible for c in self.case_stability)
        return {
            "library_run_id": self.library_run_id,
            "timestamp": self.timestamp,
            "provider": self.provider,
            "model": self.model,
            "runs_per_case": self.runs_per_case,
            "total_cases": self.total_cases,
            "total_runs": total,
            "successful_runs": successful,
            "failed_runs": failed,
            "parse_failures": parse_failures,
            "truncation_runs": truncation,
            "n_confidence_observations": total,
            "n_confidence_eligible": confidence_eligible,
            "n_confidence_ineligible": total - confidence_eligible,
            "label_distribution": label_dist,
            "error_distribution": error_dist,
            "unstable_label_cases": unstable,
            "parse_fragile_cases": parse_fragile,
            "truncation_risk_cases": truncation_cases,
            "provider_error_cases": error_cases,
            "high_score_variance_cases": high_var,
            "thresholds": {"high_score_variance": HIGH_SCORE_VARIANCE_THRESHOLD},
        }


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_library(
    provider: BaseProvider,
    cases: list[tuple[Path, Task]],
    runs_per_case: int = 1,
    out_dir: Path | None = None,
    library_run_id: str | None = None,
    write_artifacts: bool = True,
) -> LibrarySummary:
    """Run each case ``runs_per_case`` times and compute a stability summary.

    If ``out_dir`` is None and ``write_artifacts`` is True, artifacts go to
    ``runs/library/<library_run_id>/``. Set ``write_artifacts=False`` (tests) to
    skip disk writes entirely.
    """
    library_run_id = library_run_id or f"lib_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"
    records: list[dict] = []
    by_case: dict[str, list[dict]] = {}

    for case_file, task in cases:
        for i in range(runs_per_case):
            rec = run_single(provider, case_file, task, i, library_run_id)
            records.append(rec)
            by_case.setdefault(task.id, []).append(rec)

    case_stability = [_case_stability(cid, recs) for cid, recs in by_case.items()]

    summary = LibrarySummary(
        library_run_id=library_run_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider=getattr(provider, "name", "unknown"),
        model=getattr(provider, "model", "") or "",
        runs_per_case=runs_per_case,
        total_cases=len(cases),
        total_runs=len(records),
        records=records,
        case_stability=case_stability,
    )

    if write_artifacts:
        target = out_dir or (LIBRARY_RUNS_DIR / library_run_id)
        _write_artifacts(target, summary)

    return summary


def _write_artifacts(target: Path, summary: LibrarySummary) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    manifest = {
        "library_run_id": summary.library_run_id,
        "timestamp": summary.timestamp,
        "provider": summary.provider,
        "model": summary.model,
        "runs_per_case": summary.runs_per_case,
        "total_cases": summary.total_cases,
        "total_runs": summary.total_runs,
        "cases": [c.case_id for c in summary.case_stability],
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2))
    with open(target / "results.jsonl", "w") as f:
        for r in summary.records:
            f.write(json.dumps(r) + "\n")
    full_summary = summary.summary_dict()
    full_summary["case_stability"] = [c.as_dict() for c in summary.case_stability]
    (target / "summary.json").write_text(json.dumps(full_summary, indent=2))
    (target / "summary.md").write_text(render_summary_md(summary))
    return target


# ---------------------------------------------------------------------------
# Markdown summary
# ---------------------------------------------------------------------------

def render_summary_md(summary: LibrarySummary) -> str:
    s = summary.summary_dict()
    lines: list[str] = []
    lines.append(f"# Case Library Run Summary — `{s['library_run_id']}`\n")
    lines.append(f"**Timestamp:** {s['timestamp']}  ")
    lines.append(f"**Provider / model:** {s['provider']} / {s['model'] or '—'}  ")
    lines.append(f"**Runs per case:** {s['runs_per_case']}\n")

    lines.append("## Totals\n")
    lines.append(f"- Cases: **{s['total_cases']}**")
    lines.append(f"- Individual runs: **{s['total_runs']}**")
    lines.append(f"- Successful: {s['successful_runs']} | Failed: {s['failed_runs']}")
    lines.append(f"- Parse failures: {s['parse_failures']} | Truncation-suspected runs: {s['truncation_runs']}\n")
    lines.append(
        f"- Confidence eligible: {s['n_confidence_eligible']}/"
        f"{s['n_confidence_observations']} | "
        f"Ineligible: {s['n_confidence_ineligible']}\n"
    )

    lines.append("## Label distribution (detected)\n")
    if s["label_distribution"]:
        for lab, n in sorted(s["label_distribution"].items(), key=lambda x: -x[1]):
            lines.append(f"- {lab}: {n}")
    else:
        lines.append("- (none)")
    lines.append("")

    if s["error_distribution"]:
        lines.append("## Provider errors\n")
        for et, n in sorted(s["error_distribution"].items(), key=lambda x: -x[1]):
            lines.append(f"- {et}: {n}")
        lines.append(f"\nCases with provider errors: {', '.join(s['provider_error_cases']) or '—'}\n")

    lines.append("## Stability flags\n")
    lines.append(f"- Unstable-label cases: {', '.join(s['unstable_label_cases']) or '—'}")
    lines.append(f"- Parse-fragile cases: {', '.join(s['parse_fragile_cases']) or '—'}")
    lines.append(f"- Truncation-risk cases: {', '.join(s['truncation_risk_cases']) or '—'}")
    lines.append(f"- High-score-variance cases (range > {s['thresholds']['high_score_variance']}): "
                 f"{', '.join(s['high_score_variance_cases']) or '—'}\n")

    lines.append("## Per-case stability\n")
    lines.append("| Case | gold | runs | ok | parse_fail | trunc | labels | consistency | "
                 "score mean | range | flags |")
    lines.append("|" + "---|" * 11)
    for c in summary.case_stability:
        active = [k for k, v in c.flags.items() if v]
        lines.append(
            f"| {c.case_id} | {c.gold_label or '—'} | {c.n_runs} | {c.successful_runs} | "
            f"{c.parse_failures} | {c.truncation_count} | {'/'.join(c.unique_labels) or '—'} | "
            f"{c.label_consistency_rate} | {c.score_mean if c.score_mean is not None else '—'} | "
            f"{c.score_range if c.score_range is not None else '—'} | {', '.join(active) or '—'} |"
        )
    lines.append("")

    inspect = sorted(
        {*s["unstable_label_cases"], *s["parse_fragile_cases"],
         *s["truncation_risk_cases"], *s["provider_error_cases"],
         *s["high_score_variance_cases"]}
    )
    lines.append("## Recommended cases to inspect manually\n")
    lines.append(", ".join(inspect) if inspect else "None — all cases stable in this run.")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_provider(fake: bool, provider: str, model: str | None):
    if fake:
        return FakeLibraryProvider(model=model or "fake-model")
    from agent_arena.providers import get_provider
    kwargs = {}
    if model:
        kwargs["model"] = model
    return get_provider(provider, **kwargs)


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="agent_arena.run_library",
        description="Batch-run the study_forensics case library with a stability summary.",
    )
    p.add_argument("--task-family", default="study_forensics",
                   help="Task family / type to select (default: study_forensics).")
    p.add_argument("--case-id", default=None, help="Run a single case by ID.")
    p.add_argument("--label", default=None,
                   help="Filter by gold_label (solid/overclaim/mechanism_vs_evidence/correlation_vs_causation).")
    p.add_argument("--all", action="store_true", help="Run all matching cases.")
    p.add_argument("--limit", type=int, default=None, help="Limit number of cases.")
    p.add_argument("--synthetic-only", action="store_true", help="Only synthetic fixtures.")
    p.add_argument("--runs-per-case", type=int, default=1, help="Repeat each case N times.")
    p.add_argument("--provider", default="anthropic", help="Provider name for live runs.")
    p.add_argument("--model", default=None, help="Model id for live runs.")
    p.add_argument("--fake", "--dry-run", dest="fake", action="store_true",
                   help="Use the deterministic in-process fake provider (no network).")
    p.add_argument("--include-retired", action="store_true",
                   help="Also run cases flagged status: retired / excluded_from_active_metrics "
                        "(excluded from active runs by default).")
    p.add_argument("--out-dir", default=None, help="Override output directory.")
    args = p.parse_args(argv)

    cases = discover_cases(
        task_family=args.task_family,
        case_id=args.case_id,
        limit=args.limit,
        synthetic_only=args.synthetic_only,
        label=args.label,
        include_retired=args.include_retired,
    )
    if not cases:
        print("No matching cases found.")
        return 1

    # Report active vs retired counts for transparency.
    all_active = discover_cases(task_family=args.task_family)
    retired = [t for _, t in discover_cases(task_family=args.task_family, include_retired=True)
               if is_retired(t)]
    print(f"Library: {len(all_active)} active case(s), {len(retired)} retired "
          f"(retired excluded by default; use --include-retired to include).")

    if not (args.all or args.case_id or args.limit):
        print(f"{len(cases)} cases match. Pass --all to run them, or --limit N / --case-id.")
        return 1

    provider = _build_provider(args.fake, args.provider, args.model)
    mode = "FAKE (no network)" if args.fake else f"LIVE {args.provider}/{args.model or 'default'}"
    print(f"Running {len(cases)} case(s) x {args.runs_per_case} run(s) — provider: {mode}")

    out_dir = Path(args.out_dir) if args.out_dir else None
    summary = run_library(provider, cases, runs_per_case=args.runs_per_case, out_dir=out_dir)

    s = summary.summary_dict()
    print(f"Library run: {s['library_run_id']}")
    print(f"  total runs: {s['total_runs']} | ok: {s['successful_runs']} | failed: {s['failed_runs']}")
    print(f"  parse failures: {s['parse_failures']} | truncation: {s['truncation_runs']}")
    print(f"  unstable-label cases: {len(s['unstable_label_cases'])}")
    target = out_dir or (LIBRARY_RUNS_DIR / s["library_run_id"])
    print(f"  artifacts: {target}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
