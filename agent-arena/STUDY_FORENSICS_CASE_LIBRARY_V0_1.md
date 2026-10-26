# Study Forensics Case Library v0.1 (Phase 3)

Curated expansion of the `study_forensics` task set from 29 to **50 cases**. The 21 Phase-3 additions (`case043`–`case063`) are **synthetic fixtures** — each inspired by a common, real-world claim-forensics pattern but written without fabricated citations, journals, or product names. Every new case sets `origin: synthetic_fixture`.

All existing cases are preserved and un-renumbered. New cases use the next available numbers after the previous highest (`042`).

## Label taxonomy (code-compatible)

The engine's `gold_label` taxonomy has four values; new cases map onto these without inventing an incompatible taxonomy:

- **solid** — communication matches the evidence (fair reporting / positive control)
- **overclaim** — conclusion/marketing exceeds the evidence (rhetorical inflation)
- **mechanism_vs_evidence** — an evidence-tier gap (cell/animal/biomarker/surrogate → human outcome)
- **correlation_vs_causation** — causal claim from an observational/confounded design

The richer *intended classification* column below (supported, cautious_supported, misleading, ambiguous, …) is documentation-only and is **not** encoded in code.

## Taxonomy overview — pattern groups

| Group | Case range | Patterns covered |
|---|---|---|
| A. Biomedical / Clinical | case043–case052 | cell→human, animal→human, biomarker→outcome, correlation→causation, small pilot, surrogate endpoint, safety overclaim, 'clinically proven', + two fair positive controls |
| B. Scientific / Market Communication | case053–case057 | missing head-to-head, decorative hedging, follow-up-window extrapolation, subgroup overreach, relative-vs-absolute risk |
| C. AI / Technology | case058–case061 | benchmark overclaim, energy/lifecycle blind spot, synthetic→real generalisation, autonomy overclaim |
| D. Environment / Policy / Social | case062–case063 | lifecycle-boundary overclaim, policy-causality overreach |

## Per-case reference table

| Case | Title | Category | gold_label | Intended classification | Expected failure mode | Evidence tier | Overclaim mechanism | Difficulty | Discrimination value | Why it matters |
|---|---|---|---|---|---|---|---|---|---|---|
| case043 | In-vitro compound kills cancer cells, framed as a cancer treatment | Biomedical | overclaim | overclaim / ambiguous (borderline; alt: mechanism_vs_evidence) | missing_overclaim | in-vitro (cell) | cell-death → human cure, sold as fact | hard | ambiguous edge (borderline) | Tests cytotoxicity-≠-cure AND the overclaim-vs-tier-gap priority rule. Gold reviewed in Phase 4 (see note below). |
| case044 | Memory boost in mice framed as a possible human mechanism | Biomedical | mechanism_vs_evidence | mechanism_vs_evidence (clean control) | accepting_mechanism_as_evidence | animal (mice) | animal → possible human mechanism (hedged) | medium | catches weak models | Clean hedged animal-to-human tier gap; reworded in Phase 4 (see note below). |
| case045 | Lowering an inflammatory marker framed as preventing heart attacks | Biomedical | overclaim | overclaim / ambiguous (borderline; alt: mechanism_vs_evidence) | missing_overclaim | biomarker/surrogate | marker change → clinical event, sold as fact | hard | ambiguous edge (borderline) | Surrogate-marker-to-outcome fallacy sold as fact; gold reviewed in Phase 4 (see note). |
| case046 | Coffee drinkers live longer, framed as coffee causing longevity | Biomedical | correlation_vs_causation | misleading (causal) | missing_confounders | observational (human) | association → causation + advice | medium | catches weak models | Classic coffee/longevity correlation-causation with advice. |
| case047 | 12-person pilot presented as proof a therapy works | Biomedical | overclaim | overclaim | missing_overclaim | limited human (pilot) | tiny uncontrolled pilot → proof | medium | catches weak models | 'Proved effective' from a 12-person uncontrolled pilot. |
| case048 | Tumour shrinkage framed as a survival benefit | Biomedical | overclaim | overclaim / ambiguous (borderline; alt: mechanism_vs_evidence) | missing_overclaim | surrogate endpoint (Ph2) | tumour response → survival, sold as fact | hard | ambiguous edge (borderline) | Response-rate-≠-survival sold as fact ('saves lives'); gold reviewed in Phase 4 (see note). |
| case049 | No serious adverse events framed as completely safe | Biomedical | overclaim | overclaim (safety) | missing_overclaim | limited human (safety) | no AEs → 'completely safe' | medium | catches weak models | Absence-of-evidence safety overclaim + unstudied groups. |
| case050 | 'Clinically proven' supplement on uncontrolled evidence | Biomedical | overclaim | overclaim | missing_overclaim | uncontrolled self-report | 'clinically proven' weak data | easy | catches weak models (easy) | Low-difficulty 'clinically proven' anchor. |
| case051 | Fairly communicated observational finding (positive control) | Biomedical | solid | cautious_supported | false_positive_overclaim | observational (human) | (none — fair) | medium | separates weak from strong | Positive control: fair, well-caveated association (must NOT over-flag). |
| case052 | Strong RCT communicated fairly (positive control) | Biomedical | solid | supported | false_positive_overclaim | clinical (RCT) | (none — fair) | easy | too easy for all but broken | Positive control: strong RCT, in-scope language. |
| case053 | 'Best in class' claim with no head-to-head comparison | Market/Comms | overclaim | misleading (comparative) | missing_overclaim | single-arm (device) | 'best in class', no head-to-head | medium | separates weak from strong | Superiority claim without any direct comparison. |
| case054 | 'May be comparable' hedging that implies equivalence | Market/Comms | overclaim | overclaim / ambiguous | accepting_hedged_overclaim | in-vitro dissolution | decorative hedge → equivalence | hard | hard / ambiguous edge (borderline) | 'May be comparable' hedge masking equivalence. |
| case055 | 'Long-term benefit' claimed from short follow-up | Market/Comms | overclaim | overclaim | missing_overclaim | limited human (short) | short follow-up → 'permanent' | medium | catches weak models | Durability claimed beyond the follow-up window. |
| case056 | Subgroup result generalised to everyone | Market/Comms | overclaim | misleading (subgroup) | missing_overclaim | post-hoc subgroup | subgroup → 'works for everyone' | medium | separates weak from strong | Subgroup overreach hiding a null primary. |
| case057 | '50% risk reduction' hiding a tiny absolute change | Market/Comms | overclaim | misleading (risk framing) | missing_overclaim | clinical (RCT framing) | relative RR hides absolute | medium | separates weak from strong | 50% RRR vs 2%→1% ARR — risk-arithmetic literacy. |
| case058 | 'AI beats doctors' from a narrow benchmark | AI/Technology | overclaim | overclaim | missing_overclaim | benchmark (vignettes) | benchmark → 'beats doctors' | medium | catches weak models | Narrow benchmark generalised to clinical readiness. |
| case059 | 'AI saves energy' ignoring compute lifecycle and rebound | AI/Technology | overclaim | overclaim / ambiguous | missing_overclaim | operational pilot | partial saving → net benefit | hard | hard / ambiguous edge (borderline) | Energy blind spot: lifecycle + rebound omitted. |
| case060 | Synthetic-benchmark success framed as real-world readiness | AI/Technology | overclaim | overclaim | missing_overclaim | simulation | sim success → real world | medium | catches weak models | Sim-to-real generalisation overclaim. |
| case061 | 'Fully autonomous agent' from scripted demo tasks | AI/Technology | overclaim | overclaim (contradicted) | missing_overclaim | scripted demo | scripted → 'fully autonomous' | medium | catches weak models | Autonomy claim contradicted by human-in-the-loop. |
| case062 | 'Green product' claim ignoring production and disposal | Environment/Policy | overclaim | misleading (greenwash) | missing_overclaim | use-phase LCA | use-phase → full lifecycle | medium | separates weak from strong | 'Carbon neutral' ignoring production/disposal. |
| case063 | 'Policy caused the improvement' without controlling confounders | Environment/Policy | correlation_vs_causation | misleading (causal) | missing_confounders | observational pre/post | pre/post → policy causation | medium | separates weak from strong | Policy causal claim with a concurrent confounder. |

## Difficulty & discrimination distribution (new cases)

Difficulty: easy=2, hard=5, medium=14.

gold_label: correlation_vs_causation=2, mechanism_vs_evidence=1, overclaim=16, solid=2.

The set is intentionally balanced toward realistic overclaim patterns while including two `solid` positive controls (case051, case052) to guard against over-flagging, plus five `borderline` ambiguous edge cases (case043, case045, case048, case054, case059).

## Curator rule — mechanism_vs_evidence vs overclaim boundary

When a biomedical claim has an evidence-tier gap (cell/animal/biomarker/surrogate → human outcome), decide the primary label by **how the conclusion is stated**:

- **Hedged / analytical tier-gap language → `mechanism_vs_evidence`.** The text presents a *possible mechanism*, *may / could*, *unknown in humans*, *would require clinical study* — it does not assert a clinical benefit as fact and recommends no reader action. Examples: case024, case028, case044.
- **Active clinical-benefit selling or reader-action recommendation → `overclaim`.** The text states a clinical benefit as fact ("treats cancer", "helps prevent heart attacks", "saves lives") or tells the reader to act, even though the evidence tier does not reach that conclusion. The rhetorical inflation is primary; the tier gap is secondary (preserve it as `gold_alternative_reading`). Examples: case043, case045, case048.

This mirrors the study-forensics prompt PRIORITY RULE and requires **no** change to prompts, scoring, or code — only correct gold labelling of fixtures.

### Phase 4 gold-review notes (live stability audit)

A Phase-4 live multi-run probe (Opus 4.5, 3 runs/case) surfaced that four synthetic Phase-3 mechanism fixtures were written with actively-selling language and were consistently classified as `overclaim`, while the pre-existing hedged mechanism cases (case024, case028) were correctly and stably classified as `mechanism_vs_evidence`. The issue was fixture wording, not the prompt/taxonomy. Actions taken:

- **case043** (was mechanism_vs_evidence, clear/high) → `overclaim`, borderline/medium. Text sells "treats cancer" / "natural alternative to chemotherapy" as fact (3/3 overclaim, conf 0.94).
- **case045** (was mechanism_vs_evidence, clear/high) → `overclaim`, borderline/medium. Text sells "helps prevent heart attacks" as fact (3/3 overclaim, conf 0.92).
- **case048** (was mechanism_vs_evidence, clear/high) → `overclaim`, borderline/medium. Text sells "extends survival" / "saves lives" as fact (3/3 overclaim, conf 0.92).
- **case044** (mechanism_vs_evidence, kept) → **reworded** to remove the flat "could prevent dementia" headline and the consumer dietary recommendation. NOTE: this first rewrite over-corrected (the full baseline read it as `solid`); it was re-balanced in Phase 4.1 — see below.

## Phase 4.1 — full 50-case baseline gold-review

First full single-run baseline (Opus 4.5, `--all --runs-per-case 1`): **46/50 = 92% label_correct**, with 50/50 successful runs, 0 parse failures, 0 truncation, 0 provider errors. The four initial misses were reviewed:

| Case | gold | detected | decision |
|---|---|---|---|
| case044 | mechanism_vs_evidence | solid | **Text re-balanced.** The Phase-4 rewrite over-hedged, removing all human-benefit reach, so the model read it as fair reporting. Phase 4.1 re-added a hedged, forward-looking human-benefit reach (mirroring the live-validated case024/case028) so the animal-to-human tier gap is visible again as `mechanism_vs_evidence`. Kept clear/high; a live re-check is recommended. |
| case040 | overclaim | correlation_vs_causation | Marked borderline in 4.1; **primary label flipped in Phase 4.2** — see below. |
| case042 | overclaim | solid | **Marked borderline (medium).** No text change (real arXiv-sourced case). The surrounding text is a careful analytical paper that critiques the industry positioning, so a fair-reporting `solid` reading is defensible; overclaim kept primary because the central claim under evaluation ("is ready…") overextends. |
| case054 | overclaim (borderline) | mechanism_vs_evidence | **Left unchanged.** Already borderline; the in-vitro-dissolution → clinical-equivalence tier gap makes `mechanism_vs_evidence` a legitimate alternative reading. Documented as a known borderline case. |

Net effect of Phase 4.1: no primary-label changes; case040 and case042 moved `clear → borderline`; case044 text re-balanced (label unchanged).

### Phase 4.2 — case040 curator-quality review (primary label flipped)

A targeted 3-run re-check confirmed the three remaining borderline candidates are **stable on their documented alternative reading**: case040 → correlation_vs_causation ×3 (conf 0.92), case042 → solid ×3 (conf 0.84), case054 → mechanism_vs_evidence ×3 (conf 0.91). A curator-quality review of case040 concluded:

- **case040 → primary label flipped `overclaim` → `correlation_vs_causation` (clear/high), text unchanged.** The claim (an uncontrolled pre/post employment gain attributed causally to the program) maps most cleanly to correlation_vs_causation: a causal claim from a confounded, non-experimental design. The case's own curator note already described the error as "structural (absence of comparison arm), not rhetorical." overclaim is retained as the documented secondary/alternative reading. The case is kept because the missing-counterfactual pattern is a valuable, distinct forensic lesson — only the original label mapping was wrong, not the case.
- **case042 kept** as a documented borderline (overclaim primary, solid alternative). It is a hard but legitimate discriminator (distinguishing the evaluated industry claim from the surrounding analytical paper) sourced from a real arXiv paper; not removed. Flagged as a future-replacement candidate only if it keeps scoring as a stable miss.
- **case054 kept** unchanged as a documented borderline (overclaim primary, mechanism alternative). Productive ambiguity testing decorative-hedge detection.

Overall 50-case gold distribution after Phase 4.2: overclaim=24, solid=14, mechanism_vs_evidence=6, correlation_vs_causation=6. Case count unchanged (50). No scoring, prompt, parser, provider, judge, harness, or Python changes.

Each borderline overclaim case preserves the tier-gap reading as `gold_alternative_reading`. No scoring, prompt, parser, provider, judge, or harness logic was changed.

## Source integrity

- All Phase-3 cases are **synthetic fixtures** (marked in `origin` and in `curator_notes`). No real citations, journals, brands, or people are named.
- Pre-existing cases (e.g. case041 GLP-1, case042 edge-AI) that reference real public reports keep their own source metadata; they are unchanged in this phase.
- No test in this phase requires live web or API access.
