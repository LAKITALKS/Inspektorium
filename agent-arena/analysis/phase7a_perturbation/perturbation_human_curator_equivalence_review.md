# Phase 7A — Perturbation Human-Curator Equivalence Review (WP-3 final, blocker-only)

Final blocker-only curator review of the frozen perturbation pool at checkpoint `d4b3e32`. Two
reviews only: **(A)** gold safety of the four newly authored neutral anchors, and **(B)** meaning
equivalence of the 50 perturbation variants. The question is **not** "can these be improved"; it is
"is any gold unsafe / does any transformation change the proper gold". Boundary (`3bdabaf`) and
Adversarial (`e9e13e3`) science, the base-selection algorithm, A1–A8 / B1–B3 definitions, thresholds,
model conditions, and N=5 are **not** reopened. **0 evaluation-model calls; no external
semantic-judge model; holdout untouched.** No Stacy-Sims/INSPEKTORIUM insight was incorporated (§6).

---

## Section A — Neutral-anchor verdicts (blocker-only, §7)

| ID | gold | claim provenance (real, bounded) | evidence adequacy | independence | disposition |
|---|---|---|---|---|---|
| **P7A-NEU-001** | `solid` | CDC "About Folic Acid" (`cdc.gov/folic-acid`), bounded exact span; real public-health guidance | MRC RCT Lancet 1991 (PMID 1677062, ~72%); USPSTF Grade A — strongest tier | distinct from Shingrix (BND-011) / SPRINT (BND-012); fp-disjoint | **PASS** |
| **P7A-NEU-002** | `overclaim` | FTC v. Sensa press release (`ftc.gov`, 2014, $26.5M), bounded marketing span | FTC evidence assessment: no competent & reliable evidence; studies not adequately controlled | distinct proposition (weight loss) from Airborne cold-prevention (ADV-001) & all A-overclaims | **PASS** |
| **P7A-NEU-003** | `correlation_vs_causation` | IARC/WHO Monographs Vol 116 / PR N°244 (`iarc.who.int`, 2016) documenting the "coffee causes cancer" claim; bounded causal span | IARC 2016 Group 3; prior association attributed to **confounding by smoking** | distinct confounder from alcohol (BND-004), dog (BND-005), breakfast (ADV-005), games (ADV-006) | **PASS** |
| **P7A-NEU-004** | `mechanism_vs_evidence` | FDA consumer update (`fda.gov`, 2016) documenting the marketed benefits; bounded mechanism→benefit span | FDA: no cleared device, lack of evidence; Cochrane 2015 (PMID 26383887) insufficient — a genuine **gap**, not refutation | distinct domain from senolytics (BND-009), ginkgo (BND-016), red-light (ADV-013), nattokinase (ADV-017) | **PASS** |

**Special watch §8 (NEU-003):** the frozen YAML carries a real, identifiable documenting source (IARC
PR244) and a **bounded** claim span that genuinely crosses the causal boundary — "Coffee causes
cancer … so drinking coffee raises your cancer risk." This follows the **already-approved ADV-005
standard** (checkpoint `e9e13e3`): a durable authoritative source that documents+refutes a ubiquitous
public causal claim, `claim_source_type: news_media_summary`. Not a generic archetype → **PASS** (no
repair).

**Special watch §9 (NEU-004):** the frozen YAML has an identifiable real source (FDA consumer update),
a bounded exact span, an actual mechanistic rationale (extreme cold → vasoconstriction / blunted acute
inflammation), an implied **human** clinical benefit (recovery, chronic-pain relief, wellbeing), and
**insufficient** direct clinical evidence for that benefit (FDA lack-of-evidence + Cochrane
"insufficient" — a gap, not a refuting RCT, so `mechanism_vs_evidence` is uniquely defensible and does
not fall into the retired-ADV-014 trap). → **PASS**.

**Non-blocking observations (do not affect gold safety, §25):**
- NEU-002's claim contains "clinically studied / in our studies", which shares surface with the A1
  decorative-citation family. The gold is **robust to either reading** (A1's gold is also `overclaim`),
  and the decisive proposition (weight loss) is distinct from Airborne (cold prevention). Not a blocker.
- NEU-003/NEU-004 anchor `claim_source_url` to the documenting authority (IARC / FDA) rather than an
  origin utterance — identical to the approved ADV-005 pattern; the bounded claim spans are present.

**Neutral gold distribution:** `solid`=1 · `overclaim`=1 · `correlation_vs_causation`=1 ·
`mechanism_vs_evidence`=1. ✔

---

## Section B — 50-variant equivalence matrix

All 50 reviewed. Families: P1 paraphrase · P2 hedging · P3 order · P4 distractor · P5 formatting.

| variant | base | family | gold | equivalence | material check |
|---|---|---|---|---|---|
| P7A-PRT-01-P1 | P7A-NEU-001 | P1 | `solid` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-01-P2 | P7A-NEU-001 | P2 | `solid` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-01-P3 | P7A-NEU-001 | P3 | `solid` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-01-P4 | P7A-NEU-001 | P4 | `solid` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-01-P5 | P7A-NEU-001 | P5 | `solid` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-02-P1 | P7A-NEU-002 | P1 | `overclaim` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-02-P2 | P7A-NEU-002 | P2 | `overclaim` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-02-P3 | P7A-NEU-002 | P3 | `overclaim` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-02-P4 | P7A-NEU-002 | P4 | `overclaim` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-02-P5 | P7A-NEU-002 | P5 | `overclaim` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-03-P1 | P7A-NEU-003 | P1 | `correlation_vs_causation` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-03-P2 | P7A-NEU-003 | P2 | `correlation_vs_causation` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-03-P3 | P7A-NEU-003 | P3 | `correlation_vs_causation` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-03-P4 | P7A-NEU-003 | P4 | `correlation_vs_causation` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-03-P5 | P7A-NEU-003 | P5 | `correlation_vs_causation` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-04-P1 | P7A-NEU-004 | P1 | `mechanism_vs_evidence` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-04-P2 | P7A-NEU-004 | P2 | `mechanism_vs_evidence` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-04-P3 | P7A-NEU-004 | P3 | `mechanism_vs_evidence` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-04-P4 | P7A-NEU-004 | P4 | `mechanism_vs_evidence` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-04-P5 | P7A-NEU-004 | P5 | `mechanism_vs_evidence` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-05-P1 | P7A-BND-017 | P1 | `overclaim` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-05-P2 | P7A-BND-017 | P2 | `overclaim` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-05-P3 | P7A-BND-017 | P3 | `overclaim` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-05-P4 | P7A-BND-017 | P4 | `overclaim` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-05-P5 | P7A-BND-017 | P5 | `overclaim` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-06-P1 | P7A-BND-009 | P1 | `mechanism_vs_evidence` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-06-P2 | P7A-BND-009 | P2 | `mechanism_vs_evidence` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-06-P3 | P7A-BND-009 | P3 | `mechanism_vs_evidence` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-06-P4 | P7A-BND-009 | P4 | `mechanism_vs_evidence` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-06-P5 | P7A-BND-009 | P5 | `mechanism_vs_evidence` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-07-P1 | P7A-BND-011 | P1 | `solid` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-07-P2 | P7A-BND-011 | P2 | `solid` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-07-P3 | P7A-BND-011 | P3 | `solid` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-07-P4 | P7A-BND-011 | P4 | `solid` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-07-P5 | P7A-BND-011 | P5 | `solid` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-08-P1 | P7A-ADV-010 | P1 | `overclaim` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-08-P2 | P7A-ADV-010 | P2 | `overclaim` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-08-P3 | P7A-ADV-010 | P3 | `overclaim` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-08-P4 | P7A-ADV-010 | P4 | `overclaim` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-08-P5 | P7A-ADV-010 | P5 | `overclaim` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-09-P1 | P7A-ADV-001 | P1 | `overclaim` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-09-P2 | P7A-ADV-001 | P2 | `overclaim` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-09-P3 | P7A-ADV-001 | P3 | `overclaim` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-09-P4 | P7A-ADV-001 | P4 | `overclaim` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-09-P5 | P7A-ADV-001 | P5 | `overclaim` | PASS | prose->labelled bullets; all decisive tokens preserved |
| P7A-PRT-10-P1 | P7A-ADV-011 | P1 | `overclaim` | PASS | synonym paraphrase; causal/comparative/magnitude/certainty/endpoint preserved |
| P7A-PRT-10-P2 | P7A-ADV-011 | P2 | `overclaim` | PASS | external attributive framing only; embedded proposition identical |
| P7A-PRT-10-P3 | P7A-ADV-011 | P3 | `overclaim` | PASS | pure paragraph-order swap (evidence<->claim); no content change |
| P7A-PRT-10-P4 | P7A-ADV-011 | P4 | `overclaim` | PASS | base intact + one irrelevant packaging/logistics distractor |
| P7A-PRT-10-P5 | P7A-ADV-011 | P5 | `overclaim` | PASS | prose->labelled bullets; all decisive tokens preserved |

**Result: 50 PASS · 0 FAIL · 0 regenerated.**

Family-level findings:
- **P2 (highest risk, §14):** all 10 keep the **embedded quoted proposition byte-for-byte** and change
  only external attributive framing ("marketed with an upbeat sales pitch", "in the brand's own
  confident words", "stating it as plain fact", "reporting the trial result as it stands"). None inserts
  a force-changing hedge ("may/might"); none repairs a defect. This is exactly the §14-valid form.
- **P1 (§20):** every causal verb, comparative/superiority, magnitude, certainty, and endpoint is
  preserved under synonym substitution (see watchlist below).
- **P3 (§21):** mechanically verified pure two-paragraph order swap (evidence↔claim); no item lost/added.
- **P4 (§22):** base two paragraphs verbatim + one appended distractor about packaging / product format /
  logistics / media reach — none supplies evidence, comparator, mechanism, population, endpoint, or a
  credibility signal material to the claim.
- **P5 (§23):** prose→labelled-bullet reformat; every decisive token (numbers, causal verbs, comparator
  names, endpoints, agency names) preserved.

---

## Section C — Expanded watchlist analysis (§15)

| variant | material forensic feature that MUST survive | survived? |
|---|---|---|
| **P7A-PRT-02-P2** (Sensa hedge) | proven/quantified unsupported-efficacy force ("watch the pounds come off … clinically studied … 30 pounds") | **YES** — embedded quote identical; only "marketed with an upbeat sales pitch" added externally |
| **P7A-PRT-09-P2** (Airborne hedge) | "clinically proven" proof-force resting on a non-probative decorative citation | **YES** — embedded quote identical; "in the brand's own confident words" is pure attribution, does not drop "clinically proven" or insert "may" |
| **P7A-PRT-03-P1** (coffee causal paraphrase) | explicit **causal** claim drawn from a confounded observational association | **YES** — "Coffee causes cancer … drinking coffee **must** raise your cancer risk"; causal force intact, NOT softened to "associated with" |
| **P7A-PRT-03-P2** (coffee causal hedge) | same causal force | **YES** — "stating it as plain fact" reinforces attribution; embedded causal claim unchanged |
| **P7A-PRT-10-P1** (Nexium superiority paraphrase) | unsupported **superiority over the comparator** (Prilosec) | **YES** — "does a better job than Prilosec … the better purple pill"; superiority + comparator preserved |
| **P7A-PRT-05-P1** (Delhi magnitude paraphrase) | literal per-day **magnitude** overreach ("44 cigarettes a day", literal total-harm equivalence) | **YES** — "the equivalent of smoking 44 cigarettes … as lethal as a pack-a-day habit … literally burning your lungs away" |

No variant carried genuinely uncertain equivalence. A minor, non-semantic typographic artifact (some
perturbed quotes render the base em-dash "—" as a spaced hyphen "-") appears in a few claim-level
variants; it does not touch any material dimension and is not a defect (§25).

---

## Section D — Regenerated variants

**None.** All 50 frozen variants pass meaning-preservation as authored; no in-family regeneration was
required (§18), so no fingerprint changed.

---

## Section E — Final counts / recommendation

- Neutral anchors: **4/4 PASS** (gold safe, real bounded provenance, independent); distribution 1/1/1/1.
- Variants reviewed: **50** · initial PASS **50** · initial FAIL **0** · regenerated **0** · final PASS **50**.
- Family counts: P1=10 · P2=10 · P3=10 · P4=10 · P5=10.
- Gold inheritance: **50/50** variant gold == base gold.
- Clustering: **10 independent bases**, 50 derived variants — not 50 independent cases.
- Deterministic 10-base selection: unchanged from `d4b3e32`.
- Prior Boundary/Adversarial pools: unchanged. Holdout: untouched. Evaluation-model calls: **0**.

**Recommendation: PERTURBATION POOL READY FOR HUMAN CURATOR FINAL APPROVAL.** This is a docs-only
outcome (no scientific artifact changed); next step is human final approval → WP-4 thin
execution/reporting readiness. Do not start WP-4.
