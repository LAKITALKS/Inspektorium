# ASA 25/261 — PREMIUM GROUNDING · AGENT ARENA RUN 001 — MAIN ADJUDICATION

**Case:** ASA_25_261_PREMIUM_GROUNDING · **Run:** run_001 · **Date:** 2026-08-23
**Input freeze SHA-256:** `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069`
**Model:** claude-opus-5 · **Research:** CLOSED · **Evidence cut-off:** 2026-08-22


## 1. What this run is

The first production-style Agent Arena adjudication of the frozen INSPEKTORIUM
scientific evidence substrate for ASA Decision 25/261 (Premium Grounding,
website advertisement). Scientific research is **CLOSED**: no new literature
discovery was performed, no database was searched, and the evidence eligibility
cut-off remains 2026-08-22.

The ASA regulatory outcome is **quarantined**. It establishes case identity and
procedural history only. It is not used as a gold label, a convergence target,
or an input to any scientific inference. No proposition cites it as evidence.
No desired verdict was encoded.

This run adjudicates the frozen wording only. It produces **no** replacement
advertising language, compliant wording, marketing recommendation, legal advice
or regulator recommendation — those occur downstream after verdict freeze.

## 2. Input integrity

| File | Role | SHA-256 | Bytes |
|---|---|---|---|
| `input/01_FINAL_EVIDENCE_FREEZE_v1.md` | CANONICAL SCIENTIFIC SUBSTRATE | `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069` | 119130 |
| `provenance/01_CLOSED_CASE_SCIENTIFIC_EVIDENCE_PACKAGE_v1.md` | PROVENANCE (audit trail only) | `193877cacc4a3f3393b86b639a965a9446a3ba467b00c8baa632c024720c97d4` | 109112 |
| `provenance/02_TARGETED_EVIDENCE_CLOSURE_v1.md` | PROVENANCE (audit trail only) | `7ae78f2b84cdca24fe8c327173672706fcf9a0e6ed01c88f6291bb42a151474b` | 34052 |
| `provenance/03_PRE_FREEZE_TERMINOLOGY_ROBUSTNESS_CHECK_v1.md` | PROVENANCE (audit trail only) | `4d8df9fb9c145cba278e5a63ccf74074e3e5de3656faf56daff8b612ddc0fed2` | 18068 |

Canonical Final Evidence Freeze integrity: **PASS** — observed SHA-256 equals
the expected `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069` at exactly 119130 bytes.
The freeze was never edited; it is installed read-only.

## 3. Verdict vocabulary

Agent Arena carries two frozen vocabularies, and both are used unchanged.

**Frozen claim taxonomy** (`forensic_report`, schema 6.3.0) —
`solid`, `overclaim`, `correlation_vs_causation`, `mechanism_vs_evidence`,
or `null` for a non-adjudicable input. Label selection follows the repository's
frozen precedence rule: a specific label outranks the generic `overclaim` only
where its definitional trigger is genuinely present, and the surrogate-to-
clinical gap is routed to `overclaim` by the taxonomy itself.

**Frozen strength lattice** (`schemas.SUMMARY_STRENGTH_ORDER`, record contract
0.1.0) — `not_assessed` · `mixed` · `not_directly_established` · `limited_support` · `not_supported` · `contradicted` · `disproven`.
This is the ceiling on what any downstream summary may assert, enforced
deterministically by the release gate.

The reporting family requested for this run — SOLID / QUALIFIED / OVERCLAIM /
UNSUPPORTED / UNCERTAIN — is delivered as a **documented overlay** on top of
both, not as a replacement for either. Neither frozen contract was modified.
The overlay is an adjudicated judgement about the *exact advertised wording*;
the frozen label is a judgement about the *failure mode*; the lattice value is
the *evidential ceiling*. They are distinct dimensions and are reported
separately.

Definitions used:

- **SOLID** — supported within the evidence, with no material qualifier that
  would change what a reader takes away.
- **QUALIFIED** — supported only within documented bounds (population,
  timeframe, product, endpoint), which must be stated.
- **OVERCLAIM** — the public wording asserts materially more than the evidence
  establishes.
- **UNSUPPORTED** — no material evidence supports the claim as worded. Where
  this rests on a search, it is a bounded retrieval finding, never proof of
  nonexistence.
- **UNCERTAIN** — irreducible ambiguity prevents a determination; the specific
  uncertainty must be named.
- **OUTSIDE BIOMEDICAL EVIDENCE SCOPE** — routed out of biomedical
  adjudication; commercial substantiation required.

## 4. Verdict distribution

| Verdict | Count |
|---|---:|
| SOLID | 0 |
| QUALIFIED | 3 |
| OVERCLAIM | 10 |
| UNSUPPORTED | 11 |
| UNCERTAIN | 0 |
| OUTSIDE BIOMEDICAL EVIDENCE SCOPE (routing) | 2 |
| **Total** | **26** |

### Why zero SOLID

No proposition reaches SOLID, and this is a structural property of the
substrate rather than an artefact of scepticism. The freeze records that **no
evidence line receives DIRECT PRODUCT MATCH** and that PRODUCT EQUIVALENCE
UNCERTAIN applies to every scientific proposition. The exact 2025 product and
configuration were never identified. A product-specific claim therefore cannot
reach an unqualified verdict on this substrate, however good the underlying
science is. M-01a — directly demonstrated in humans by three independent
groups — is bounded to QUALIFIED for exactly this reason and no other.

### Why zero UNCERTAIN

UNCERTAIN was considered for every proposition and assigned to none. Each
candidate resolved to a more specific state: a bounded search finding, an
unmeasured required endpoint, a tier mismatch, a quality failure, a
non-operationalisable wording, or a routing decision. The full audit is in
`CONSISTENCY_CHECK.md`. Notably, `MIXED / CONFLICTING` was **not** collapsed
into UNCERTAIN: S-01, S-03, E-01 and R-01 carry the strength ceiling `mixed`
and were adjudicated on their wording, exactly as the source-precedence rules
require.

## 5. Verdicts

| ID | Verdict | Frozen label | Strength ceiling | Frozen preparation state |
|---|---|---|---|---|
| `M-01a` | **QUALIFIED** | `solid` | `limited_support` | SOME DIRECT EVIDENCE LOCATED |
| `M-01b` | **UNSUPPORTED** | `overclaim` | `not_directly_established` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `M-02` | **UNSUPPORTED** | `mechanism_vs_evidence` | `not_directly_established` | INDIRECT / MECHANISTIC ONLY |
| `M-03` | **UNSUPPORTED** | `mechanism_vs_evidence` | `not_directly_established` | INDIRECT / MECHANISTIC ONLY |
| `I-01` | **OVERCLAIM** | `overclaim` | `not_directly_established` | VERY LIMITED DIRECT EVIDENCE |
| `I-02` | **UNSUPPORTED** | `overclaim` | `not_supported` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `S-01` | **OVERCLAIM** | `overclaim` | `mixed` | MIXED / CONFLICTING |
| `S-02` | **OVERCLAIM** | `overclaim` | `not_directly_established` | VERY LIMITED DIRECT EVIDENCE |
| `S-03` | **OVERCLAIM** | `overclaim` | `mixed` | MIXED / CONFLICTING |
| `S-04` | **OVERCLAIM** | `overclaim` | `not_directly_established` | VERY LIMITED DIRECT EVIDENCE |
| `P-01` | **QUALIFIED** | `overclaim` | `limited_support` | SOME DIRECT EVIDENCE LOCATED |
| `P-02` | **UNSUPPORTED** | `overclaim` | `not_supported` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `P-03` | **OVERCLAIM** | `overclaim` | `not_directly_established` | VERY LIMITED DIRECT EVIDENCE |
| `P-04` | **OVERCLAIM** | `overclaim` | `not_directly_established` | VERY LIMITED DIRECT EVIDENCE |
| `P-05` | **UNSUPPORTED** | `overclaim` | `not_supported` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `V-01` | **UNSUPPORTED** | `overclaim` | `not_supported` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `E-01` | **OVERCLAIM** | `overclaim` | `mixed` | MIXED / CONFLICTING |
| `E-02` | **UNSUPPORTED** | `overclaim` | `not_supported` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `E-03` | **OVERCLAIM** | `overclaim` | `not_directly_established` | VERY LIMITED DIRECT EVIDENCE — GROUNDING COMPONENT NOT ISOLABLE |
| `C-01` | **OVERCLAIM** | `overclaim` | `not_directly_established` | VERY LIMITED DIRECT EVIDENCE |
| `R-01` | **QUALIFIED** | `overclaim` | `mixed` | MIXED / CONFLICTING |
| `W-01` | **UNSUPPORTED** | `overclaim` | `not_directly_established` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `X-01` | **UNSUPPORTED** | `overclaim` | `not_supported` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `X-02` | **UNSUPPORTED** | `overclaim` | `not_supported` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `Q-01` | **OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION REQUIRED** | `null (insufficient_input)` | `not_assessed` | NO MATERIAL DIRECT EVIDENCE LOCATED |
| `Q-02` | **OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION REQUIRED** | `null (insufficient_input)` | `not_assessed` | NO MATERIAL DIRECT EVIDENCE LOCATED |

## 6. What the adjudication turned on

**The mechanism chain breaks at the second link.** M-01a is directly
demonstrated: a conductive path changes measurable human electrical state.
M-01b — that Earth-origin electrons enter the body in the direction, quantity
and distribution the advertisement implies — was never measured. The
advertisement presents the whole chain as established. Everything downstream of
that break (M-02, M-03) inherits it, and the run records explicitly that
evidence for M-01a is never counted as evidence for M-01b.

**Almost every therapeutic claim rests on surrogates.** Inflammation,
cardiovascular health, immune function and cortisol are advertised as
therapeutic effects; the evidence is CRP, cytokines, zeta potential, viscosity,
perfusion, IFN-γ and a salivary cortisol profile. The taxonomy routes surrogate
endpoints framed as clinical outcomes to `overclaim`, and that is what happened
in each case.

**Five named conditions have no qualifying study.** Arthritis, headache,
varicose veins, brain fog and immune function survived a documented,
proposition-specific negative search that was deliberately hardened with
barefoot and Earth-contact terminology — precisely because that terminology
drift had previously hidden H33. Each is reported at `documented_search`
breadth and none is represented as proof of nonexistence.

**Where real evidence exists, it is bounded, and the bounds are stated.**
P-01 rests on a randomised sham-controlled trial in 84 patients with a
significant primary pain result; R-01 rests on an independent randomised
triple-blind recovery trial. Both are QUALIFIED, not dismissed. Both bounds —
acute postoperative and induced-soreness contexts; eccentric-exercise recovery
protocols — are recorded on the verdict.

**The best-studied outcome is genuinely mixed.** Sleep has more controlled
human trials than anything else advertised, and they disagree: a large
pointwise 12-week PSQI difference against a uniformly null day-31 prespecified
questionnaire set, with a model coefficient at p=.053, 31.8% attrition, and an
actigraphy timepoint the source cannot resolve. That conflict is preserved
unresolved.

**The bundle fails on every dimension independently.** X-01 was adjudicated by
component rather than dismissed as untestable. Benefits, conditions,
populations, timeframes and products each fail on their own component evidence.

## 7. Adversarial and Steelman layers

Both layers ran on all 26 propositions, and the Steelman layer ran
**before** any adverse verdict was frozen. 10 propositions produced
material disagreement that had to be resolved:

| Proposition | Disagreement | Resolution |
|---|---|---|
| `M-01a` | MATERIAL — Steelman argued SOLID on the generic physical reading; the adversarial layer's product-specificity objection was accepted, resolving to QUALIFIED. | **QUALIFIED** |
| `M-03` | MATERIAL — Steelman established genuine indirect marker support; the adversarial layer showed the process-specific attribution fails. Resolved by verdicting the exact wording while recording the surviving marker-level support. | **UNSUPPORTED** |
| `I-01` | MATERIAL — Steelman defended a genuine repeated biomarker signal; the adversarial layer showed none of it reaches a clinical endpoint. Resolved as OVERCLAIM with the biomarker signal explicitly preserved. | **OVERCLAIM** |
| `S-01` | MATERIAL — Steelman defended a real positive lean; the adversarial layer showed the prespecified comparisons are null. Resolved by verdicting the advertised certainty as overclaim while recording the evidence state as genuinely mixed rather than empty. | **OVERCLAIM** |
| `S-03` | MATERIAL — Steelman credited repeated positive signals; the adversarial layer showed the strongest one is not attributable and the controlled ones were null. | **OVERCLAIM** |
| `P-01` | MATERIAL AND DECISIVE — the Steelman layer established genuine bounded efficacy evidence while the adversarial layer established that the advertised framing is far broader than that evidence. Resolved as QUALIFIED: supported within documented acute bounds, not supported as advertised. | **QUALIFIED** |
| `E-01` | MATERIAL — the Steelman layer correctly discounted the null for product mismatch, but this did not rescue the claim: the remaining support is one small self-report line on an unoperationalised construct. | **OVERCLAIM** |
| `E-03` | MATERIAL — the Steelman layer established a genuine, condition-relevant and statistically strong human study; the adversarial layer established that none of its effect is attributable to grounding. Resolved as OVERCLAIM with the mandatory qualifier GROUNDING COMPONENT NOT ISOLABLE carried on the verdict, and the positive study explicitly preserved. | **OVERCLAIM** |
| `C-01` | MATERIAL — the Steelman layer identified genuine mechanistic convergence; the adversarial layer showed the clinical endpoint is entirely absent and the blood-pressure evidence is largely uncontrolled. | **OVERCLAIM** |
| `R-01` | MATERIAL AND DECISIVE — the Steelman layer established a genuine independent positive trial and correctly limited the null's reach on product-mismatch grounds; the adversarial layer established that the trials are small, multiply tested and unregistered. Resolved as QUALIFIED, with the evidence state recorded as mixed. | **QUALIFIED** |

### Report-module status note

The per-proposition claim-forensics reports carry the report module's own
unconditional banner `DEVELOPMENT PROTOTYPE — claim-forensics report
(Phase 6.3)`. That banner is a property of the frozen 6.3.0
module and was not suppressed or patched. The reports' own
`development_or_production_status` field correctly reads `production`, and
`synthetic_fixture` is `false`. The banner is recorded here so the artifacts are
not mistaken for synthetic prototype output: the *substrate and adjudication*
are production; the *report renderer* is still a prototype module.

## 8. Consistency and gate

All 15 cross-proposition consistency checks pass. The deterministic
Phase-7B representation gate ran all 5 mandatory
controls over the structured record and returned
**releasable = True** (no blocking (critical/major) QA findings).

## 9. What this run does not establish

A classification describes the relationship between a claim and the cited
evidence. It is not proof that any claim is factually false. No proposition is
recorded as contradicted or disproven. Negative states are bounded retrieval
findings within documented routes and terminology, valid to the
2026-08-22 cut-off, and they do not establish that no relevant study
exists. Reader-impact risk is a qualitative category, never a computed harm
probability.

## 10. Provenance

| Field | Value |
|---|---|
| Agent Arena version | agent-arena 0.1.0 (package metadata); internal contracts: forensic_report 6.3.0, ForensicRecord 0.1.0, release gate 0.1.0 |
| Repository branch | `feat/case-library-run-harness` |
| Repository commit | `84d75d4b3d931090500151a23c3ef939e910cde0` |
| Working tree at run start | DIRTY — untracked scratch files and datasets present before the run; no tracked file was modified by this run |
| Model | claude-opus-5 |
| Provider | anthropic |
| Reasoning / effort setting | NOT EXPOSED |
| Temperature | NOT EXPOSED |
| Seed | NOT EXPOSED |
| Context / mode | NOT EXPOSED |
| Test suite | PASS — 1484 passed (full suite, run before adjudication) |
| Code changes for this run | NONE |
