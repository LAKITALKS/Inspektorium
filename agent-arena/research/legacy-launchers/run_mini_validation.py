#!/usr/bin/env python3
"""Mini-Validation Sprint — 8 new cases × 3 models = 24 runs.

Tests only the newly merged cases (033-040) to validate integration.

Usage:
    PYTHONPATH=src python3 run_mini_validation.py
"""

from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_arena.agent_loader import load_agent_config
from agent_arena.evaluator import evaluate_run
from agent_arena.journal import append_record
from agent_arena.providers import get_provider
from agent_arena.reporter import generate_report
from agent_arena.runner import run_agent
from agent_arena.task_loader import load_task


# ---------------------------------------------------------------------------
# Config — only the 8 new cases
# ---------------------------------------------------------------------------

NEW_CASES = [
    "tasks/study_forensics/case033_literacy_rct.yaml",
    "tasks/study_forensics/case034_gas_stoves_asthma.yaml",
    "tasks/study_forensics/case035_ai_tutoring.yaml",
    "tasks/study_forensics/case036_antioxidant_mice_memory.yaml",
    "tasks/study_forensics/case037_mindfulness_app.yaml",
    "tasks/study_forensics/case038_mediterranean_diet.yaml",
    "tasks/study_forensics/case039_nlp_benchmark.yaml",
    "tasks/study_forensics/case040_vocational_training.yaml",
]

AGENT_CONFIGS = [
    Path("agents/claude_sonnet.yaml"),
    Path("agents/claude_haiku.yaml"),
    Path("agents/claude_opus.yaml"),
]

RUNS_DIR = Path("runs/mini_validation")
REPORTS_DIR = Path("reports/mini_validation")
JOURNAL_DIR = Path(".agent_arena")
RESULTS_FILE = RUNS_DIR / "mini_validation_results.json"


def main():
    # Load tasks
    tasks = []
    for tf in NEW_CASES:
        p = Path(tf)
        if not p.exists():
            print(f"WARNING: {tf} not found, skipping")
            continue
        tasks.append(load_task(p))

    print(f"Mini-Validation Sprint: {len(tasks)} new cases")

    # Load agents
    agents = []
    for ac_path in AGENT_CONFIGS:
        cfg = load_agent_config(ac_path)
        provider = get_provider(
            cfg.provider, model=cfg.model,
            temperature=cfg.temperature, label=cfg.label,
        )
        agents.append((cfg, provider))
        print(f"  Agent: {cfg.label} ({cfg.model})")

    total_runs = len(tasks) * len(agents)
    print(f"\nTotal runs: {len(tasks)} tasks × {len(agents)} models = {total_runs}")
    print()

    # Create output dirs
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []
    errors = []
    run_count = 0
    start_time = time.monotonic()

    for task in tasks:
        print(f"=== {task.id} ({task.task_family}) ===")

        for cfg, provider in agents:
            run_count += 1
            short_id = uuid.uuid4().hex[:6]
            run_id = f"minival_{task.id}_{cfg.label.replace(' ', '_')}_{short_id}"

            print(f"  [{run_count}/{total_runs}] {cfg.label}...", end=" ", flush=True)

            try:
                result = run_agent(provider, task)
                record = evaluate_run(task, run_id, [result])

                # Persist
                run_path = RUNS_DIR / f"{run_id}.json"
                run_path.write_text(record.model_dump_json(indent=2))

                report_md = generate_report(record)
                report_path = REPORTS_DIR / f"{run_id}.md"
                report_path.write_text(report_md)

                # Extract metrics
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
                        result.parsed.final_answer[:200] if result.parsed else ""
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

    # Save results
    RESULTS_FILE.write_text(json.dumps(all_results, indent=2))
    elapsed = time.monotonic() - start_time

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"MINI-VALIDATION SPRINT COMPLETE")
    print(f"{'='*60}")
    print(f"Total runs: {run_count}")
    print(f"Errors: {len(errors)}")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Results saved: {RESULTS_FILE}")

    if all_results:
        correct = sum(1 for r in all_results if r["label_correct"])
        total = len(all_results)
        print(f"\nLabel accuracy: {correct}/{total} = {correct/total:.1%}")

        # Per-model
        models = sorted(set(r["model"] for r in all_results))
        print("\nPer-model accuracy:")
        for model in models:
            mr = [r for r in all_results if r["model"] == model]
            mc = sum(1 for r in mr if r["label_correct"])
            print(f"  {model}: {mc}/{len(mr)} = {mc/len(mr):.1%}")

        # Per-family
        families = sorted(set(r["task_family"] for r in all_results if r["task_family"]))
        print("\nPer-family accuracy:")
        for fam in families:
            fr = [r for r in all_results if r["task_family"] == fam]
            fc = sum(1 for r in fr if r["label_correct"])
            print(f"  {fam}: {fc}/{len(fr)} = {fc/len(fr):.1%}")

        # Per-case detail
        print("\nPer-case detail:")
        for task in tasks:
            tr = [r for r in all_results if r["task_id"] == task.id]
            labels = {r["model"]: r["detected_label"] for r in tr}
            correct_flags = {r["model"]: r["label_correct"] for r in tr}
            all_correct = all(correct_flags.values())
            all_wrong = all(not v for v in correct_flags.values())
            flag = ""
            if all_wrong:
                flag = " *** ALL WRONG ***"
            elif not all_correct:
                flag = " ** PARTIAL **"
            print(f"  {task.id} (gold={task.gold_label}): "
                  f"{labels}{flag}")

        # Average scores
        print("\nAverage total score per model:")
        for model in models:
            mr = [r for r in all_results if r["model"] == model]
            avg = sum(r["total_score"] for r in mr) / len(mr)
            print(f"  {model}: {avg:.1f}")

        # Disagreement analysis
        print("\nDisagreement cases (models disagree on label):")
        for task in tasks:
            tr = [r for r in all_results if r["task_id"] == task.id]
            labels = [r["detected_label"] for r in tr]
            if len(set(labels)) > 1:
                detail = {r["model"]: r["detected_label"] for r in tr}
                print(f"  {task.id}: {detail}")

    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  {e['task_id']} / {e['model']}: {e['error']}")


if __name__ == "__main__":
    main()
