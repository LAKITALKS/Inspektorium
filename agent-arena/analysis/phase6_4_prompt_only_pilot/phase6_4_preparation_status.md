# Phase 6.4A — Preparation Status (for curator review)

Prepared, frozen, validated, and documented a fair prompt-only comparison pilot. **The
pilot was not executed**; no model/provider or network call; no private development
result or sealed holdout accessed. **Nothing committed — stops for curator review.**

## Checkpoint

- HEAD `9b89945b8f9af1a112e8265653d17186c70f61c0` — verified; tracked tree clean before work.
- Phase 6.2 results and Phase 6.3 report schema untouched.

## Baseline design (concise)

A competent, neutral, non-adversarial prompt-only arm. **Accurate treatment contrast (not
a single prompt-string difference):** the same model (dated snapshot `claude-haiku-4-5-20251001`), 27
cases, user-visible case content (`task.prompt`), runtime parameters, replication count,
and evaluation targets (top label + confidence) are held fixed; the arms differ as **whole
packages** — the system prompt **and** the model-facing response contract (~11 structured
forensic fields vs 3: `predicted_label, confidence, brief_reason`) **and** the parser
(Agent Arena `parse_structured_output` with truncation repair + heuristic label vs the
baseline's stricter no-repair parser reading `predicted_label` directly). Both arms are
normalized to the same evaluated outputs; parser-completion differences are reported
separately and never conflated with classification accuracy. The pilot estimates a
descriptive **package-level** contrast, not the causal effect of one system-prompt string.
The baseline receives the claim/evidence, the four labels with accurate definitions, the
biological `mechanism_vs_evidence` scope, the frozen confidence meaning, and a strict
`{predicted_label, confidence, brief_reason}` output instruction — and nothing
answer-bearing. Its lighter 3-field response burden is a documented **conservative
asymmetry** and its stricter no-repair parser is an **arm-specific design choice**.

## Frozen identity

- **Contract ID:** `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`
- **Exact model ID:** `claude-haiku-4-5-20251001`
- **Prompt SHA-256:** `85e7b929253e37d2600a055e7212ffd755cf03fccdd3ddea40a745297eebbff6`
- projection SHA-256 `3aef083b…`; parser SHA-256 `62e62ef1…`; source checkpoint
  `9b89945…`; runtime: temperature 0.0, max_output_tokens 4096, replication 1, concurrency
  1, timeout 120s, transport-retries 2, `top_p` omitted, `seed` UNSUPPORTED.

## Input projection

`task.prompt` only (identical to the Agent Arena arm's user message). Every answer-bearing
field is excluded (`INPUT_PROJECTION_EXCLUDED`); `validate_no_forbidden_fields` reuses
`packet_integrity.check_contamination` plus explicit id/path checks. DEV identifiers never
enter the prompt.

## Files created

- `src/agent_arena/prompt_only_baseline.py` (new)
- `tests/test_prompt_only_baseline.py` (new; 49 tests)
- `analysis/phase6_4_prompt_only_pilot/`: `phase6_4_startup.md`, `pilot_rationale.md`,
  `baseline_design_principles.md`, `prompt_only_system_prompt.txt` + `.sha256`,
  `baseline_input_projection.md`, `prompt_only_output_contract.json`,
  `prompt_only_runtime_contract_haiku.json`, `paired_comparison_protocol.md`,
  `interpretation_rules.md`, `private_execution_handoff.md`,
  `phase6_4_acceptance_criteria.md`, `phase6_4_risk_register.md`, this status file,
  `build_artifacts.py`, `synthetic_fixtures/` (responses + projection tasks),
  `deterministic_fixture_outputs/`.

No Phase 6.2 or 6.3 result modified; no frozen taxonomy/label/gold/status/runtime contract
modified.

## Synthetic fixtures

**20** total: 13 response fixtures (4 labels valid + missing/invalid-string/boolean/
out-of-range/zero confidence + unknown label + malformed JSON + extra field + empty) and
7 projection-task fixtures (biological mechanism, non-biological "mechanism", correlation
without causal language, explicit causal overreach, unsupported superiority, empty
evidence, and a deliberately leaked gold-token task that the guard flags). All SYNTHETIC.

## Validation results

| gate | result |
|---|---|
| targeted 6.4A tests | **52 passed** |
| 6.4A + runtime-contract + confidence + output-contract + packet-integrity | **160 passed** |
| full test suite | **1299 passed** (was 1247; +52) |
| ruff on changed source/test/generator files | **clean** |
| deterministic regeneration (2 independent processes) | **byte-for-byte identical**; matches on-disk |
| leakage scan | **clean** — the only 64-hex values are the 3 public reproducible hashes; no canonical/BIAA/HLD/salt/private-path/raw-response token; DEV-#### appears only as the allowed opaque identity space (docs) and detector regex (module) |

## Contrast-identity correction (curator gate)

A public code-and-protocol audit found that the earlier single-prompt-string framing was
**not literally true**: the Agent Arena arm elicits ~11 structured forensic fields and parses
them with `parse_structured_output` (truncation repair; heuristic `final_answer` label),
whereas the baseline elicits 3 fields and uses a stricter no-repair parser reading
`predicted_label` directly. All artifacts now describe a **package-level** contrast (both
arms normalized to top label + confidence), report parser/confidence completion
separately from accuracy, document the baseline's lighter response burden as a
conservative asymmetry, and record the no-repair parser as an arm-specific choice. The
runtime contract carries a frozen accurate `treatment_contrast`, and
`validate_runtime_contract` plus a doc scan prevent a future single-prompt-string
misframing. **Neither arm's frozen endpoints were changed; the prompt SHA-256 is
unchanged.** The contract field is `repository_source_checkpoint` (pre-preparation
baseline, not the execution HEAD).

## Unresolved limitations (documented)

- **Ceiling risk:** Haiku was 27/27 in Phase 6.2; accuracy may not distinguish the arms.
  Interpretation rules pre-commit to reporting a ceiling and not calling the arms
  equivalent.
- **Small n:** 27 cases; `correlation_vs_causation` and `mechanism_vs_evidence` at n=2 are
  `small_n` / `descriptive_only`.
- **Single replication + residual nondeterminism:** `temperature=0` and unsupported seed
  reduce but do not eliminate sampling variation; only the analysis is deterministic.
- **Numeric-only reasoning is not judged offline:** the fairness of the baseline's actual
  classifications can only be assessed after the (later, authorized) private execution.

## Boundaries

No pilot execution; no model/provider/network call; no access to `AgentArena_IAA_Private/`,
`internal_only/`, `candidate_eligibility.csv`, private manifests/mappings, result
envelopes, raw responses, retry ledgers, sealed holdout, `research/`, or unrelated
untracked files. **Phase 6 closeout not begun.**

## Proposed commit paths (nothing staged)

```
src/agent_arena/prompt_only_baseline.py
tests/test_prompt_only_baseline.py
analysis/phase6_4_prompt_only_pilot/
```

Proposed commit message:

```
Phase 6.4 preparation: freeze Haiku prompt-only comparison pilot
```
