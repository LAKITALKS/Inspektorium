# Agent Arena — Architecture Ledger (as of v0.7.7)

*Facts describe current code/behavior. Interpretations and recommendations are labelled.*

## Case schema [FACT]
Defined by the Pydantic `Task` model (`src/agent_arena/schemas.py`). Relevant fields:
`id, title, domain, difficulty, task_type, prompt, context, expected_answer,
reference_solution, evaluation, output_schema, origin, key_insights, common_errors,
task_family, trap_type, ambiguity_level, expected_failure_modes, discriminative_dimensions,
diagnostic_focus, gold_label, gold_summary, expected_findings, gold_evidence_spans,
gold_confidence, gold_justification, gold_alternative_reading, gold_case_type, curator_notes`.
Added at v0.7.7: **`status: str | None`** and **`excluded_from_active_metrics: bool = False`**
(both optional/defaulted → back-compatible). The loader (`task_loader.load_task` = `Task(**data)`)
uses pydantic default `extra="ignore"`, so unknown YAML keys (e.g. `intake_review`,
`suite_history`, `superseded_by`) are tolerated but not acted upon by the engine.

## Supported labels / taxonomy [FACT]
`gold_label` is one of exactly four values enforced by tests:
`solid`, `overclaim`, `mechanism_vs_evidence`, `correlation_vs_causation`.
Richer intended classifications (misleading, insufficient_evidence, cautious_supported, …) exist
**only in documentation**, not in code.

## Task YAML structure [FACT]
One file per case in `tasks/study_forensics/`. Convention: `caseNNN_slug.yaml` with internal id
`study-forensics-NNN`. 50 files exist. Cases carry gold label + justification + alternative
reading + expected findings + evidence spans + curator notes. New Phase-3 cases set
`origin: synthetic_fixture`; the two showcase cases use `curated_showcase` (041) and
`demo_derived` (042).

## Evaluator / judge prompt structure [FACT]
- Study-forensics system prompt lives in `runner.py` (`STUDY_FORENSICS_PROMPT`) and includes an
  EVIDENCE-TIER CHECK and a PRIORITY RULE (overclaim vs mechanism_vs_evidence). **Not changed in
  this dossier.**
- The evaluator (`evaluator.py`) produces `DiagnosticScores` (10 weighted dimensions) plus a
  `study_forensics` dict (`detected_label`, `label_correct`, finding recall, false positives,
  hedge-overclaim). Scoring semantics unchanged since before this dossier.
- Optional LLM judge (`judge.py`) is a separate model path; its parser was harmonized in Phase 2.5.

## Provider abstraction [FACT]
`BaseProvider` (abstract `send_prompt`, concrete `generate → ModelResponse`). Registry:
`anthropic`, `openai`, `ollama` (+ in-process `FakeLibraryProvider` for offline runs). Errors are
normalized via `classify_error_type`.

## Parser / normalization layer [FACT]
`output_contract.py`: `extract_json_object` (shared) and `parse_structured_output` (agent path).
Handles fenced/unfenced JSON, pre/post prose, string-aware brace scanning, best-effort truncation
repair, and returns `ParseDiagnostics` (strategy, fence_closed, truncation_suspected, repaired,
missing/unexpected fields, finish_reason). Never raises.

## Run harness [FACT]
`run_library.py`: `discover_cases`, `run_single`, `run_library`, stability computation,
`render_summary_md`, and an argparse CLI (`python -m agent_arena.run_library`). Artifacts:
`runs/library/<id>/{manifest.json, results.jsonl, summary.json, summary.md}` (`runs/` is
git-ignored).

## Case discovery + active/retired filtering [FACT]
`discover_cases(task_family, case_id, limit, synthetic_only, label, include_retired)`:
- Selects study_forensics tasks by filename order.
- **Excludes retired cases by default** — `is_retired(t)` = `excluded_from_active_metrics` OR
  `status == "retired"`.
- `include_retired=True` returns all; an explicit `case_id` for a retired case still returns it.
- Current counts: **49 active, 1 retired** (case042).

## Multi-run analysis [FACT]
Descriptive only: label consistency, unique labels, score mean/min/max/range/std, confidence
stats (uncalibrated self-report), and flags `stable_label / unstable_label / parse_fragile /
truncation_risk / provider_error_seen / high_score_variance`. No proper scoring / Bayesian /
Brier — by design.

## Report generation [FACT]
- Per-run internal dossier (`reporter.py`) and client report (`reporting.py`, optional weasyprint
  PDF) exist from earlier versions; not modified in Phases 0–5A.
- Library summary MD/JSON produced by `run_library`.
- Phase-5A offline analysis bundle produced by an **out-of-repo scratchpad generator**
  (the artifacts are committed; the generator script is not — see risks/recommendations).

## Current analysis artifacts [FACT]
- `analysis/phase5a/lib_20260704_134553_55aa66/` — 12 committed report files (v0.7.6).
- `analysis/phase4_9_retrospective/` — this dossier (uncommitted).

## Current test coverage [FACT]
`pytest -q` = **988 passed** at v0.7.7. Notable suites: output_contract, provider_contract,
judge_parser, study_forensics, case_library, run_library (incl. `TestRetirement`). Tests use
fixtures/fakes; **no live API keys required**.

## Known untracked cruft [FACT]
21 untracked entries in the working tree (ad-hoc `run_*.py` scripts, `Dataset *.pdf/json`,
`.DS_Store`, `.agent_arena/` journal). Intentionally never committed. `.env` is git-ignored.

## Interpretation [INTERPRETATION]
The engine is now cleanly layered (providers → parser → evaluator → harness → reporting) with a
real, tested retirement mechanism. The main non-code-quality gap is epistemic: the benchmark has
only been exercised against **one strong model**, and the taxonomy is a single 4-way label with no
precedence rule when two labels legitimately apply.

---

## Recommended future architecture [RECOMMENDATION — not current facts]
These are proposals for review, not implemented behavior.

- **Suite architecture: Core / Boundary / Retired / Quarantine.** Promote the Phase-5A
  `suite_assignment_draft` into first-class metadata so headline metrics report Core separately
  from Boundary, and Retired/Quarantine are excluded by default (retirement filtering already
  exists; the multi-suite split does not).
- **Explicit taxonomy precedence rules.** A documented, tested rule for which label wins when two
  legitimately apply (e.g., specific evidence-gap label vs generic overclaim). Apply consistently
  across the library.
- **Stable-alternative adjudication policy.** A written protocol: stable-alternative → human review;
  never auto-flip; record the decision + rationale in `suite_history`.
- **Active-vs-retired metrics reporting.** Report/regeneration layer that always states active
  count, retired count, and never silently mixes historical and active metrics.
- **Replacement-case workflow.** Formalize `supersedes` / `superseded_by` linkage and a checklist
  for replacing a retired case with a clean new case_id.
- **Real-world case intake checklist.** Enforced fields for archived source, citation, provenance,
  and verification before a real-world case counts.
- **Model-panel Phase 5B.** Weak/mid/strong panel + cross-model disagreement (entropy) and
  weak-model error rate as the discrimination metric.
- **Metamorphic robustness tests.** Label-preserving perturbations (paraphrase, reorder, hedge
  swaps) to test that gold labels are robust to surface changes.
- **Evidence-hierarchy upgrade.** Optional explicit evidence-tier weighting instead of relying only
  on the prompt's EVIDENCE-TIER CHECK.
- **Negative-space auditing.** Track what the library does NOT cover (missing patterns/domains).
- **Report engine / customer-safe outputs.** A hardened report path with source-safety (no full
  third-party article reproduction) and calibration caveats before any external use.
- **Holdout set.** A set never used for gold tuning, to bound co-evolution/overfitting risk.

---

## Current update as of v0.8.2 — Claim Novelty Auditor deduplication integration

*Appended 2026-07-10. Everything above is preserved as the **v0.7.7 snapshot** and is
not rewritten. This section records the forward-roadmap state after the Phase 5.0 /
5.05 work (tags v0.8.0 → v0.8.2) and the Claim Novelty Auditor deduplication audit.
Documentation only — no code, schema, YAML, prompt, or metric changes.*

### Status correction (roadmap altitude) [FACT]
- **Phase 5.05b** (strongly anonymized multi-annotator blind packets) — **COMPLETE** (v0.8.2).
- **Active next operational step: Phase 5.05c** — import blind annotator responses and
  compute agreement (see `../phase5_05_blind_iaa_design/next_steps_after_iaa.md`).
- **After 5.05c:** IAA disposition, then **Holdout Freeze**.
- **Small Model Panel (Phase 5B / 5.1)** remains **gated** behind 5.05c + holdout freeze.
- **Real-world case intake** remains **deferred** (intake/provenance schema not ready).
- **Historical Phase-5A metrics remain frozen** — never recalculated.

### Greenfield correction — components that ALREADY EXIST [FACT]
The "Recommended future architecture" list above must be read as **extension targets,
not greenfield builds**. The following are already implemented and tested:
- **`calibrate.py` (Gen 2)** — `generate_calibration_report` → CalibrationReport /
  CalibrationProposal (fp_reduction, gold_review, category_refinement, model_confusion,
  data_gap). Suggests, never mutates.
- **`disagreement_lab.py` (Gen 5)** — `analyze_disagreements` → DisagreementLabReport
  (alternative readings, borderline assessment, root-issue attribution). Never flips labels.
- **`audit_trail.py` (Gen 6)** — `DecisionEntry` + upstream provenance chain
  (`UpstreamStep`, `dependency_confidence`, `propagation_risk_level`, `review_override`).
- **`reasoning_graph.py`** — `GroundingAudit` (direct/indirect/unsupported) + MechanismAnalysis.
- **`reporting.py` — Report Engine v1** — Executive Summary / Key Findings / What To Change /
  Method Note (incl. "What This Audit Does Not Cover" + "Confidence Levels") / Technical
  Appendix (incl. 10-axis `DiagnosticScores` Score Matrix).

Any future calibration / disagreement / provenance / grounding / report work is an
**extension or integration** of these — **not a parallel module**.

### Roadmap Changes from Claim Novelty Auditor Analysis
Design principles and governance rules only. **No new numbered phase; no code in this pass.**
1. **Adversarial Evidence Evaluation** — design principle: a verdict should survive a
   structured attempt to find the strongest counter-source / counterargument.
2. **Evidence-traceable verdicts** — every verdict should trace to evidence spans
   (reuse `EvidenceSpan` + `GroundingAudit`), not free assertion.
3. **Coverage-honest verdicts** — a verdict states what it did **not** examine (extends the
   existing "What This Audit Does Not Cover").
4. **Coverage-bounded confidence** — confidence must be bounded by coverage; do not report
   high confidence over an admittedly partial review.
5. **Falsification-open reports** — a report should state what would change the verdict.
6. **Retrieval/context/source/reasoning-path independence** — governance rule: independent
   evidence/reasoning paths should corroborate a verdict; a verdict resting on a single path
   is weaker. Measured only if/when defined; no retrieval layer is built by this rule.
7. **Claim Novelty Auditor — PARKED** as a later internal ASCR/LEM tool (not a phase, not built now).
8. **No seven-agent or free-debate architecture** — the deterministic Gen 1–7 tool stack stands;
   `pipeline.py` orchestrates deterministic modules and "does NOT add new intelligence".

### Report Engine v1 extensions (extend `reporting.py`, NOT a new engine)
Documentation of intended fields; **no code in this pass**.
- **Coverage Summary** — extends the existing "What This Audit Does Not Cover" concept.
- **Confidence by Axis** — must **reuse `DiagnosticScores` + existing confidence logic**
  (FAILURE/CONSISTENCY confidence maps); no new confidence system.
- **What Would Change This Verdict?** — a **genuinely new** field.
- **Alternative Reading** and **Falsification Condition** must remain **distinct** concepts
  (alternative = a different defensible reading; falsification = what evidence would flip it).
- This is an **extension of `reporting.py`**, not a second report engine.

### Three-case adversarial challenge experiment (small, gated)
- **Placement:** after Phase 5.05c, after **Holdout Freeze**, before the Small Model Panel;
  **non-holdout cases only** (running it on holdout cases would contaminate the holdout).
- **Purpose:** test whether a structured challenge pass yields **≥1 measurable benefit** —
  finds a missed substantive counter-source/counterargument, narrows an over-absolute verdict,
  recalibrates confidence, improves evidence traceability, or confirms robustness.
- **Reuse:** `run_library`, `consistency`, `disagreement_lab`, and `GroundingAudit` where applicable.
- **Constraints:** no new UI, no new database, no autonomous debate system, and **no permanent
  harness integration unless the experiment demonstrates benefit**.

### Duplicate-prevention notes (do NOT create)
Do **not** create: a standalone `EvidenceLedger` module, a standalone `CoverageLedger` module,
a parallel calibration module, a parallel disagreement module, a parallel reproducibility
framework, a second report engine, a second roadmap, or a seven-agent architecture.
**Likely extension targets instead:** `EvidenceSpan`, `audit_trail`, `calibrate`,
`disagreement_lab`, `reasoning_graph` / `GroundingAudit`, `reporting.py`, run `manifest` / `journal`.

### Parked backlog (documented only — not scheduled, not built)
- Claim Novelty Auditor (internal ASCR/LEM tool)
- Strongest-Threat Rank (as a formal benchmark metric)
- Evidence Independence Score
- Counterevidence Recall (as a formal cross-track metric)
- Prior-Art Forensics
- Cross-Community Retrieval
- Residual Novelty analysis
