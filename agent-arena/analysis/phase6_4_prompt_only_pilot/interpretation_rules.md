# Phase 6.4A — Interpretation Rules (FROZEN BEFORE EXECUTION)

These rules are frozen before any prompt-only result exists and govern how the later
paired comparison may be described.

## Permitted language

- "On this 27-case development pilot…"
- "The Agent Arena arm showed a descriptively higher/lower …"
- "No difference was observed on this pilot…"
- "The pilot did not establish a general advantage…"
- "The result is compatible with a ceiling effect…"

## The contrast is package-level (state accurately)

- Describe the contrast as **package-level**: the completed Agent Arena forensic
  prompting/scaffolding **package** vs a competent minimal prompt-only **package**, with
  the model, cases, user-visible content, runtime parameters, replication count, and
  evaluation targets held fixed.
- Do **not** say the arms differ "only in the system prompt": they also use a different
  model-facing **response contract** (~11 vs 3 fields) and a different **parser**.
- The pilot **does not isolate the causal effect of one system-prompt string alone**.
- Report **parser/confidence completion separately** from classification accuracy; never
  conflate them.
- Note the baseline's lighter response burden as a **conservative asymmetry**, and the
  baseline's stricter no-repair parser as an **arm-specific design choice**.

## Forbidden language

- "Agent Arena is proven superior."
- "Agent Arena universally outperforms prompt-only models."
- "The baseline is statistically defeated."
- "The result validates production performance."
- "The holdout confirms…"
- "The larger number of predictions increases n to 54."
- "The two arms differ only in the system prompt." (they differ as whole packages)
- "The pilot isolates the effect of the Agent Arena system prompt." (it is package-level)

## If both arms achieve 27/27 (accuracy ceiling)

- Report an **accuracy ceiling** explicitly.
- **Do not** call the arms equivalent.
- Examine Brier, confidence behavior, and reportability (parser/confidence completion)
  **cautiously**, with `n` and small-sample caveats.
- State plainly that the pilot **could not distinguish classification accuracy**.

## If the baseline outperforms the Agent Arena arm

- Report it **without suppression**.
- **Do not** alter or exclude cases.
- **Do not** change the frozen baseline retroactively.
- Document possible explanations as **hypotheses only** (e.g. ceiling, prompt fit, task
  distribution), never as conclusions.

## If Agent Arena outperforms the baseline

- Report the **paired development observation** for this pool only.
- **Do not** generalize beyond the pilot (no universal-superiority, no production, no
  holdout inference).

## General

- The 54 predictions are paired outputs on the same 27 cases — never framed as 54
  independent cases.
- No winner is declared solely from this pilot.
- Distinguish clearly between observed results, methodological interpretation, and
  unsupported speculation.
- All small-sample and `n = 2` label limitations are stated wherever the corresponding
  numbers appear.
