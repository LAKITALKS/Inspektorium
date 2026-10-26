# Phase 5.05d — Curator Recommendations

Read-only review of run `iaa_20260801_162800`. Nothing was changed or committed. No
holdout frozen. All actions below **require explicit curator approval** before execution.

## Final Phase-5.05d disposition

### **B. STRONG — MINOR CURATION REQUIRED FIRST**

**Basis (multi-signal, no single statistic):**
- **Taxonomy clarity:** high on clear/anchor cases; the only friction is the two known
  definitional boundaries (mechanism-vs-overclaim, corr-vs-overclaim), handled correctly
  via secondary labels.
- **Soft cases (003/007/016):** all **retain gold**; in each the lone dissenter's secondary
  equals gold. None warrants a gold flip. BIAA-007 is a genuine ~50/50 boundary.
- **Source-voice / claim-isolation:** 6 minor, 2 material (BIAA-016, BIAA-019), 1 unsuitable
  without revision (BIAA-013). None changes a primary gold label.
- **Shortcut audit:** no demonstrated leakage; one packet-construction defect (BIAA-013).
- **Perfect-gold pattern:** strong but **not** independent validation — material caution
  from model-assisted gold co-evolution; recommend an out-of-loop check.
- **Sensitivity stability:** swapping the primary triad rater (Rater 1 → Rater 2) changed
  nothing (identical labels, identical Fleiss 0.8568, zero consensus changes).
- **Serious disagreements:** **0**.

Agreement is strong and stable and no taxonomy revision or serious-disagreement cluster
exists, so this is **not** MODERATE/WEAK. But three concrete curation items (one packet
defect + material ambiguities + the gold-independence caveat) must be resolved before a
holdout freeze, so this is **not** "A — ready for freeze" either.

## Proposed actions (require curator approval; none executed)

**Packet / fixture**
1. **BIAA-013 — revise packet wording (priority):** remove the embedded analysis
   instruction that names all four taxonomy terms; normalise to the neutral template and
   heading structure; reduce length. Re-annotate after revision.
2. **BIAA-016 — revise packet wording:** separate the company claim from the embedded
   university critique so exactly one claim is isolated.
3. **BIAA-019 — clarify source voice:** make explicit whose claim is under evaluation
   (enthusiast implicit claim vs expert caution), or retire if it cannot be isolated.

**Gold rationale / taxonomy notes (no label changes)**
4. **BIAA-003 — clarify gold rationale** and **mark borderline** (label attaches to the
   investigator's "all ages" statement, not the methodology).
5. **BIAA-007 — add taxonomy precedence note** (unhedged promotional "treats cancer" ⇒
   `overclaim` primary; hedged mechanism language ⇒ `mechanism_vs_evidence`) and
   **request independent human review** (true boundary case).
6. **BIAA-016 — mark borderline** in sample metadata.

**Validity**
7. **Out-of-loop validation:** obtain labels for the same 20 from a human expert (or a
   non-LM baseline) *outside* the gold-curation loop, to test the perfect-gold pattern for
   circularity before any validity claim.

**Holdout suitability**
8. Do **not** admit BIAA-013 (and, until revised, BIAA-016/019) into a holdout set as-is.

## Explicitly NOT recommended
- No gold-label change on any case (no case crossed the "reconsider gold" threshold).
- No taxonomy revision.
- No holdout freeze in this phase.
- No adjudication by majority vote.

**Disposition label:** STRONG — MINOR CURATION REQUIRED FIRST · **PROVISIONAL, awaiting
curator decision.**
