#!/usr/bin/env python3
"""Praxislauf — First real end-to-end run on 19 study-forensics cases × 3 models.

Usage:
    source ~/.zshrc  # load ANTHROPIC_API_KEY
    .venv/bin/python run_praxis.py

Writes:
    - .agent_arena/journal.jsonl  (journal entries)
    - runs/praxis/               (individual run JSONs)
    - reports/praxis/            (individual reports)
    - stdout: progress + summary
"""

from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_arena.agent_loader import load_agent_config
from agent_arena.evaluator import evaluate_run
from agent_arena.journal import append_record
from agent_arena.providers import get_provider
from agent_arena.reporter import generate_report
from agent_arena.runner import run_agent
from agent_arena.task_loader import load_task


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TASK_DIR = Path("tasks/study_forensics")
AGENT_CONFIGS = [
    Path("agents/claude_sonnet.yaml"),
    Path("agents/claude_haiku.yaml"),
    Path("agents/claude_opus.yaml"),
]
RUNS_DIR = Path("runs/praxis")
REPORTS_DIR = Path("reports/praxis")
JOURNAL_DIR = Path(".agent_arena")
RESULTS_FILE = RUNS_DIR / "all_results.json"


def main():
    # Discover all tasks
    task_files = sorted(TASK_DIR.glob("*.yaml"))
    print(f"Found {len(task_files)} study-forensics tasks")

    # Load agent configs + providers
    agents = []
    for ac_path in AGENT_CONFIGS:
        cfg = load_agent_config(ac_path)
        provider = get_provider(
            cfg.provider, model=cfg.model,
            temperature=cfg.temperature, label=cfg.label,
        )
        agents.append((cfg, provider))
        print(f"  Agent: {cfg.label} ({cfg.model})")

    print(f"\nTotal runs: {len(task_files)} tasks × {len(agents)} models "
          f"= {len(task_files) * len(agents)}")
    print()

    # Create output dirs
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)

    # Track results
    all_results = []
    errors = []
    run_count = 0
    total_runs = len(task_files) * len(agents)
    start_time = time.monotonic()

    for task_file in task_files:
        task = load_task(task_file)
        print(f"=== {task.id} ({task.task_family}) ===")

        for cfg, provider in agents:
            run_count += 1
            short_id = uuid.uuid4().hex[:6]
            run_id = f"praxis_{task.id}_{cfg.label.replace(' ', '_')}_{short_id}"

            print(f"  [{run_count}/{total_runs}] {cfg.label}...", end=" ", flush=True)

            try:
                # Run agent
                result = run_agent(provider, task)

                # Evaluate
                record = evaluate_run(task, run_id, [result])

                # Persist run JSON
                run_path = RUNS_DIR / f"{run_id}.json"
                run_path.write_text(record.model_dump_json(indent=2))

                # Persist report
                report_md = generate_report(record)
                report_path = REPORTS_DIR / f"{run_id}.md"
                report_path.write_text(report_md)

                # Append to journal
                append_record(record, JOURNAL_DIR)

                # Extract key metrics
                er = record.results[0]
                sf = er.study_forensics or {}

                entry = {
                    "task_id": task.id,
                    "task_family": task.task_family or "",
                    "gold_label": getattr(task, "gold_label", ""),
                    "gold_case_type": getattr(task, "gold_case_type", ""),
                    "model": cfg.label,
                    "model_id": cfg.model,
                    "run_id": run_id,
                    "parse_ok": result.parse_ok,
                    "error": result.error or "",
                    "latency_ms": result.latency_ms,
                    "total_score": er.scores.total,
                    "correctness": er.scores.correctness,
                    "detected_label": sf.get("detected_label", ""),
                    "label_correct": sf.get("label_correct", False),
                    "finding_recall": sf.get("finding_recall", 0.0),
                    "n_failures": len(er.failures),
                    "n_flags": len(er.forensic_flags),
                    "n_contradictions": sum(
                        1 for f in er.consistency_findings if f.status == "fail"
                    ),
                    "reasoning_integrity": (
                        er.reasoning_integrity.get("classification", "")
                        if er.reasoning_integrity else ""
                    ),
                    "confidence": (
                        result.parsed.confidence if result.parsed else 0.0
                    ),
                    "final_answer": (
                        result.parsed.final_answer[:100] if result.parsed else ""
                    ),
                }
                all_results.append(entry)

                status = "OK" if entry["label_correct"] else "WRONG"
                print(f"{status} | score={entry['total_score']:.1f} | "
                      f"label={entry['detected_label']} | "
                      f"{entry['latency_ms']}ms")

            except Exception as e:
                print(f"ERROR: {e}")
                errors.append({
                    "task_id": task.id,
                    "model": cfg.label,
                    "error": str(e),
                })

    # Save all results
    RESULTS_FILE.write_text(json.dumps(all_results, indent=2))
    elapsed = time.monotonic() - start_time

    # Print summary
    print(f"\n{'='*60}")
    print(f"PRAXIS RUN COMPLETE")
    print(f"{'='*60}")
    print(f"Total runs: {run_count}")
    print(f"Errors: {len(errors)}")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Results saved: {RESULTS_FILE}")

    if all_results:
        # Overall accuracy
        correct = sum(1 for r in all_results if r["label_correct"])
        total = len(all_results)
        print(f"\nLabel accuracy: {correct}/{total} = {correct/total:.1%}")

        # Per-model accuracy
        models = sorted(set(r["model"] for r in all_results))
        print("\nPer-model accuracy:")
        for model in models:
            model_results = [r for r in all_results if r["model"] == model]
            mc = sum(1 for r in model_results if r["label_correct"])
            mt = len(model_results)
            print(f"  {model}: {mc}/{mt} = {mc/mt:.1%}")

        # Per-family accuracy
        families = sorted(set(r["task_family"] for r in all_results if r["task_family"]))
        print("\nPer-family accuracy:")
        for fam in families:
            fam_results = [r for r in all_results if r["task_family"] == fam]
            fc = sum(1 for r in fam_results if r["label_correct"])
            ft = len(fam_results)
            print(f"  {fam}: {fc}/{ft} = {fc/ft:.1%}")

        # Average scores per model
        print("\nAverage total score per model:")
        for model in models:
            model_results = [r for r in all_results if r["model"] == model]
            avg = sum(r["total_score"] for r in model_results) / len(model_results)
            print(f"  {model}: {avg:.1f}")

    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  {e['task_id']} / {e['model']}: {e['error']}")


if __name__ == "__main__":
    main()
