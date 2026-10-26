# Phase 7A — Perturbation Curator Review Surface (7A.2, WP-3)

Fast-inspection surface for the pre-model perturbation freeze. **50 meaning-preserving variants = 10 independent base clusters × 5 frozen families (P1–P5). NOT 50 independent cases.** 0 model/evaluation calls; gold frozen before any Phase-7A model output.

- Boundary approved checkpoint: `3bdabaf` — not reopened.
- Adversarial approved checkpoint: `e9e13e3` — not reopened.
- Full original↔perturbed text for every variant: `tasks/study_forensics_robustness/perturbation_variants.yaml`.


## Part A — 10-base deterministic selection (contract §6)

| slot | base id | origin | stratum | gold | fp (short) | selection rule |
|---|---|---|---|---|---|---|
| 1 | P7A-NEU-001 | neutral_anchor | neutral:solid | `solid` | `168fed4886` | neutral anchor for 'solid' (auto-included per contract §6 step 1) |
| 2 | P7A-NEU-002 | neutral_anchor | neutral:overclaim | `overclaim` | `254ab43703` | neutral anchor for 'overclaim' (auto-included per contract §6 step 1) |
| 3 | P7A-NEU-003 | neutral_anchor | neutral:correlation_vs_causation | `correlation_vs_causation` | `5bc0f712e5` | neutral anchor for 'correlation_vs_causation' (auto-included per contract §6 step 1) |
| 4 | P7A-NEU-004 | neutral_anchor | neutral:mechanism_vs_evidence | `mechanism_vs_evidence` | `66de577e7c` | neutral anchor for 'mechanism_vs_evidence' (auto-included per contract §6 step 1) |
| 5 | P7A-BND-017 | boundary | B1 | `overclaim` | `0495f2c997` | rank 1 of 5 by ascending case_fingerprint in stratum B1 |
| 6 | P7A-BND-009 | boundary | B2 | `mechanism_vs_evidence` | `19a710bc2c` | rank 1 of 5 by ascending case_fingerprint in stratum B2 |
| 7 | P7A-BND-011 | boundary | B3 | `solid` | `436c6452a8` | rank 1 of 4 by ascending case_fingerprint in stratum B3 |
| 8 | P7A-ADV-010 | adversarial | adversarial:A5 | `overclaim` | `001d6fe0a3` | distinct-family pick #1: first fingerprint-ordered case of new family A5 |
| 9 | P7A-ADV-001 | adversarial | adversarial:A1 | `overclaim` | `10681b9faa` | distinct-family pick #2: first fingerprint-ordered case of new family A1 |
| 10 | P7A-ADV-011 | adversarial | adversarial:A6 | `overclaim` | `1a191e3548` | distinct-family pick #3: first fingerprint-ordered case of new family A6 |

The six existing-pool picks are mechanically the lowest-`case_fingerprint` case in each boundary stratum (B1/B2/B3) and the first three fingerprint-ordered adversarial cases from distinct families (A5, A1, A6). Reproduce with `python3 -m agent_arena.robustness_pool`.


## Part B — Four neutral anchors (contract §5)

| id | gold | claim (decisive proposition) | claim source | load-bearing evidence | difficulty | fp (short) |
|---|---|---|---|---|---|---|
| P7A-NEU-001 | `solid` | Periconceptional folic acid substantially reduces neural-tube-defect risk | CDC guidance (cdc.gov/folic-acid) | MRC RCT Lancet 1991 (~72%); USPSTF Grade A | D1 | `168fed4886` |
| P7A-NEU-002 | `overclaim` | Sensa causes ~30 lb loss with no diet/exercise, 'clinically studied' | FTC action 2014 (ftc.gov) | FTC: no competent & reliable evidence | D2 | `254ab43703` |
| P7A-NEU-003 | `correlation_vs_causation` | 'Coffee causes cancer' from a confounded observational association | popular media; IARC/WHO | IARC 2016 Vol 116: Group 3, confounded by smoking | D2 | `5bc0f712e5` |
| P7A-NEU-004 | `mechanism_vs_evidence` | Cryotherapy anti-inflammatory mechanism → speeds recovery/relieves pain | studio marketing; FDA | FDA 2016: lack of evidence; Cochrane 2015 insufficient | D2 | `66de577e7c` |

Independence: 4 unique fingerprints, disjoint from all Boundary/Adversarial (active+retired) fingerprints; one anchor per frozen label; no duplicate decisive proposition (see candidate log). Provenance structurally complete on all four.


## Part C — Five frozen perturbation families (contract §7 / design §3; §14)

| id | family | allowed transformation | forbidden semantic changes | certification criteria |
|---|---|---|---|---|
| P1 | claim paraphrase | Re-express the same scientific proposition in different wording/syntax. | May not change population, comparator, endpoint, magnitude, causal/mechanistic/clinical-benefit force, certainty, temporal scope, superiority, evidence tier, or scientific meaning; may not repair or introduce a defect. | The decisive proposition and every §12 dimension are materially unchanged; only surface wording differs. |
| P2 | hedging variation (neutral) | Add/adjust a superficial (attributional/discourse) hedge in how the claim is framed. | The superficial hedge may not change the substantive proposition or its force; specifically it may not soften an overclaim, weaken a causal/mechanistic claim, downgrade certainty, or otherwise repair the original defect (a hedge that materially weakens the claim is INVALID, §13). | The asserted force/certainty and all §12 dimensions are unchanged; the hedge is packaging only. |
| P3 | order (claim/evidence context) | Reorder sentences / evidence items (here: present the evidence/context before the claim) while preserving semantic content. | May not add, drop, or edit any claim or evidence content; only sequence changes. | The perturbed prompt is a pure reordering of the base content; no decisive term added/removed. |
| P4 | distractor context | Add irrelevant-but-plausible material that does not bear on the claim. | The added material may not bear on the claim, add or alter scientific evidence, or change any §12 dimension (no new comparator/endpoint/evidence, §23). | The claim and its evidence set are unchanged; the added text is demonstrably irrelevant to the forensic judgment. |
| P5 | formatting | Re-render the same content in a different format (prose <-> bullets, section ordering, metadata/label placement). | May not add, drop, or alter any claim, evidence item, or decisive term; format only. | Every claim and evidence item is preserved; only presentation/format differs. |

Exactly five families (invariance tests). No sixth family; citation-surface variation remains deferred (design §3).


## Part D — 50-variant matrix

### D.1 — compact status matrix

| variant id | base | family | gold | meaning-preservation | var fp (short) |
|---|---|---|---|---|---|
| P7A-PRT-01-P1 | P7A-NEU-001 | P1 (claim paraphrase) | `solid` | PASS | `5c945ef1dc` |
| P7A-PRT-01-P2 | P7A-NEU-001 | P2 (hedging variation (neutral)) | `solid` | PASS | `cd947d5054` |
| P7A-PRT-01-P3 | P7A-NEU-001 | P3 (order (claim/evidence context)) | `solid` | PASS | `3d6e116421` |
| P7A-PRT-01-P4 | P7A-NEU-001 | P4 (distractor context) | `solid` | PASS | `bcb8215732` |
| P7A-PRT-01-P5 | P7A-NEU-001 | P5 (formatting) | `solid` | PASS | `c58a696f85` |
| P7A-PRT-02-P1 | P7A-NEU-002 | P1 (claim paraphrase) | `overclaim` | PASS | `ac51965c86` |
| P7A-PRT-02-P2 | P7A-NEU-002 | P2 (hedging variation (neutral)) | `overclaim` | PASS | `23bd42ed37` |
| P7A-PRT-02-P3 | P7A-NEU-002 | P3 (order (claim/evidence context)) | `overclaim` | PASS | `0b9f879092` |
| P7A-PRT-02-P4 | P7A-NEU-002 | P4 (distractor context) | `overclaim` | PASS | `6e3048c96d` |
| P7A-PRT-02-P5 | P7A-NEU-002 | P5 (formatting) | `overclaim` | PASS | `559dcf4880` |
| P7A-PRT-03-P1 | P7A-NEU-003 | P1 (claim paraphrase) | `correlation_vs_causation` | PASS | `c63a76a7fc` |
| P7A-PRT-03-P2 | P7A-NEU-003 | P2 (hedging variation (neutral)) | `correlation_vs_causation` | PASS | `a016c35f65` |
| P7A-PRT-03-P3 | P7A-NEU-003 | P3 (order (claim/evidence context)) | `correlation_vs_causation` | PASS | `d158c4a4ce` |
| P7A-PRT-03-P4 | P7A-NEU-003 | P4 (distractor context) | `correlation_vs_causation` | PASS | `2c1737df5f` |
| P7A-PRT-03-P5 | P7A-NEU-003 | P5 (formatting) | `correlation_vs_causation` | PASS | `b037e12738` |
| P7A-PRT-04-P1 | P7A-NEU-004 | P1 (claim paraphrase) | `mechanism_vs_evidence` | PASS | `6f3d3e06c8` |
| P7A-PRT-04-P2 | P7A-NEU-004 | P2 (hedging variation (neutral)) | `mechanism_vs_evidence` | PASS | `89eb824e64` |
| P7A-PRT-04-P3 | P7A-NEU-004 | P3 (order (claim/evidence context)) | `mechanism_vs_evidence` | PASS | `c91f6f8f1b` |
| P7A-PRT-04-P4 | P7A-NEU-004 | P4 (distractor context) | `mechanism_vs_evidence` | PASS | `84abd8783e` |
| P7A-PRT-04-P5 | P7A-NEU-004 | P5 (formatting) | `mechanism_vs_evidence` | PASS | `681ba5180c` |
| P7A-PRT-05-P1 | P7A-BND-017 | P1 (claim paraphrase) | `overclaim` | PASS | `638b7ad9ad` |
| P7A-PRT-05-P2 | P7A-BND-017 | P2 (hedging variation (neutral)) | `overclaim` | PASS | `2f280650f4` |
| P7A-PRT-05-P3 | P7A-BND-017 | P3 (order (claim/evidence context)) | `overclaim` | PASS | `83236f64fd` |
| P7A-PRT-05-P4 | P7A-BND-017 | P4 (distractor context) | `overclaim` | PASS | `460199df51` |
| P7A-PRT-05-P5 | P7A-BND-017 | P5 (formatting) | `overclaim` | PASS | `d0f941d66c` |
| P7A-PRT-06-P1 | P7A-BND-009 | P1 (claim paraphrase) | `mechanism_vs_evidence` | PASS | `d748c40786` |
| P7A-PRT-06-P2 | P7A-BND-009 | P2 (hedging variation (neutral)) | `mechanism_vs_evidence` | PASS | `7a98151aa3` |
| P7A-PRT-06-P3 | P7A-BND-009 | P3 (order (claim/evidence context)) | `mechanism_vs_evidence` | PASS | `c873af51fd` |
| P7A-PRT-06-P4 | P7A-BND-009 | P4 (distractor context) | `mechanism_vs_evidence` | PASS | `8d4f2c5d56` |
| P7A-PRT-06-P5 | P7A-BND-009 | P5 (formatting) | `mechanism_vs_evidence` | PASS | `dd8508cbb1` |
| P7A-PRT-07-P1 | P7A-BND-011 | P1 (claim paraphrase) | `solid` | PASS | `65f7a43588` |
| P7A-PRT-07-P2 | P7A-BND-011 | P2 (hedging variation (neutral)) | `solid` | PASS | `03c71f3799` |
| P7A-PRT-07-P3 | P7A-BND-011 | P3 (order (claim/evidence context)) | `solid` | PASS | `e17f87f6d6` |
| P7A-PRT-07-P4 | P7A-BND-011 | P4 (distractor context) | `solid` | PASS | `dacca13e00` |
| P7A-PRT-07-P5 | P7A-BND-011 | P5 (formatting) | `solid` | PASS | `833d48cd10` |
| P7A-PRT-08-P1 | P7A-ADV-010 | P1 (claim paraphrase) | `overclaim` | PASS | `77924af1ad` |
| P7A-PRT-08-P2 | P7A-ADV-010 | P2 (hedging variation (neutral)) | `overclaim` | PASS | `bd3e814428` |
| P7A-PRT-08-P3 | P7A-ADV-010 | P3 (order (claim/evidence context)) | `overclaim` | PASS | `1a7af5615c` |
| P7A-PRT-08-P4 | P7A-ADV-010 | P4 (distractor context) | `overclaim` | PASS | `1bfa9ce0b6` |
| P7A-PRT-08-P5 | P7A-ADV-010 | P5 (formatting) | `overclaim` | PASS | `8b7174feb9` |
| P7A-PRT-09-P1 | P7A-ADV-001 | P1 (claim paraphrase) | `overclaim` | PASS | `7dd005a38a` |
| P7A-PRT-09-P2 | P7A-ADV-001 | P2 (hedging variation (neutral)) | `overclaim` | PASS | `2eea4e44af` |
| P7A-PRT-09-P3 | P7A-ADV-001 | P3 (order (claim/evidence context)) | `overclaim` | PASS | `adae39ba7a` |
| P7A-PRT-09-P4 | P7A-ADV-001 | P4 (distractor context) | `overclaim` | PASS | `7c961ec1ba` |
| P7A-PRT-09-P5 | P7A-ADV-001 | P5 (formatting) | `overclaim` | PASS | `cc339ffdd9` |
| P7A-PRT-10-P1 | P7A-ADV-011 | P1 (claim paraphrase) | `overclaim` | PASS | `dd3bc8d604` |
| P7A-PRT-10-P2 | P7A-ADV-011 | P2 (hedging variation (neutral)) | `overclaim` | PASS | `2bb27fdd2c` |
| P7A-PRT-10-P3 | P7A-ADV-011 | P3 (order (claim/evidence context)) | `overclaim` | PASS | `80f229397e` |
| P7A-PRT-10-P4 | P7A-ADV-011 | P4 (distractor context) | `overclaim` | PASS | `d8d3d2981a` |
| P7A-PRT-10-P5 | P7A-ADV-011 | P5 (formatting) | `overclaim` | PASS | `b55410e27b` |

### D.2 — per-cluster claim wording (original vs the wording-changing families P1/P2)

P3 (order), P4 (distractor), P5 (formatting) do not alter the claim wording — they reorder, append an irrelevant sentence, or reformat the same content — so only the claim-level families are shown here. Full text: `perturbation_variants.yaml`.


**Slot 1 — P7A-NEU-001 · `solid` · folic acid → prevents neural tube defects**

- **Original claim:** A public-health guidance page advises: "Taking a folic acid supplement before conception and during the first weeks of pregnancy substantially reduces the risk of neural tube defects such as spina bifida and anencephaly. All women who could become pregnant are advised to take 400 micrograms of folic acid a day."
- **P1 (paraphrase):** A public-health guidance page advises: "Women who take a folic acid supplement from before conception through the first weeks of pregnancy face a substantially lower risk of having a baby with a neural tube defect such as spina bifida or anencephaly. Every woman who could become pregnant should take 400 micrograms of folic acid each day."
- **P2 (hedging):** A public-health guidance page advises, presenting it as standard, well-established public-health advice: "Taking a folic acid supplement before conception and during the first weeks of pregnancy substantially reduces the risk of neural tube defects such as spina bifida and anencephaly. All women who could become pregnant are advised to take 400 micrograms of folic acid a day."

**Slot 2 — P7A-NEU-002 · `overclaim` · Sensa 'sprinkle & lose weight'**

- **Original claim:** A weight-loss product is marketed as follows: "Sprinkle Sensa on everything you eat and watch the pounds come off - no dieting, no exercise, no calorie counting. In our studies, Sensa users lost an average of 30 pounds. It's the revolutionary, clinically studied way to lose weight."
- **P1 (paraphrase):** A weight-loss product is marketed as follows: "Just shake Sensa onto everything you eat and watch the weight fall off - no dieting, no exercise, no counting calories. In our studies, Sensa users shed an average of 30 pounds. It's the revolutionary, clinically studied way to slim down."
- **P2 (hedging):** A weight-loss product is marketed with an upbeat sales pitch: "Sprinkle Sensa on everything you eat and watch the pounds come off - no dieting, no exercise, no calorie counting. In our studies, Sensa users lost an average of 30 pounds. It's the revolutionary, clinically studied way to lose weight."

**Slot 3 — P7A-NEU-003 · `correlation_vs_causation` · 'coffee causes cancer' (confounded by smoking)**

- **Original claim:** A widely shared health article warns: "Coffee causes cancer. Studies found that people who drink coffee have higher rates of bladder cancer, so drinking coffee raises your cancer risk - cut out coffee to protect yourself."
- **P1 (paraphrase):** A widely shared health article warns: "Coffee causes cancer. Because people who drink coffee turn out to have higher rates of bladder cancer, drinking coffee must raise your cancer risk - cut coffee out to protect yourself."
- **P2 (hedging):** A widely shared health article warns, stating it as plain fact: "Coffee causes cancer. Studies found that people who drink coffee have higher rates of bladder cancer, so drinking coffee raises your cancer risk - cut out coffee to protect yourself."

**Slot 4 — P7A-NEU-004 · `mechanism_vs_evidence` · whole-body cryotherapy → recovery/pain**

- **Original claim:** A wellness studio advertises whole-body cryotherapy: "Stepping into our -140 C cryo-chamber triggers your body's natural anti-inflammatory response and reduces muscle-tissue damage, so it speeds athletic recovery, relieves chronic pain, and boosts your overall wellbeing."
- **P1 (paraphrase):** A wellness studio advertises whole-body cryotherapy: "Step into our -140 C cryo-chamber and it kick-starts your body's natural anti-inflammatory response and cuts muscle-tissue damage, so it speeds up athletic recovery, eases chronic pain, and lifts your overall wellbeing."
- **P2 (hedging):** A wellness studio advertises whole-body cryotherapy in a bold promotional pitch: "Stepping into our -140 C cryo-chamber triggers your body's natural anti-inflammatory response and reduces muscle-tissue damage, so it speeds athletic recovery, relieves chronic pain, and boosts your overall wellbeing."

**Slot 5 — P7A-BND-017 · `overclaim` · Delhi air = 44 cigarettes/day**

- **Original claim:** A widely shared article warns: "Breathing the air in Delhi is like smoking 44 cigarettes a day. Just going outside is as deadly as a pack-a-day smoking habit — every day you spend in the city is literally smoking your lungs away."
- **P1 (paraphrase):** A widely shared article warns: "Spending a day breathing Delhi's air is the equivalent of smoking 44 cigarettes. Simply stepping outside is as lethal as a pack-a-day habit - every day in the city is literally burning your lungs away one cigarette at a time."
- **P2 (hedging):** A widely shared article warns readers in no uncertain terms: "Breathing the air in Delhi is like smoking 44 cigarettes a day. Just going outside is as deadly as a pack-a-day smoking habit - every day you spend in the city is literally smoking your lungs away."

**Slot 6 — P7A-BND-009 · `mechanism_vs_evidence` · senolytics 'clear zombie cells → reverse aging'**

- **Original claim:** A longevity brand promotes a senolytic supplement: "Aging is caused by 'zombie' senescent cells that poison your body. Clear them out with senolytics and you can reverse aging, restore youthful function, and add healthy years to your life."
- **P1 (paraphrase):** A longevity brand promotes a senolytic supplement: "Ageing happens because 'zombie' senescent cells build up and poison the body. Sweep them away with senolytics and you can turn back ageing, bring back youthful function, and add healthy years to your life."
- **P2 (hedging):** A longevity brand promotes a senolytic supplement, pitching it as cutting-edge longevity science: "Aging is caused by 'zombie' senescent cells that poison your body. Clear them out with senolytics and you can reverse aging, restore youthful function, and add healthy years to your life."

**Slot 7 — P7A-BND-011 · `solid` · Shingrix 97.2% vaccine efficacy (faithful)**

- **Original claim:** A public health summary states: "In the phase 3 ZOE-50 randomized controlled trial of adults aged 50 and older, the recombinant shingles vaccine (Shingrix) reduced the incidence of shingles by 97.2% compared with placebo over a mean follow-up of about three years."
- **P1 (paraphrase):** A public health summary states: "In ZOE-50, a phase 3 randomized controlled trial in adults aged 50 and over, the recombinant shingles vaccine (Shingrix) lowered shingles incidence by 97.2% relative to placebo across a mean follow-up of roughly three years."
- **P2 (hedging):** A public health summary states, reporting the trial result as it stands: "In the phase 3 ZOE-50 randomized controlled trial of adults aged 50 and older, the recombinant shingles vaccine (Shingrix) reduced the incidence of shingles by 97.2% compared with placebo over a mean follow-up of about three years."

**Slot 8 — P7A-ADV-010 · `overclaim` · antibacterial soap 'kills 99.9% → protects'**

- **Original claim:** An antibacterial hand soap is advertised: "Kills 99.9% of germs. Protect your family from illness and infection — switch to antibacterial soap for a healthier home."
- **P1 (paraphrase):** An antibacterial hand soap is advertised: "Eliminates 99.9% of germs. Keep your family safe from illness and infection - make the switch to antibacterial soap for a healthier home."
- **P2 (hedging):** An antibacterial hand soap is advertised with a familiar marketing promise: "Kills 99.9% of germs. Protect your family from illness and infection - switch to antibacterial soap for a healthier home."

**Slot 9 — P7A-ADV-001 · `overclaim` · Airborne 'clinically proven' cold prevention**

- **Original claim:** A supplement label and its advertising state: "Airborne is clinically proven to help prevent colds. In a double-blind, placebo-controlled study, Airborne was shown to help your body combat germs — created by a schoolteacher who was sick of catching colds."
- **P1 (paraphrase):** A supplement label and its advertising state: "Airborne is clinically proven to help stop colds before they start. A double-blind, placebo-controlled study showed Airborne helps your body fight off germs - invented by a schoolteacher who was tired of catching colds."
- **P2 (hedging):** A supplement label and its advertising state, in the brand's own confident words: "Airborne is clinically proven to help prevent colds. In a double-blind, placebo-controlled study, Airborne was shown to help your body combat germs - created by a schoolteacher who was sick of catching colds."

**Slot 10 — P7A-ADV-011 · `overclaim` · Nexium 'better than Prilosec'**

- **Original claim:** Advertising for Nexium (esomeprazole) positions it against Prilosec (omeprazole): "Nexium, the new purple pill, heals acid-reflux damage and relieves heartburn better than Prilosec. Ask your doctor to switch you to the better purple pill."
- **P1 (paraphrase):** Advertising for Nexium (esomeprazole) positions it against Prilosec (omeprazole): "Nexium, the new purple pill, does a better job than Prilosec at healing acid-reflux damage and easing heartburn. Ask your doctor to switch you to the better purple pill."
- **P2 (hedging):** Advertising for Nexium (esomeprazole) positions it against Prilosec (omeprazole) with a direct sales pitch: "Nexium, the new purple pill, heals acid-reflux damage and relieves heartburn better than Prilosec. Ask your doctor to switch you to the better purple pill."

## Part E — Aggregate clustering / counts (pseudoreplication guard, §24/§25)

| quantity | value |
|---|---|
| n_independent_perturbation_bases | **10** |
| n_perturbation_clusters | **10** |
| n_perturbation_variants | **50** |
| n_perturbation_families | **5** |
| variants per base | [5] (all 5) |
| variants per family | P1=10, P2=10, P3=10, P4=10, P5=10 (all 10) |
| base strata | 4 neutral + 1 B1 + 1 B2 + 1 B3 + 3 adversarial (distinct families A5/A1/A6) |
| variants are independent cases? | **NO** — nested in 10 bases |

> **50 variants ≠ 50 independent cases.** Downstream metrics must report cluster-aware: `n_independent_perturbation_bases = 10`, `n_perturbation_variants = 50`.


## Human-review watchlist (§31) — closest-equivalence variants

Meaning-preservation was most delicate for the **P2 (hedging)** variants of the four *defective*-gold bases and the **P1 (paraphrase)** variants that reword a defect-bearing claim, because a careless hedge/paraphrase could repair the defect and flip the gold. Each still passes; the rest (solid bases, and all P3/P4/P5) are structurally safe.

| variant | why equivalence is close | why it still passes |
|---|---|---|
| P7A-PRT-02-P2 (Sensa) | a hedge could soften 'proven weight loss' into a tentative claim | uses attributional framing only ('upbeat sales pitch'); 'clinically studied / avg 30 lb' force intact → still overclaim |
| P7A-PRT-09-P2 (Airborne) | dropping 'clinically proven' would repair the decorative-citation overclaim | keeps 'clinically proven … double-blind study'; adds only 'in the brand's own confident words' → still overclaim |
| P7A-PRT-03-P1/P2 (coffee) | 'causes'→'associated with' would remove the correlation-as-cause error | keeps the explicit causal verb ('must raise your cancer risk') → still correlation_vs_causation |
| P7A-PRT-10-P1 (Nexium) | dropping 'better than Prilosec' would delete the A6 superiority structure | keeps the explicit comparator superiority → still overclaim |
| P7A-PRT-05-P1 (Delhi) | a hedged 'roughly comparable' would soften the magnitude overreach | keeps 'the equivalent of smoking 44 cigarettes … literally' → still overclaim |

No variant was left in with genuinely uncertain equivalence; uncertain drafts were regenerated or rejected (see `perturbation_authoring_log.md`).


**FAIL / regenerated in the frozen set: 0. PASS: 50/50. Variant gold == base gold: 50/50.**

