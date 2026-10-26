# BIAA-003 — Case Decision

**Approved actions:** retain gold · re-designate borderline · clarify gold rationale.

**Authoritative designation source:** the case YAML field `gold_case_type` (was `clear`)
plus `ambiguity_level` (was `medium`); the historical `blind_case_index.csv` sample_reason
("clear overclaim — anchor") is left unchanged as run provenance.

**Implemented (source YAML, metadata/rationale only):**
- `gold_case_type`: `clear` → `borderline`
- `ambiguity_level`: `medium` → `high`
- `gold_justification`: appended a precedence clarification — the label attaches to the
  investigator's claim (explicit "all ages" extrapolation ⇒ `overclaim`, no specific
  trigger applies); the `solid` reading is plausible but secondary because it must
  discount an explicit generalization.
- `curator_notes`: recorded the Phase 5.05e re-designation and its reason.

**Not changed:** gold_label (`overclaim`), public claim (`prompt`), evidence (`context`),
taxonomy. **No revised packet** (no packet-visible wording changed).

**Holdout eligibility:** eligible after standard process (no packet defect); no targeted
revalidation required beyond the existing blind annotation.
