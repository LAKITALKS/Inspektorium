# Fable 5 Audit Brief — Agent Arena (self-contained)

*A compact briefing for an external benchmark-integrity auditor. Written neutrally; it does not
claim benchmark validity from a single-model run. Facts, interpretations, and open questions are
labelled.*

## What Agent Arena is [FACT]
A local-first evaluation engine for **claim-forensics**: given a short text making a scientific or
commercial claim, an agent must classify the epistemic failure mode and support it with evidence.
The primary task family is `study_forensics`. Each case has a curator gold label, a justification,
a documented alternative reading, expected findings, and evidence spans. The engine scores an
agent's structured response across diagnostic dimensions; an optional LLM judge is a separate path.

## Current repo state [FACT]
- Tag: **v0.7.7-retire-case042** (commit `19aa295`).
- Library: **49 active cases + 1 retired** (case042). 50 case files on disk.
- Tests: **988 passed**. No live model run after v0.7.7.
- Taxonomy: 4 gold labels — `solid`, `overclaim`, `mechanism_vs_evidence`,
  `correlation_vs_causation` (single label per case).

## What has been built [FACT]
- Hardened structured-output parser (shared by agent + judge) that never crashes on malformed/
  truncated/fenced JSON.
- Normalized provider contract (`ModelResponse`: finish_reason, usage, latency, error_type).
- Curated case library expanded 29 → 50 (mostly synthetic fixtures, no fabricated citations).
- A multi-run stability harness (`run_library`) with a deterministic offline fake provider.
- A real **case-retirement mechanism**: retired cases are excluded from default active discovery
  but kept and reachable for audit.
- A Phase-5A single-model diagnostic bundle and an intake policy (`docs/case_intake_policy.md`).

## What was validated [FACT]
- Engine behavior: 988 unit/integration tests (fixtures/fakes; no live keys).
- One live single-model baseline (Opus 4.5, 50×3 = 150 runs): 150/150 successful, 0 parse/
  truncation/provider errors, **96% accuracy**, 0 unstable cases.
- [INTERPRETATION] This establishes internal consistency and a **single strong model ceiling** — it
  does **not** establish discrimination power or benchmark validity.

## Problems found (and how handled) [FACT]
- **case040** (uncontrolled pre/post vocational-training claim): mislabeled generic overclaim →
  **flipped to correlation_vs_causation** on taxonomy grounds (the specific causal-inference gap);
  overclaim kept as alternative.
- **case041** (GLP-1 / aleniglipron weight-loss pill, showcase-derived): audited for demo-origin
  contamination; **kept active Core** because the claim is isolated and the source voice
  (company/analysts, promotional) is unambiguous; annotated `curated_showcase` / intake passed;
  prompt unchanged.
- **case042** (Edge-AI readiness, showcase-derived): **retired from active metrics** because the
  target claim is embedded in an analytical paper that critiques it (ambiguous source voice,
  non-isolated claim) — a task-design confound. Not deleted, not label-flipped.
- Four synthetic mechanism fixtures (043/044/045/048) had been written with selling language and
  were relabeled/reworded so the mechanism-vs-overclaim boundary is clean.

## What remains unresolved — case054 [OPEN]
Current gold `overclaim`; a strong model stably reads `mechanism_vs_evidence`. Both are defensible:
decorative-hedge equivalence selling (overclaim) vs an in-vitro→clinical tier gap (mechanism). This
is a **taxonomy-precedence** question, not a clear error. We have deliberately **not** auto-flipped
it. A general rule (specific evidence-gap label vs generic overclaim) is undecided.

## Current risks [INTERPRETATION]
1. Single-model ceiling (no discrimination measurement yet).
2. Co-evolution risk if gold labels track one model (mitigated by taxonomy-first rule; no holdout
   set yet).
3. Single-label taxonomy can't represent dual failure modes; no precedence rule.
4. Latent demo-origin/task-design issues may exist in un-audited active cases.
5. Confidence is uncalibrated self-report.
6. Analysis generators are out-of-repo (reproducibility gap).

## Concrete questions for Fable 5
See `audit_questions_for_fable.md` (15 questions). The three we most want challenged:
- Is retiring (not deleting/flipping) case042 the right call?
- How should case054 be adjudicated, and should specific labels outrank generic overclaim?
- Where are we overfitting to one strong model, and what would you prioritize next?

## Reviewer package [FACT]
`analysis/phase4_9_retrospective/` (this dossier) + `analysis/phase5a/...` (historical metrics) +
`docs/case_intake_policy.md` + the four cited case YAMLs + `run_library.py`/`schemas.py`.
