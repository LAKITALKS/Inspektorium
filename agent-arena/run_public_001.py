#!/usr/bin/env python3
"""Public Audit Case 001 — Single Sonnet run.

Usage:
    source ~/.zshrc && PYTHONPATH=src python3 run_public_001.py
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


TASK_FILE = Path("tasks/study_forensics/case_public_001_exercise_intensity.yaml")
AGENT_CONFIG = Path("agents/claude_sonnet.yaml")
OUTPUT_DIR = Path("runs/public_001")
REPORTS_DIR = Path("reports/public_001")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    task = load_task(TASK_FILE)
    cfg = load_agent_config(AGENT_CONFIG)
    provider = get_provider(cfg.provider, model=cfg.model, temperature=cfg.temperature, label=cfg.label)

    print(f"Public Audit Case 001: {task.title}")
    print(f"Model: {cfg.label} ({cfg.model})")
    print(f"Gold label: {task.gold_label}")
    print("=" * 70)

    start = time.time()
    result = run_agent(provider, task)
    elapsed = time.time() - start
    print(f"Run complete: {result.latency_ms}ms ({elapsed:.1f}s wall)")

    run_id = f"public001_sonnet_{uuid.uuid4().hex[:6]}"
    record = evaluate_run(task, run_id, [result])

    run_path = OUTPUT_DIR / f"{run_id}.json"
    run_path.write_text(record.model_dump_json(indent=2))

    report = generate_report(record)
    report_path = REPORTS_DIR / f"{run_id}.md"
    report_path.write_text(report)

    # Print results
    er = record.results[0]
    sf = er.study_forensics or {}
    parsed = er.agent_result.parsed

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Label: {sf.get('detected_label')} (gold: {task.gold_label})")
    print(f"Label correct: {sf.get('label_correct')}")
    print(f"Score: {er.scores.total:.1f}")
    print(f"Finding recall: {sf.get('finding_recall', 0):.0%}")
    print(f"Expected findings: {sf.get('expected_findings')}")
    print(f"Detected findings: {sf.get('detected_findings')}")
    print(f"Matched findings: {sf.get('matched_findings')}")
    print(f"Missed findings: {sf.get('missed_findings')}")
    print(f"False positives: {sf.get('false_positives')}")
    print(f"Failures: {len(er.failures)}")
    for f in er.failures:
        print(f"  [{f.severity}] {f.category}: {f.description[:100]}")

    if parsed:
        print(f"\n{'='*70}")
        print("AGENT OUTPUT")
        print(f"{'='*70}")
        print(f"\nFinal Answer:\n{parsed.final_answer}")
        print(f"\nKey Claims:")
        for i, c in enumerate(parsed.key_claims, 1):
            print(f"  {i}. {c}")
        print(f"\nSteps:")
        for i, s in enumerate(parsed.steps, 1):
            print(f"  {i}. {s[:150]}")
        if parsed.uncertainties:
            print(f"\nUncertainties:")
            for u in parsed.uncertainties:
                print(f"  - {u}")
        if parsed.alternative_hypotheses:
            print(f"\nAlternative Hypotheses:")
            for h in parsed.alternative_hypotheses:
                print(f"  - {h}")

    print(f"\nRun saved: {run_path}")
    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    main()
