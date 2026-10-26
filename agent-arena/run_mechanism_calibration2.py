#!/usr/bin/env python3
"""Mechanism Calibration Sprint 2 — post Case029 relabel + new Case032.

7 cases x 3 models = 21 runs.

Cases:
  - case013 (gut microbes) — mechanism_vs_evidence, clear
  - case024 (Klotho gene therapy) — mechanism_vs_evidence, clear
  - case028 (NAD+ Alzheimer's mice) — mechanism_vs_evidence, clear
  - case029 (amyloid antibody) — RELABELED to solid, clear
  - case030 (APJ exercise mimetic) — mechanism_vs_evidence, clear
  - case031 (rapamycin longevity) — mechanism_vs_evidence, borderline
  - case032 (cholesterol drug biomarker) — mechanism_vs_evidence, clear, NEW

Usage:
    source ~/.zshrc && PYTHONPATH=src python3 run_mechanism_calibration2.py
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
CASES = [
    "case013_gut_microbes.yaml",
    "case024_klotho_gene_therapy.yaml",
    "case028_nad_alzheimers_mice.yaml",
    "case029_amyloid_antibody_biomarkers.yaml",
    "case030_apj_exercise_mimetic.yaml",
    "case031_rapamycin_longevity.yaml",
    "case032_cholesterol_drug_biomarker.yaml",
]
AGENT_CONFIGS = [
    Path("agents/claude_haiku.yaml"),
    Path("agents/claude_sonnet.yaml"),
    Path("agents/claude_opus.yaml"),
]
OUTPUT_DIR = Path("runs/mechanism_calibration2")
REPORTS_DIR = Path("reports/mechanism_calibration2")
RESULTS_FILE = Path("runs/mechanism_calibration2/all_results.json")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    tasks = [load_task(TASK_DIR / f) for f in CASES]

    agents = []
    for ac_path in AGENT_CONFIGS:
        cfg = load_agent_config(ac_path)
        provider = get_provider(cfg.provider, model=cfg.model, temperature=cfg.temperature, label=cfg.label)
        agents.append((cfg, provider))

    total_runs = len(tasks) * len(agents)
    mech_count = sum(1 for t in tasks if t.gold_label == "mechanism_vs_evidence")
    solid_count = sum(1 for t in tasks if t.gold_label == "solid")
    print(f"Mechanism Calibration Sprint 2: {len(tasks)} cases x {len(agents)} models = {total_runs} runs")
    print(f"  mechanism_vs_evidence: {mech_count} | solid: {solid_count}")
    print(f"  Clear: {sum(1 for t in tasks if t.gold_case_type == 'clear')} | Borderline: {sum(1 for t in tasks if t.gold_case_type == 'borderline')}")
    print("=" * 70)

    all_results = []
    run_count = 0

    for task in tasks:
        print(f"\n{'='*70}")
        print(f"CASE: {task.id} — {task.title}")
        print(f"Gold: {task.gold_label} | Type: {task.gold_case_type} | Confidence: {task.gold_confidence}")
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
                    "gold_case_type": task.gold_case_type,
                    "gold_confidence": task.gold_confidence,
                    "model": cfg.label,
                    "model_id": cfg.model,
                    "error": str(e),
                    "elapsed_s": round(elapsed, 1),
                })
                continue

            run_id = f"mc2_{task.id}_{cfg.label.lower().replace(' ', '_')}_{uuid.uuid4().hex[:6]}"
            record = evaluate_run(task, run_id, [result])

            run_path = OUTPUT_DIR / f"{run_id}.json"
            run_path.write_text(record.model_dump_json(indent=2))

            report = generate_report(record)
            report_path = REPORTS_DIR / f"{run_id}.md"
            report_path.write_text(report)

            er = record.results[0]
            sf = er.study_forensics or {}
            parsed = er.agent_result.parsed

            entry = {
                "case_id": task.id,
                "gold_label": task.gold_label,
                "gold_case_type": task.gold_case_type,
                "gold_confidence": task.gold_confidence,
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
                "finding_recall": sf.get("finding_recall", 0.0),
                "false_positives": sf.get("false_positives", []),
                "n_failures": len(er.failures),
                "latency_ms": er.agent_result.latency_ms,
                "raw_answer": parsed.final_answer[:500] if parsed else "",
                "raw_key_claims": parsed.key_claims[:5] if parsed else [],
            }
            all_results.append(entry)

            status = "PASS" if entry["label_correct"] else "MISS"
            fp_str = f" FP:{entry['false_positives']}" if entry["false_positives"] else ""
            print(f"    [{status}] Score: {entry['total_score']:.1f} | "
                  f"Label: {entry['predicted_label']} (gold: {task.gold_label}) | "
                  f"Recall: {entry['finding_recall']:.0%}{fp_str}")

    RESULTS_FILE.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\nAll results saved to: {RESULTS_FILE}")
    _print_summary(all_results)


def _print_summary(results: list[dict]):
    print("\n" + "=" * 70)
    print("MECHANISM CALIBRATION SPRINT 2 SUMMARY")
    print("=" * 70)

    models = sorted(set(r["model"] for r in results if "error" not in r))
    ok = [r for r in results if "error" not in r]

    # A. Overall
    print("\n### A. Per-Model Overview (all 7 cases)")
    print(f"{'Model':<18} {'Accuracy':>10} {'Avg Score':>10} {'Avg Recall':>11}")
    print("-" * 55)
    for model in models:
        mr = [r for r in ok if r["model"] == model]
        acc = sum(1 for r in mr if r["label_correct"]) / len(mr) if mr else 0
        avg_s = sum(r["total_score"] for r in mr) / len(mr) if mr else 0
        avg_r = sum(r["finding_recall"] for r in mr) / len(mr) if mr else 0
        print(f"{model:<18} {acc:>9.0%} {avg_s:>9.1f} {avg_r:>10.0%}")

    # B. By gold_label
    for gl in ["mechanism_vs_evidence", "solid"]:
        subset = [r for r in ok if r["gold_label"] == gl]
        if not subset:
            continue
        print(f"\n### B. {gl.upper()} cases only")
        print(f"{'Model':<18} {'Accuracy':>10} {'Avg Score':>10}")
        print("-" * 40)
        for model in models:
            mr = [r for r in subset if r["model"] == model]
            if not mr:
                continue
            acc = sum(1 for r in mr if r["label_correct"]) / len(mr)
            avg_s = sum(r["total_score"] for r in mr) / len(mr)
            print(f"{model:<18} {acc:>9.0%} {avg_s:>9.1f}")

    # C. Clear mechanism only
    clear_mech = [r for r in ok if r["gold_label"] == "mechanism_vs_evidence" and r["gold_case_type"] == "clear"]
    if clear_mech:
        print(f"\n### C. Clear mechanism_vs_evidence cases only")
        print(f"{'Model':<18} {'Accuracy':>10}")
        print("-" * 30)
        for model in models:
            mr = [r for r in clear_mech if r["model"] == model]
            if not mr:
                continue
            acc = sum(1 for r in mr if r["label_correct"]) / len(mr)
            print(f"{model:<18} {acc:>9.0%}")

    # D. Per-case matrix
    cases = [load_task(TASK_DIR / c).id for c in CASES]
    print("\n### D. Per-Case Label Matrix")
    header = f"{'Case':<35}" + "".join(f"{m:>18}" for m in models)
    print(header)
    print("-" * (35 + 18 * len(models)))
    for case in cases:
        case_r = [r for r in ok if r["case_id"] == case]
        if not case_r:
            continue
        gl = case_r[0]["gold_label"]
        ct = case_r[0]["gold_case_type"]
        marker = f" [{ct[0].upper()}]" if ct else ""
        tag = f" ({gl[:4]})" if gl != "mechanism_vs_evidence" else " (mve)"
        row = f"{case + tag + marker:<35}"
        for model in models:
            mr = [r for r in case_r if r["model"] == model]
            if mr:
                r = mr[0]
                status = "PASS" if r["label_correct"] else f"MISS({r['predicted_label'][:5]})"
                row += f"{status:>18}"
            else:
                row += f"{'ERROR':>18}"
        print(row)

    # E. Borderline
    border = [r for r in ok if r["gold_case_type"] == "borderline"]
    if border:
        print("\n### E. Borderline Cases")
        for r in border:
            status = "PASS" if r["label_correct"] else f"MISS({r['predicted_label']})"
            print(f"  {r['model']} on {r['case_id']}: {status}")

    # F. Case029 (relabeled)
    c029 = [r for r in ok if r["case_id"] == "study-forensics-029"]
    if c029:
        print("\n### F. Case029 (relabeled solid)")
        for r in c029:
            status = "PASS" if r["label_correct"] else f"MISS({r['predicted_label']})"
            fp = r["false_positives"]
            print(f"  {r['model']}: {status} | FP: {fp if fp else 'none'}")

    # G. Case032 (new biomarker)
    c032 = [r for r in ok if r["case_id"] == "study-forensics-032"]
    if c032:
        print("\n### G. Case032 (new biomarker-mechanism)")
        for r in c032:
            status = "PASS" if r["label_correct"] else f"MISS({r['predicted_label']})"
            print(f"  {r['model']}: {status} | recall={r['finding_recall']:.0%}")

    # H. Mislabel patterns
    print("\n### H. Mislabel Patterns")
    misses = [r for r in ok if not r["label_correct"]]
    if misses:
        from collections import Counter
        confusion = Counter()
        for r in misses:
            confusion[r["predicted_label"]] += 1
        for label, count in confusion.most_common():
            who = [f"{r['model']}({r['case_id'][-3:]})" for r in misses if r["predicted_label"] == label]
            print(f"  Predicted '{label}': {count}x — {', '.join(who)}")
    else:
        print("  No misses!")

    # Errors
    errors = [r for r in results if "error" in r]
    if errors:
        print(f"\n### Errors ({len(errors)})")
        for e in errors:
            print(f"  {e['model']} on {e['case_id']}: {e['error'][:100]}")


if __name__ == "__main__":
    main()
