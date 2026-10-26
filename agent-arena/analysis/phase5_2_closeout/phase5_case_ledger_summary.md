# Phase 5 — Case Ledger Summary (aggregate; approved committed records only)

| metric | value |
|--------|-------|
| total known canonical cases | 50 |
| active cases | 48 |
| retired cases | 2 |
| development-only cases | 1 |
| holdout-ineligible cases (retired ∪ development-only) | 3 |
| unique approved BIAA identifiers | 23 (20 original + 3 Phase 5.1a additions) |

## Approved packet-version exceptions
- **BIAA-013_v3** (latest approved version; claim-isolation remediation, final revalidation passed).
- **BIAA-016_v2** (latest approved version; claim-isolation remediation, revalidation passed).

## Phase 5.1a additions (approved holdout candidates)
- **BIAA-021_v1**, **BIAA-022_v1**, **BIAA-023_v1** (1 correlation_vs_causation + 2 mechanism_vs_evidence).

## Approved eligible-pool counts before holdout selection
- solid: 5 · overclaim: 8 · correlation_vs_causation: 4 · mechanism_vs_evidence: 4.

## Holdout allocation
- Four per label · sixteen total.

**Not disclosed:** which canonical cases or BIAA packets entered the holdout, the HLD-to-source
mapping, or per-HLD gold labels (sealed outside Git). All aggregate counts match the approved
records.
