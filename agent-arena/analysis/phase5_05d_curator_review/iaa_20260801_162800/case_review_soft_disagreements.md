# Phase 5.05d — Soft-Disagreement Case Review (anonymized)

Read-only. No annotation, gold label, packet, or taxonomy was changed. Rater identities
are anonymized (Rater 1–4); the rater→model mapping lives only in
`internal_rater_mapping.json`.

**Cross-cutting observation.** In all three soft cases the *single* dissenting primary
label comes from the **same rater (Rater 3)**, and in each case **Rater 3's secondary
label equals the gold label**. The other three raters agree with gold. So these are not
categorical misses: they are a consistent **primary↔secondary ordering** difference on
genuinely two-sided cases. This is exactly the "soft, alternative-reading" pattern the
committed analyzer is designed to route to review rather than to adjudication.

---

## BIAA-003 — gold: `overclaim` (sample_reason: "clear overclaim — anchor")
Primary labels: Rater 1 `overclaim` (0.68) · Rater 2 `overclaim` (0.80) · **Rater 3
`solid`/sec `overclaim` (0.85)** · Rater 4 `overclaim` (0.85).

1. **Exact public claim:** the lead investigator is "already convinced" the app helps and
   suggests it "might benefit people of all ages."
2. **Evidence tier:** a wait-list crossover RCT in 89 autistic adults with replication and
   6-week persistence — solid *for the studied population*.
3. **Strongest applicable trigger:** `overclaim` — extrapolation to a population not
   studied ("all ages") plus conviction-as-evidence.
4. **Why gold takes precedence:** the documented gold rationale isolates the *interpretive*
   overclaim (generalisation beyond the sample), not the methodology; the method being
   sound is precisely why the failure is framing, i.e. `overclaim`.
5. **Strongest alternative argument (Rater 3):** the *study itself* is solid, so one could
   score the case on the methodology and treat the "all ages" line as a marginal aside →
   `solid` primary, `overclaim` secondary.
6. **Alternative reading:** *plausible but secondary.* Gold's own alternative-reading note
   calls the alternative "weak"; the explicit "all ages" generalisation is textbook.
7. **Cause of disagreement:** taxonomy boundary (methodology-vs-interpretation): does the
   label attach to the study or to the investigator's statement?
8. **Clear/borderline defensible?** The "clear — anchor" tag is *defensible but slightly
   optimistic*: a capable independent rater read it as solid. Recommend **mark borderline**.
9. **Shortcut evidence?** None. Rater 3's reasoning is substantive, not lexical.
10. **Action to consider:** retain gold; **retain-but-mark-borderline** + **clarify gold
    rationale** (state explicitly that the label attaches to the investigator's claim).

## BIAA-007 — gold: `overclaim` (sample_reason: "borderline overclaim (high amb) — mechanism-vs-overclaim boundary")
Primary: Rater 1 `overclaim`/sec `mechanism_vs_evidence` (0.60) · Rater 2 same (0.60) ·
**Rater 3 `mechanism_vs_evidence`/sec `overclaim` (0.95)** · Rater 4 `overclaim` (0.95).

1. **Exact public claim:** Compound X "treats cancer" and could be a "natural alternative
   to chemotherapy," from 90% tumour-cell kill in a petri dish.
2. **Evidence tier:** in-vitro cytotoxicity only; no animal or human data.
3. **Strongest applicable trigger:** genuinely two triggers — an evidence-tier gap
   (cell→human) and rhetorical inflation ("treats cancer" as fact).
4. **Why gold takes precedence:** the documented gold applies the project priority rule —
   the text *actively sells* clinical benefit in unhedged promotional language, so
   `overclaim` is primary and the tier gap is secondary; canonical
   `mechanism_vs_evidence` fixtures instead *hedge* ("could"/"suggested").
5. **Strongest alternative (Rater 3):** the deep problem is *where the evidence comes
   from* (a dish, not a patient); read "treats cancer" as shorthand for the implied
   conclusion and `mechanism_vs_evidence` becomes primary.
6. **Alternative reading:** *equally plausible.* The gold's own alternative-reading note
   calls this "borderline" and defensible — the strongest of the three soft cases.
7. **Cause of disagreement:** taxonomy boundary (promotional-inflation vs evidence-tier
   gap) — a definitional precedence question, not an error.
8. **Clear/borderline defensible?** Yes — correctly tagged high-ambiguity/hard.
9. **Shortcut evidence?** None. Note the two high-confidence raters split *opposite ways*
   (one each side), which argues against any shared lexical cue.
10. **Action to consider:** retain gold; **add taxonomy precedence note** (unhedged
    marketing ⇒ overclaim primary) + **request independent human review** (true 50/50).

## BIAA-016 — gold: `overclaim` (sample_reason: "borderline overclaim — review-sensitive")
Primary: Rater 1 `overclaim`/sec `correlation_vs_causation` (0.70) · Rater 2 same (0.85) ·
**Rater 3 `correlation_vs_causation`/sec `overclaim` (0.90)** · Rater 4 `overclaim`/sec
`correlation_vs_causation` (0.85).

1. **Exact public claim:** the company declares the app could "revolutionize mental health
   care" and "replace clinical therapies," from a 2-week, 15-person uncontrolled pilot.
2. **Evidence tier:** tiny uncontrolled before/after, self-reported, no control arm.
3. **Strongest applicable trigger:** grandiose extrapolation (`overclaim`) with a genuine
   uncontrolled-design flaw (`correlation_vs_causation`) underneath.
4. **Why gold takes precedence:** gold identifies the *core* error as exaggerated
   generalisation of early results (`overclaim`); the missing control group is real but
   secondary to the rhetorical leap.
5. **Strongest alternative (Rater 3):** the causal-inference defect (no counterfactual) is
   the structural root → `correlation_vs_causation` primary.
6. **Alternative reading:** *plausible but secondary.* Three of four raters put `overclaim`
   primary with `correlation_vs_causation` secondary — the ordering the gold prefers.
7. **Cause of disagreement:** taxonomy boundary (rhetorical inflation vs design flaw) +
   a claim-isolation load (company claim vs embedded university critique).
8. **Clear/borderline defensible?** Yes — correctly tagged borderline/review-sensitive.
9. **Shortcut evidence?** None.
10. **Action to consider:** retain gold; **retain-but-mark-borderline** + **revise packet
    wording** to isolate the company claim from the critique.

---

### Summary of proposed actions (none executed)
| case | disposition |
|------|-------------|
| BIAA-003 | retain gold · mark borderline · clarify gold rationale |
| BIAA-007 | retain gold · add taxonomy precedence note · request independent human review |
| BIAA-016 | retain gold · mark borderline · revise packet wording (isolate claim) |

No case reaches "reconsider gold label": in every case the dissenter's *secondary* is the
gold, and 3/4 raters reproduce gold as primary.
