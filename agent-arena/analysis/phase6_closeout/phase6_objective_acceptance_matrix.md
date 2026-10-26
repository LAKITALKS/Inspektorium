# Phase 6 — Objective Acceptance Matrix

Each Phase 6 objective is evaluated against committed evidence. Dispositions: **PASS**,
**CONDITIONAL**, **FAIL**. All ten objectives **PASS**; two carry forward-looking notes for
Phase 7 (not defects). Evidence references committed artifacts rather than duplicating them.

| # | objective | disposition | evidence (committed) |
|---|-----------|-------------|----------------------|
| 1 | Governance & execution levels | **PASS** | `phase6_0_startup/governance_levels.md` (3 tiers by highest-impact surface; least-privilege prep/result checkpoints); one-purpose handoffs (`phase6_4_prompt_only_pilot/private_execution_handoff.md`); no destructive/uncontrolled workflow; Level 3 not taken (holdout sealed, gold/taxonomy frozen) |
| 2 | Packet integrity | **PASS** | `src/agent_arena/packet_integrity.py` `check_contamination`; reused as the baseline leak guard (`prompt_only_baseline.validate_no_forbidden_fields`); `tests/test_packet_integrity.py` |
| 3 | Confidence semantics | **PASS** | `phase6_1_confidence_protocol/confidence_semantics.md`; `confidence_validity.classify_confidence` (VALID/MISSING/INVALID, no 0.0 coercion) reused unchanged in calibration, forensic-report, and prompt-only paths; `tests/test_confidence_validity.py` |
| 4 | Development-pool governance | **PASS** | `phase6_1_confidence_protocol/development_pool_public_manifest.json` — `AA-DEVPOOL-6100`, salted-sha256 commitment `679233c6…4332`, aggregate 8/15/2/2/27; public docs expose no pool identities; holdout sealed (`development_pool_freeze.md`) |
| 5 | Runtime freeze | **PASS** | `phase6_2_runtime_freeze/phase6_2_runtime_contract_{haiku,sonnet,opus}.json` — dated snapshots, prompt/config/parser SHA-256, temperature 0.0, `top_p` omitted, seed UNSUPPORTED, timeout 120 s, ≤2 transport retries; residual-nondeterminism note present |
| 6 | Calibration engine | **PASS** (note) | `src/agent_arena/calibration.py` + `phase6_2_calibration/metric_definitions.md` — Brier primary, ECE secondary, 5 fixed bins (empty retained), costed abstention, denominator rules, small-n flags; `select_operating_threshold()` raises; `tests/test_calibration.py`. Note: sparse-bin ECE is documented as high-variance and not used to assert calibration quality |
| 7 | Three-model development characterization | **PASS** | `phase6_2_results/haiku_/sonnet_/opus_calibration_report.{json,md}` (separate) + `cross_model_descriptive_comparison.{json,md}` — same 27 cases, **no 81-case pool**, no universal-superiority; banner **DEVELOPMENT CALIBRATION — NOT HOLDOUT** |
| 8 | Forensic-report prototype | **PASS** | `src/agent_arena/forensic_report.py`; `phase6_3_report_prototype/forensic_report_schema.json` (`report_schema_version` const **6.3.0**); one validated object → JSON + full MD + executive summary; four labels + biological `mechanism_vs_evidence`; missing/invalid confidence explicit; parser failure ≠ verdict; rewrites are unverified proposals (no-safe-rewrite guard); synthetic fixtures only; `tests/test_forensic_report.py` |
| 9 | Prompt-only paired development pilot | **PASS** (note) | `phase6_4_prompt_only_pilot/*` (frozen prompt/runtime/parser + hashes) and `phase6_4_prompt_only_results/*` — competent non-adversarial baseline; same dated Haiku snapshot + paired 27 cases; **package-level** contrast; parser completion separated from accuracy; **no 54-case pool**; no universal-superiority; banner **DEVELOPMENT PILOT — NOT HOLDOUT**. Note: single replication per arm (Phase 7 to add replication) |
| 10 | Reproducibility & leakage | **PASS** | Deterministic generators reproduce committed outputs byte-for-byte (`phase6_reproducibility_audit.md`); full suite + Phase 6 targeted tests + ruff pass; no private identity/mapping/raw-response/holdout material in any Phase 6 tracked artifact (`phase6_security_and_leakage_audit.md`) |

## Notes on the two "PASS (note)" objectives

- **#6 (ECE):** ECE is retained per protocol as a **secondary/descriptive** metric. At
  N = 27 with confidences concentrated in the top bins it is high-variance — Sonnet had the
  **lowest** ECE while being the **only** model with errors. This is a documented property,
  not an engine defect; Brier (primary) exposed the high-confidence errors correctly.
- **#9 (replication):** the pilot is a single run per arm; residual model nondeterminism is
  disclosed. This is the frozen pilot design, not a deficiency — Phase 7 pre-freezes a
  replication count.

## Not-in-scope for Phase 6 (correctly deferred)

Multi-run stability, harder boundary cases, perturbation/adversarial robustness, external
human validation, holdout evaluation, and any production claim were **deliberately not
undertaken**. They are Phase 7 priorities (`phase7_handoff.md`), not Phase 6 gaps.
