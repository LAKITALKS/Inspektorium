# Phase 7 — Real-World (LaVita) Pilot Postmortem (STEP 3 + STEP 4)

**Data-safety note first.** No LaVita pilot artifact exists in this repository (verified: no
match for lavita / fantacone / skerrett / gombart / mosgöller / muss across the tree, excluding
`.venv`/`.git`). The pilot enters Phase 7 **only** through the failure-mode descriptions in the
initialization brief. Therefore every regression fixture must be a **sanitized, synthetic**
reconstruction built from **public** facts (public papers, public web claims) that reproduces the
methodological failure while carrying **no** client-specific workflow material, correspondence, or
private PDFs. Outcomes must not be fabricated: a fixture encodes the *documented* failure, nothing
invented (brief §19, §27). The three pilot cases are referenced abstractly below.

## STEP 3 — Failure mode → root cause → controls → regression

The brief documents **5 failure modes** and **8 regression behaviors**. Mapped:

### FM1 — Provenance drift
- **Observed:** a later representation stated a source was *absent* from a citation list that a
  live check showed *present*; different page/source states were mixed.
- **Root cause:** claim provenance was reconstructed freely from downstream model context instead
  of being frozen at capture; no separation of *archived snapshot* vs *current live* state.
- **Existing control:** run/model provenance + `content_fingerprint` machinery
  (`forensic_report`); leakage scan. **Not** web-claim provenance.
- **Missing control:** immutable `claim.provenance` with `provenance_state`
  (archived_snapshot / current_live); never silently overwrite historical state with live state.
- **Preventive control:** freeze provenance at capture; downstream objects reference the frozen id.
- **Regression:** **R1 (Provenance)** — a current LaVita source state must retain the
  Skerrett/Willett association; a mismatch of *live vs snapshot* must be surfaced, not silently
  resolved. Maps to `system_qa` code `provenance_drift` (BLOCKER when the client artifact asserts
  presence/absence contradicting the frozen provenance state).

### FM2 — Search-scope generalization
- **Observed:** "no head-to-head study was identified **in the reviewed sources**" → "no such
  study **exists**."
- **Root cause:** absence-of-evidence in a bounded search was promoted to evidence-of-absence in
  the world; no machine-readable search scope.
- **Existing control:** none (`search_scope` genuinely absent).
- **Missing control:** `evidence.search_scope` + a linguistic gate: negative existence claims
  require an explicit level.
- **Preventive control:** the four-level lattice — A: cited source lacks X · B: not identified in
  reviewed sources · C: not identified in documented search across A/B/C · D: does not exist.
  **Level D forbidden by default** unless genuine evidence-of-absence / sufficient methodology.
- **Regression:** **R2 (Search language)** — given no head-to-head study in a defined scope,
  "not identified in the reviewed sources" passes; "no such study exists" is blocked. Maps to
  `search_scope_generalization`.

### FM3 — Compression overclaim
- **Observed:** "not directly demonstrated in the reviewed evidence" → "not supported";
  "partially supported under this definition" → "unsupported."
- **Root cause:** summarization is a claim transformation but was unconstrained; strength drifted
  upward during compression.
- **Existing control:** `_rewrite_guard` (numeric containment only); exec summary preserves
  *material uncertainty*; renderer renders only from the report object. All **partial**.
- **Missing control:** a `summary_strength` lattice + a **semantic monotonicity** rule:
  a client summary may never be stronger than its internally validated parent finding.
- **Preventive control:** `allowed_summary_strength` on the finding; validator: client ≤ parent.
- **Regression:** **R5 (Summary strength)** — internal "not directly established" allows equal or
  weaker client wording; "disproven/does not exist/unproven" is blocked without an internal basis.
  Maps to `compression_overclaim` (absorbs summary_strength_escalation — see STEP 4).

### FM4 — Artifact source-binding drift
- **Observed:** during artifact assembly, claim / nearby text / source references were mismatched
  even when the underlying analysis was directionally correct.
- **Root cause:** the client artifact is assembled without a final check that visible claims stay
  bound to their exact parent finding/source objects.
- **Existing control:** single-source-of-truth builder; `evidence_refs` (but not resolve-checked).
- **Missing control:** stable `evidence_id`; a `client_finding` bound to a parent `finding_id`;
  a final binding check (exact quote / correct source / correct DOI-PMID / traces to a finding id).
- **Preventive control:** `artifact_binding_check` gate over the finished artifact.
- **Regression:** **R4 (Claim binding)** — different table vs prose claims get distinct
  claim/finding ids; evidence from one claim may not be silently used for another. Maps to
  `artifact_source_binding_drift` (absorbs renderer_generated_claim & model_output_to_literature).

### FM5 — Asymmetrical evidence selection
- **Observed:** a source with both favorable and unfavorable/null findings can be reported so that
  only the evidence strengthening *our* criticism survives.
- **Root cause:** asymmetric skepticism — our criticism was not held to the same evidence rules as
  the company claim.
- **Existing control:** `EvidenceRole` + `contradicting_or_limiting` (data model only); no symmetry
  enforcement; anti-co-evolution rule (`taxonomy_precedence.md`) is philosophically aligned.
- **Missing control:** `evidence.source_symmetry` omission pass; a symmetry check.
- **Preventive control:** if a source contributes evidence in one direction, materially relevant
  opposite-direction findings from the **same source** must remain visible.
- **Regression:** **R3 (Fantacone symmetry)** — an RCT with both null measured immune-function
  findings and favorable self-reported illness-duration findings must keep **both** directions.
  Maps to `asymmetric_evidence_selection`.

### Remaining regressions (R6–R8) mapped to the same controls
- **R6 (Product bridge):** a bioavailability study without a direct immune/superiority comparator
  must not yield a product-superiority conclusion → guarded by search_scope (no comparator in
  scope) + monotonicity (conclusion may not exceed finding) + the existing claim-level
  `unsupported_superiority_claim` / `mechanism_to_human_benefit_leap` modes.
- **R7 (Modelled value):** an internally modelled estimate must stay marked as modelling and never
  reappear as a published literature value → `provenance_state ∈ {modelled}` vs
  `{published_literature}`; binding check BLOCKER on state confusion. (LaVita Case 02, ~75-day cell
  renewal; Sender/Milo public cell-number estimates.)
- **R8 ("All values" compression):** results with exceptions/mixed outcomes may not compress into a
  universal "all values" claim → `compression_overclaim` + `source_symmetry` (exceptions are a
  material category). (LaVita Case 01, bioavailability vs Muss/Mosgöller/Endler 2015.)

## STEP 4 — Taxonomy boundary (two separate taxonomies)

**A. Claim-level forensic taxonomy (FROZEN, unchanged):** `solid`, `overclaim`,
`correlation_vs_causation`, `mechanism_vs_evidence`. No renames, no additions.
`mechanism_vs_evidence` stays biologically scoped (preclinical/mechanistic → implied human
clinical benefit); surrogate/in-vitro gaps route to `overclaim` (`taxonomy_precedence.md`).

**B. System/pipeline QA taxonomy (NEW, separate):** describes failures of the *pipeline and its
artifacts*, never of the claim. It lives in a `system_qa` block and must never contaminate the four
labels. The brief lists eight candidate codes; **deduplicate first** — several collapse:

| brief candidate code | disposition | final code |
|---|---|---|
| provenance_drift | keep | **provenance_drift** |
| search_scope_to_world_generalization | keep (rename shorter) | **search_scope_generalization** |
| compression_overclaim | keep | **compression_overclaim** |
| summary_strength_escalation | merge → compression_overclaim (a strength escalation *is* a compression overclaim) | — |
| artifact_source_binding_drift | keep | **artifact_source_binding_drift** |
| renderer_generated_claim | merge → artifact_source_binding_drift (a new claim from rendering is a binding failure) | — |
| model_output_to_literature_fact | merge → provenance_drift **or** artifact_source_binding_drift (a modelled value presented as literature is a provenance-state binding failure) → route to provenance_drift via `provenance_state` | — |
| asymmetric_evidence_selection | keep | **asymmetric_evidence_selection** |

**Minimal deduped set (5):** `provenance_drift`, `search_scope_generalization`,
`compression_overclaim`, `artifact_source_binding_drift`, `asymmetric_evidence_selection`.
Each carries a severity (BLOCKER/MAJOR/MINOR — semantics frozen against repo convention in 7B.6,
not here). This is a QA vocabulary, **not** a fifth claim label and **not** an addition to the 11
claim-level `failure_modes`.

## Product-philosophy anchor (brief §23)

Agent Arena must test *both* "is the company claim too strong?" and "is our criticism too
strong?" The evaluator must not enjoy an asymmetric burden of proof. R3 (symmetry) and the
`self_audit` block (steelman / prosecution / critic-overreach / counterevidence) operationalize
this. A critical finding is not stronger merely because it is skeptical.
