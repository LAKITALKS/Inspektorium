# Resume Instructions

**Last completed batch:** none
**Open batch:** batch-001 (3 of 10 curator-ready)
**Completed curator-ready candidates:** 3 / 150
**Next candidate ID:** AAEXP-0004

> **PENDING TARGET CORRECTION (not applied):** operation target proposed to move
> to 170 candidates / 17 batches, so that 48 active + 170 = 218 leaves headroom
> above 200 after curator rejections. Recorded in `research_state.json` →
> `pending_operation_target_correction`. Apply at a batch boundary, not mid-batch.
> Note it also affects the §26 global audit cadence (currently defined at
> batches 005/010/015) and all §31 completion artifacts.

## Files to read first, in order

1. `research_state.json` — global state; all blocking decisions RESOLVED
2. `quality_control_log.md` — QC-001 (resolved), QC-002 (closed)
3. `batches/batch-001/batch_plan.md` — revised target mix
4. `batches/batch-001/raw_leads.jsonl` — 5 open leads
5. `future_taxonomy_review_issue.md` — deferred, do not resolve this run

## Accepted so far in Batch 001

| ID | Label | Domain | Score |
|---|---|---|---:|
| AAEXP-0001 | `overclaim` | software & cybersecurity | 47/50 |
| AAEXP-0002 | `correlation_vs_causation` | business & market claims | 47/50 |
| AAEXP-0003 | `solid` | psychology & behavioural science | 46/50 |

Mean 46.7 · min 46 · all four §16 critical fields ≥ 4 on every accepted candidate.

## Remaining Batch 001 target

| Label | Still needed |
|---|---:|
| `correlation_vs_causation` | 3 |
| `solid` | 2 |
| `overclaim` | 1 |
| `mechanism_vs_evidence` | 1 (must be biomedical — frozen scope, QC-001) |

## Standing rules confirmed this session

- **QC-001:** frozen biological scope for `mechanism_vs_evidence` stands. Non-biological
  cases take the label matching the actual dominant defect, plus
  `future_taxonomy_review.possible_domain_general_mechanism_analogue: true`.
- **Depth over speed.** No loosening of verification. Ten cases is an output
  checkpoint, not a speed quota. Batches may exceed 25–40 leads and span sessions.
- **Revised portfolio (150):** solid 46 · overclaim 37 · correlation_vs_causation 52 ·
  mechanism_vs_evidence 15.
- **Do not modify** `docs/study_forensics_taxonomy.md` or any existing gold label.
- **Do not access** the private holdout or IAA `internal_only` material.

## Hardest remaining target: `solid` (3 needed)

§28 forbids using `solid` as a leftover category — each must survive an
adversarial attempt to disconfirm it, and should be a claim that could
plausibly have been an overclaim but is actually well supported. None of the
current 5 open leads is a likely `solid`. Plan dedicated discovery for these
rather than expecting them to fall out of overclaim-hunting.

## Immediate next actions

1. Dedicated `solid` discovery — search for well-scoped claims that preserve
   population limits, report absolute effects, and match design to causal wording.
2. `mechanism_vs_evidence` — biomedical only. Animal/preclinical mechanism
   presented as human clinical benefit (frozen Shapes A and C).
3. Work open leads: L-002 (agriculture), **L-003 (vendor email-security claim —
   omitted in error from an earlier resume block; still open)**, L-004
   (consumer/FTC), L-005 (AI firewall validation — check whether results are
   published; if only an announcement exists there is no evidence source, reject
   under §10.6), L-007 (CMU press pairing for AAEXP-0003).

   Lead ledger after the 2026-08-03 state repair: 8 allocated (L-001…L-008),
   3 converted (L-001→0001, L-006→0002, L-008→0003), 5 open. L-008 is
   numbered out of chronological order by design — IDs are never recycled.
4. Untouched priority domains: energy & sustainability, psychology & behavioral,
   agriculture & food systems.
5. Discovery funnel: 6 raw leads recorded, 2 converted. Continue expanding.

## Verification standard to apply (do not shortcut)

Every quote read from the primary document. No secondary-source figures — QC-002
records a live instance where a secondary summary carried materially different
numbers (28/99/95) from the primary paper (100% ASR). Contrary-evidence,
correction, and retraction searches per candidate. Duplicate control against all
48 active canonical cases plus all prior AAEXP candidates. Full §17 adversarial
review. Unretrieved material recorded as an explicit unresolved question, never
assumed.

## Isolation status

Holdout not accessed — private path not mounted into the agent filesystem. IAA
`internal_only` material not opened. Canonical library not modified.
