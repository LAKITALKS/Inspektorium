# Agent Arena — Library Expansion 150

Append-only research workspace for the 150-candidate library expansion operation.

## Scope and isolation

This workspace is **additive only**. Nothing in it modifies:

- `tasks/study_forensics/` (canonical + quarantine case files)
- `docs/` (frozen taxonomy, precedence rules, intake policy)
- `analysis/` (Phase 4.9 / 5.x artifacts, IAA results, closeout records)

Candidates written here are **provisional research output for curator review**.
They are not canonical cases, they carry no gold labels, and they have not
entered the authoritative library.

## Holdout isolation

The private holdout lives outside this repository at
`__LOCAL_HOME__/Documents/AgentArena_IAA_Private/phase5_1_holdout/`. That path is **not
mounted into this agent's filesystem** — isolation is structural, not merely
promised. The connected mount is `Projects/agent-arena` only.

No holdout information was accessed, inferred, or used to select, balance, or
tune any candidate in this workspace.

Additionally, the following in-repo material was deliberately **not** opened,
because §2 of the operating protocol excludes private evaluator packets and
blind-ID-to-gold mappings:

- `analysis/phase5_05_blind_iaa_packets/internal_only/blind_case_index.csv`
- `analysis/phase5_05c_iaa_results/**/annotator_vs_gold.csv`

Consequence: the identity of the single development-only case (BIAA-007) was
not resolved, because resolving it requires the blind-ID mapping. It is
recorded by blind ID only.

## Authoritative sources used at startup

| Purpose | File |
|---|---|
| Frozen taxonomy | `docs/study_forensics_taxonomy.md` (v0.6.5) |
| Label precedence | `docs/taxonomy_precedence.md` |
| Intake requirements | `docs/case_intake_policy.md` |
| Authoritative ledger | `analysis/phase5_2_closeout/phase5_case_ledger_summary.md` |
| Phase 6 handoff | `analysis/phase5_2_closeout/phase6_handoff.md` |
| Case-level truth | `tasks/study_forensics/*.yaml` |

## Layout

```
research_state.json          global resumable state
current_coverage.json        machine-readable coverage baseline
coverage_gap_report.md       narrative coverage analysis + deficits
resume_instructions.md       exact restart procedure
batches/batch-001/           per-batch plan, leads, candidates, audit, checkpoint
```

## Status

Startup complete. Batch 001 planned but **not started** — one blocking
provenance decision is open. See `coverage_gap_report.md` §6 and
`batches/batch-001/batch_plan.md` §8.
