# Current State Snapshot (v0.7.7-retire-case042)

## Repo/tag state [FACT]
- Current tag: **v0.7.7-retire-case042** (commit `19aa295`).
- Full tag chain intact from `v0.6-agent-arena-baseline` (3327605) to `v0.7.7` (19aa295).
- Working tree clean except 21 known untracked cruft entries.
- Tests: **988 passed** (`pytest -q`).

## Active vs retired library [FACT]
- Case **files** on disk: 50.
- **Active cases (default discovery): 49.**
- **Retired cases: 1 — case042** (`study-forensics-042`).
- case042: not hard-deleted, not label-flipped, prompt byte-identical; excluded from default
  active discovery; reachable via `--include-retired` or explicit `--case-id`.

## Historical metrics — Phase 5A at v0.7.6 [FACT]
Single-model run `lib_20260704_134553_55aa66` (Opus 4.5, 50×3). **These are historical and were
computed over all 50 cases including case042, before retirement. They should NOT be silently
recalculated; regenerate against the active set for any forward-looking metric.**

- 50 cases, 150 total runs, **150/150 successful**
- 0 parse failures, 0 truncations, 0 provider errors
- Per-run accuracy: **144/150 = 96.0%**
- Case-majority accuracy: **48/50 = 96.0%**
- All 50 cases label-consistent (0 unstable)
- Stable-correct: **48**
- Stable-alternative: **2 — case042 and case054**
- High-score-variance cases: **0**
- `solid_as_problem_rate` (gold solid, predicted non-solid): **0/42 = 0%**
- `problem_as_solid_rate` (gold non-solid, predicted solid): **3/108 = 2.78%**, entirely case042
- Per-label accuracy: solid 100%, correlation_vs_causation 100%, mechanism_vs_evidence 100%,
  overclaim 66/72 = 92% (the 6 misses = case042 ×3 + case054 ×3)

## Current active state — v0.7.7 [FACT]
- 49 active cases; 1 retired historical case (case042).
- **No live rerun has been performed after v0.7.7.** Any "active-set accuracy" number therefore
  does not yet exist as a measured value; it would require a new run over the 49 active cases.
- [INTERPRETATION] If the historical Phase-5A run were simply filtered to the 49 active cases,
  case042's 3 misses drop out, leaving case054 as the only stable-alternative miss. That is an
  *arithmetic projection*, not a fresh measurement, and is not recorded as an official metric.

## Interpretation of the 96% [INTERPRETATION]
96% is a **single strong model ceiling** figure, not a benchmark-validity figure. It shows the
library is internally consistent and that one strong model finds ~all cases unambiguous. It does
**not** demonstrate discrimination power (ability to separate strong from weak models). See
`benchmark_integrity_risks.md`.

## Facts vs interpretations [FACT]
- Fact: 988 tests pass; 49 active / 1 retired; case042 retired without deletion or label flip.
- Fact: Phase-5A historical metrics as listed above.
- Interpretation: the library is "clean and stable for one model," not "validated."
- Open: case054 adjudication; taxonomy precedence rule.
