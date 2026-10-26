# Phase 6.4A — Acceptance Criteria & Stop Conditions

Pre-specified acceptance for the prompt-only pilot **preparation** (this session). Each
has a disposition and its evidence.

| id | criterion | disposition | evidence |
|---|---|---|---|
| C-1 | Baseline is competent and non-adversarial | **MET** | fair prompt with claim/evidence + 4 accurate label definitions + biological `mechanism_vs_evidence` scope + strict output; `baseline_design_principles.md` |
| C-2 | Exact prompt frozen and hashed | **MET** | `prompt_only_system_prompt.txt` + `.sha256`; `baseline_prompt_digest()`; `test_prompt_bytes_and_digest_frozen` |
| C-3 | Input projection excludes all answer-bearing metadata | **MET** | projection = `task.prompt` only; `validate_no_forbidden_fields` reuses `check_contamination`; exclusion tests |
| C-4 | Runtime settings frozen | **MET** | `prompt_only_runtime_contract_haiku.json` + `validate_runtime_contract`; params tests |
| C-5 | No provider call occurred | **MET** | pure/offline module; no provider import in execution path; no network |
| C-6 | No private or holdout access occurred | **MET** | synthetic fixtures only; sealed-path markers rejected; no private read |
| C-7 | Comparison metrics + interpretation rules frozen before results | **MET** | `paired_comparison_protocol.md`, `interpretation_rules.md` (frozen; reuse Phase 6.1/6.2 defs) |
| C-8 | Execution handoff one-purpose and least-privilege | **MET** | `private_execution_handoff.md` |
| C-9 | All synthetic fixtures clearly synthetic | **MET** | fixtures marked SYNTHETIC; no real DEV/canonical ids |
| C-10 | Tests and lint pass | **MET (this session)** | targeted + full suite green; ruff clean on changed files |
| C-11 | Deterministic regeneration passes | **MET** | `build_artifacts.py` byte-for-byte across independent processes |
| C-12 | Leakage scan passes | **MET** | no private id/path/salt/holdout/raw response/completed prediction in artifacts |
| C-13 | No Phase 6.2 or 6.3 result modified | **MET** | only new files + no edits to Phase 6.2/6.3 artifacts |

## Frozen-methodology guarantees

- The four-label taxonomy, label definitions, and the **biological** `mechanism_vs_evidence`
  scope are **unchanged**; the pilot reuses them.
- The Phase 6.1 confidence semantics and Phase 6.2 metric definitions/bins/thresholds/costs
  are reused unchanged; no new threshold is introduced after results.
- No 54-case pooling; the 54 predictions are paired outputs on 27 cases.

## Stop conditions (respected)

- No pilot execution; no model/provider or network call.
- No access to `AgentArena_IAA_Private/`, `internal_only/`, `candidate_eligibility.csv`,
  private manifests/mappings, result envelopes, raw responses, retry ledgers, sealed
  holdout, `research/`, or unrelated untracked files.
- No modification of the frozen taxonomy, labels, gold, status, Phase 5/6.1/6.2/6.3
  artifacts, or completed runtime contracts.
- Phase 6 closeout not begun. No auto-commit; stops for curator review.
