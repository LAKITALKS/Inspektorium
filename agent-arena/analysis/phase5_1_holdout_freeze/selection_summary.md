# Phase 5.1 — Selection Summary (aggregate; no case identities)

- **Algorithm:** holdout_select_v1
- **Seed (original, unchanged):** `agentarena-phase5.1-holdout-v1|f8efe474d3068b7fbc4d149d9be1816b12b1e9cd`
- **Target size:** 16 · **Selected:** 16 · **Exactly four per label:** yes.

## Aggregate selected distribution
| dimension | distribution |
|-----------|--------------|
| gold label | solid 4 · overclaim 4 · correlation_vs_causation 4 · mechanism_vs_evidence 4 |
| source domain | study_forensics 16 |
| source voice type | 13 distinct trap/voice types across the 16 cases |
| evidence tier | medium 13 · hard 3 |

- **No manual swaps**; selection is the deterministic first-4-per-label by ranking hash.
- Whether BIAA-013_v3 or BIAA-016_v2 was selected is **not disclosed** here.
- **No individual case identity** appears in this file.
- Selected source identities and per-HLD gold assignments **remain private** (sealed outside Git).
