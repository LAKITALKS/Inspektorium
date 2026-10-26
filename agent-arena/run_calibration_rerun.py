#!/usr/bin/env python3
"""v0.6.3 Calibration Re-Run — 7 cases × 3 models = 21 runs.

Targeted re-run after calibration fixes:
- Fix 1: Analytical reference FP suppression
- Fix 2: Label detection priority (final_answer >> body)
- Fix 3: Criticism-direction heuristic

Cases: 5 solid + 2 mechanism_vs_evidence
  - case001 (solid), case004 (solid), case021 (solid), case022 (solid), case026 (solid)
  - case013 (mechanism_vs_evidence), case024 (mechanism_vs_evidence)

Usage:
    source ~/.zshrc && PYTHONPATH=src python3 run_calibration_rerun.py
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from agent_arena.agent_loader import load_agent_config
from agent_arena.evaluator import evaluate_run
from agent_arena.providers import get_provider
from agent_arena.reporter import generate_report
from agent_arena.runner import run_agent
from agent_arena.task_loader import load_task


TASK_DIR = Path("tasks/study_forensics")
SELECTED_CASES = [
    "case001_social_media.yaml",
    "case004_multivitamin.yaml",
    "case021_virtual_tutoring.yaml",
    "case022_four_day_workweek.yaml",
    "case026_air_sensor_validation.yaml",
    "case013_gut_microbes.yaml",
    "case024_klotho_gene_therapy.yaml",
]
AGENT_CONFIGS = [
    Path("agents/claude_haiku.yaml"),
    Path("agents/claude_sonnet.yaml"),
    Path("agents/claude_opus.yaml"),
]
OUTPUT_DIR = Path("runs/calibration_rerun")
REPORTS_DIR = Path("reports/calibration_rerun")
RESULTS_FILE = Path("runs/calibration_rerun/all_results.json")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    tasks = [load_task(TASK_DIR / f) for f in SELECTED_CASES]

    agents = []
    for ac_path in AGENT_CONFIGS:
        cfg = load_agent_config(ac_path)
        provider = get_provider(cfg.provider, model=cfg.model, temperature=cfg.temperature, label=cfg.label)
        agents.append((cfg, provider))

    total_runs = len(tasks) * len(agents)
    print(f"Calibration Re-Run: {len(tasks)} cases x {len(agents)} models = {total_runs} runs")
    print("=" * 70)

    all_results = []
    run_count = 0

    for task in tasks:
        print(f"\n{'='*70}")
        print(f"CASE: {task.id} — {task.title}")
        print(f"Gold: {task.gold_label}")
        print(f"{'='*70}")

        for cfg, provider in agents:
            run_count += 1
            print(f"\n  [{run_count}/{total_runs}] {cfg.label} ({cfg.model})...", end=" ", flush=True)

            start_time = time.time()
            try:
                result = run_agent(provider, task)
                elapsed = time.time() - start_time
                print(f"OK ({result.latency_ms}ms)", flush=True)
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"ERROR: {e}", flush=True)
                all_results.append({
                    "case_id": task.id,
                    "gold_label": task.gold_label,
                    "model": cfg.label,
                    "model_id": cfg.model,
                    "error": str(e),
                    "elapsed_s": round(elapsed, 1),
                })
                continue

            # Evaluate
            run_id = f"cal_{task.id}_{cfg.label.lower().replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
            record = evaluate_run(task, run_id, [result])

            # Save run JSON
            run_path = OUTPUT_DIR / f"{run_id}.json"
            run_path.write_text(record.model_dump_json(indent=2))

            # Save report
            report = generate_report(record)
            report_path = REPORTS_DIR / f"{run_id}.md"
            report_path.write_text(report)

            # Extract key metrics
            er = record.results[0]
            sf = er.study_forensics or {}
            parsed = er.agent_result.parsed

            entry = {
                "case_id": task.id,
                "gold_label": task.gold_label,
                "model": cfg.label,
                "model_id": cfg.model,
                "run_id": run_id,
                "parse_ok": er.agent_result.parse_ok,
                "total_score": er.scores.total,
                "predicted_label": sf.get("detected_label"),
                "label_correct": sf.get("label_correct", False),
                "expected_findings": sf.get("expected_findings", []),
                "detected_findings": sf.get("detected_findings", []),
                "matched_findings": sf.get("matched_findings", []),
                "missed_findings": sf.get("missed_findings", []),
                "extra_findings": sf.get("extra_findings", []),
                "false_positives": sf.get("false_positives", []),
                "finding_recall": sf.get("finding_recall", 0.0),
                "n_failures": len(er.failures),
                "failure_categories": [f.category for f in er.failures],
                "n_flags": len(er.forensic_flags),
                "flag_types": [f.flag_type for f in er.forensic_flags],
                "latency_ms": er.agent_result.latency_ms,
                "raw_answer": parsed.final_answer[:500] if parsed else "",
                "raw_key_claims": parsed.key_claims[:5] if parsed else [],
                "run_path": str(run_path),
                "report_path": str(report_path),
            }
            all_results.append(entry)

            # Print summary line
            status = "PASS" if entry["label_correct"] else "MISS"
            print(f"    [{status}] Score: {entry['total_score']:.1f} | "
                  f"Label: {entry['predicted_label']} (gold: {task.gold_label}) | "
                  f"Recall: {entry['finding_recall']:.0%} | "
                  f"FP: {entry['false_positives']}")

    # Save all results
    RESULTS_FILE.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\nAll results saved to: {RESULTS_FILE}")

    # Print summary
    _print_summary(all_results)


def _print_summary(results: list[dict]):
    print("\n" + "=" * 70)
    print("CALIBRATION RE-RUN SUMMARY (v0.6.3)")
    print("=" * 70)

    models = sorted(set(r["model"] for r in results if "error" not in r))
    cases = sorted(set(r["case_id"] for r in results))

    # Overall metrics per model
    print("\n### Per-Model Overview")
    print(f"{'Model':<18} {'Label Acc':>10} {'Avg Score':>10} {'Avg Recall':>11} {'FP Count':>10}")
    print("-" * 65)
    for model in models:
        mr = [r for r in results if r["model"] == model and "error" not in r]
        if not mr:
            continue
        label_acc = sum(1 for r in mr if r["label_correct"]) / len(mr)
        avg_score = sum(r["total_score"] for r in mr) / len(mr)
        avg_recall = sum(r["finding_recall"] for r in mr) / len(mr)
        fp_count = sum(len(r["false_positives"]) for r in mr)
        print(f"{model:<18} {label_acc:>9.0%} {avg_score:>9.1f} {avg_recall:>10.0%} {fp_count:>10}")

    # Solid cases FP detail
    print("\n### False Positives in Solid Cases")
    solid_results = [r for r in results if r["gold_label"] == "solid" and "error" not in r]
    fp_runs = [r for r in solid_results if r["false_positives"]]
    print(f"  Solid runs with FP: {len(fp_runs)}/{len(solid_results)}")
    for r in fp_runs:
        print(f"    {r['model']} on {r['case_id']}: {r['false_positives']}")
    if not fp_runs:
        print("  None detected — CLEAN!")

    # Per-case matrix
    print("\n### Label Accuracy Matrix")
    header = f"{'Case':<30}" + "".join(f"{m:>18}" for m in models)
    print(header)
    print("-" * (30 + 18 * len(models)))
    for case in cases:
        row = f"{case:<30}"
        for model in models:
            mr = [r for r in results if r["case_id"] == case and r["model"] == model and "error" not in r]
            if mr:
                r = mr[0]
                status = "PASS" if r["label_correct"] else f"MISS({r['predicted_label']})"
                row += f"{status:>18}"
            else:
                row += f"{'ERROR':>18}"
        print(row)

    # Mechanism cases detail
    print("\n### Mechanism Cases Detail")
    mech_results = [r for r in results if r["gold_label"] == "mechanism_vs_evidence" and "error" not in r]
    for r in mech_results:
        print(f"  {r['model']} on {r['case_id']}: label={r['predicted_label']} "
              f"correct={r['label_correct']} recall={r['finding_recall']:.0%}")

    # Errors
    errors = [r for r in results if "error" in r]
    if errors:
        print(f"\n### Errors ({len(errors)})")
        for e in errors:
            print(f"  {e['model']} on {e['case_id']}: {e['error'][:100]}")


if __name__ == "__main__":
    main()
