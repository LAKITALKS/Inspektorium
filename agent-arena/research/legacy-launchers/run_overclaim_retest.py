#!/usr/bin/env python3
"""Overclaim-Collision-Fix Retest — targeted retest after priority rule addition.

Tests:
  - 3 overclaim collision cases (032, 038, 040)
  - 2 mechanism controls (013, 036)
  - 2 overclaim anchors (009, 025) — previously stable
  - 1 solid anchor (001)

Usage:
    ANTHROPIC_API_KEY=... PYTHONPATH=src python3 run_overclaim_retest.py
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


TEST_CASES = [
    # Primary collision cases (overclaim mislabeled as mechanism)
    "tasks/study_forensics/case032_cholesterol_drug_biomarker.yaml",
    "tasks/study_forensics/case038_mediterranean_diet.yaml",
    "tasks/study_forensics/case040_vocational_training.yaml",
    # Mechanism controls (must stay mechanism_vs_evidence)
    "tasks/study_forensics/case013_gut_microbes.yaml",
    "tasks/study_forensics/case036_antioxidant_mice_memory.yaml",
    # Overclaim anchors (previously stable, must stay overclaim)
    "tasks/study_forensics/case009_turmeric_alzheimers.yaml",
    "tasks/study_forensics/case025_fasting_cancer.yaml",
    # Solid anchor (collateral check)
    "tasks/study_forensics/case001_exercise_dementia.yaml",
]

AGENT_CONFIGS = [
    Path("agents/claude_sonnet.yaml"),
    Path("agents/claude_haiku.yaml"),
    Path("agents/claude_opus.yaml"),
]

RUNS_DIR = Path("runs/overclaim_retest")
REPORTS_DIR = Path("reports/overclaim_retest")
RESULTS_FILE = RUNS_DIR / "overclaim_retest_results.json"


def main():
    tasks = []
    for tf in TEST_CASES:
        p = Path(tf)
        if not p.exists():
            print(f"WARNING: {tf} not found, skipping")
            continue
        tasks.append(load_task(p))

    print(f"Overclaim-Collision-Fix Retest: {len(tasks)} cases")

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
            run_id = f"ocfix_{task.id}_{cfg.label.replace(' ', '_')}_{short_id}"

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
    print(f"OVERCLAIM-COLLISION-FIX RETEST COMPLETE")
    print(f"{'='*60}")
    print(f"Total runs: {run_count}")
    print(f"Errors: {len(errors)}")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Results saved: {RESULTS_FILE}")

    if all_results:
        correct = sum(1 for r in all_results if r["label_correct"])
        total = len(all_results)
        print(f"\nOverall accuracy: {correct}/{total} = {correct/total:.1%}")

        # By role
        collision = [r for r in all_results if r["task_id"] in
                     {"study-forensics-032", "study-forensics-038", "study-forensics-040"}]
        mech_ctrl = [r for r in all_results if r["task_id"] in
                     {"study-forensics-013", "study-forensics-036"}]
        oc_anchor = [r for r in all_results if r["task_id"] in
                     {"study-forensics-009", "study-forensics-025"}]
        solid_anchor = [r for r in all_results if r["task_id"] == "study-forensics-001"]

        if collision:
            cc = sum(1 for r in collision if r["label_correct"])
            print(f"\nCollision cases (032,038,040): {cc}/{len(collision)} = {cc/len(collision):.1%}")
        if mech_ctrl:
            mc = sum(1 for r in mech_ctrl if r["label_correct"])
            print(f"Mechanism controls (013,036): {mc}/{len(mech_ctrl)} = {mc/len(mech_ctrl):.1%}")
        if oc_anchor:
            oa = sum(1 for r in oc_anchor if r["label_correct"])
            print(f"Overclaim anchors (009,025): {oa}/{len(oc_anchor)} = {oa/len(oc_anchor):.1%}")
        if solid_anchor:
            sa = sum(1 for r in solid_anchor if r["label_correct"])
            print(f"Solid anchor (001): {sa}/{len(solid_anchor)} = {sa/len(solid_anchor):.1%}")

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

    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  {e['task_id']} / {e['model']}: {e['error']}")


if __name__ == "__main__":
    main()
