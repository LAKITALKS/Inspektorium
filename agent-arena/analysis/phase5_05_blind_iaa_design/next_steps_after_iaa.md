# Next Steps After IAA — Decision Rules

*Pre-committed decision rules so the outcome drives action, not the other way
around. All thresholds are on **primary-label Cohen's κ** over the 20-case sample,
read together with per-label agreement and the disagreement matrix (never κ alone).*

## Decision bands

### STRONG — κ ≥ 0.80 (and no serious structural flags)
- **Proceed** to **Holdout Freeze** planning, then the **Phase 5.1 small model
  panel probe**.
- Record the IAA result as the gold-credibility baseline.
- Any soft disagreements (blind lands on documented alternative, e.g. case054) are
  logged as expected borderline behavior — **no relabels**.

### MODERATE — κ 0.60–0.79
- **Do not scale yet.** First **review the taxonomy definitions and the specific
  ambiguous cases** driving disagreement (likely the borderline / boundary set).
- Clarify definitions / precedence wording where the disagreement is definitional
  (update `taxonomy_precedence.md` / `study_forensics_taxonomy.md`) — **without
  changing any case label**.
- Then proceed to Holdout Freeze + Phase 5.1, noting the caveat.

### WEAK — κ < 0.60
- **Stop scaling.** Do not run the model panel, do not freeze a holdout on these
  labels.
- Revise taxonomy / consider Schema v2 (secondary-label support), re-examine the
  weakest categories (thin specific classes), and **repeat IAA** on a refreshed
  sample.
- Treat the current gold as provisional until agreement improves.

## Rules that apply regardless of κ
- **Document every disagreement** in the curator-review queue with dispositions;
  keep the full audit trail.
- **Never silently relabel** to match the second annotator. A label revision
  requires an independent taxonomy justification and a logged before/after (the
  case040 precedent), with annotator/model agreement only as corroboration.
- **Structural flags** (`source_voice_clear = no` / `claim_isolated = no`) route to
  intake review independent of κ; handle via the intake policy (rewrite under a new
  case_id or retire), never a silent edit.
- **Historical Phase-5A reports stay frozen**; IAA outputs are a new artifact.
- Keep the phase ladder: **IAA → Holdout Freeze → Phase 5.1 panel → (later)
  paraphrase robustness / real-world intake**. No public benchmark or
  customer-facing accuracy claims at this stage under any κ.

## Readiness note
A STRONG or MODERATE result makes the project **ready for Holdout Freeze planning**
(freeze before the panel so the panel never touches held-out cases). A WEAK result
defers holdout freeze until labels are revised and IAA repeats.

---

## Phase 5.05c metric plan — multi-annotator (model-assisted proxy IAA)

*Appended 2026-07-10 (v0.8.2). This document's decision bands above are unchanged; this
section only specifies the agreement statistics to compute once the three anonymized
annotator response sheets (A/B/C) are returned. No responses have been imported yet.*

### Nature of the study — IMPORTANT framing
This is a **strongly anonymized, model-assisted PROXY inter-annotator study** (annotators
A: GLM-5.2, B: Fable 5, C: another strong model). **It is NOT a human IAA** and must never
be described as one. It measures whether the gold labels are reproducible by independent
*model* annotators; a human independent annotator would be required before any "human IAA"
claim. The original gold curator has also seen model outputs (see `iaa_risk_notes.md`).

### Statistics to compute (over the 20 scored `BIAA-###` items; case042/TRAIN-042 excluded)
- **Pairwise Cohen's κ** — A↔B, A↔C, B↔C on the primary label.
- **Pairwise agreement against gold** — each annotator vs the (hidden) gold primary label.
- **One multi-rater statistic** — prefer **Krippendorff's α (nominal)** for 3 raters over
  nominal labels; use **Fleiss' κ** if the simpler implementation path is preferred. Report
  which was used and why.
- **Raw agreement** — overall and split by clear (11) vs borderline (9) strata.
- **Per-label agreement** — per the four labels, with explicit small-N caveats (thin
  mechanism/correlation classes).
- **Disagreement matrix** — rater×rater and rater×gold confusion over the 20 items.
- **Soft vs serious disagreement** — soft = lands on a case's documented alternative reading
  (e.g. the case054 item); serious = a genuinely different failure mode. Per
  `adjudication_and_kappa_plan.md`.
- **Confidence & ambiguity analyses** — distribution of each annotator's `confidence`,
  `ambiguity_notes` frequency, and the `source_voice_clear` / `claim_isolated` structural flags.

### Handling
Report all statistics as a **new** artifact; never recompute or overwrite the frozen
Phase-5A metrics. Route disagreements to the documented curator-review queue; **no silent
relabels** (independent taxonomy justification required, as in the case040 precedent).

### Analyzer status (v0.8.3+) [FACT]
- **Analyzer prepared:** `src/agent_arena/iaa_analysis.py` + CLI `agent-arena iaa`
  (+ `tests/test_iaa_analysis.py`). Deterministic, offline, stdlib-only; reuses the
  taxonomy label set from `disagreement_lab` (no duplicate module).
- **Multi-rater statistic:** **Fleiss' kappa** (fixed 3-rater, complete-data design;
  no new dependency). Krippendorff's alpha is the documented alternative if
  missing/variable-rater data later appears.
- **Responses NOT yet collected.** The three response sheets are still blank templates;
  the analyzer recognizes them as templates and **refuses** to compute final agreement
  from blank data (a structure-validation-only mode exists, clearly labelled).
- **No IAA result exists yet.** Phase 5.05c remains **incomplete** until real A/B/C
  responses are imported.
- **Next human action:** distribute `annotator_facing/` separately to annotators A/B/C,
  collect the three completed sheets, then run `agent-arena iaa` to produce a new
  `analysis/phase5_05c_iaa_results/<run_id>/` artifact.
- This remains a **model-assisted proxy IAA**, not human IAA.
