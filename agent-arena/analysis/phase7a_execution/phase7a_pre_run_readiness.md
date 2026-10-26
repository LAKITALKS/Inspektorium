# Phase 7A — Pre-Run Execution Readiness (WP-4)

Compact readiness artifact for the **single, pre-registered** Phase-7A execution. WP-4 prepares and
freezes the execution/reporting contract; it makes **0 real analytical model calls**. The science is
frozen; nothing here alters cases, gold, thresholds, model conditions, or N.

## Approved scientific checkpoints (frozen)
- Boundary: `3bdabaf` — human-curator approved
- Adversarial: `e9e13e3` — human-curator approved
- Perturbation / equivalence: `84d75d4` — human-curator approved

## Execution universe (deterministic; retired → 0 units)
| unit type | count |
|---|---:|
| boundary_base | 14 |
| adversarial_base | 16 |
| neutral_base | 4 |
| **independent bases** | **34** |
| perturbation_variant | 50 |
| **evaluated units** | **84** |

- Perturbation clusters: **10** (5 variants each) — 50 variants are **nested** in 10 independent
  bases; downstream reporting reports **34 independent bases / 84 evaluated units**, **never** 84
  independent cases or 50 independent perturbation cases.
- Selected perturbation cluster roots (frozen §6): 4 neutral (`P7A-NEU-001..004`) + B1 `P7A-BND-017`
  + B2 `P7A-BND-009` + B3 `P7A-BND-011` + adversarial `P7A-ADV-010` (A5) / `P7A-ADV-001` (A1) /
  `P7A-ADV-011` (A6).

## Primary models (frozen; both independently primary)
- `claude-haiku-4-5-20251001`
- `claude-sonnet-4-5-20250929`
- Opus is **not** a primary condition; no prompt-only primary; no ensemble.

## Replication + call plan
- N = **5** (independent calls per unit; transport retries are infrastructure, **not** replications)
- Planned analytical calls = 84 × 5 × 2 = **840**
- Max transport-retry exposure = 840 × 2 = **1680** (retries never counted as replications)
- Package condition = `agent_arena_package`; prompt-only baseline = false

## Runtime contract (frozen, from `runtime_contract.build_contract`)
- temperature `0.0` · top_p `OMITTED_FROM_REQUEST` · seed `UNSUPPORTED` · request_timeout `120s`
- transport retries ≤ `2` · semantic/quality retries `PROHIBITED`
- Both primary contracts validate as **executable** (dated model id == pinned agent-config model).

## Frozen fingerprints (recomputed and gate-verified)
| artifact | sha256 |
|---|---|
| execution manifest | `9c43aa4bf189f373079f00a313c671b5619bf7737ee73e5cefab73e274fcdb89` |
| scientific manifest | `55217a9de2b159388a13fca2038d284e3289f5d5e835b39cea3d980f1467f45c` |
| call plan | `7b1b58e730e394e4985e89c4ab1624266656aa540d1fcd4ee8b00a7389828e4e` |
| package / prompt | `6f572faa5ede59c15648ced5258e6d0d54f068871faf64bac9f3d5f5c7dbf3f4` |
| runtime contract (haiku) | `7bd5509aeb8ef0d11567996a80e40452c50e727977f84b78a8f8d85d4e3b9d0f` |
| runtime contract (sonnet) | `d3e175f3aea0403be977fb080c9ca4850e29be58dd65c570075c131bb7217cb3` |

Machine artifacts: [`phase7a_execution_manifest.json`](phase7a_execution_manifest.json),
[`phase7a_call_plan.json`](phase7a_call_plan.json).

## Fail-closed pre-run gate (`phase7a_execution.verify_pre_run`)
Recomputes the manifest/plan from the live repo and **fails closed** on any of: a scientific case
fingerprint, variant fingerprint, runtime contract, model id, N, evaluated-unit manifest, or
committed-artifact fingerprint that differs; or any accounting violation (34/84/50/10), foreign/
retired/Class-A/Phase-7B unit, or holdout/client/LaVita/Stacy term. **Current status: PASS (0 errors).**

## Result record contract (replication-level; reuses `run_library.run_single`, enriched)
Each of the 840 records preserves: `unit_id`, `base_case_id`, `cluster_root_id`, `unit_type`,
`family_id` / `perturbation_family`, `model`, `run_index` (0–4), `unit_fingerprint`,
`runtime_contract_fingerprint`, `package_fingerprint`, parsed `label`, `confidence`,
`confidence_state` (VALID/MISSING/INVALID), `label_correct`, `brier_contribution`, `parse_ok`,
`finish_reason`, `truncation_suspected`, `error` / `error_type`, `dry_run`. **Raw replication-level
records are preserved before aggregation** (no early aggregation to modal/accuracy only).

## Reporting (per model, never pooled)
Per-model families computed by `build_model_report`: model summary (accuracy all/bases/variants, mean
Brier over VALID confidences — Brier primary, ECE secondary/diagnostic), boundary-family results,
adversarial-family results, perturbation cluster/family results, replication stability tiers
(5/5 unanimous · 4/5 stable-majority · 3/5 fragile · ≤2 unstable), confusion matrix, high-confidence
wrong, systematic-failure triggers, limitations, taxonomy-review flags. **No pooled Agent-Arena
Robustness Score; Haiku and Sonnet never averaged.**

Frozen systematic-failure computations (facts only — WP-4 does not decide results), each **per model**
(cross-model recurrence is corroboration, not required):
- **Boundary** — same directional confusion (same `family:gold→pred`) on ≥2 independent cases, each
  wrong modal ≥3/5 → BLOCK; a single such case → INVESTIGATE.
- **Adversarial** — per A1–A8 family (2 cases): 0/2 PASS · 1/2 INVESTIGATE · 2/2 BLOCK
  (majority failure = wrong modal ≥3/5).
- **Perturbation** — same family majority-flips ≥2 clusters, or one cluster flips under ≥2 families
  (flip = variant modal ≠ cluster-root modal, ≥3/5) → BLOCK.
- **Replication** — ≥2 same-family bases fragile-or-worse (infra failures excluded) → BLOCK.

## Dry-run status (fake provider only; §30/§38)
- Provider: in-process `FakeLibraryProvider` — **0 real analytical calls**.
- End-to-end: 84 units × 5 × 2 = **840 records**, aggregation + per-model report families exercised.
- Rule-path tests proven: 5/5, 4/5, 3/5, provider-error; boundary blocker; adversarial 2/2; perturbation
  multi-cluster; single-cluster/multi-family; Haiku-only blocker; Sonnet-only blocker.
- All dry-run output is marked `dry_run: true` / `synthetic_non_analytical: true` — **never** to be
  presented as Phase-7A results.

## Resume / provider-error semantics (§34)
- `merge_records` keys each call on `(model, unit_id, run_index)`: a **completed** replication is never
  overwritten; a duplicate completed key is rejected; an errored key may be replaced by a later
  completed retry. Provider errors (`error`/`error_type`, no label) stay distinguishable from
  analytical errors (label present but wrong). Frozen `partial_run_recovery_rule`: resume only
  not-yet-executed calls; never re-run completed or failed calls; no selective reruns.

## Result freeze plan (§35) — future sequence, not executed now
PRE-RUN CONTRACT VERIFY (`verify_pre_run` == PASS) → REAL EXECUTION → RAW RESULT FREEZE (persist the
840 replication-level records) → RESULT MANIFEST / FINGERPRINT → **NO TUNING** → DETERMINISTIC
ANALYSIS (per-model report families). No result-driven prompt/gold changes; no result-driven case
retirement (governance: `docs/case_intake_policy.md` + runtime-contract prohibitions; any post-run
validity challenge stays visible in suite history).

## Executable QA provenance (WP-4.1 §3–§6) — the harness claims only what it ran
The GO decision is bound to a **real pytest execution**, never to a constant, expected count, or prose.
`phase7a_execution.real_run_preflight(run_qa=True)` (CLI `--preflight`) actually runs pytest in a
subprocess and records the command, `exit_code`, and collected/passed/failed/skipped counts parsed from
that process's own output, fingerprinted (outcome fields only). **Fail-closed**: no genuine execution →
`TESTS_NOT_EXECUTED` → NO-GO; `exit_code != 0`, any failure/error, or 0 collected → NO-GO. GO requires
the fingerprint gate **and** an all-green QA record.

Authoritative QA execution record for this readiness (regenerated fresh at real launch):
[`phase7a_qa_execution.json`](phase7a_qa_execution.json)
- exit_code `0` · collected **1525** · passed **1525** · failed **0** · skipped **0**
- qa_record_fingerprint `e8bc9dd02f766b82dd261a0079cbef2db8c27443188549a2d6b448a47c6724de`
- The **executed** count is authoritative; the number above is whatever that pytest process reported
  (it grows as tests are added and is never hardcoded as the truth condition). Scoped Ruff on changed
  Python: clean.

## Execution-type + three-layer provenance (WP-4.1 §7–§10)
- Every result record carries `execution_type`: the upcoming Haiku/Sonnet batch is
  `independent_model_adjudication`; a later replay/rerender of frozen records is
  `deterministic_reproduction_existing_records` (`run_metadata` flags `reproduction_of_frozen_records`),
  so a reproduction is never presented as a new independent judgment.
- Three layers are distinguishable (`run_metadata.layers`): **model** (model id +
  `runtime_contract_fingerprint`), **harness** (`execution_plan_version` + `package_fingerprint`),
  **report/render** (reporter + report-contract version).
- **Freeze separation**: the scientific/evidence freeze (case + variant fingerprints, committed at
  `84d75d4`) is distinct from the future raw analytical-result freeze; execution writes no scientific
  file, so a model run cannot overwrite the scientific freeze, and a reproduction gets its own
  `execution_type`.
- **Path portability**: the real-run path is repository-relative (`cwd` = repo root; artifacts under
  `analysis/phase7a_execution/`); the QA subprocess uses the local venv interpreter (`sys.executable`).
  No `/mnt/data/...` dependency.

## Known limitations
- Token/$ cost estimation is intentionally not built (WP-4 §33); only the mechanical call/retry counts
  are reported. Estimate cost externally from 840 calls × package size before launch if desired.
- The dry run proves mechanics and rule paths only; it asserts **nothing** about model performance.
- Post-render PDF/HTML QA and Stacy-Sims lessons are deferred (Phase 7B / 8+), out of Phase-7A scope.

## GO / NO-GO
**GO FOR REAL PHASE-7A EXECUTION.** All §43 criteria met: 34 bases / 84 units / 50 variants / 10
clusters resolve exactly; 2 exact model ids; N=5; 840 planned calls; runtime + scientific fingerprints
frozen and gate-verified (PASS); replication-level schema complete; per-model reports + all frozen
blocker rules computable; fake-provider dry run passes; resume/error semantics adequate; no holdout
leakage; 0 real analytical calls; full suite green.

## Exact launch command (future — DO NOT run in WP-4)
The WP-4 CLI is dry-run only (`--dry-run` uses the fake provider). The real Phase-7A run is a separate,
explicitly-guarded invocation that a later work package wires to the frozen Anthropic provider under
the runtime contract above, e.g.:

```bash
python -m agent_arena.phase7a_execution --preflight   # fingerprint gate + real pytest QA; must print GO first
# then the guarded real-execution entrypoint (WP-5), which must refuse to run unless verify_pre_run() PASSES
```

Do **not** execute the real run now. Next: HUMAN GO → REAL EXECUTION → RAW RESULT FREEZE →
DETERMINISTIC ANALYSIS.
