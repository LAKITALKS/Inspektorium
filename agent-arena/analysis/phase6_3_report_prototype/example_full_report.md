> **DEVELOPMENT PROTOTYPE — claim-forensics report (Phase 6.3)**
> **SYNTHETIC EXAMPLE — not real Agent Arena performance**

# Claim-forensics report — FR-SYN-MECH-04
schema `6.3.0` · status `complete` · development · synthetic=True · generated_at=2026-08-05T12:00:00+00:00

**⚠ Warnings**
- recommended rewrite is an UNVERIFIED proposal; numeric guard passed but factual/semantic support still requires human review

## Claim
> Because compound Z clears amyloid plaques in mice, it will prevent Alzheimer's disease in older adults.
- Context: SYNTHETIC illustration — not a real scientific or medical conclusion.
- Source: _not supplied_
- Scope: human therapeutic prevention
- Audience: patients and caregivers

## Verdict
**Biological or preclinical evidence is presented as human clinical benefit**  (`mechanism_vs_evidence`)

Preclinical or mechanistic evidence is used to imply a human clinical benefit the evidence tier does not reach.

- Confidence: **VALID (0.87)**
- _Model's self-assessed probability that its own primary classification is correct (Phase 6.1 semantics). Not a calibrated probability._
- _A forensic classification describes the relationship between the claim and the cited evidence. It is not, by itself, proof that the claim is factually false._

## Why this verdict
- **mechanism_to_human_benefit_leap** — Mouse amyloid clearance is presented as human Alzheimer's prevention.  (evidence: synthetic preclinical D)
- **evidence_tier_mismatch** — Evidence tier is animal; conclusion tier is human therapeutic.
- **missing_human_evidence** — No human clinical data exist for compound Z.

## Evidence assessment
- Sufficiency: **insufficient** — Preclinical animal mechanism cannot establish human clinical prevention.
- (animal · supporting) [synthetic preclinical D] In transgenic mice, compound Z reduced amyloid plaque burden. — Animal mechanism; no human clinical outcome.
- (not_applicable · missing_expected) No human trials of compound Z have been reported. — The human clinical tier is absent.

## What is missing
- Comparison group missing: unknown / not assessed
- Causal chain missing: no
- Human evidence missing: yes
- _no further missing evidence noted_

## Reader-impact risk
- Risk level: **high**
- Rationale: Patients/caregivers may expect prevention from an unproven compound.
- Likely misunderstanding: That compound Z is a proven Alzheimer's preventive for people.
- Affected decision: health/treatment expectation
- Risk uncertainty: Preclinical-to-clinical translation frequently fails.
- _Reader-impact risk is a qualitative category describing how a non-specialist might misread the claim. It is NOT a computed medical, legal, or financial harm probability._

## Uncertainty
- Are any human trials planned or underway?
- Alternative plausible label: `overclaim` — If the text actively sold clinical benefit as fact, overclaim would apply; here the framing is a tier leap.

Scope limitations:
- Single preclinical study.
- _Confidence caveat: Model's self-assessed probability that its own primary classification is correct (Phase 6.1 semantics). Not a calibrated probability._
- _Development prototype output on synthetic input — small-sample characterization, not a validated production judgement._

## Safer rewrite
_Unverified proposal — needs review._
> In mice, compound Z reduced amyloid plaques; whether this translates to preventing Alzheimer's in people is unknown and requires human trials.
- _This rewrite is an UNVERIFIED proposal copied from the analysis input. The numeric-containment guard only checks that it introduces no unsupported number; it does NOT verify factual or semantic accuracy. Its factual support still requires human review._
- Rationale: Keeps the claim at the animal evidence tier and states the human gap explicitly.

Remove / narrow:
- will prevent Alzheimer's disease in older adults

Qualifiers to add:
- in mice
- preclinical
- requires human trials

Remains supportable:
- Compound Z reduced amyloid plaques in a mouse model.

## Provenance & audit
- model / provider: SYNTHETIC-MODEL / synthetic
- prompt contract: SYNTHETIC-CONTRACT-0
- repository commit: 5349ad0
- analysis source: phase6_3 synthetic fixture
- parser status: ok
- input digest: `8b1cbb8b546c2688c33ec9b6050ed7f4d2dff93abbf8de0185adf7651c9f59b7`
- report digest: `67b8df9d1128f4cf46f57586c8af0ee4b47049393e874ce4197e8b96efb6e20d`

Audit trail:
- input validated against forensic_report schema 6.3.0
- analysis_status=complete
- confidence classified as VALID (no coercion to 0.0)
- 3 failure mode(s) echoed from analysis (not inferred)
- rewrite guard: clean (numeric-only); rewrite marked unverified_proposal

Warnings:
- recommended rewrite is an UNVERIFIED proposal; numeric guard passed but factual/semantic support still requires human review
