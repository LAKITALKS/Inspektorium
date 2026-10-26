# Phase 7A — Boundary Pool Curator Review v2 (post-audit REPAIR re-freeze)

Compact review surface for the **repaired** Phase-7A Boundary Pool: **14 ACTIVE re-frozen cases +
3 RETIRED historical cases**. Generated after the role-separated curator audit
(`boundary_curator_gold_audit.md`) and the human-curator-authorized repair, **before any Haiku/
Sonnet/Opus evaluation run**. This file does **not** overwrite the original authoring review
(`boundary_curator_review.md`) or the audit.

## Governance language (accurate)

- Gold was **authored pre-model by the Claude repo agent (an LLM)** and frozen before any evaluation
  run. **No separate evaluation model or external LLM judge determined gold.**
- A **role-separated Claude curator audit** challenged the frozen pool and is preserved as a distinct
  commit (`docs: record phase 7A boundary gold audit`).
- The **human curator authorized this repair.** This is **not** human authorship, human validation,
  or human inter-annotator agreement. No case has been described as `human-authored`,
  `human-validated`, or `human IAA`.
- Evaluation models have **not** seen these cases before this re-freeze (0 evaluation-model calls).

## Resolved claim-provenance standard (curator decision)

**REAL, IDENTIFIABLE PUBLIC-CLAIM PROVENANCE IS REQUIRED** for every active Boundary case:
`claim_source_url` (real) + a bounded exact public claim (`claim_exact_span`) + `claim_source_role`
+ `claim_source_type` + `claim_source_publisher`/`claim_source_date`/`claim_context`, with the
scientific **evidence** basis kept separate and each evidence item carrying a declared `source_role`.
`REPRESENTATIVE CLAIM TYPE ≠ FROZEN PUBLIC CLAIM`; `SCIENTIFIC EVIDENCE PROVENANCE ≠ PUBLIC CLAIM
PROVENANCE`. Source **role** (function) is separated from source **quality**; controlled vocabulary:
`public_claim_source | primary_research | systematic_review | regulatory_assessment |
trial_registration | secondary_discovery | other`.

Structural completeness is enforced by `robustness_pool.claim_provenance_status` +
`tests/test_phase7a_boundary_pool.py`. Scientific source **fidelity** remains curator-reviewed.

---

## 1. Active 14-case matrix

Fingerprints are the first 16 hex chars (full SHA-256 in each YAML and `boundary_manifest.yaml`).

### B1 — overclaim ↔ correlation_vs_causation (5)

| ID | gold | alt | diff | real public claim (bounded) | claim source (role) | evidence (role) | boundary rationale | fp16 |
|---|---|---|---|---|---|---|---|---|
| 001 | overclaim | correlation | D3 | "processed meat … as dangerous as smoking … no safe amount" | 2015 media misreading of IARC Group 1, documented by Cancer Council Australia (public_claim_source) | IARC/WHO Q&A (regulatory_assessment) | causation established (IARC Group 1) → correlation loses; defect = hazard-category-vs-risk-magnitude | 8183b3bb03f42f5e |
| 002 | overclaim | correlation | D2 | "you must walk 10,000 steps every day … anything less is not enough" | ubiquitous wellness mandate (manpo-kei origin), documented by McGill OSS (public_claim_source) | Paluch 2022 Lancet PH (systematic_review); manpo-kei origin (secondary_discovery) | fabricated 10k threshold + certainty is the checkable defect; correlation a real but secondary attractor | fd7e595d106cbef1 |
| 004 | correlation | overclaim | D2 | "a daily glass of wine protects your heart … if you don't drink, consider starting" | J-curve lifestyle claim, documented/cautioned by AHA + Mayo (public_claim_source) | Zhao 2023 JAMA Netw Open (systematic_review) | causal+prescriptive claim from confounded observational w/ corrupted reference group → correlation primary | bf57c20cedfa8596 |
| 005 | correlation | overclaim | D2 | "owning a dog reduces your risk of death by 24% — so … get a dog" | AHA News 2019 + widespread "get a dog to live longer" (public_claim_source) | Kramer 2019 Circ CQO (systematic_review) | causal/prescriptive from non-randomized data (authors' own caveat) → correlation primary | 61d2b0cf4104c02f |
| 017 | overclaim | correlation | D3 | "breathing Delhi's air is like smoking 44 cigarettes a day … as deadly as a pack-a-day habit" | Berkeley Earth cigarette-equivalence, widely reported (public_claim_source) | IARC air-pollution Group 1 (regulatory_assessment); Berkeley Earth conversion (secondary_discovery) | causation established (IARC Group 1) → correlation loses; defect = misapplying a long-term risk metric to per-day/total-harm | 0495f2c997c8e8de |

### B2 — overclaim ↔ mechanism_vs_evidence (5)

| ID | gold | alt | diff | real public claim (bounded) | claim source (role) | evidence (role) | boundary rationale | fp16 |
|---|---|---|---|---|---|---|---|---|
| 018 | overclaim | mechanism | D3 | "take a daily calcium + vitamin D supplement to build strong bones and protect yourself from fractures … everyone over 50" | Bone Health & Osteoporosis Foundation + supplement marketing (public_claim_source) | Zhao 2017 JAMA meta-analysis (systematic_review); USPSTF 2018 (regulatory_assessment) | real calcium/vitamin-D bone mechanism tempts mechanism, but mechanism/BMD surrogate framed as fracture prevention, contradicted by RCTs → Shape-B overclaim | (see manifest) |
| ~~006~~ | RETIRED → 018 | — | — | fluoride/BMD Shape-B; no real PUBLIC-FACING fluoride claim under final standard (only scientific assertions) | — | Riggs 1990 NEJM RCT | superseded by 018 (same forensic object, real public claim) | retired |
| 009 | mechanism | overclaim | D2 | "clear senescent 'zombie' cells with senolytics and you can reverse aging … add healthy years" | senolytic-supplement marketing, documented by Cedars-Sinai (public_claim_source) | Xu 2018 Nat Med, animal (primary_research) | preclinical (aged-mice) → implied human anti-aging; no human efficacy → mechanism primary | 19a710bc2cf484bb |
| 010 | mechanism | overclaim | D3 | "fasting regenerates your pancreas and reverses diabetes … no drugs required" | ProLon/FMD marketing, USC press "may reverse diabetes" (public_claim_source) | Cheng 2017 Cell, mice + in-vitro human cells (primary_research) | mouse + in-vitro-human → implied patient cure; human cells ≠ clinical outcome → mechanism primary | 3044e41de4be53a5 |
| 015 | overclaim | mechanism | D3 | Avastin "tumor-starving therapy … cuts off blood supply … shrinks tumors … a powerful weapon" | Genentech Avastin promotion (public_claim_source) | E2100 RCT PFS (primary_research); FDA 2011 withdrawal (regulatory_assessment) | real anti-angiogenesis mechanism tempts mechanism, but human SURROGATE (PFS) framed as patient benefit (no OS/QoL; indication revoked) → Shape-B overclaim | fe0e35d20a8835dd |
| 016 | overclaim | mechanism | D2 | ginkgo "increases blood flow to your brain … sharpens memory and protects against dementia" | ginkgo memory-supplement marketing, documented by NIH NCCIH (public_claim_source) | GEM JAMA 2008 RCT; GuidAge 2012 RCT (primary_research) | real cerebral-blood-flow mechanism tempts mechanism, but surrogate/mechanism framed as clinical benefit, contradicted by direct human RCTs → Shape-B overclaim | 771ce00f4d13cd6f |

### B3 — solid ↔ overclaim (4)

| ID | gold | alt | diff | real public claim (bounded) | claim source (role) | evidence (role) | boundary rationale | fp16 |
|---|---|---|---|---|---|---|---|---|
| 011 | solid | overclaim | D2 | Shingrix "reduced shingles by 97.2% vs placebo … adults 50 and older" | CDC Shingles Vaccination (public_claim_source) | Lal 2015 ZOE-50 RCT (primary_research) | faithful strong-effect reporting scoped to trial; dramatic number tempts overclaim but nothing exceeds evidence → solid | 436c6452a8311085 |
| 012 | solid | overclaim | D3 | SPRINT "~25% fewer CV events, ~27% lower death … also increased hypotension/syncope/AKI … may not generalize" | NIH/NHLBI SPRINT release (public_claim_source) | SPRINT 2015 NEJM RCT (primary_research) | benefit + harms + scope + early-stop reported → honest mixed reporting → solid | d2deda46bacfd849 |
| 013 | overclaim | solid | D3 | "everyone over 60 should take a daily low-dose aspirin … no reason not to" | long-standing aspirin advice, documented by Mayo Clinic (public_claim_source) | ASPREE 2018 RCT (primary_research); USPSTF 2022 (regulatory_assessment) | scoped secondary-prevention benefit over-generalized to healthy elderly + harms omitted → overclaim | afbda45c8bd726de |
| 014 | overclaim | solid | D2 | Lumosity "games make you smarter … protect against cognitive decline and dementia" | Lumosity ads, documented by FTC 2016 action (public_claim_source, same-source evidence §7) | FTC 2016 enforcement (regulatory_assessment) | narrow trained-task effect generalized to far-transfer + dementia prevention → overclaim | 8c1a1d930880c6b7 |

---

## 2. Provenance matrix (§32)

| Case | Real claim source? | Exact quote/span? | Claim URL? | Claim source type | Primary evidence? | Evidence source type | Gold | Boundary quality |
|---|---|---|---|---|---|---|---|---|
| 001 | YES (Cancer Council AU / 2015 media) | YES | YES | news_media_summary | authoritative assessment | regulatory_assessment | overclaim | ADEQUATE |
| 002 | YES (McGill OSS / wellness mandate) | YES | YES | marketing_claim | meta-analysis | systematic_review + secondary | overclaim | ADEQUATE |
| 004 | YES (AHA / Mayo) | YES | YES | news_media_summary | meta-analysis | systematic_review | correlation | STRONG |
| 005 | YES (AHA News) | YES | YES | news_media_summary | meta-analysis | systematic_review | correlation | STRONG |
| 018 | YES (Bone Health & Osteoporosis Foundation + supplement mkt) | YES | YES | public_health_summary | RCT meta-analysis + guideline | systematic_review + regulatory_assessment | overclaim | STRONG |
| 009 | YES (senolytic supplement mkt / Cedars-Sinai) | YES | YES | marketing_claim | animal RCT | primary_research | mechanism | STRONG |
| 010 | YES (ProLon / USC) | YES | YES | marketing_claim | animal + in-vitro | primary_research | mechanism | STRONG |
| 011 | YES (CDC) | YES | YES | public_health_summary | RCT | primary_research | solid | ADEQUATE |
| 012 | YES (NIH/NHLBI) | YES | YES | clinical_summary | RCT | primary_research | solid | ADEQUATE-STRONG |
| 013 | YES (Mayo / advice) | YES | YES | news_media_summary | RCT + guideline | primary_research + regulatory_assessment | overclaim | STRONG |
| 014 | YES (FTC-documented ads) | YES | YES | marketing_claim | enforcement | regulatory_assessment | overclaim | STRONG |
| 015 | YES (Genentech) | YES | YES | marketing_claim | RCT + FDA withdrawal | primary_research + regulatory_assessment | overclaim | STRONG |
| 016 | YES (ginkgo mkt / NCCIH) | YES | YES | marketing_claim | RCT x2 | primary_research | overclaim | STRONG |
| 017 | YES (Berkeley Earth / media) | YES | YES | news_media_summary | authoritative + heuristic | regulatory_assessment + secondary | overclaim | ADEQUATE |

**Provenance status: 14/14 PASS** (structural). The final curator-resolution slice replaced the one
weak-provenance case (former 006, a fluoride/BMD surrogate-marketing archetype with no real
public-facing claim) with **P7A-BND-018** (calcium/vitamin-D "build strong bones / prevent
fractures"), which preserves the same Shape-B forensic object but carries a real, identifiable,
ubiquitous public claim (Bone Health & Osteoporosis Foundation + supplement marketing) and RCT/
guideline evidence. See `boundary_final_curator_resolution.md`. All 14 active claims are now real
identifiable public claims (no archetype-only claim remains).

---

## 3. B2 repair audit table (§33) — all 5 active B2

| ID | Gold | Real mechanistic/preclinical evidence? | Mechanistic evidence materially used? | Human clinical benefit claimed? | Direct human efficacy evidence? | Why mechanism_vs_evidence is plausible | Why final gold wins |
|---|---|---|---|---|---|---|---|
| 018 | overclaim | Yes — real calcium/vitamin-D bone mechanism ("building blocks of bone") + BMD surrogate | Yes (explicit basis) | Yes (fracture prevention, "everyone over 50") | Yes (Zhao 2017 RCT meta-analysis: no fracture reduction) | textbook bone mechanism invoked | mechanism/BMD surrogate framed as fracture prevention, contradicted by RCTs → Shape-B routes to overclaim |
| 015 | overclaim | Yes — anti-angiogenesis (VEGF/Folkman) preclinical + human SURROGATE (PFS) | Yes ("starves tumors") | Yes (breast-cancer benefit) | Surrogate improved; OS/QoL did NOT; FDA revoked | real anti-angiogenesis mechanism invoked | surrogate (PFS) framed as patient benefit → Shape-B routes to overclaim |
| 016 | overclaim | Yes — cerebral blood flow / antioxidant, human surrogate | Yes ("increases blood flow to the brain") | Yes (memory / dementia prevention) | Direct RCTs (GEM, GuidAge) tested and null | real blood-flow mechanism is the explicit basis | surrogate/mechanism framed as clinical benefit, contradicted by human RCTs → Shape-B overclaim |
| 009 | mechanism | Yes — aged-mice interventional (Xu 2018) | Yes | Yes (reverse aging) | No (only small phase-1/2 disease pilots) | gold IS mechanism; overclaim secondary | preclinical→human leap is central |
| 010 | mechanism | Yes — mice + in-vitro human cells (Cheng 2017) | Yes | Yes (reverse diabetes) | No (in-vitro donor cells only) | gold IS mechanism; overclaim secondary | preclinical/in-vitro→patient leap is central |

**All 5 active B2 cases exercise a genuine mechanism_vs_evidence tension** (real mechanistic/
preclinical evidence materially invoked). Retired 007 (no mechanism) and 008 (human RCT, no
mechanism doing rhetorical work) are replaced by 015 and 016.

---

## 4. B1 repair audit table (§34) — all 5 active B1

| ID | Gold | Claim causal force | Evidence design | Specific causal trigger present? | Why correlation_vs_causation is plausible | Why final gold wins |
|---|---|---|---|---|---|---|
| 001 | overclaim | equivalence/hazard framing (not a fresh causal inference) | IARC systematic review; causation established | No (causation established) | diet–cancer is epidemiological (surface attractor) | causation established → defect is magnitude/hazard = overclaim |
| 002 | overclaim | causal benefit language on a fabricated threshold | observational cohort meta-analysis | Weak/secondary | step–mortality data are observational | decisive checkable defect is the fabricated 10k threshold/certainty = overclaim |
| 017 | overclaim | equivalence framing (per-day/total-harm smoking) | IARC Group 1 + risk heuristic; causation established | No (causation established) | air-pollution epidemiology is observational | causation established → defect is risk-metric magnitude = overclaim |
| 004 | correlation | causal + prescriptive ("start drinking") | confounded observational; corrupted reference group | YES | causal claim from confounded design | causal-inference crossing IS the failure → correlation |
| 005 | correlation | causal + prescriptive ("get a dog") | non-randomized; unadjusted confounders | YES | causal claim from non-randomized data | causal-inference crossing IS the failure → correlation |

**All 5 active B1 cases have genuine tension** — the two `overclaim`-with-established-causation cases
(001, 017) keep correlation as a real-but-defeated attractor; the two `correlation` cases (004, 005)
have a present causal trigger; 002 keeps a checkable non-causal defect. Retired 003 (predictive
claim → correlation only reflex) is replaced by 017.

---

## 5. Retired historical cases (excluded from active metrics)

| old ID | prior family | prior gold | reason | replacement |
|---|---|---|---|---|
| P7A-BND-003 | B1 | overclaim | real public claim is PREDICTIVE ("single best predictor"); correlation only a reflex attractor → weak B1 | P7A-BND-017 |
| P7A-BND-006 | B2 | overclaim | no real PUBLIC-FACING fluoride claim under final standard (only scientific assertions); Shape-B object preserved in replacement | P7A-BND-018 |
| P7A-BND-007 | B2 | overclaim | EFSA found NO plausible mechanism → nothing to over-extrapolate → not diagnostic for B2 | P7A-BND-015 |
| P7A-BND-008 | B2 | overclaim | load-bearing evidence is human RCT (Cochrane); genuine alternative is `solid`, not mechanism → not diagnostic for B2 | P7A-BND-016 |

Retired cases keep their files, gold labels, prior fingerprints (in `suite_history`), and
`superseded_by` links; `status: retired` + `excluded_from_active_metrics: true`. Nothing is deleted.

---

## 6. Independence & security

- **Independence:** all 14 active bases are distinct scientific propositions; replacements checked
  against active + retired Boundary cases and the tracked Class-A library. 015 (oncology PFS Shape-B)
  vs 018 (bone BMD/calcium Shape-B) vs 016 (ginkgo blood-flow Shape-B) are distinct agents/surrogates/domains.
  017 shares 001's established-causation-plus-magnitude *architecture* but is a distinct proposition
  (ambient PM2.5 vs processed meat; distinct evidence; distinct forensic error), acceptable under the
  same standard by which the audit kept 004/005 (shared template, distinct propositions). Holdout not
  inspected.
- **Security:** Holdout NO · Holdout gold NO · private mappings NO · salts/envelopes NO · private raw
  responses NO · client/LaVita material NO · evaluation-model calls 0. Web/source research only.
