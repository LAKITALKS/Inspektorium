# Phase 7 — Startup / Reconstruction (planning only; implements nothing)

This document reconstructs authoritative state, records what Phase 7 originally was, and
frames what the real-world pilot changes. It runs **no** model, opens **no** holdout,
changes **no** schema, and commits **no** code. Companion documents:

- `existing_control_inventory.md` — requirement → existing component → coverage → gap.
- `real_world_pilot_postmortem.md` — documented failure modes → root cause → controls → regression.
- `phase7_roadmap_and_acceptance.md` — minimal schema deltas, 7A/7B roadmap, acceptance tests, first slice.
- `phase7_status.md` — files, tests/lint, security/data-boundary attestation, recommendation.

## A. Starting state (verified, read-only)

| item | observed |
|---|---|
| branch | `feat/case-library-run-harness` |
| HEAD | `ec57472c188f801cf223c46faf027ae8bb97588d` |
| expected checkpoint | `ec57472…` — **matches exactly** |
| tag `v0.9.0-phase6-closeout` | annotated, points to **HEAD**; message *"Close Phase 6; authorize Phase 7 robustness track"* |
| later commits | **none** (HEAD is the closeout commit) |
| working tree (tracked) | **clean** — no tracked modifications |
| working tree (untracked) | datasets (`Dataset *.pdf/json`), `run_*.py` probes, `research/` (150-case library expansion — **not** LaVita), `.agent_arena/` (decisions/journal jsonl), `.DS_Store`. **None** is LaVita pilot material. |
| Phase-6 decision | **GO FOR PHASE 7** (`phase6_go_no_go_review.md`) — explicitly not conditional |
| baseline tests | **1309 passed** (8.18 s) |
| baseline lint | `ruff check .` → 132 findings (33 in `src/`); all style-nits (F401/F541/F841/E741); **pre-existing at the closeout commit** (see `phase7_status.md`) |

**No STOP condition.** State materially equals the expected checkpoint. No reset / no history
rewrite / no discard was performed or is needed.

## B. What Phase 7 originally was (from repository evidence)

Reconstructed from `phase6_closeout/phase7_handoff.md`, `phase6_go_no_go_review.md`,
`phase6_objective_acceptance_matrix.md`, `phase6_integrated_findings.md`. Phase 7 was scoped as
the **robustness track on development material**, entered under standing governance safeguards —
**not** a defect-remediation phase. Six original priorities:

1. **Boundary-case robustness** — overclaim vs `correlation_vs_causation`; overclaim vs
   `mechanism_vs_evidence`; multi-plausible-mode cases; explicit primary-label prioritization
   (pre-register expected + acceptable-alternate labels).
2. **Perturbation robustness (label-preserving)** — paraphrase, claim/evidence reorder,
   distractor text, weak hedges, source-format changes; invariant: label must not change.
3. **Adversarial robustness** — marketing language, citation decoration, benchmark exaggeration,
   unsupported superiority, causal verbs on correlation, mechanistic language resembling human
   evidence; each adversarial family mapped to the label it attacks.
4. **Replication / stability** — **freeze a replication count (3–5) before execution**;
   deterministic aggregation + disagreement reporting; replication frequency is **not** a
   calibrated probability.
5. **Difficulty / ceiling management** — preserve all cases; nominate harder cases *separately*;
   **no result-driven retirement or relabeling**.
6. **Governance efficiency** — reduce redundant artifacts toward one machine report + one human
   report + one audit manifest + one deterministic generator.

Optional **7b** — independent expert / human validation, objective frozen *before* data; does
not by itself authorize holdout access.

Carry-forward hypothesis (test, do not assume): **overclaim → over-specific** mislabeling
(recurs on DEV-0011/DEV-0013 across Sonnet-6.2 and prompt-only-6.4). The frozen precedence rule
that governs this already exists: `docs/taxonomy_precedence.md`.

## C. What the real-world (LaVita) pilot changes

Freeze the design premise:

```
ANALYSIS QUALITY ≠ ARTIFACT QUALITY
```

Phase 6 controlled the `SOURCE → ANALYSIS` transition. The pilot showed that a scientifically
careful internal analysis can acquire **new** errors in `ANALYSIS → SUMMARY → CLIENT ARTIFACT`:
compression, provenance assignment, and evidence selection are themselves epistemic operations.
Phase 7 therefore gains a second, conceptually distinct track:

```
7A — ANALYSIS ROBUSTNESS          (the original handoff work, preserved)
7B — ARTIFACT / REPRESENTATION ROBUSTNESS   (pilot-driven; new)
```

The pilot is **robustness evidence, not an embarrassment**. Its lesson, which the architecture
must encode: *source-bound analysis is not enough — the representation of that analysis must
itself remain source-bound.* The five documented failure modes and eight regression behaviors
are mapped to concrete controls in `real_world_pilot_postmortem.md`.

## Governance clarification (curator, entering the first slice)

The LaVita commercial pilot is **not** part of the Agent Arena Case Library. Freeze three
distinct data classes:

- **A. Case Library / evaluation data** — the study-forensics cases under `tasks/`.
- **B. Phase-7 robustness evaluation cases** — future boundary/perturbation/adversarial material.
- **C. Pipeline QA regression fixtures** — sanitized synthetic reconstructions of observed
  pipeline failures. **LaVita belongs only conceptually to C.**

LaVita material never enters the case library, development pool, validation/benchmark pool,
holdout, calibration dataset, model-comparison dataset, case counts, difficulty statistics,
accuracy/Brier/ECE, or replication statistics. It is **REAL-WORLD PIPELINE QA EVIDENCE** only.
Class-C fixtures are structurally isolated (`tests/fixtures/pipeline_qa/`, `*.json` ForensicRecords)
and provably excluded from case discovery (see `test_pipeline_qa_isolation.py`).

## Guardrails held this session (unchanged)

- Holdout **sealed**; not inspected, not mapped, not tuned against.
- Frozen claim taxonomy unchanged: `solid`, `overclaim`, `correlation_vs_causation`,
  `mechanism_vs_evidence`; the last stays **biologically scoped** (see `taxonomy_precedence.md`,
  case054). System-QA reason codes are kept **separate** from the four labels.
- No model calls, no schema migration, no fixture generation, no commit, no tag, no version bump.

## Recommendation

See `phase7_status.md` §N. Short form: **READY TO IMPLEMENT PHASE 7 VERTICAL SLICE** — pending
curator approval of the frozen plan. No implementation was started.
