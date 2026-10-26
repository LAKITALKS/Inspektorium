# Phase 5.05d Curator Decision

- **Decision date:** 2026-08-01
- **Approved disposition:** B — STRONG, MINOR CURATION REQUIRED FIRST
- **Proxy-IAA study type:** strongly anonymized model-assisted proxy IAA
- **Human IAA completed:** no
- **Holdout frozen:** no
- **Taxonomy revision required:** no
- **Gold-label changes approved:** no

This record ratifies the Phase 5.05d curator review of run `iaa_20260801_162800`. It is an
archival decision only; no remediation is executed here.

## Approved future remediation targets (not yet executed)

### 1. BIAA-013
- revise packet construction
- remove embedded analysis instruction
- normalize packet structure (align to the neutral fixture template)
- exclude from holdout until revalidated

### 2. BIAA-016
- isolate the exact evaluated claim
- mark as borderline
- revalidate the revised packet

### 3. BIAA-019
- clarify source voice
- determine whether revision is sufficient or retirement is required
- exclude from holdout until resolved

### 4. BIAA-003
- retain gold label
- change review designation from clear/anchor to borderline
- clarify gold rationale

### 5. BIAA-007
- retain gold label
- add taxonomy-precedence explanation
- request independent human review before holdout eligibility

### 6. Model-capability note
- Annotator C's three primary disagreements all retained the gold label as **secondary**.
- This is consistent with label-ranking or taxonomy-precedence differences.
- Model tier, inference mode, and reasoning budget are possible moderators.
- No causal conclusion is established.
- Annotator C remains **fully included** in all reported metrics.

## Standing constraints
- No remediation was executed in Phase 5.05d.
- Historical Phase 5.05c and Phase 5.05d artifacts must remain **immutable**.
- Revised packets must later be **versioned** and must **not** silently overwrite the
  packets used in the original blind run.
- **No holdout preparation may begin** until the approved remediation and targeted
  revalidation are complete.
