# Phase 7A — Adversarial Pool Curator Review (WP-2)

Compact review surface for the **Phase-7A Adversarial Pool**: **16 ACTIVE frozen cases** = 8 frozen
adversarial families (A1-A8) × 2 independent cases. Generated from the frozen
`tasks/study_forensics_robustness/P7A-ADV-*.yaml` records, **before any Haiku/Sonnet/Opus evaluation
run** (0 evaluation-model calls). Lets the human curator inspect all 16 without opening every YAML.

## Governance language (accurate)

- Gold was **authored pre-model by the Claude repo agent (an LLM)** and frozen before any evaluation
  run. **No separate evaluation model or external LLM judge determined gold.** This is
  **LLM-authored pre-model gold**, not human IAA / human-authored / independent human validation.
- **Boundary pool: human-curator approved before WP-2 = YES** (checkpoint `3bdabaf`). The Boundary
  track is CLOSED and untouched by WP-2.
- Selection was **family-driven** (frozen A1-A8 contract) + scientific suitability, **never**
  error-driven (no Phase-7A model results exist).

## Provenance standard (inherited from the Boundary repair)

Every active adversarial case carries **real, identifiable public-claim provenance**
(`claim_source_url` + bounded `claim_exact_span` + `claim_source_role` + `claim_source_type` +
`claim_source_publisher`/`claim_context`), with the scientific **evidence** kept separate and each
evidence item carrying a declared controlled-vocabulary `source_role`
(`primary_research | systematic_review | regulatory_assessment | trial_registration |
secondary_discovery | other`). Structural completeness is enforced by
`robustness_pool.claim_provenance_status` + `tests/test_phase7a_adversarial_pool.py`; scientific
source **fidelity** remains curator-reviewed.

---

## 1. Active 16-case matrix

Fingerprints are the first 16 hex chars (full SHA-256 in each YAML and `adversarial_manifest.yaml`).

### A1 — decorative citation → overclaim (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 001 | overclaim | solid | D2 | "Airborne is clinically proven to help prevent colds. In a double-blind, placebo-controlled study…" | Airborne Health (marketing) | FTC 2008 action (regulatory_assessment) | a named "clinical study" is non-probative (no clinic/scientists, unpublished) → proof-claim without proof; no specific trigger → overclaim | 10681b9faa8bbceb |
| 002 | overclaim | solid | D3 | "Backed by $35 million in medical research… helps prevent and treat heart disease, prostate cancer, and erectile dysfunction" | POM Wonderful (marketing) | FTC 2013 Commission Opinion (regulatory_assessment) | research volume/prestige cited as proof of disease outcomes the studies don't establish → overclaim | 3850cc04df208f83 |

### A2 — citation supports mechanism but not outcome → mechanism_vs_evidence (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 003 | mechanism | overclaim | D2 | "Metformin is an anti-aging drug… so taking metformin will slow your aging and add years to your life" | longevity clinic (marketing) | Martin-Montalvo 2013 Nat Commun, mouse (primary_research); TAME (trial_registration) | prestige mouse-lifespan citation → human anti-aging outcome; animal mechanism→human benefit → mechanism_vs_evidence | e85e7533086b2ab2 |
| 004 | mechanism | overclaim | D3 | "A Nature Medicine study proved spermidine protects the heart and extends lifespan — so a daily supplement will… help you live longer" | spermidine supplement (marketing) | Eisenberg 2016 Nat Med, mouse + human observational (primary_research) | mouse cardioprotection/lifespan citation → human outcome; confounded human associations as evidence-tier lure → mechanism_vs_evidence | f2f6a940bdae072f |

### A3 — causal verb on observational data → correlation_vs_causation (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 005 | correlation | overclaim | D3 | "people who skip breakfast weigh more, so skipping breakfast makes you gain weight — eat… and you will lose weight" | diet media (news_media_summary) | Sievert 2019 BMJ RCT meta-analysis (systematic_review) | causal/prescriptive claim from confounded observational data; RCTs refute → correlation_vs_causation | 41a48d00c17bc536 |
| 006 | correlation | overclaim | D3 | "Violent video games are causing real-world violence… turning our young people into killers and driving mass shootings" | political/media discourse (political_or_media_claim) | APA 2020 resolution (regulatory_assessment) | correlational aggression research → causal violence; authoritative body rejects attribution → correlation_vs_causation | c3f83b14e6c2c0dd |

### A4 — subgroup → general-population generalization → overclaim (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 007 | overclaim | solid | D2 | "…everyone should cut gluten to lose weight, boost energy, and feel healthier" | wellness media (news_media_summary) | gluten-free-diet review (systematic_review) | celiac (~1%) benefit generalized to everyone; no general-population benefit → overclaim | 72f3e8732e705e9d |
| 008 | overclaim | solid | D2 | "Feeling tired, low energy, low sex drive as you get older? It could be Low T. Testosterone therapy can restore your energy, drive, and vitality" | "Low T" DTC campaign (marketing) | FDA 2015 restriction to classical hypogonadism (regulatory_assessment) | hypogonadism-subgroup benefit generalized to all aging men; benefit not established + possible harm → overclaim | d43c8f716d891cdd |

### A5 — surrogate endpoint → clinical benefit (Shape B, positive control) → overclaim (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 009 | overclaim | mechanism | D3 | "clearing the amyloid-beta plaques… a breakthrough that treats Alzheimer's" | Biogen Aduhelm (marketing) | FDA 2021 accelerated approval on amyloid surrogate (regulatory_assessment) | human surrogate (amyloid PET) framed as clinical benefit; Shape-B routes to overclaim, NOT mechanism_vs_evidence | 10b04f62dcb58ff5 |
| 010 | overclaim | solid | D2 | "Kills 99.9% of germs. Protect your family from illness and infection" | antibacterial-soap ads (marketing) | FDA 2016 final rule (regulatory_assessment) | lab germ-kill surrogate framed as illness-prevention clinical outcome; Shape-B → overclaim | 001d6fe0a3a14250 |

### A6 — unsupported superiority / comparator manipulation → overclaim (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 011 | overclaim | solid | D3 | "…heals acid-reflux damage and relieves heartburn better than Prilosec… switch to the better purple pill" | AstraZeneca Nexium (marketing) | Kahrilas 2000 head-to-head RCT, 40 vs 20 mg, 93.7% vs 84.2% healing (primary_research) | clinical superiority built on a rigged 40-vs-20 mg comparison; narrows at equal doses; edge is an acid-suppression surrogate → overclaim | 1a191e3548bd5beb |
| 012 | overclaim | solid | D2 | "Listerine antiseptic mouthwash is as effective as floss… Why floss? Just rinse" | Pfizer Listerine (marketing) | McNeil-PPC v. Pfizer, 351 F.Supp.2d 226 (regulatory_assessment) | equivalence claim over-generalized beyond narrow (mild-moderate gingivitis) studies; court enjoined → overclaim | dbbb7c7fa3d54465 |

### A7 — biologically plausible mechanism → implied human efficacy → mechanism_vs_evidence (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 013 | mechanism | overclaim | D2 | "By supercharging your cells' energy, our panel reverses aging, heals your body, and restores youthful vitality" | red-light device (marketing) | photobiomodulation cytochrome c oxidase, animal (primary_research) | real cellular mechanism (mostly preclinical) → broad human benefit not shown → mechanism_vs_evidence (Shape C) | cde0fa24209e929f |
| 017 | mechanism | overclaim | D3 | "take nattokinase daily to dissolve clots … and prevent heart attacks and strokes" | nattokinase supplement (marketing) | Sumi 1987 in-vitro fibrinolysis (primary_research) + RCT systematic review, surrogates only (systematic_review) | real fibrinolytic mechanism → undemonstrated human clinical outcome (no MI/stroke trial) → mechanism_vs_evidence (Shape C); replaces retired 014 | 21c3b148c1e5e189 |

### A8 — technically-true-but-misleading number → overclaim (2)

| ID | gold | alt | diff | exact public claim (bounded) | claim source (type) | evidence (role) | why adversarial / precedence | fp16 |
|---|---|---|---|---|---|---|---|---|
| 015 | overclaim | solid | D3 | "Lipitor reduces the risk of heart attack by 36% … 3% (placebo) vs 2% (Lipitor)" | Pfizer Lipitor (marketing) | ASCOT-LLA via FDA label, 1.9% vs 3.0%; 36% RRR (regulatory_assessment) | true relative risk reduction framed to overstate a ~1pp absolute benefit; fine-print hedge doesn't repair → overclaim | f05d8c4949bff464 |
| 016 | overclaim | solid | D2 | "More than 80% of dentists recommend Colgate. Colgate — used and recommended by most dentists" | Colgate-Palmolive (marketing) | UK ASA 2007 UPHELD adjudication (regulatory_assessment) | technically-true multiple-response survey (rival recommended almost as much) framed to imply a preference → overclaim | 8f093928edae5384 |

---

## 2. Aggregate tables

**Family counts (frozen):** A1=2 · A2=2 · A3=2 · A4=2 · A5=2 · A6=2 · A7=2 · A8=2 → **16**.

**Gold distribution (emergent, frozen pre-model):**

| gold label | count | families |
|---|---:|---|
| overclaim | 10 | A1, A4, A5, A6, A8 (each ×2) |
| mechanism_vs_evidence | 4 | A2, A7 (each ×2) |
| correlation_vs_causation | 2 | A3 (×2) |
| solid | 0 | — |

This distribution **emerges from the frozen family gold-logic**; it is **not** an imposed cosmetic
4-label balance (the frozen Phase-7A design imposes no adversarial gold balance — contrast Boundary).

**Difficulty distribution (property-based, pre-result):** D2 = 8 · D3 = 8 · D1 = 0. (No case is D1:
every adversarial case carries ≥1 misleading surface cue and a genuinely plausible alternate, so
D2/D3 is the defensible range; the design forbids forcing all to D3.)

**Strongest-alternative distribution:** solid (10), overclaim (4), mechanism_vs_evidence (1),
correlation_vs_causation (0) — every case's competing label differs from its gold.

---

## 3. Family audit table (§34)

| Family | Frozen definition | Case 1 | Case 2 | Structural trigger present? | Gold defensible? | Adversarial pressure genuine? |
|---|---|---|---|---|---|---|
| A1 | decorative citation (citation present, does not support the claim) | 001 Airborne (non-probative "clinical study") | 002 POM ($35M research decoration) | YES — both cite research that does not support the claim | YES — overclaim (proof-claim without proof) | YES — a named study/research volume lends false authority |
| A2 | citation supports mechanism but not outcome | 003 metformin (mouse lifespan → human) | 004 spermidine (mouse cardio/lifespan → human) | YES — a real preclinical citation establishes the mechanism/animal outcome, wielded for a human outcome | YES — mechanism_vs_evidence (animal mechanism→human) | YES — prestige citation adjacency (supports the wrong step) |
| A3 | causal verb on observational/correlational data | 005 breakfast (RCTs refute) | 006 video games (APA rejects attribution) | YES — causal claim from correlational/observational data | YES — correlation_vs_causation (counterfactual missing/refuting) | YES — familiarity/emotion make the causal leap feel evidenced |
| A4 | subgroup → general-population generalization | 007 gluten-free (celiac ~1%) | 008 "Low T" (classical hypogonadism) | YES — a subgroup-specific benefit generalized to the whole population | YES — overclaim (extrapolation beyond evidenced population) | YES — the subgroup benefit is genuine, lending credibility |
| A5 | surrogate endpoint → clinical benefit ("Shape B") | 009 Aduhelm (amyloid PET) | 010 antibacterial soap (germ-kill) | YES — a surrogate framed as the clinical outcome | YES — overclaim (Shape-B positive control; taxonomy excludes it from mechanism_vs_evidence) | YES — mechanistic/quantitative dressing pulls toward mechanism/solid |
| A6 | unsupported superiority / cherry-picking / missing comparator | 011 Nexium (rigged 40-vs-20 mg) | 012 Listerine (over-generalized comparator) | YES — a comparator-based superiority/equivalence claim exceeding the fair comparison | YES — overclaim (superiority beyond evidence) | YES — real trials + genuine surrogate edge make it look evidenced |
| A7 | biologically plausible mechanism → implied human efficacy | 013 red light (mitochondria/ATP) | 017 nattokinase (fibrinolysis) | YES — a real, preclinical mechanism extrapolated to an undemonstrated human clinical outcome | YES — mechanism_vs_evidence (Shape C); claimed outcome has NO human trial | YES — a real/vivid mechanism makes efficacy sound inevitable |
| A8 | technically-true-but-misleading value; hedges do not repair | 015 Lipitor (36% RRR vs ~1pp ARR) | 016 Colgate (multiple-response survey) | YES — a numerically-correct value framed to mislead | YES — overclaim (framing inflation of an accurate number) | YES — accuracy (and partial disclosure) makes it look honest |

Every family is complete (2 cases), both cases structurally instantiate the trigger, gold is a single
defensible primary under the frozen taxonomy/precedence, and the adversarial pressure is a genuine
surface feature (not decorative metadata).

---

## 4. Especially close / precedence-sensitive cases (curator attention)

- **009 Aduhelm (A5)** — the strongest alternative is `mechanism_vs_evidence` (amyloid clearance is a
  "mechanism"). Gold `overclaim` relies on the frozen taxonomy rule that **Shape B (surrogate→clinical)
  is excluded from mechanism_vs_evidence and routed to overclaim**. This is the family's designed
  positive control; flagged for explicit curator confirmation of the routing.
- **004 spermidine (A2)** and **017 nattokinase (A7)** — both have supportive-but-weak human data
  (observational associations / human surrogate-marker studies). Gold stays `mechanism_vs_evidence`
  because the load-bearing basis is the preclinical mechanism and the claimed human clinical OUTCOME is
  not established by any trial; the human data are on surrogates/associations, not the claimed outcome,
  and are weighed in each steelman without reaching `solid`.
- **015 Lipitor (A8)** and **011 Nexium (A6)** — accurate numbers / real drug edges create a strong
  `solid` pull; gold `overclaim` rests on framing (relative-vs-absolute; rigged 40-vs-20 mg comparator).

> **WP-2 gold-review update:** the original A7 case 014 (psychobiotic "cure your anxiety/depression")
> was **retired** and replaced by **017 (nattokinase)**. Re-adjudication found direct human RCT/
> meta-analytic evidence exists for probiotics in depression (adjunct, not stand-alone), so `overclaim`
> was at least equally defensible and `mechanism_vs_evidence` was not uniquely defensible — a gold
> blocker. Nattokinase is a clean A7 because the claimed clinical outcome (MI/stroke prevention) has no
> human outcome trial. See `adversarial_human_curator_gold_review.md`.

No active case has two equally-defensible primary labels; where two labels were co-defensible, the
candidate was rejected (see candidate log §2).
