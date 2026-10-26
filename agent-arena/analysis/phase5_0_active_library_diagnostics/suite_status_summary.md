# Suite Status Summary — Active Library (Phase 5.0)

*Offline summary. Suite groupings below are a **historical-derived draft** (from the
frozen Phase-5A `suite_assignment_draft.csv`), not a ratified suite split. Schema
has no formal `suite` field yet.*

## Active vs retired [FACT]
- Active: **49** cases (default discovery).
- Retired: **1** — `study-forensics-042` (default-excluded; loadable on request).

## Suite draft over the 49 active cases [DERIVED — historical draft]
Joining the frozen Phase-5A suite-assignment draft to the current active IDs:

| draft suite | active count |
|---|---:|
| core_candidate | 35 |
| boundary_candidate | 9 |
| anchor_candidate | 5 |

- These are **candidate** labels only. No Core/Boundary/Anchor split has been
  ratified into the schema. `boundary_candidate` ≈ the 9 `borderline` cases.
- **Retired** is the only status enforced today (via `excluded_from_active_metrics`).

## Ambiguity level (active) [FACT]
| ambiguity_level | count |
|---|---:|
| low | 34 |
| medium | 10 |
| high | 5 |

## Documented alternative readings [FACT]
- **26 / 49** active cases carry a non-empty `gold_alternative_reading`.
- All 9 `borderline` active cases have an alternative reading (schema-enforced by
  `test_case_library`).

## Metadata-completeness gaps [FACT]
- **Missing `origin` (27 active cases):** the hand-curated legacy block
  `001, 004, 007, 009, 013, 019, 021, 022, 023, 024, 025, 026, 027, 028, 029, 030,
  031, 032, 033, 034, 035, 036, 037, 038, 039, 040`, plus `public-001`.
  (The Phase-3 synthetic cases 043–063 and the showcase 041 carry `origin`.)
- **Missing `intake_review` (48 active cases):** only **case041** carries an explicit
  `intake_review: passed`. Every other active case lacks the field.

## Cases that may need retrospective intake review [INTERPRETATION]
Prioritised by risk signal, per the intake policy:
1. **Legacy hand-curated cases missing `origin`** (the 27 above) — provenance is
   undocumented; candidates for a lightweight provenance backfill.
2. **`public-001`** — the only `public`-prefixed case; provenance/source-voice
   should be confirmed against the real-world intake policy before any external use.
3. **Boundary / stable-alternative cases** — case054 (adjudicated, documented) and
   the other 8 borderline cases: confirm each has an isolated claim + clear source
   voice (the case042 failure mode).
4. **case041** — already reviewed and passed; retained as the audited exemplar.

None of the above is a defect to fix now; they are the queue for a future
retrospective intake audit (see `post_v079_open_risks.md`).
