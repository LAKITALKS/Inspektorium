# ASA 25/261 — PREMIUM GROUNDING · AGENT ARENA RUN 001 — CONSISTENCY CHECK

**Case:** ASA_25_261_PREMIUM_GROUNDING · **Run:** run_001 · **Date:** 2026-08-23
**Input freeze SHA-256:** `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069`
**Model:** claude-opus-5 · **Research:** CLOSED · **Evidence cut-off:** 2026-08-22

## Cross-proposition consistency

| Check | Status | Observed |
|---|---|---|
| M-01a / M-01b separation preserved | **PASS** | M-01a=QUALIFIED/limited_support; M-01b=UNSUPPORTED/not_directly_established |
| Downstream mechanism does not assume M-01b | **PASS** | M-02=UNSUPPORTED; M-03=UNSUPPORTED |
| X-01 does not assume immune benefit | **PASS** | I-02=UNSUPPORTED; X-01=UNSUPPORTED |
| X-01 does not represent sleep as uniformly established | **PASS** | S-01 strength=mixed; X-01=UNSUPPORTED |
| E-03 preserves GROUNDING COMPONENT NOT ISOLABLE | **PASS** | VERY LIMITED DIRECT EVIDENCE — GROUNDING COMPONENT NOT ISOLABLE |
| No exact-product verdict assumes study-product identity | **PASS** | SOLID verdicts=0 |
| Q-01 / Q-02 not adjudicated on biomedical absence | **PASS** | Q-01=OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION REQUIRED; Q-02=OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION REQUIRED |
| Bounded negative search routed only where documented | **PASS** | scoped=['E-02', 'I-02', 'P-02', 'P-05', 'V-01'] |
| Overlapping cohorts not counted as independent replications | **PASS** | collapse noted in I-01, C-01, E-01 |
| Within-group significance not converted to between-group effect | **PASS** | explicit block recorded in I-02 |
| H31 exact p-value preserved | **PASS** | p=.010511 recorded; CK p=.534106 recorded |
| H30 actigraphy timepoint left unresolved | **PASS** | conflict preserved unresolved in S-01 |
| H10 2.70 not read as a health improvement | **PASS** | recorded as zeta-potential magnitude ratio in C-01 |
| Verdicts not derived mechanically from preparation state | **PASS** | NO MATERIAL DIRECT EVIDENCE LOCATED maps to UNSUPPORTED and to OUTSIDE BIOMEDICAL SCOPE; SOME DIRECT EVIDENCE LOCATED maps to QUALIFIED for both M-01a and P-01 on different grounds |
| ASA outcome quarantined | **PASS** | no proposition cites the ASA outcome as evidence |

### Requirements in full

- **M-01a / M-01b separation preserved** — Evidence for M-01a must not be counted as evidence for M-01b; the two must not share a verdict. → **PASS**
- **Downstream mechanism does not assume M-01b** — If M-01b is not established, M-02 and M-03 free-radical reasoning must not silently assume it as proven. → **PASS**
- **X-01 does not assume immune benefit** — If I-02 lacks functional immune evidence, X-01 must not silently assume immune benefit. → **PASS**
- **X-01 does not represent sleep as uniformly established** — If S-01 is mixed, X-01 must not represent sleep as uniformly established without additional reasoning. → **PASS**
- **E-03 preserves GROUNDING COMPONENT NOT ISOLABLE** — E-03 relies on H33 and must carry the mandatory qualifier; it must never revert to NO MATERIAL DIRECT EVIDENCE LOCATED. → **PASS**
- **No exact-product verdict assumes study-product identity** — Product equivalence is uncertain across all propositions, so no verdict may silently assume study-product identity. → **PASS**
- **Q-01 / Q-02 not adjudicated on biomedical absence** — Absent biomedical literature must not be treated as evidence against a commercial proposition. → **PASS**
- **Bounded negative search routed only where documented** — Only the five propositions with documented proposition-specific negative-search work may carry a search-scope basis; M-01b must not. → **PASS**
- **Overlapping cohorts not counted as independent replications** — H03/H04, H13/H14/H15 and H21/H22 must be collapsed to one evidence line each. → **PASS**
- **Within-group significance not converted to between-group effect** — H34's differing within-group p-values must not be read as a between-group effect. → **PASS**
- **H31 exact p-value preserved** — P-01 must record p=.010511, not the historical p<.01. → **PASS**
- **H30 actigraphy timepoint left unresolved** — The day-31 / day-38 conflict must not be resolved by inference. → **PASS**
- **H10 2.70 not read as a health improvement** — The 2.70 figure is a zeta-potential magnitude ratio. → **PASS**
- **Verdicts not derived mechanically from preparation state** — Propositions sharing an evidence-preparation state must not all receive the same verdict. → **PASS**
- **ASA outcome quarantined** — No verdict may derive from or be calibrated to the ASA outcome. → **PASS**

---

## Deterministic representation gate (Phase-7B 0.1.0)

Record fingerprint: `98bb2eec89f6247d9ad5fb6860654377c034d619e66177b8da778c91aa8a97e0`

| Mandatory control | Status | Findings |
|---|---|---|
| `finding_artifact_binding` | ran | 0 |
| `summary_strength_monotonicity` | ran | 0 |
| `evidence_symmetry` | ran | 0 |
| `value_origin_provenance` | ran | 0 |
| `search_scope_binding` | ran | 0 |

**Releasable:** True — no blocking (critical/major) QA findings


> A gate PASS means the structured artifact satisfies the implemented representation-QA contract. It does **not** certify scientific truth, source quality, literature exhaustiveness or causal validity.

---

## Uncertainty calibration audit

`UNCERTAIN` was considered for every proposition and assigned to none. It is reserved for irreducible ambiguity that prevents a determination, and is not used to avoid a difficult judgment. The specific distinctions actually drawn were:

| Situation | Propositions | Recorded as |
|---|---|---|
| No evidence located, after documented proposition-specific negative search | P-02, P-05, V-01, E-02, I-02 | UNSUPPORTED with `documented_search` scope |
| Required direct endpoint never measured | M-01b | UNSUPPORTED — explicitly *not* a bounded negative search |
| Mechanistic / preclinical only | M-02, M-03 | UNSUPPORTED with the ex-vivo signal preserved |
| Weak or single-study evidence | S-04, P-03, P-04 | OVERCLAIM on evidence quality |
| Surrogate endpoint only | I-01, C-01 | OVERCLAIM on tier mismatch |
| Genuinely mixed evidence | S-01, S-03, E-01, R-01 | strength `mixed`; verdict adjudicated separately — MIXED does **not** mechanically equal UNCERTAIN |
| Non-operationalisable wording | W-01 | UNSUPPORTED — the claim admits no endpoint, so the world-state is not what is unknown |
| Undefined comparator | X-02 | UNSUPPORTED |
| Product-transfer uncertainty | all 24 biomedical | mandatory qualifier on every verdict; blocks any SOLID |
| Outside biomedical scope | Q-01, Q-02 | routed; `not_assessed`, null label |
