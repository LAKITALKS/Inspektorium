# Phase 6.4A — Pilot Rationale

## What this pilot is

A deliberately minimal, **one-model, paired** comparison pilot on the frozen 27-case
development pool. It contrasts two **prompting/scaffolding packages**:

- **Agent Arena arm** — the completed Phase 6.2 Haiku run under the full forensic
  scaffold (`STUDY_FORENSICS_PROMPT`), read-only, not re-run.
- **Prompt-only baseline arm** — one new Haiku run under a frozen minimal prompt that
  gives a capable general model enough to classify fairly, without reproducing the Agent
  Arena scaffold.

**Held fixed:** the model (dated snapshot), the 27 cases, the user-visible case content
(`task.prompt`), runtime parameters, replication count, and the evaluation targets (top
label + confidence). **The arms are not merely a different prompt string:** they also use
**different model-facing response contracts** (~11 structured forensic fields vs 3:
`predicted_label, confidence, brief_reason`) and **different parsers** (Agent Arena
`parse_structured_output` with truncation repair and a heuristic `final_answer` label vs
the baseline's stricter no-repair parser reading `predicted_label` directly). Both arms are
normalized to the same evaluated outputs. The pilot therefore estimates a descriptive
**package-level** contrast, not the causal effect of one system-prompt string alone.

## The scientific question

> When the model, cases, runtime parameters, and output target are held fixed, does the
> Agent Arena forensic scaffolding show a **descriptive** advantage over a competent
> minimal prompt-only baseline on the same 27 development cases?

## Why one model, and why Haiku

The pilot contrasts the two prompting/scaffolding **packages** by holding the model fixed
(it does not isolate one system-prompt string). Haiku (`claude-haiku-4-5-20251001`) is
chosen for operational reasons only:

- lowest expected API cost;
- fastest practical pilot;
- plausibility as a future low-cost deployment model;
- cleanest package-level contrast with the model held fixed.

This is **not** a claim that Haiku is universally superior, and the model is fixed before
results and never changed after seeing baseline outputs. No Sonnet or Opus baseline is
run in this pilot.

## Why paired, and why not pooled

Both arms classify the **same 27 cases** with the **same opaque `DEV-0001…DEV-0027`
identities**, so the comparison is **paired** (per-case). The 54 predictions are two
paired outputs on 27 cases — **not** 54 independent cases. They are never pooled into a
54-case benchmark, and no single pooled score is computed.

## What the pilot can and cannot say

**Can** (descriptive, this pool only): accuracy, top-label Brier, descriptive ECE,
confidence behavior, high-confidence errors, fixed-threshold selective behavior, paired
correctness disagreements, per-label descriptive results, parser/confidence completion,
and the paired arm-vs-arm differences.

**Cannot**: universal Agent Arena superiority, general model superiority, production
readiness, holdout performance, statistical proof from 27 cases, independence of the 54
predictions, or causal attribution beyond the descriptive **package-level** contrast
(system prompt + response contract + parser together, not one system-prompt string).

## The treatment contrast is package-level (not a single prompt string)

The two arms differ as whole packages: system prompt, model-facing response contract
(~11 vs 3 fields), and parser (truncation-repairing vs strict no-repair). Consequences
that the analysis keeps explicit:

- **Parser-completion** (parse_ok / confidence-validity coverage) is reported
  **separately** and is **never** conflated with classification accuracy.
- The baseline's **lighter 3-field response burden** may favor the baseline — a
  documented **conservative asymmetry**.
- The baseline's **stricter no-repair parser** is an **arm-specific design choice** (see
  `phase6_4_risk_register.md` and the limitations), not a property of the model.

## Anticipated ceiling effect

In Phase 6.2, Haiku classified all 27 cases correctly. Accuracy may therefore be unable
to distinguish the arms (a ceiling). The protocol pre-commits to reporting an accuracy
ceiling honestly, examining Brier/confidence/reportability cautiously, and **not**
declaring the arms equivalent merely because both reach 27/27.
