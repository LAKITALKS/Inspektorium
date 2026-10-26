#!/usr/bin/env python3
"""Mechanism-Fix Retest — targeted retest of mechanism cases after prompt hardening.

Tests:
  - 7 mechanism_vs_evidence cases (013, 024, 028, 030, 031, 036, case007-now-solid)
  - 2 solid controls (001, 034) to check for regression

Usage:
    ANTHROPIC_API_KEY=... PYTHONPATH=src python3 run_mechanism_retest.py
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


# Mechanism cases + solid controls
TEST_CASES = [
    # mechanism_vs_evidence cases
    "tasks/study_forensics/case013_gut_microbes.yaml",
    "tasks/study_forensics/case024_klotho_gene_therapy.yaml",
    "tasks/study_forensics/case028_nad_alzheimers_mice.yaml",
    "tasks/study_forensics/case030_apj_exercise_mimetic.yaml",
    "tasks/study_forensics/case031_rapamycin_longevity.yaml",
    "tasks/study_forensics/case036_antioxidant_mice_memory.yaml",
    # Solid controls (must remain solid after prompt change)
    "tasks/study_forensics/case007_vitamin_d_covid.yaml",       # relabeled to solid
    "tasks/study_forensics/case034_gas_stoves_asthma.yaml",     # solid control
]

AGENT_CONFIGS = [
    Path("agents/claude_sonnet.yaml"),
    Path("agents/claude_haiku.yaml"),
    Path("agents/claude_opus.yaml"),
]

RUNS_DIR = Path("runs/mechanism_retest")
REPORTS_DIR = Path("reports/mechanism_retest")
RESULTS_FILE = RUNS_DIR / "mechanism_retest_results.json"


def main():
    tasks = []
    for tf in TEST_CASES:
        p = Path(tf)
        if not p.exists():
            print(f"WARNING: {tf} not found, skipping")
            continue
        tasks.append(load_task(p))

    print(f"Mechanism-Fix Retest: {len(tasks)} cases")

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
    print(f"\nTotal runs: {len(tasks)} tasks x {len(agents)} models = {total_runs}")
    print()

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []
    errors = []
    run_count = 0
    start_time = time.monotonic()

    for task in tasks:
        print(f"=== {task.id} (gold={task.gold_label}, family={task.task_family}) ===")

        for cfg, provider in agents:
            run_count += 1
            short_id = uuid.uuid4().hex[:6]
            run_id = f"mechfix_{task.id}_{cfg.label.replace(' ', '_')}_{short_id}"

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

    # Summary
    print(f"\n{'='*60}")
    print(f"MECHANISM-FIX RETEST COMPLETE")
    print(f"{'='*60}")
    print(f"Total runs: {run_count}")
    print(f"Errors: {len(errors)}")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Results saved: {RESULTS_FILE}")

    if all_results:
        correct = sum(1 for r in all_results if r["label_correct"])
        total = len(all_results)
        print(f"\nOverall accuracy: {correct}/{total} = {correct/total:.1%}")

        # Mechanism vs solid split
        mech_results = [r for r in all_results if r["task_family"] == "mechanism_vs_evidence"]
        solid_results = [r for r in all_results if r["task_family"] == "solid"]

        if mech_results:
            mc = sum(1 for r in mech_results if r["label_correct"])
            print(f"\nMechanism accuracy: {mc}/{len(mech_results)} = {mc/len(mech_results):.1%}")
        if solid_results:
            sc = sum(1 for r in solid_results if r["label_correct"])
            print(f"Solid control accuracy: {sc}/{len(solid_results)} = {sc/len(solid_results):.1%}")

        # Per-model
        models = sorted(set(r["model"] for r in all_results))
        print("\nPer-model accuracy:")
        for model in models:
            mr = [r for r in all_results if r["model"] == model]
            mc = sum(1 for r in mr if r["label_correct"])
            print(f"  {model}: {mc}/{len(mr)} = {mc/len(mr):.1%}")

        # Per-case detail
        print("\nPer-case detail:")
        for task in tasks:
            tr = [r for r in all_results if r["task_id"] == task.id]
            if not tr:
                continue
            labels = {r["model"]: r["detected_label"] for r in tr}
            correct_flags = {r["model"]: r["label_correct"] for r in tr}
            all_correct = all(correct_flags.values())
            all_wrong = all(not v for v in correct_flags.values())
            flag = ""
            if all_wrong:
                flag = " *** ALL WRONG ***"
            elif not all_correct:
                flag = " ** PARTIAL **"
            print(f"  {task.id} (gold={task.gold_label}): {labels}{flag}")

        # Before/after comparison header
        print("\n--- BEFORE/AFTER COMPARISON ---")
        print("Previous mechanism accuracy (Full 27): 8/18 = 44.4%")
        if mech_results:
            mc = sum(1 for r in mech_results if r["label_correct"])
            print(f"Current mechanism accuracy: {mc}/{len(mech_results)} = {mc/len(mech_results):.1%}")
            delta = (mc / len(mech_results) * 100) - 44.4
            print(f"Delta: {delta:+.1f} percentage points")

    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  {e['task_id']} / {e['model']}: {e['error']}")


if __name__ == "__main__":
    main()
