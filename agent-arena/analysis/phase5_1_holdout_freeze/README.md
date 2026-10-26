# Phase 5.1 — Prospective Holdout Selection and Freeze

## Purpose
Select, blind, seal, and freeze the Agent Arena v1.0 **prospective internal holdout** (16 opaque
cases, four per primary gold label) using deterministic stratified hash selection with a
precommitted algorithm and seed.

## What is committed vs sealed
- **Committed (this directory):** policies, aggregate summaries, and cryptographic commitments only
  (hashes/sizes). No source identities, no HLD→source mapping, no per-HLD gold, no packet contents.
- **Sealed (outside Git):** the private HLD→source map, per-HLD gold, evaluator packets, bundle,
  blank response sheet, eligibility ledger, and selection log.

## Key facts
- 16 opaque cases (HLD-001…HLD-016); four per label (solid/overclaim/correlation_vs_causation/
  mechanism_vs_evidence). Deterministic selection (holdout_select_v1, original frozen seed).
- **Prospective, not historically untouched** — some cases participated in earlier Phase 5 work.
- **No evaluation performed; no results collected.** No development access after freeze (see
  `freeze_policy.md`). Holdout evaluation requires a separately precommitted protocol.
- **Phase 5.2 is the next phase.**

*(No gold label is disclosed beside any HLD ID in committed artifacts.)*
