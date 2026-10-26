# Phase 6.4A — Startup Report (before implementation)

**Scope:** prepare, freeze, validate, and document a fair **prompt-only comparison
pilot**. This session **does not execute** the pilot, makes **no** model/provider or
network call, and touches **no** private development results or the sealed holdout. Only
tracked public repository material and synthetic fixtures are used.

## Checkpoint verification

- Expected HEAD `9b89945b8f9af1a112e8265653d17186c70f61c0` — **verified**.
- Tracked working tree **clean** before work.
- Phase 6.2 results (`5349ad0…`) and Phase 6.3 report schema present and **untouched**.

## Exact pilot question

> When the model, cases, runtime parameters, and output target are held fixed, does the
> Agent Arena forensic scaffolding show a **descriptive** advantage over a competent
> minimal **prompt-only** baseline on the same 27 development cases?

Paired, one model, one replication, no holdout. Descriptive only.

## Why Haiku (operational reasons only)

`claude-haiku-4-5-20251001` is chosen for lowest expected API cost, fastest practical
pilot, plausibility as a future low-cost deployment model, and the ability to contrast
the two prompting/scaffolding **packages** with the model held fixed. **This is not a claim that
Haiku is universally superior.** The model is fixed *before* results and is not changed
after seeing baseline outputs.

## The two arms — a package-level contrast (not a single-prompt-string difference)

**Held fixed:** model (dated snapshot), the 27 cases, the user-visible case content
(`task.prompt`), runtime parameters, replication count, and the **evaluation targets**
(predicted top label + confidence). **Differs (whole package):** system prompt **and** the
model-facing response contract **and** the parser.

| | Agent Arena arm | Prompt-only baseline arm | held fixed? |
|---|---|---|---|
| model (dated snapshot) | `claude-haiku-4-5-20251001` | same | **yes** |
| user content | `task.prompt` | **same** `task.prompt` | **yes** |
| runtime params / replication | frozen | same | **yes** |
| **evaluated outputs** | top label + confidence | top label + confidence | **yes** (normalized) |
| system prompt | Agent Arena `STUDY_FORENSICS_PROMPT` (full forensic scaffold) | minimal baseline prompt | no |
| **response contract** | ~11 structured forensic fields | 3 fields (`predicted_label, confidence, brief_reason`) | **no** |
| **parser** | `parse_structured_output` (truncation repair; label via `final_answer` heuristic) | stricter no-repair parser; `predicted_label` read directly | **no** |
| source of results | completed Phase 6.2 Haiku run (read-only) | one new prompt-only Haiku run (later, private) | — |

- **Agent Arena arm** = the already-completed Phase 6.2 Haiku envelope
  (`AA-6.2-RUN-6a3b93a24af7431e`). Not re-run; not modified.
- **Prompt-only arm** = a single new Haiku run under the frozen prompt-only runtime
  contract, executed later in a least-privilege private session.

Because the response contract and parser differ, the pilot estimates a descriptive
**package-level** contrast between the completed Agent Arena forensic prompting/scaffolding
package and a competent minimal prompt-only package. It does **not** isolate the causal
effect of one system-prompt string alone. Both arms are normalized to the same evaluated
outputs; **parser-completion differences are reported separately and never conflated with
classification accuracy**. The baseline's lighter 3-field response burden may favor the
baseline — a **conservative asymmetry** — and the baseline's stricter no-repair parser is
an **arm-specific design choice** (see the risk register and limitations).

## Fairness safeguards

- The baseline is **competent and non-adversarial**: it receives the claim/evidence, the
  four labels, accurate concise definitions, the **biologically constrained**
  `mechanism_vs_evidence` definition, the frozen confidence meaning, and a strict JSON
  output instruction — enough for a capable general model.
- It does **not** receive gold/expected labels, canonical or DEV ids, strata, curator/
  adjudication notes, expected failure modes, Phase 6.2 results, Agent Arena internal
  checks, the evidence-tier decision procedure, or any hidden comparison information.
- Input projection = `task.prompt` only; every answer-bearing field is excluded and this
  is proven by reusing `packet_integrity.check_contamination`.
- Metrics, bins, thresholds, abstention costs, and interpretation rules are **frozen
  before any result exists**; no threshold is introduced after results; the 54
  predictions are **never** pooled into a 54-case benchmark.

## Private-access boundaries (handoff, not performed here)

The later private session is authorized to read **only**: the frozen private 27-case
membership manifest, the existing private Haiku DEV↔canonical mapping (to preserve the
same `DEV-0001…DEV-0027` identities), the public frozen runtime contract, and tracked
public case material. It must **not** read completed Agent Arena predictions, any
completed envelope, calibration/accuracy reports, or holdout material, and it must not
compute comparison metrics.

## Methodological risks (see risk register)

Ceiling effect (Haiku was 27/27 in Phase 6.2 — accuracy may not distinguish the arms);
small n (27; corr/mech at n=2, descriptive only); single replication; residual
nondeterminism despite `temperature=0` and unsupported seed; the temptation to pool 54
predictions or declare a winner — all explicitly guarded.

## Planned files and tests

- `src/agent_arena/prompt_only_baseline.py` — frozen prompt, projection, strict parser,
  confidence classify (no 0.0 coercion), no-forbidden-fields validator, runtime-contract
  builder + digests.
- `tests/test_prompt_only_baseline.py` — prompt bytes/digest, four-label vocabulary,
  biological `mechanism_vs_evidence` scope (and non-biological "mechanism" not
  auto-triggering it), deterministic projection/serialization, forbidden-field exclusion
  (gold/expected/canonical/DEV/strata cannot enter the prompt), confidence VALID/MISSING/
  INVALID (bool + out-of-range rejected, no 0.0 coercion), malformed JSON → parser
  failure, extra/unknown fields rejected, no semantic-retry, exact runtime params, top_p
  omitted, seed absent, dated model id, paired-comparison contract, no-54-independent
  interpretation, fixed metric definitions, no threshold optimization, no holdout/private
  path, deterministic regeneration, one-char prompt change → digest change.
- `analysis/phase6_4_prompt_only_pilot/` — prompt txt + sha256, output contract, runtime
  contract, projection/protocol/interpretation/handoff docs, acceptance/risk/status,
  synthetic fixtures, deterministic fixture outputs.

**Contract ID:** `AA-RTC-6.4-HAIKU-PROMPT-ONLY-001`. No auto-commit; stops for curator
review. Phase 6 closeout not begun.
