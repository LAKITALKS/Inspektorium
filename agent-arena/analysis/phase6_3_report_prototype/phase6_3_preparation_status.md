# Phase 6.3 — Preparation Status (for curator review)

Minimal, deterministic claim-forensics **report prototype**: a versioned machine-readable
schema (`6.3.0`) plus a human-readable renderer (full + executive) that turn one Agent
Arena analysis into a clear, auditable claim-forensics report. No model was run; no
network; no private/holdout material accessed. **Nothing committed — stops for curator
review.**

## Checkpoint

- HEAD `5349ad091bdbb5668e057c4327767bd2ccc415c9` — verified; tracked tree clean before work.
- Only tracked public material + synthetic fixtures used.

## What was built

- `src/agent_arena/forensic_report.py` — `validate_forensic_report_input`,
  `build_forensic_report`, `validate_forensic_report`, `render_forensic_report_markdown`,
  `render_executive_summary`, `canonical_report_bytes`, `report_digest`. One validated
  object → JSON + Markdown (full + exec). Reuses `confidence_validity.classify_confidence`
  (no 0.0 coercion) and the frozen label / evidence-tier vocabularies. No threshold or
  model-selection logic.
- `src/agent_arena/cli.py` — added a minimal `forensic-report` command (offline, matches
  the existing `@cli.command` + lazy-import convention). Also fixed two **pre-existing**
  F541 lint warnings in the unrelated `run` command (removed an `f` prefix on two constant
  strings; behavior-preserving) so the changed file lints clean.
- `tests/test_forensic_report.py` — 80 tests.
- `analysis/phase6_3_report_prototype/` — schema, design/field/risk docs, 15 synthetic
  fixtures, a deterministic example generator, and worked example artifacts.

## Frozen vocabularies (reused, not redefined)

- Labels `solid · overclaim · correlation_vs_causation · mechanism_vs_evidence`
  (`study_forensics_checker`); `mechanism_vs_evidence` kept **biologically scoped**.
- Evidence tiers `cell · animal · biomarker · limited_human · clinical_human`
  (`runner.py`).
- Confidence `VALID / MISSING / INVALID` (Phase 6.1) — never coerced to 0.0.
- Evidence roles `supporting · weakening · contradictory · missing_expected`
  (`schemas.EvidenceRole`).
- Added, documented: reader-impact risk `low · moderate · high · critical (+ unknown)`;
  `analysis_status`; `evidence_sufficiency`.

## Synthetic examples

15 fixtures cover all four labels + missing/invalid confidence, missing/empty evidence,
parser failure, high reader-impact, no-safe-rewrite (guard blocks a fabricated number),
multiple failure modes, unsupported superiority, missing comparison group, missing causal
chain. All marked `synthetic_fixture=true`; the worked example renders `04_mechanism_vs_evidence`.

## Validation results

| gate | result |
|---|---|
| targeted 6.3 tests | **80 passed** |
| 6.3 + confidence + output-contract tests | **139 passed** |
| full test suite | **1242 passed** (was 1162; +80) |
| ruff on changed source/test files | **clean** (`forensic_report.py`, `cli.py`, `test_forensic_report.py`, `build_examples.py`) |
| deterministic regeneration (2 independent processes) | **byte-for-byte identical**; matches on-disk examples |
| leakage scan of data-bearing artifacts (fixtures + examples) | **clean** — the only 64-hex values are the example's own `input_digest`/`report_generation_digest`, both **reproducible from the committed synthetic fixture** (public, not private) |

_Leakage-scan notes:_ the forbidden-token literals present are exclusively (a) the
leakage-**detector's** own regex vocabulary in `forensic_report.py` and (b) boundary
**documentation** (startup doc, schema `x_forbidden_anywhere`) naming what is forbidden —
neither is private data. The rejection test assembles forbidden tokens at runtime so the
tracked test file contains no literal canonical/BIAA/HLD/DEV id or private path.

## Boundaries respected

No access to `AgentArena_IAA_Private/`, `internal_only/`, `candidate_eligibility.csv`,
private mappings, raw responses, sealed holdout, `research/`, or unrelated datasets. No
frozen taxonomy/label/gold/status/Phase-5/6.1/6.2/runtime-contract artifact modified;
committed Phase 6.2 result reports untouched. **Phase 6.4 not begun.** No auto-commit.

## Proposed commit paths (nothing staged yet)

```
src/agent_arena/forensic_report.py            (new)
src/agent_arena/cli.py                          (modified: forensic-report cmd + 2 lint fixes)
tests/test_forensic_report.py                   (new)
analysis/phase6_3_report_prototype/             (new: schema, docs, 15 fixtures, generator, examples)
```

Proposed commit message:

```
Phase 6.3 prototype: deterministic claim-forensics report schema and renderer
```
