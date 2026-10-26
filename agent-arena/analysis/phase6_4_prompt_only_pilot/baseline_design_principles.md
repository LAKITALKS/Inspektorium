# Phase 6.4A — Baseline Design Principles

The prompt-only baseline must be a **fair, competent, neutral, non-adversarial**
opponent. A weak baseline would make any Agent Arena advantage meaningless. These
principles are enforced in `src/agent_arena/prompt_only_baseline.py` and its tests.

## 1. Competent and fair

The baseline receives enough to classify fairly:

- the public claim and the same user-visible evidence content the Agent Arena arm sees
  (`task.prompt`, verbatim);
- the four allowed labels with **accurate, concise** definitions;
- the **biologically constrained** definition of `mechanism_vs_evidence`;
- the frozen confidence meaning (belief that the selected top label is correct, in [0,1]);
- a strict machine-readable output instruction.

It is never described as inferior, and carries no Agent Arena branding.

## 2. Minimal, not scaffolded

The baseline prompt is a concise instruction sufficient for a capable general model. It
does **not** reproduce the Agent Arena forensic scaffold: no evidence-tier decision
procedure, no bridge-step algorithm, no multi-agent roles, no self-check protocol, no
benchmark history, no priority-rule machinery. Holding the model fixed, this is one part
of the **package-level** contrast the pilot describes — the arms also differ in their
model-facing response contract (3 fields vs ~11) and parser (see §4 and §6); the pilot
does not isolate the effect of one system-prompt string alone.

## 3. Answer-blind

The baseline never receives gold/expected labels, canonical case identifiers, DEV
identifiers, strata, curator/adjudication notes, reviewer disagreements, expected failure
modes, known-answer hints, Phase 6.2 model results, Agent Arena internal checks, or any
hidden comparison information. The input projection uses **only** `task.prompt`.

## 4. Strict, minimal output

The model returns exactly `{"predicted_label", "confidence", "brief_reason"}` — strict
JSON, no markdown, no code fence, no chain-of-thought, no extra fields. `predicted_label`
is one of the four frozen labels; `confidence` is a JSON number in [0,1] (booleans
invalid); `brief_reason` is one or two concise sentences grounded only in the supplied
text.

## 5. Confidence honesty (Phase 6.1, reused)

Confidence is classified `VALID / MISSING / INVALID` via
`confidence_validity.classify_confidence`. A missing or invalid confidence is **never
coerced to 0.0** — it is recorded and excluded from confidence metrics, exactly as the
Agent Arena arm handles it.

## 6. Failure cannot masquerade as a verdict

A malformed response — or one only recoverable by best-effort truncation repair — is
recorded as a **parser failure** (`parse_ok = false`), never a verdict, and is **never
retried**. There are no semantic/quality retries and no selective reruns.

## 7. Frozen and hashed

The exact prompt bytes, the input-projection contract, and the parser contract are frozen
and SHA-256-hashed into the runtime contract. A one-character prompt change changes the
digest and would be a deliberate, reviewed re-freeze.

## 8. Same evidence, same identities

Both arms see the same `task.prompt`; the baseline result envelope reuses the same
`DEV-0001…DEV-0027` opaque identities as the completed Agent Arena Haiku arm, enabling a
strict paired comparison without exposing any private identity.
