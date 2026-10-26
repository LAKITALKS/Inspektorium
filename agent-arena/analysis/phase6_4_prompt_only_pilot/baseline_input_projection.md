# Phase 6.4A — Baseline Input Projection

The projection defines **exactly** what the prompt-only baseline sends to the model for
one case. It is deterministic, reuses the established packet-integrity tooling, and is
proven to exclude every answer-bearing field.

## The projection

For a `Task`, the model-facing message pair is:

- **system** = the frozen baseline system prompt (`prompt_only_system_prompt.txt`);
- **user** = `build_baseline_input_projection(task)` = **`task.prompt` verbatim** — the
  single field of model-visible claim/evidence, identical to the user message the Agent
  Arena arm sends.

Nothing else from the task is sent. Implementation:
`agent_arena.prompt_only_baseline.build_baseline_messages`.

## Included fields (model-visible)

| field | why |
|---|---|
| `prompt` | the sole user-facing claim/evidence text; the same content both arms receive |

## Excluded fields (never sent)

`id` (canonical), `gold_label`, `expected_answer`, `reference_solution`, `gold_summary`,
`gold_justification`, `gold_alternative_reading`, `gold_confidence`, `gold_case_type`,
`status`, `excluded_from_active_metrics`, `expected_findings`, `gold_evidence_spans`,
`curator_notes`, `evaluator_notes`, `task_family`, `trap_type`, `ambiguity_level`,
`key_insights`, `common_errors`, `expected_failure_modes`, `discriminative_dimensions`,
`diagnostic_focus`, `expected_mechanism_terms`, `fragile_points`, `likely_shortcuts`, and
any `dev_id` / `stratum`. (`INPUT_PROJECTION_EXCLUDED` in code.)

**DEV identifiers never enter the prompt.** They exist only in the result envelope, keyed
by `dev_id`, produced by the private execution session.

## Proof of exclusion

`validate_no_forbidden_fields(task)` builds the exact model-facing packet and:

1. runs `packet_integrity.check_contamination` (reused) — flags gold label tokens,
   verbatim gold rationale text, evidence-span annotations, internal finding codes, IAA
   identifiers, and case identifiers appearing in the user message;
2. adds explicit checks for the `gold_label` / `expected_answer` value as a technical
   token, and for any canonical `study-forensics-#`, `DEV-###`, `BIAA-#`, or `HLD-#`
   identifier, or sealed-path marker, anywhere in the combined message.

Because the projection reads **only** `task.prompt`, an answer-bearing field can reach the
model **only** if the case text itself already contains it — which the contamination
check catches (fixture `t07_leaked_gold_token_in_prompt` demonstrates the guard firing).
Tests assert that clean synthetic tasks project cleanly and that the projected user
content equals `task.prompt`.

## Determinism

The projection is a pure function of `task.prompt`; the projection contract descriptor is
SHA-256-hashed (`input_projection_sha256`) into the runtime contract, so any change to the
projection changes the contract hash.
