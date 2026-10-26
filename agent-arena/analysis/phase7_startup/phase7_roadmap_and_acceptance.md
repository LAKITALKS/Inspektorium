# Phase 7 — Schema Deltas, Roadmap, Acceptance, First Slice (STEP 5–8)

## STEP 5 — Minimal schema deltas (proposed)

> **Curator governance update (first slice).** The 6.3.0 forensic-report contract is **NOT
> bumped** by the first vertical slice. The slice adds a **separate, additive** `ForensicRecord`
> QA contract (`FORENSIC_RECORD_SCHEMA_VERSION = "0.1.0"`, `schemas.py`) for the CLAIM→PROVENANCE→
> EVIDENCE→FINDING→CLIENT-FINDING chain — the frozen 6.3.0 report stays byte-compatible (zero
> migration). The full §5.1–§5.8 field set below (and any eventual `6.3.0 → 6.4.0` bump of the
> report itself) remains a **later** 7B work package, not this slice. Fields required for the QA
> gate are mandatory in the new QA path but the historical report contract is unchanged.

The natural home for later report-side deltas is the existing report contract
(`analysis/phase6_3_report_prototype/forensic_report_schema.json` + `src/agent_arena/forensic_report.py`).
If/when bumped, every addition stays **optional** and back-compatible: all current 6.3.0 fixtures
must still validate unchanged. No parallel reporting architecture; no universal ontology.

### 5.1 `claim.provenance` (immutable web-claim provenance)
```
claim.provenance = {
  canonical_url, page_title, retrieved_at,           # capture identity
  exact_span, context_before, context_after,          # the quoted claim, in situ
  content_fingerprint,                                # sha256 via existing canonical-bytes
  snapshot_reference,                                 # archived copy pointer (opaque id/path-free)
  provenance_state ∈ {archived_snapshot, current_live, modelled, published_literature},
  footnote_marker?, linked_source_ids?                # optional citation linkage
}
```
Rules: frozen at capture; downstream objects reference it, never re-derive it; live and snapshot
are **separate states**, never overwritten silently. `claim.claim_source_reference` stays for
back-compat. No absolute paths / private ids (existing leak scan applies).

### 5.2 `evidence.search_scope` + negative-evidence lattice
```
evidence.search_scope = { scope_id, sources_reviewed[], queries[], date_cutoff,
                          completeness ∈ {single_source, reviewed_set, documented_search} }
# per negative/absence assertion:
negative_evidence_level ∈ { A_cited_source_absent, B_not_in_reviewed,
                            C_not_in_documented_search, D_does_not_exist }
```
Validator: a negative existence assertion requires a level; **D is rejected** unless an explicit
`evidence_of_absence` justification is attached. Absence in scope never auto-promotes to D.

### 5.3 Evidence ids + resolve-check
`evidence.evidence_items[].evidence_id` (optional string). When any id is present, every
`failure_modes.detected[].evidence_refs` and every `client_finding` evidence ref must resolve to
a declared `evidence_id`, else validation error. (No behavior change when ids are absent.)

### 5.4 `evidence.source_symmetry` (omission audit)
```
evidence.source_symmetry[] = { source_ref, categories_considered: {
   favorable, unfavorable, null_findings, mixed, limitations, subgroup,
   author_conclusion, adverse_events, alternative_explanations } }   # each: present|absent|n_a + note
```
Not every category must be populated; the *material* ones must be considered. Contract test: if a
source contributes a weakening/contradictory item, materially relevant favorable items from the
**same** source must also appear (and vice versa).

### 5.5 Client finding + semantic monotonicity
```
verdict.allowed_summary_strength ∈ STRENGTH_LATTICE
client_finding = { display_claim, client_verdict, client_explanation, finding_id }   # bound to parent
STRENGTH_LATTICE (ordered, weak→strong):
  not_assessed < not_directly_established < limited_support < mixed
              < not_supported < contradicted < disproven
```
Validator: `strength(client_finding) ≤ allowed_summary_strength(parent)`. Evidence-strength and
search-certainty are **separate dimensions** — a strong search result does not raise evidence
strength. No new scientific proposition may appear in a `client_finding` that is absent from its
parent finding.

### 5.6 `system_qa` (deduped, separate from the 4 labels)
```
system_qa.checks[] = { code ∈ {provenance_drift, search_scope_generalization,
                               compression_overclaim, artifact_source_binding_drift,
                               asymmetric_evidence_selection},
                       severity ∈ {BLOCKER, MAJOR, MINOR}, detail }
```

### 5.7 `artifact_binding_check` (final gate)
```
artifact_binding_check = { findings[]{ check ∈ {A..G}, severity, detail },
                           release_status ∈ {releasable, blocked} }
release_status = releasable  ⇔  BLOCKER == 0 AND MAJOR == 0
```
Checks A–G (brief §17): A exact quotations · B correct provenance/URL · C source actually the one
analyzed · D DOI/PMID/title correct · E every central client statement traces to a finding id ·
F rendering introduced no new proposition · G client wording ≤ parent strength.

### 5.8 `self_audit` (one structured pass, not 10 agents)
```
self_audit = { steelman, prosecution, critic_overreach_check,
               failed_criticisms[], remaining_uncertainties[] }
```
Optional; operationalizes symmetric skepticism. Reuses `uncertainty.alternative_plausible_label`.

## STEP 6 — Updated Phase-7 roadmap (fits existing convention)

Convention observed: `analysis/phaseN_*` dirs + annotated `vX.Y.Z-<slug>` tags + separate
prep/result checkpoints + hashed contracts. Phase 7 keeps this. **Two tracks, no renumbering of
prior phases.** Title: **Phase 7 — End-to-End Forensic Robustness.**

**7A — Analysis robustness** (original handoff, preserved):
- 7A.1 Boundary cases (overclaim vs correlation / vs mechanism; multi-mode; primary-label prioritization) — pre-registered labels.
- 7A.2 Perturbation robustness (label-preserving) — pre-registered families + invariant.
- 7A.3 Adversarial robustness — families mapped to the attacked label.
- 7A.4 Replication / stability — **freeze count (3–5) before run**; deterministic aggregation + disagreement reporting.
- 7A.5 Difficulty / ceiling — nominate harder cases *separately*; no result-driven retirement/relabel.
- 7A.6 Governance efficiency — consolidate to one machine report + one human report + one audit manifest + one generator (reuse `audit_trail`).

**7B — Artifact / representation robustness** (pilot-driven; matches brief P7.0–P7.8):
- 7B.0 Real-world pilot postmortem — **done this session** (`real_world_pilot_postmortem.md`).
- 7B.1 Failure/control mapping — **done this session** (`existing_control_inventory.md`).
- 7B.2 Minimal ForensicRecord contract extension — §5.1, §5.3, §5.5 (provenance + ids + parent/child binding); schema `6.4.0`.
- 7B.3 Search-scope gate — §5.2.
- 7B.4 Evidence symmetry / omission check — §5.4.
- 7B.5 Client-summary binding + semantic monotonicity — §5.5.
- 7B.6 Final artifact binding check + severity freeze — §5.7.
- 7B.7 **Pipeline QA regression suite** — R1–R8 as sanitized synthetic **pipeline-QA
  fixtures** (data class C). These are never case-library / benchmark / robustness-pool cases
  and never enter model-performance statistics.
- 7B.8 Release gate — BLOCKER=0 ∧ MAJOR=0.

Sequencing: 7B.2 → 7B.3/7B.4/7B.5 (parallel, each a small contract) → 7B.6 → 7B.7 → 7B.8. 7A runs
independently and may interleave; its results feed no 7B gate. **Report-engineering for later
phases stays out**; Phase 7 encodes only the QA contract that prevents the observed failures.

## STEP 7 — Acceptance-test design (kept in separate suites; not one score)

| suite | scope | examples |
|---|---|---|
| **unit** | pure helpers | strength-lattice ordering; `provenance_state` enum; negative-level parser; fingerprint determinism |
| **contract** | schema `6.4.0` back-compat + new validators | every 6.3.0 fixture still validates; D-level rejected without evidence-of-absence; unresolved `evidence_ref` fails; monotonicity `client ≤ parent`; symmetry (same-source both directions) |
| **regression (7B)** | the 8 documented real-world behaviors, explicit | R1 provenance · R2 search language · R3 Fantacone symmetry · R4 claim binding · R5 summary strength · R6 product bridge · R7 modelled value · R8 "all values" compression |
| **artifact-QA** | the final binding gate | A–G checks; release_status truth table; BLOCKER/MAJOR → blocked |
| **7A robustness** | analysis-layer stability (kept separate) | boundary-label prioritization; perturbation label-preservation; adversarial hold; replication stability + disagreement structure |
| **manual controls** | not auto-decided | curator sign-off on Level-3 actions; harder-case nomination; human-validation objective (7b) frozen *before* data |

7A robustness metrics and 7B regression pass/fail are **not** merged into one undifferentiated
number. Replication frequency (7A.4) is never reported as a calibrated correctness probability.

## STEP 8 — First vertical slice (design only; do not implement yet)

**Chain to prove:** `FROZEN CLAIM → FROZEN PROVENANCE → EVIDENCE ITEM → INTERNAL FINDING →
CLIENT FINDING → FINAL BINDING CHECK`.

**Chosen case: R3 — Fantacone evidence symmetry (from LaVita Case 03, isolated).**

*Why this case (clearest architecture signal, least fixture complexity):*
- It exercises **every link** of the chain substantively with the **fewest** fixtures — a single
  public source (one RCT) carrying **two** evidence items (one null/measured, one favorable/
  self-reported). Contrast: R7 (modelled value) is lower-complexity but exercises mainly the
  provenance link and one gate; it is the recommended **second** slice to isolate `provenance_state`.
- It proves the **most distinctive Agent-Arena principle** — symmetric skepticism (§23): our
  criticism is held to the same evidence rules as the company claim.
- It is fully **synthesizable from public facts** (Fantacone is a public RCT) with **no** client
  material — satisfying the data-safety boundary.
- Its failure mode (asymmetric selection) is the one controlled benchmarks under-surfaced, so it
  gives the highest robustness signal per unit of work.

**Slice objects (synthetic, public-derived):**
- **Claim (frozen):** a product immune-benefit claim leaning on the RCT.
- **Provenance (frozen):** `provenance_state = published_literature`, `content_fingerprint`, exact
  span of the cited result.
- **Evidence items:** `E1` — measured immune-function endpoints, non-significant (`role=weakening`
  for the company claim; **must remain visible** in our critical report); `E2` — self-reported
  illness-duration/severity, favorable (`role=…`; **must not be omitted** because it is
  inconvenient for our criticism).
- **Internal finding:** verdict on the company claim with **both** E1 and E2 bound; predicted
  claim label unchanged by this slice (label taxonomy untouched); `allowed_summary_strength` set.
- **Client finding:** `display_claim` + `client_explanation` that preserves both directions;
  strength ≤ parent.
- **Final binding check:** run A–G; specifically `source_symmetry` + `asymmetric_evidence_selection`.

**Pass/fail conditions:**
- PASS: both E1 and E2 survive into the client finding; `client ≤ parent` strength; A–G clean →
  `release_status = releasable` (BLOCKER=0, MAJOR=0).
- FAIL (must be caught, not shipped): a variant fixture that drops E2 (or E1) → symmetry check
  fires `asymmetric_evidence_selection = BLOCKER` → `release_status = blocked`. A variant that
  escalates client wording above parent strength → `compression_overclaim = BLOCKER`.

**Scope discipline:** the slice implements only what R3 needs (§5.1 provenance minimal, §5.4
symmetry, §5.5 monotonicity, §5.7 gate for A/E/F/G). It does **not** build search-scope,
adversarial suites, or the client PDF renderer. One case, one clean end-to-end proof.
