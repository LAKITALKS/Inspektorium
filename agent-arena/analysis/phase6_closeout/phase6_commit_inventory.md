# Phase 6 — Commit Inventory (authoritative sequence)

Reconstructed from git history. Phase 6 was authorized by the Phase 5.2 closeout commit and
proceeded through separate **preparation** and **result** checkpoints per the Level-2/3
governance rule (freeze methodology before seeing the numbers it will be judged against).

| # | commit | date | milestone |
|---|--------|------|-----------|
| — | `cfb78de` | 2026-08-02 | Phase 5.2 closeout and **Phase 6 authorization** (entry point) |
| 1 | `3983b7f` | 2026-08-04 | **Phase 6.0 startup** — governance levels, inventory, execution contract, packet-integrity automation |
| 2 | `54c06c4` | 2026-08-04 | **Phase 6.1 handoff** — confidence semantics and development-pool freeze |
| 3 | `57aa701` | 2026-08-04 | **Phase 6.1 preparation** — confidence semantics, calibration protocol, salted dev-pool commitment, provisioning workflow |
| 4 | `cf65149` | 2026-08-04 | **Phase 6.1 private provisioning** — freeze development-pool commitment (public commitment only) |
| 5 | `f9a7e28` | 2026-08-04 | **Phase 6.1 tooling fix** — align approved private provisioning paths |
| 6 | `327e769` | 2026-08-04 | **Phase 6.2 preparation** — calibration/abstention engine, contracts, synthetic tests |
| 7 | `dd53226` | 2026-08-04 | **Phase 6.2 runtime freeze** — dated model snapshots, provider timeout/retry, three per-model runtime contracts + tooling |
| 8 | `5349ad0` | 2026-08-05 | **Phase 6.2 results** — three-model development calibration and abstention analysis |
| 9 | `9b89945` | 2026-08-05 | **Phase 6.3 prototype** — deterministic claim-forensics report schema (6.3.0) and renderer |
| 10 | `b4ce7e2` | 2026-08-05 | **Phase 6.4 preparation** — freeze Haiku prompt-only comparison pilot |
| 11 | `605660c` | 2026-08-06 | **Phase 6.4 results** — paired Haiku package-level development comparison (current HEAD) |

## Curator-named checkpoints (cross-check)

- Phase 6.2 calibration results: `5349ad091bdbb5668e057c4327767bd2ccc415c9` (= #8) ✓
- Phase 6.3 report prototype: `9b89945b8f9af1a112e8265653d17186c70f61c0` (= #9) ✓
- Phase 6.4 prompt-only pilot preparation: `b4ce7e2a65e158b4833b33ce769e3bce067be43c` (= #10) ✓
- Phase 6.4 paired comparison results: `605660c9fca8705ffaac3f6a329db61ea8f1663a` (= #11, HEAD) ✓

## Artifact directories (tracked)

`analysis/phase6_0_startup/` · `analysis/phase6_1_confidence_protocol/` ·
`analysis/phase6_2_calibration/` · `analysis/phase6_2_runtime_freeze/` ·
`analysis/phase6_2_results/` · `analysis/phase6_3_report_prototype/` ·
`analysis/phase6_4_prompt_only_pilot/` · `analysis/phase6_4_prompt_only_results/`.
Source: `src/agent_arena/` (`confidence_validity.py`, `dev_manifest.py`, `calibration.py`,
`forensic_report.py`, `prompt_only_baseline.py`, `packet_integrity.py`). Tests: the
corresponding `tests/test_*.py`.

## Provenance discipline observed across Phase 6

- Every Level-2 operation used **separate preparation and result checkpoints**.
- The development pool was frozen by a **public salted-sha256 commitment** before results.
- Runtime parameters, prompts, parsers, and configs were **hashed and frozen** before
  execution.
- No tag was created for any Phase 6 milestone; tagging is proposed at closeout only
  (`phase6_go_no_go_review.md`).
