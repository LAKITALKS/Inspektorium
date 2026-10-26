# Case Library Run Harness — Phase 4

Branch: `feat/case-library-run-harness` (from `v0.7.0-case-library`)

A reproducible batch harness for the 50-case `study_forensics` library. It runs
cases (optionally repeated), stores structured per-run results, and produces a
basic multi-run **stability** summary. It changes no scoring, prompt, provider,
parser, judge, or report logic — scores/labels come from the existing evaluator,
and `truncation_suspected` is read (read-only) from the existing Phase-1 parser.

Module: `src/agent_arena/run_library.py`.

---

## Quick fake-provider test (no network)

```bash
python -m agent_arena.run_library --limit 3 --runs-per-case 2 --fake
```

The `--fake` (alias `--dry-run`) provider is deterministic and echoes each
case's `gold_label` as valid JSON — used by the test suite and for offline
sanity checks. No API key required.

## Live smoke test (requires provider key in env)

Recommended escalation (cost control):

```bash
# 1) tiny smoke
python -m agent_arena.run_library --limit 3 --runs-per-case 1 --provider anthropic --model claude-opus-4-5
# 2) small stability probe
python -m agent_arena.run_library --limit 5 --runs-per-case 3 --provider anthropic --model claude-opus-4-5
# 3) only later: full library
python -m agent_arena.run_library --task-family study_forensics --all --runs-per-case 3 --provider anthropic --model claude-opus-4-5
```

Selection flags: `--all`, `--case-id study-forensics-043`, `--limit N`,
`--label overclaim|solid|mechanism_vs_evidence|correlation_vs_causation`,
`--synthetic-only`. Multi-run: `--runs-per-case N`.

## Output directory structure

Artifacts go to `runs/library/<library_run_id>/` (or `--out-dir`). `runs/` is
git-ignored, so results are never committed.

```
runs/library/<library_run_id>/
  manifest.json     run metadata + case list
  results.jsonl     one JSON object per individual run (raw runs kept, not averaged)
  summary.json      aggregate summary + per-case stability
  summary.md        human-readable summary
```

Each `results.jsonl` record contains: `library_run_id, case_id, case_file,
gold_label, run_index, provider, model, label, label_correct, score,
confidence, parse_ok, finish_reason, truncation_suspected, error, error_type,
latency_ms, usage, timestamp, raw_result_ref`.

## Stability metrics (per case)

Descriptive only — no calibration, no Brier/log/Bayesian scoring:
`n_runs, successful_runs, failed_runs, parse_failures, truncation_count,
unique_labels, label_consistency_rate (top-label freq / labelled runs),
score_mean, score_min, score_max, score_range, confidence_mean, error_types`.

## Flags and thresholds

| Flag | Condition |
|---|---|
| `stable_label` | exactly one unique label and every run produced it |
| `unstable_label` | more than one unique label across successful runs |
| `parse_fragile` | any run had `parse_ok == False` |
| `truncation_risk` | any run had `finish_reason == "length"` or `truncation_suspected` |
| `provider_error_seen` | any run returned a provider error |
| `high_score_variance` | `score_range > HIGH_SCORE_VARIANCE_THRESHOLD` |

Documented constant: `HIGH_SCORE_VARIANCE_THRESHOLD = 15.0` (points on the
0–100 total scale), defined in `run_library.py`.

## API-key safety

Keys are read by the provider SDK from the environment only. The harness never
prints, logs, or writes keys; artifacts contain no secrets; `.env` stays
git-ignored.

## Limitations

- Descriptive stability only; this is **not** calibration (no proper scoring,
  no Bayesian updating, no evidence-hierarchy weighting).
- `truncation_suspected` is re-derived read-only from the parser; it is not yet
  persisted on `AgentResult` itself.
- Single provider/model per library run (no provider routing/mixing here).
- `raw_result_ref` is reserved (null) — full `RunRecord` dumps are not stored to
  keep artifacts lean.
- Fake provider is label-correct and stable by design; instability/parse/
  truncation behavior is exercised via test-only fakes.

## Recommended next phase

`feat/library-calibration-surface` — turn repeated-run stability into a
calibration surface (reliability by confidence bucket, proper scoring) as a
separate, opt-in module. Does not belong in this harness phase.
