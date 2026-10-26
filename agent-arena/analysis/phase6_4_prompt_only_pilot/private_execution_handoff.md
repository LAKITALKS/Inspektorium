# Phase 6.4A — Private Execution Handoff (prepared, NOT performed)

This describes the **one-purpose, least-privilege** private session that will later run
the prompt-only baseline arm. **This public session does not perform it** and makes no
model/provider or network call. The handoff is documented and frozen here so the private
session has a fixed, minimal mandate.

## Single purpose

Execute the prompt-only baseline (arm B) on the frozen 27 development cases under the
frozen runtime contract `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`, preserving the same
`DEV-0001…DEV-0027` identities as the completed Agent Arena Haiku arm, and emit one
anonymized result envelope. **The execution session computes no comparison metrics.**

## Treatment-contrast note (accurate)

Arm B is **not** the Agent Arena arm with merely a swapped prompt string. The two arms
differ as **whole packages** — system prompt, model-facing response contract (~11
structured forensic fields for arm A vs 3 for arm B), and parser (arm A truncation-
repairing; arm B strict no-repair). The execution session must faithfully implement arm
B's frozen package (prompt bytes, projection, strict no-repair parser) and must **not**
alter arm A or borrow arm A's response contract/parser.

## Commit-provenance requirement (execution checkpoint)

The runtime contract's `repository_source_checkpoint` =
`9b89945b8f9af1a112e8265653d17186c70f61c0` is the **pre-preparation source baseline**
(Phase 6.3 HEAD), **not** the execution HEAD. The private execution session must:

1. run from the eventual **Phase 6.4A preparation commit** — the commit that lands this
   preparation — at an **exact, clean HEAD**:
   `PHASE_6_4A_EXECUTION_HEAD_TO_BE_FILLED_AFTER_COMMIT`;
2. **validate the frozen runtime contract and its hashes** before any call
   (`validate_runtime_contract`; `system_prompt_sha256`, `input_projection_sha256`,
   `parser_contract_sha256` reproduce; prompt SHA-256 =
   `85e7b929253e37d2600a055e7212ffd755cf03fccdd3ddea40a745297eebbff6`);
3. abort if HEAD is dirty or any frozen hash does not reproduce.

The placeholder above is replaced only through a **separately reviewed public handoff
update** after the preparation commit exists, if the repository's governance requires the
exact post-commit hash inside a tracked file. **Do not attempt a self-referential contract
hash**, and do not silently modify the frozen runtime contract.

## May read (only these — least privilege)

- the frozen private **27-case development manifest** required for membership;
- the existing private **Haiku DEV↔canonical mapping** required to preserve the same
  opaque identifiers;
- the **public frozen prompt-only runtime contract** and prompt
  (`prompt_only_runtime_contract_haiku.json`, `prompt_only_system_prompt.txt`);
- tracked **public case/task material** required to build the input packets.

## Must NOT read

- completed Haiku **Agent Arena predictions**;
- completed **Sonnet or Opus** predictions;
- any completed **result envelope**;
- accuracy or **calibration reports**;
- **holdout** material (maps, gold, results);
- private annotations **beyond** the minimum membership/mapping requirement.

## Will create

- private prompt-only Haiku **raw outputs**;
- a **retry ledger** (transport-only retries: connection, timeout, 429, 5xx, 529);
- an **execution attestation** (what was read, parameters used, hashes reproduced);
- **one anonymized prompt-only result envelope** (Phase 6.2 `envelope_version 6.2.0`
  contract), records keyed by opaque `DEV-####` only.

## Envelope requirements

- uses the **same `DEV-0001…DEV-0027`** identities as the completed Agent Arena Haiku arm
  (paired comparison);
- gold aggregate 8 / 15 / 2 / 2 (gold labels only);
- confidence VALID / MISSING / INVALID preserved, **never coerced to 0.0**;
- **no** canonical / BIAA / HLD ids, salt, private paths, or raw responses in the envelope;
- parser failures recorded as failed records (`parse_ok=false`), never re-run.

## Execution discipline (from the runtime contract)

`temperature=0.0`, `max_output_tokens=4096`, `replication_count=1`, `concurrency=1`,
`request_timeout_seconds=120`, `max_transport_retries_after_initial_request=2`, `top_p`
omitted, `seed` absent/unsupported. Retries only for connection/timeout/429/5xx/529.
**No** retry for parser failure, malformed JSON, missing/invalid/low confidence, semantic
quality, or suspected wrong classification. **No selective reruns.**

## Downstream (separate, later, authorized)

A separate analysis step computes the paired comparison metrics from the two anonymized
envelopes using the frozen `paired_comparison_protocol.md`. That step is **not** part of
the execution session and **not** part of this preparation.
