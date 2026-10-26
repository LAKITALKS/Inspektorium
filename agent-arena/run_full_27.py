#!/usr/bin/env python3
"""Full 27-case validation run — all study-forensics cases × 3 models.

Usage:
    ANTHROPIC_API_KEY=... PYTHONPATH=src python3 run_full_27.py
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
from agent_arena.providers import get_provider
from agent_arena.reporter import generate_report
from agent_arena.runner import run_agent
from agent_arena.task_loader import load_task


TASK_DIR = Path("tasks/study_forensics")
AGENT_CONFIGS = [
    Path("agents/claude_sonnet.yaml"),
    Path("agents/claude_haiku.yaml"),
    Path("agents/claude_opus.yaml"),
]
RUNS_DIR = Path("runs/full_27")
REPORTS_DIR = Path("reports/full_27")
RESULTS_FILE = RUNS_DIR / "all_results.json"


def main():
    task_files = sorted(TASK_DIR.glob("*.yaml"))
    # Exclude quarantine and non-case files
    task_files = [f for f in task_files if not str(f).endswith('.md') and 'quarantine' not in str(f)]
    print(f"Found {len(task_files)} study-forensics tasks")

    agents = []
    for ac_path in AGENT_CONFIGS:
        cfg = load_agent_config(ac_path)
        provider = get_provider(
            cfg.provider, model=cfg.model,
            temperature=cfg.temperature, label=cfg.label,
        )
        agents.append((cfg, provider))
        print(f"  Agent: {cfg.label} ({cfg.model})")

    total_runs = len(task_files) * len(agents)
    print(f"\nTotal runs: {len(task_files)} tasks × {len(agents)} models = {total_runs}")
    print()

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []
    errors = []
    run_count = 0
    start_time = time.monotonic()

    for task_file in task_files:
        task = load_task(task_file)
        print(f"=== {task.id} ({task.task_family}) ===")

        for cfg, provider in agents:
            run_count += 1
            short_id = uuid.uuid4().hex[:6]
            run_id = f"full27_{task.id}_{cfg.label.replace(' ', '_')}_{short_id}"

            print(f"  [{run_count}/{total_runs}] {cfg.label}...", end=" ", flush=True)

            try:
                result = run_agent(provider, task)
                record = evaluate_run(task, run_id, [result])

                run_path = RUNS_DIR / f"{run_id}.json"
                run_path.write_text(record.model_dump_json(indent=2))

                report_md = generate_report(record)
                report_path = REPORTS_DIR / f"{run_id}.md"
                report_path.write_text(report_md)

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

    RESULTS_FILE.write_text(json.dumps(all_results, indent=2))
    elapsed = time.monotonic() - start_time

    print(f"\n{'='*60}")
    print(f"FULL 27-CASE RUN COMPLETE")
    print(f"{'='*60}")
    print(f"Total runs: {run_count}")
    print(f"Errors: {len(errors)}")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Results saved: {RESULTS_FILE}")

    if all_results:
        correct = sum(1 for r in all_results if r["label_correct"])
        total = len(all_results)
        print(f"\nLabel accuracy: {correct}/{total} = {correct/total:.1%}")

        models = sorted(set(r["model"] for r in all_results))
        print("\nPer-model accuracy:")
        for model in models:
            mr = [r for r in all_results if r["model"] == model]
            mc = sum(1 for r in mr if r["label_correct"])
            print(f"  {model}: {mc}/{len(mr)} = {mc/len(mr):.1%}")

        families = sorted(set(r["task_family"] for r in all_results if r["task_family"]))
        print("\nPer-family accuracy:")
        for fam in families:
            fr = [r for r in all_results if r["task_family"] == fam]
            fc = sum(1 for r in fr if r["label_correct"])
            print(f"  {fam}: {fc}/{len(fr)} = {fc/len(fr):.1%}")

        # Per-case detail
        print("\nPer-case detail:")
        task_ids = []
        for task_file in task_files:
            task = load_task(task_file)
            task_ids.append(task.id)

        for tid in task_ids:
            tr = [r for r in all_results if r["task_id"] == tid]
            if not tr:
                continue
            gold = tr[0]["gold_label"]
            labels = {r["model"]: r["detected_label"] for r in tr}
            correct_flags = {r["model"]: r["label_correct"] for r in tr}
            all_correct = all(correct_flags.values())
            all_wrong = all(not v for v in correct_flags.values())
            flag = ""
            if all_wrong:
                flag = " *** ALL WRONG ***"
            elif not all_correct:
                flag = " ** PARTIAL **"
            print(f"  {tid} (gold={gold}): {labels}{flag}")

        print("\nAverage total score per model:")
        for model in models:
            mr = [r for r in all_results if r["model"] == model]
            avg = sum(r["total_score"] for r in mr) / len(mr)
            print(f"  {model}: {avg:.1f}")

        # Disagreement
        print("\nDisagreement cases:")
        for tid in task_ids:
            tr = [r for r in all_results if r["task_id"] == tid]
            labels = [r["detected_label"] for r in tr]
            if len(set(labels)) > 1:
                detail = {r["model"]: r["detected_label"] for r in tr}
                print(f"  {tid}: {detail}")

        # New vs old cases comparison
        old_ids = {f"study-forensics-{n:03d}" for n in [1,4,7,9,13,19,21,22,23,24,25,26,27,28,29,30,31,32]}
        old_ids.add("study-forensics-public-001")
        new_ids = {f"study-forensics-{n:03d}" for n in range(33, 41)}

        old_results = [r for r in all_results if r["task_id"] in old_ids]
        new_results = [r for r in all_results if r["task_id"] in new_ids]

        if old_results:
            oc = sum(1 for r in old_results if r["label_correct"])
            print(f"\nOld cases (19): {oc}/{len(old_results)} = {oc/len(old_results):.1%}")
        if new_results:
            nc = sum(1 for r in new_results if r["label_correct"])
            print(f"New cases (8): {nc}/{len(new_results)} = {nc/len(new_results):.1%}")

    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  {e['task_id']} / {e['model']}: {e['error']}")


if __name__ == "__main__":
    main()
