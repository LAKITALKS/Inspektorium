# Phase 6.3 — Startup Report (before implementation)

**Scope:** design and implement a minimal, deterministic Agent Arena **claim-forensics
report prototype** — a versioned machine-readable schema plus a human-readable renderer
that turn one Agent Arena analysis into a clear, auditable claim-forensics report. This
is a report prototype, **not** a web application. No model is run; no network calls; no
private/holdout material is touched.

## Checkpoint

- Expected HEAD `5349ad091bdbb5668e057c4327767bd2ccc415c9` — **verified**.
- Tracked working tree **clean** before work.
- Only tracked public repository material and synthetic fixtures are used.

## What the repository already gives us (reused, never redefined)

| concept | source (tracked) | reuse in 6.3 |
|---|---|---|
| Frozen labels | `study_forensics_checker.py`, `schemas.Task.gold_label` | `solid`, `overclaim`, `correlation_vs_causation`, `mechanism_vs_evidence` — used verbatim |
| **Evidence tiers** | `runner.py` analysis contract (l.51–56, l.82) | `cell · animal · biomarker · limited_human · clinical_human` (weakest→strongest) — reused as the evidence-tier vocabulary |
| Conclusion tiers | `runner.py` (l.83) | `same_as_evidence · human_therapeutic · human_policy · general_public` |
| Plain-language label text | `reporting.py` `CATEGORY_LABELS` | basis for the verdict titles (refined per the Phase 6.3 brief) |
| Confidence VALID/MISSING/INVALID | `confidence_validity.classify_confidence` (Phase 6.1) | **the single source of truth** for confidence status; never coerced to 0.0 |
| Failure-mode / finding vocabulary | `study_forensics_checker._FINDING_PATTERNS`, `schemas.FailureCategory` | frozen failure-mode enum for section E |
| Evidence roles | `schemas.EvidenceRole` | `supporting · weakening · contradictory · missing_expected` |
| Robust parse diagnostics | `output_contract.ParseDiagnostics` | parser-failure → failure report (never a normal verdict) |

**Important reuse note:** `output_contract._build_response` coerces a missing/non-numeric
confidence to `0.0` (l.205–209). The forensic report must **never** consume that coerced
value — it classifies the **raw** confidence via `classify_confidence`, exactly as Phase
6.1 requires.

## `mechanism_vs_evidence` scope (preserved, not broadened)

Per `runner.py` and the Phase 6.3 brief, `mechanism_vs_evidence` stays **biologically
scoped**: it applies when biological mechanism or preclinical evidence (cell / animal /
biomarker / limited human) is used to imply **human clinical benefit**. The prototype
does not broaden it into a general mechanism/evidence category; the verdict title makes
the biological scope explicit.

## Frozen vocabularies the prototype adds (documented in `field_semantics.md` / `risk_vocabulary.md`)

- **reader-impact risk:** `low · moderate · high · critical`, plus an explicit
  `unknown` state when information is insufficient. Qualitative only — **no** computed
  medical/legal/financial harm probability.
- **analysis_status:** `complete · parser_failure · insufficient_input`.
- **evidence_sufficiency:** `sufficient · insufficient · unknown`.
- **report_schema_version:** `6.3.0`.

## Planned implementation (smallest convincing surface)

- `src/agent_arena/forensic_report.py` —
  `validate_forensic_report_input`, `build_forensic_report`, `validate_forensic_report`,
  `render_forensic_report_markdown`, `render_executive_summary`, `canonical_report_bytes`,
  `report_digest`. Integrates `confidence_validity`; introduces no threshold/model-selection
  logic.
- `tests/test_forensic_report.py` — all four labels, the biological `mechanism_vs_evidence`
  scope, confidence VALID/MISSING/INVALID (no 0.0 coercion, bool/out-of-range rejected),
  parser-failure status, empty evidence preserved, no invented source/rewrite facts,
  label↔title consistency, risk-vocabulary validation, exec-vs-full verdict parity,
  determinism (JSON + Markdown, one-char digest change), and leakage rejection.
- Optional minimal CLI command `forensic-report` (fits the existing `@cli.command` +
  `click.echo(json.dumps(...))` convention) only if it clearly helps the demo.

## Design guarantees (mapped to the brief)

- One validated report object → **both** JSON and Markdown (single truth source; the
  executive summary derives from the same object and preserves verdict/confidence/limits).
- Deterministic canonical JSON (sorted keys, fixed serialization) and a report digest;
  a one-character input change changes the digest.
- Missing/invalid values stay explicit (MISSING/INVALID/unknown), never silently filled.
- Evidence is never invented; a rewrite is guarded against introducing unsupported new
  facts (numeric-token containment guard) and drops to "no safe rewrite available" if it
  would.
- A classification is explicitly **not** presented as proof of factual falsity.
- All examples are **synthetic** and labelled as such; never presented as real Agent
  Arena performance.

## Boundaries

No access to `AgentArena_IAA_Private/`, `internal_only/`, `candidate_eligibility.csv`,
private mappings, raw provider responses, sealed holdout, `research/` expansion, or
unrelated untracked dataset files. No frozen taxonomy/label/gold/status/Phase-5/Phase-6.1/
Phase-6.2/runtime-contract artifact is modified. Phase 6.4 is not begun. No auto-commit —
stops for curator review after implementation and validation.
