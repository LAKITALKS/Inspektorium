# BIAA-007 — Case Decision

**Approved actions:** retain gold · add taxonomy-precedence explanation · request
independent human review before holdout eligibility.

**Implemented (source YAML, rationale only):**
- `gold_justification`: appended an explicit precedence explanation — under the precedence
  rule a specific label (`mechanism_vs_evidence`) outranks generic `overclaim` only when
  its trigger captures the core error; here the core error is an *unhedged* promotional
  assertion of a clinical outcome stated as fact, so `overclaim` is primary and the
  cell-to-human tier-gap reading is retained as the documented secondary. The mechanism
  reading is plausible but does not outrank the current gold.
- `curator_notes`: recorded that the case is **holdout-ineligible** until an independent
  human review is completed, and that **no such review has occurred yet**.

**Human-review request:** created at
`human_review/BIAA-007_independent_human_review_request.md` — blind (no gold, no model
votes, no model names, no desired answer; both candidate labels presented neutrally).

**Not changed:** gold_label (`overclaim`), public claim, evidence, taxonomy. **No revised
packet** (the packet wording is not defective; the case is a genuine boundary).

**Holdout eligibility:** ineligible until the independent human review is completed.
