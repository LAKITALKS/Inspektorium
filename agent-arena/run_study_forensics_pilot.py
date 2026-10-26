#!/usr/bin/env python3
"""Study Forensics Pilot Run — agent-arena v0.6.

Runs the 6 pilot study forensics cases through Agent Arena using synthetic
agent responses. No live LLM calls required.

Usage:
    python run_study_forensics_pilot.py [--output-dir DIR]

This script:
1. Loads all 6 study forensics task files
2. Creates synthetic agent responses that simulate realistic LLM output
3. Evaluates each response through the full Agent Arena pipeline
4. Generates a per-case forensic report
5. Prints a summary of results
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

from agent_arena.evaluator import evaluate_run
from agent_arena.reporter import generate_report
from agent_arena.schemas import AgentResponse, AgentResult, RunRecord
from agent_arena.task_loader import load_task


TASK_DIR = Path("tasks/study_forensics")
OUTPUT_DIR = Path("runs/pilot_study_forensics")
REPORTS_DIR = Path("reports/pilot_study_forensics")


# ---------------------------------------------------------------------------
# Synthetic agent responses — simulate what a capable LLM might produce
# ---------------------------------------------------------------------------

SYNTHETIC_RESPONSES: dict[str, dict] = {
    "study-forensics-001": {
        "final_answer": "This is a solid study. The randomised experimental design supports causal inference. The authors are careful not to overgeneralise and openly acknowledge limitations.",
        "assumptions": [
            "The study was conducted rigorously with proper randomisation",
            "Self-report measures are adequate for depression and loneliness",
        ],
        "steps": [
            "The study uses random assignment — this is a true experiment, not observational.",
            "143 participants is modest but sufficient for detecting effect sizes in within-subject designs.",
            "The evidence supports the claim: restricting social media use reduced depression and loneliness.",
            "The authors show cautious scope control by noting the study only covers college students and three platforms.",
            "No major epistemic failures detected. The conclusion matches the evidence.",
        ],
        "alternative_hypotheses": [
            "Could there be a demand effect? Unlikely given objective usage data from screenshots.",
        ],
        "uncertainties": [
            "Self-report measures may be subject to social desirability bias",
            "Three-week timeframe may not capture long-term effects",
        ],
        "key_claims": [
            "This is a solid, well-designed study with appropriate caveats",
            "Evidence matches the claim made by the authors",
            "No major epistemic failures",
        ],
        "self_check": [
            "Am I overflagging? No — the study design is genuinely strong and authors are cautious.",
            "Could I be missing a subtle issue? The sample size is modest but acknowledged.",
        ],
        "confidence": 0.88,
    },
    "study-forensics-004": {
        "final_answer": "This is a solid study. The double-blind RCT with 3,500+ participants reports a modest but real effect. The authors describe it as modest and acknowledge demographic limitations. No overclaim.",
        "assumptions": [
            "The trial was properly blinded and controlled",
            "Immediate recall is a valid cognitive measure",
        ],
        "steps": [
            "Large double-blind RCT (n>3500) — strong design.",
            "Effect size: 0.7 words improvement vs 0.4 in placebo — modest but consistent.",
            "Authors explicitly call the effect 'modest' — evidence matches claim.",
            "Demographic caveat acknowledged: predominantly white, well-educated.",
            "Authors call for more diverse populations — cautious scope control.",
            "No overclaim detected. The reporting is appropriately qualified.",
        ],
        "alternative_hypotheses": [
            "Could this be overclaim given the small effect? No — the authors frame it appropriately.",
        ],
        "uncertainties": [
            "Which specific nutrients drive the effect remains unknown",
            "Generalisability to diverse populations is uncertain",
        ],
        "key_claims": [
            "Solid study with appropriately modest claims",
            "Evidence matches the conclusion",
            "Demographic limitations properly acknowledged",
        ],
        "self_check": [
            "Is the effect too small to be meaningful? The authors address this — they call it modest.",
        ],
        "confidence": 0.85,
    },
    "study-forensics-007": {
        "final_answer": "This is an overclaim case. The primary outcome (acute infection severity) was null. The secondary finding (4 percentage points difference in lingering symptoms) is very small and framed with misleading optimism. The uncertainty language is decorative.",
        "assumptions": [
            "The trial was properly conducted despite being remote",
            "21% vs 25% is the accurate reported difference",
        ],
        "steps": [
            "Primary outcome was null: vitamin D did not change acute infection severity.",
            "Secondary outcome: 21% vs 25% — a 4 percentage point difference.",
            "This small absolute difference is described as a 'promising signal' — this conclusion exceeds the results.",
            "The phrase 'larger trials are needed' is decorative uncertainty — it accompanies but does not constrain the optimistic framing.",
            "Study started supplementation after infection onset, limiting causal interpretation.",
            "Overall: mild overclaim driven by framing a weak secondary result as promising.",
        ],
        "alternative_hypotheses": [
            "Could this be solid? No — the null primary outcome and small secondary effect don't warrant 'promising signal'.",
        ],
        "uncertainties": [
            "Statistical significance of the 4pp difference is not stated",
            "Remote conduct may introduce unmeasured biases",
        ],
        "key_claims": [
            "Primary outcome was null — acute COVID-19 severity unchanged",
            "The conclusion exceeds the results",
            "Uncertainty language is decorative, not constraining",
        ],
        "self_check": [
            "Am I being too harsh? The authors do hedge — but the framing is still optimistic beyond the data.",
        ],
        "confidence": 0.80,
    },
    "study-forensics-009": {
        "final_answer": "This is an overclaim case. Although the trial design is solid, the lead investigator's claim that they are 'already convinced' the app could help autistic adults and suggests it might benefit 'people of all ages' is an unsupported generalization that goes beyond the evidence.",
        "assumptions": [
            "The RCT design was properly executed",
            "Replication by the wait-list control is a strength",
        ],
        "steps": [
            "The trial design is solid: RCT with wait-list control and replication.",
            "Results are promising: significant reductions in anxiety and stress.",
            "However, the investigator's statement goes beyond the data: 'already convinced' suggests premature certainty.",
            "Extending the claim to 'people of all ages' is an unsupported generalization — only 89 autistic adults were studied.",
            "The conclusion exceeds the results when the investigator speaks beyond the trial's scope.",
            "This is a case where a good study leads to overclaim through investigator rhetoric.",
        ],
        "alternative_hypotheses": [
            "Could this be solid? The study itself is, but the claims made about it are not.",
        ],
        "uncertainties": [
            "Six-week persistence may not indicate long-term durability",
            "Wait-list controls can inflate effect sizes",
        ],
        "key_claims": [
            "The investigator's generalization to all ages is unsupported",
            "The conclusion exceeds what the data can support",
            "Good study design does not prevent overclaim in interpretation",
        ],
        "self_check": [
            "Am I separating the study quality from the claim quality? Yes — the study is solid but the framing is not.",
        ],
        "confidence": 0.85,
    },
    "study-forensics-013": {
        "final_answer": "This is a mechanism_vs_evidence case. The mechanistic finding in mice is solid, but the leap to human probiotic therapy is speculative. The mechanism is demonstrated in rodents but not in humans. The caution about human trials is present but insufficient to prevent the overreach.",
        "assumptions": [
            "The animal model findings are reliable",
            "Indole modulation of amygdala activity is established in mice",
        ],
        "steps": [
            "The study demonstrates a clear mechanism in mice: indoles modulate the basolateral amygdala.",
            "Causal evidence in animals: germ-free mice show heightened anxiety, reversed by colonisation.",
            "The leap to human therapy is speculative — mechanism not demonstrated in humans.",
            "The proposal of 'indole-producing probiotics for anxiety disorders' is an unsupported generalization from animal to human.",
            "The caution 'human trials are needed' shows some scope control, but the speculative framing still overreaches.",
        ],
        "alternative_hypotheses": [
            "Could this be overclaim? It's close, but the core issue is mechanism vs. evidence — not just claim inflation.",
        ],
        "uncertainties": [
            "Human gut-brain axis may work differently from mice",
            "Indole effects may not translate across species",
        ],
        "key_claims": [
            "Mechanism is demonstrated in animals but not humans",
            "The translation from mouse model to human therapy is unproven",
            "Cautious scope control is present but doesn't prevent overreach",
        ],
        "self_check": [
            "Am I distinguishing mechanism strength (mice) from evidence gap (humans)? Yes.",
        ],
        "confidence": 0.82,
    },
    "study-forensics-019": {
        "final_answer": "This is a clear correlation_vs_causation case. A cross-sectional survey found an association between houseplants and lower depression scores, but the article makes causal claims and policy recommendations from correlational data. Major confounders are acknowledged but not controlled for.",
        "assumptions": [
            "The survey data is accurately reported",
            "The 30% difference refers to average depression scores",
        ],
        "steps": [
            "Cross-sectional survey — no experimental design, no causal inference possible.",
            "The 30% lower depression score is a correlation, not causation.",
            "The article says 'bringing the outdoors in can improve mental health' — this is a causal claim from correlational data.",
            "The policy recommendation to reimburse plant purchases is an unsupported generalization.",
            "Confounders are acknowledged (income, natural light, leisure time) but not controlled for.",
            "This is correlation treated as causation, with an unsupported policy leap.",
        ],
        "alternative_hypotheses": [
            "Could higher income explain both plant ownership and lower depression? Very likely — this is a classic confounder.",
        ],
        "uncertainties": [
            "The actual causal pathway is unknown",
            "Self-selection bias is likely",
        ],
        "key_claims": [
            "Correlation is presented as causation",
            "Policy recommendation is unsupported by causal evidence",
            "Obvious confounders are noted but not addressed",
        ],
        "self_check": [
            "Is there any causal evidence here? No — purely cross-sectional, confounders uncontrolled.",
        ],
        "confidence": 0.92,
    },
}


def _build_synthetic_result(task_id: str) -> AgentResult:
    """Create an AgentResult from a synthetic response."""
    data = SYNTHETIC_RESPONSES.get(task_id)
    if not data:
        return AgentResult(
            provider="synthetic",
            model="synthetic-pilot-v1",
            error=f"No synthetic response for {task_id}",
        )
    parsed = AgentResponse(**data)
    return AgentResult(
        provider="synthetic",
        model="synthetic-pilot-v1",
        raw_output=json.dumps(data, indent=2),
        parsed=parsed,
        parse_ok=True,
        latency_ms=0,
    )


def run_pilot(output_dir: Path | None = None, reports_dir: Path | None = None):
    """Run the study forensics pilot."""
    output_dir = output_dir or OUTPUT_DIR
    reports_dir = reports_dir or REPORTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    task_files = sorted(TASK_DIR.glob("*.yaml"))
    if not task_files:
        print(f"No task files found in {TASK_DIR}")
        sys.exit(1)

    print(f"Study Forensics Pilot — {len(task_files)} cases")
    print("=" * 60)

    all_records: list[RunRecord] = []
    summary_lines: list[str] = []

    for tf in task_files:
        task = load_task(tf)
        print(f"\n--- {task.id}: {task.title} ---")
        print(f"Gold label: {task.gold_label}")

        result = _build_synthetic_result(task.id)
        run_id = f"pilot_{uuid.uuid4().hex[:8]}"
        record = evaluate_run(task, run_id, [result])
        all_records.append(record)

        # Save run
        run_path = output_dir / f"{run_id}.json"
        run_path.write_text(record.model_dump_json(indent=2))

        # Generate and save report
        report = generate_report(record)
        report_path = reports_dir / f"{run_id}_{task.id}.md"
        report_path.write_text(report)

        # Print summary
        er = record.results[0]
        sf = er.study_forensics
        total = er.scores.total
        label_ok = sf.get("label_correct", False) if sf else False
        recall = sf.get("finding_recall", 0.0) if sf else 0.0
        detected = sf.get("detected_label", "?") if sf else "?"

        status = "PASS" if label_ok else "MISS"
        line = f"  [{status}] Score: {total:.1f}/100 | Label: {detected} (gold: {task.gold_label}) | Recall: {recall:.0%}"
        print(line)
        summary_lines.append(f"{task.id}: {line}")

        # Show failures
        for f in er.failures[:3]:
            print(f"    FAIL: [{f.severity}] {f.category}: {f.description[:80]}")

    # Final summary
    print("\n" + "=" * 60)
    print("PILOT SUMMARY")
    print("=" * 60)
    n_correct = sum(1 for r in all_records
                    if r.results[0].study_forensics.get("label_correct", False))
    avg_score = sum(r.results[0].scores.total for r in all_records) / len(all_records)
    avg_recall = sum(
        r.results[0].study_forensics.get("finding_recall", 0.0) for r in all_records
    ) / len(all_records)

    print(f"Cases: {len(all_records)}")
    print(f"Label accuracy: {n_correct}/{len(all_records)} ({n_correct/len(all_records):.0%})")
    print(f"Avg score: {avg_score:.1f}/100")
    print(f"Avg finding recall: {avg_recall:.0%}")
    print()
    for line in summary_lines:
        print(f"  {line}")

    print(f"\nRuns saved to: {output_dir}")
    print(f"Reports saved to: {reports_dir}")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    run_pilot(output_dir=out)
