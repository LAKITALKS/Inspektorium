# Phase 7A — Boundary Pool FINAL Curator Resolution

Narrow, pre-model resolution of the three remaining curator questions before human final gold
approval: (A) P7A-BND-006 claim provenance, (B) P7A-BND-001 B1 tension, (C) P7A-BND-017 B1 tension.
No evaluation-model calls (0). Public web/source verification only. Gold remains pre-model, authored
by the Claude repo agent; role-separated LLM audits performed; human curator directed this
resolution; no human IAA. This document does not recreate the prior audit / review documents.

Starting HEAD `e026f58` (parent audit `f6a1d20`; WP-1 freeze `c4fc06b`); verified clean tracked tree,
14 active / 3 retired, fingerprints reproduce, no evaluation results.

---

## A. P7A-BND-006 — claim-provenance resolution

**Real identifiable PUBLIC-FACING claim found? NO.**

FIRST TRY (§6) searched the fluoride/osteoporosis episode for a real public-facing claim asserting
"fluoride raises bone density → strengthens bone / prevents fractures". What exists is a **scientific**
claim only:

- Pak et al. 1989 journal title "Safe and effective treatment of osteoporosis with intermittent slow
  release sodium fluoride: **augmentation of vertebral bone mass and inhibition of fractures**"
  (PubMed 2909549), plus slow-release-NaF patents and review articles.

These are **internal scientific hypotheses / publications**, not bounded, verifiable, public-facing
marketing, advertisement, brochure, product page, or news claims (§7B fails). Sodium fluoride was
never FDA-approved for osteoporosis, so there is no consumer-advertising corpus; a water-fluoridation
"prevents osteoporosis" public claim exists but rests on **low-dose epidemiology**, not the Riggs
75 mg/day treatment RCT, so binding it to Riggs 1990 would violate §7E (evidence must adjudicate the
same proposition) and §8 (no retrofitting).

**Decision (§8): RETIRE P7A-BND-006** (reason: *insufficient real public-claim provenance under the
final curator standard*) and **create ONE replacement B2 case, P7A-BND-018**, that preserves the same
Shape-B surrogate→clinical forensic object with a **real, identifiable, ubiquitous public claim** and
strong RCT/guideline evidence. No archetype exception created; no historical ad invented.

Retirement recorded: `status: retired` + `excluded_from_active_metrics: true` + `superseded_by:
P7A-BND-018` + `suite_history` (prior fingerprint `78de8c94…`); excluded from active metrics.

---

## D. Replacement — P7A-BND-018 (B2, gold overclaim, alt mechanism_vs_evidence)

**Public claim (real, bounded):** "Calcium and vitamin D are the building blocks of bone … take a
daily calcium plus vitamin D supplement to build strong bones and protect yourself from the fractures
of osteoporosis. Everyone over 50 should be taking them."
- **Claim source:** Bone Health & Osteoporosis Foundation (formerly NOF), *Get the Facts on Calcium
  and Vitamin D* (`bonehealthandosteoporosis.org/…/get-the-facts-on-calcium-and-vitamin-d/`), echoed
  by calcium+D supplement marketing (Caltrate/Citracal) and NIAMS bone-health messaging.
  `claim_source_role: public_claim_source`. **Real, public-facing, verifiable.**
- **Evidence (separate):** Zhao et al. 2017 *JAMA* meta-analysis, 33 RCTs / 51,145 community-dwelling
  adults — calcium/vitamin-D supplements **not** associated with lower fracture incidence
  (`systematic_review`); USPSTF 2018 recommends **against** low-dose supplementation for primary
  fracture prevention (`regulatory_assessment`).
- **Why B2 / genuine mechanism tension:** the calcium/vitamin-D bone mechanism ("building blocks of
  bone", vitamin-D-dependent absorption) is real, textbook, and the explicit rhetorical basis — so
  `mechanism_vs_evidence` is a strong, genuinely plausible competing label.
- **Why overclaim wins (frozen precedence):** direct human clinical-outcome trials (fractures) exist
  and do not support the supplement claim → the decisive gap is surrogate/mechanism-to-clinical
  against human data → Shape-B routes to overclaim (case054 precedent). The scoped "solid" reading is
  defeated because the frozen claim is unscoped ("everyone over 50").
- Preserves 006's exact BMD→fracture forensic object; distinct from 015 (oncology/PFS) and 016
  (ginkgo/blood-flow). `supersedes: P7A-BND-006`. Fingerprint `fa2221a0…`.

---

## B. P7A-BND-001 — B1 Steelman & quality

Claim: processed meat is "as dangerous as smoking … no safe amount" after IARC Group 1. Gold overclaim.

**Strongest good-faith `correlation_vs_causation` argument:**
1. *Wording creating causal inference:* the claim asserts processed meat **causes** cancer at a
   smoking-equivalent danger — a direct causal-attribution claim.
2. *Evidence design / causal status:* IARC Group 1 rests substantially on **observational** dietary
   cohort/case-control epidemiology (plus mechanistic data); dietary–cancer confounding (overall
   diet/lifestyle) is real.
3. *Specific-label trigger a careful evaluator would see:* "a causal claim drawn from confounded
   observational epidemiology" → correlation_vs_causation; moreover IARC's causal certainty for a
   **modest** observational association is itself genuinely debated by epidemiologists (residual
   confounding) — so the argument is **more than the reflex "it's observational"**; it engages a real
   scientific debate about this specific determination.
4. *Why it is nevertheless not the central failure:* the frozen taxonomy treats an IARC Group 1
   classification as **establishing causation** (sufficient evidence, integrating epidemiology +
   mechanism), so the causal-inference trigger does not fire.
5. *Actual central failure:* conflating the hazard **CATEGORY** (strength of evidence) with the
   **MAGNITUDE** of risk ("as dangerous as smoking / no safe amount") — magnitude/hazard-vs-risk
   overclaim (18% relative per 50 g/day; ~34k vs ~1M deaths/yr).
6. *If correlation were removed from the taxonomy, still defective? YES* — even fully granting
   causation, the smoking-magnitude equivalence and "no safe amount" are false. overclaim is robust.

**Final B1 quality: ADEQUATE.** The claim is directly causal-attributive, so correlation genuinely
targets its central assertion (not merely the evidence type); it loses under frozen precedence
(IARC = causation established) while the magnitude defect survives. **Remains active: YES.**

---

## C. P7A-BND-017 — B1 Steelman & quality

Claim: "breathing Delhi's air is like smoking 44 cigarettes a day … as deadly as a pack-a-day habit"
(Berkeley Earth cigarette-equivalence). Gold overclaim.

**Strongest good-faith `correlation_vs_causation` argument:**
1. *What is causal:* the claim asserts air pollution is lethal at a smoking-equivalent level ("as
   deadly as").
2. *Is the cigarettes/day equivalence a causal translation? YES* — it converts a **causal**
   PM2.5→premature-death dose-response into cigarette-equivalents.
3. *Evidence for the equivalence:* the PM2.5–mortality function is derived **entirely** from
   observational cohort studies (ACS CPS-II, Harvard Six Cities); no RCTs are possible, and the causal
   magnitude of low-level PM2.5 mortality effects is a genuinely contested topic — so the specific
   number the claim uses rests on a contested causal inference from observational data (again, more
   than a bare "it's observational" reflex).
4. *Defect type:* primarily **risk-metric misapplication + magnitude** — a long-term, population-
   average premature-death-RISK conversion presented as a literal per-day, total-harm equivalence with
   a pack-a-day smoking habit; secondarily the causal magnitude is observationally derived.
5. *Why a competent evaluator might choose correlation:* the entire quantitative mortality basis is
   observational/confounded, so "the claim over-attributes a precise causal mortality effect" is a
   real reading.
6. *Why it loses under precedence:* IARC classified outdoor air pollution & PM as **Group 1**
   carcinogens (2013), with mechanistic + quasi-experimental support (mortality falls when pollution
   falls) → causation established → the causal trigger does not fire.
7. *If correlation removed, still defective? YES* — even granting causation, the per-day/total-harm
   smoking equivalence is a false magnitude/risk-metric transfer.

**Final B1 quality: ADEQUATE (borderline, honestly disclosed).** The correlation reading engages the
contested observational causal magnitude that the "44 cigarettes" number depends on (above the
reflex bar), and is defeated under frozen precedence while a **surviving, clearly non-causal**
metric-transfer defect keeps overclaim robustly primary. **Remains active: YES.**

**Note on 001/017 independence:** both use an established-causation (IARC Group 1) + smoking-comparison
architecture, but they are distinct propositions — different agent (dietary carcinogen vs ambient
PM2.5), different evidence bodies (IARC meat monograph vs IARC air-pollution monograph + Berkeley
Earth conversion), and different specific forensic errors (hazard-CATEGORY-vs-magnitude for 001 vs
long-term-RISK-metric-transfer for 017). This shared-template / distinct-proposition pattern is
accepted under the same standard the audit applied to 004/005. Flagged for human-curator awareness.

---

## E. Final ACTIVE 14-case matrix

Fingerprints = first 16 hex (full SHA-256 in each YAML + `boundary_manifest.yaml`).

| ID | family | gold | alternative | diff | fp16 |
|---|---|---|---|---|---|
| P7A-BND-001 | B1 | overclaim | correlation_vs_causation | D3 | 8183b3bb03f42f5e |
| P7A-BND-002 | B1 | overclaim | correlation_vs_causation | D2 | fd7e595d106cbef1 |
| P7A-BND-004 | B1 | correlation_vs_causation | overclaim | D2 | bf57c20cedfa8596 |
| P7A-BND-005 | B1 | correlation_vs_causation | overclaim | D2 | 61d2b0cf4104c02f |
| P7A-BND-017 | B1 | overclaim | correlation_vs_causation | D3 | 0495f2c997c8e8de |
| P7A-BND-009 | B2 | mechanism_vs_evidence | overclaim | D2 | 19a710bc2cf484bb |
| P7A-BND-010 | B2 | mechanism_vs_evidence | overclaim | D3 | 3044e41de4be53a5 |
| P7A-BND-015 | B2 | overclaim | mechanism_vs_evidence | D3 | fe0e35d20a8835dd |
| P7A-BND-016 | B2 | overclaim | mechanism_vs_evidence | D2 | 771ce00f4d13cd6f |
| P7A-BND-018 | B2 | overclaim | mechanism_vs_evidence | D3 | fa2221a0080b6d19 |
| P7A-BND-011 | B3 | solid | overclaim | D2 | 436c6452a8311085 |
| P7A-BND-012 | B3 | solid | overclaim | D3 | d2deda46bacfd849 |
| P7A-BND-013 | B3 | overclaim | solid | D3 | afbda45c8bd726de |
| P7A-BND-014 | B3 | overclaim | solid | D2 | 8c1a1d930880c6b7 |

**Retired (excluded from active metrics):** P7A-BND-003 → 017, P7A-BND-006 → 018, P7A-BND-007 → 015,
P7A-BND-008 → 016.

---

## F. Final counts

- Family: **B1 5 · B2 5 · B3 4** ✓
- Gold: **overclaim 8 · correlation_vs_causation 2 · mechanism_vs_evidence 2 · solid 2** ✓
- Difficulty (active): D2 7 · D3 7 (not a frozen constraint).

---

## G. Fingerprint changes (this slice)

| ID | change | new fp16 |
|---|---|---|
| P7A-BND-006 | active → retired (content changed) | 20583bc34629b0e3 |
| P7A-BND-018 | new active replacement | fa2221a0080b6d19 |

All other 13 active fingerprints are unchanged from the `e026f58` repair. All active + retired
fingerprints reproduce and are globally unique (`verify_pool`).

---

## H. Final recommendation

- 006: replaced (no real public-facing claim) → **P7A-BND-018** with real public claim. ✓
- 001: B1 tension **ADEQUATE** → remains active. ✓
- 017: B1 tension **ADEQUATE** (borderline, disclosed) → remains active. ✓
- All 14 active cases: real identifiable public-claim provenance (no archetype-only claim). ✓
- All 5 active B1: genuine correlation_vs_causation tension. ✓
- All 5 active B2: genuine mechanism_vs_evidence tension (real mechanistic evidence materially
  invoked). ✓
- Counts exact (5/5/4; 8/2/2/2); fingerprints re-frozen; structural + full suite green; 0
  evaluation-model calls.

**REVIEWED BOUNDARY POOL READY FOR HUMAN CURATOR FINAL GOLD APPROVAL.**
