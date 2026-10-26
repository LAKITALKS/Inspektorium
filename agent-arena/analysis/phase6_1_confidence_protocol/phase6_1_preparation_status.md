# Phase 6.1 — Preparation Status (methodology frozen; provisioning gate CLOSED)

**Governance:** Level 2 preparation checkpoint. **Not a full closeout.** Phase 6.1
methodology is prepared and frozen; the single curator-provisioning gate is now
**closed** (private development manifest + ≥32-byte salt frozen outside Git; salted
commitment recorded). Phase 6.2 remains gated on its own execution contract. Baseline:
HEAD `54c06c4`; Phase-5 tag `v0.8.13` → `cfb78de` unchanged.

---

## Curator corrections applied (this revision)

1. **Salted commitment** replaces the plain unsalted SHA-256 digest. The public
   commitment is `SHA256(private_salt ‖ canonical_manifest_bytes)` with a ≥32-byte
   random salt kept outside Git; public verification cannot reveal membership. The
   plain `canonical_fingerprint()` was removed.
2. **Small-sample calibration reporting revised.** **Brier is the primary**
   probabilistic score; **ECE is secondary/descriptive**. Primary reliability uses
   **five fixed equal-width bins**; a ten-bin view is a sensitivity check only. Bins
   with `n < 5` are not interpreted; empty bins stay visible; correlation/mechanism
   (n = 2) are descriptive only.
3. **Provisioning workflow added** (`provision_dev_manifest.py`): deterministic
   derivation of `active − eligible` (retired excluded), aggregate validation, salt +
   salted commitment, clean public projection — **id-free**, tested with synthetic
   fixtures only. No real provisioning performed.

## Completed preparation artifacts (frozen)

| artifact | status |
|----------|--------|
| `confidence_semantics.md` | ✅ meaning, [0,1] scale, VALID/MISSING/INVALID, non-silent handling; Brier-primary/5-bin note |
| `calibration_protocol.md` | ✅ all definitions pre-registered; Brier primary, ECE secondary, 5 primary bins (+10-bin sensitivity) |
| `abstention_policy.md` | ✅ rule + full cost model; evaluated, not assumed beneficial; small-sample consistent |
| `development_pool_freeze.md` | ✅ aggregate frozen; identities private/pending; salted-commitment + provisioning handoff |
| `phase6_2_execution_contract.md` | ✅ inputs/outputs/acceptance/stop; private-runner uses salted-commitment verify; 5-bin/Brier outputs |
| `private_manifest_schema.json` | ✅ schema + validation; salted-commitment public side |
| `development_pool_public_manifest.json` | ✅ salted-commitment public side; commitment **frozen** (provisioned) |
| `src/agent_arena/confidence_validity.py` + tests | ✅ deterministic; MISSING/INVALID ≠ 0.0 |
| `src/agent_arena/dev_manifest.py` + tests | ✅ schema/aggregate validation, salted commitment, public-projection leakage guard |
| `src/agent_arena/provision_dev_manifest.py` + tests | ✅ deterministic derivation; id-free; synthetic-only |

**Tests:** full suite **1079 passed** (1027 prior + 52 new); ruff clean on all new
files. No model calls; no holdout/`internal_only`/private-mapping access; no
canonical ids accessed or inferred.

## Calibration protocol pre-registration checklist (all frozen before results)

correctness definition ✅ · confidence validity ✅ · missing-confidence handling ✅ ·
**Brier primary** ✅ · **ECE secondary/descriptive** ✅ · **5 primary fixed bins
(+10-bin sensitivity)** ✅ · accuracy-by-confidence (bin count / mean conf / accuracy /
absolute gap; n<5 not interpreted; empty bins visible) ✅ · selective accuracy +
coverage ✅ · abstention cost ✅ · class-imbalance (micro+macro) ✅ · clear-vs-borderline
strata ✅ · development-only stratum ✅ · minimum sample-size disclosures (n≥5; corr/mech
n=2 descriptive only) ✅ · no-threshold-optimization-then-unbiased-reuse ✅ ·
reproducibility manifest requirement ✅.

## Phase 6.1 acceptance criteria

| id | criterion | status |
|----|-----------|--------|
| A6.1-1 | confidence semantics incl. non-silent missing handling | ✅ frozen + tooled |
| A6.1-2 | dev pool frozen without holdout reference, from holdout-safe set | ✅ aggregate frozen; identity-level manifest **provisioned** (private; salted commitment recorded) |
| A6.1-3 | metrics/bins/thresholds pre-specified before results | ✅ frozen |
| A6.1-4 | Level-2 prep; no results-driven choices | ✅ |

The A6.1-2 "reproducible entirely from public tracked artifacts" clause was formally
revised (see `development_pool_freeze.md §1`): incompatible with holdout secrecy, so
identities live in a curator-controlled private manifest and only the aggregate + a
**salted** commitment are public.

## The provisioning gate — CLOSED (Phase 6.2 unblocked, pending its own §5 authorization)

**PROVISIONED** — completed in a one-purpose, isolated private execution in which the
curator, using the committed provisioning logic:
1. resolved the private list of 21 eligible ids → derived + validated the 27-case pool
   (solid 8 / overclaim 15 / correlation 2 / mechanism 2);
2. wrote the private manifest **and ≥32-byte salt** outside Git (curator-controlled
   storage; `0600`);
3. recorded the **salted commitment** in `development_pool_public_manifest.json`,
   replacing the PENDING sentinel;
4. confirmed `dev_manifest.assert_public_clean()` → no identities/salt in the public
   file.

`dev_manifest.verify_public_against_private()` now reports the gate as **satisfied**.
Phase 6.2 remains gated on `phase6_2_execution_contract.md §5` and explicit
result-generation authorization; **it has not begun.**

## Boundaries held (this provisioning session)

- No `phase6_1_closeout.md` marked fully-passed (this is a gate closure, not a full closeout).
- No Phase 6.2 result generation; no live model calls; no threshold tuning.
- No holdout / per-HLD gold / `internal_only` access; the sealed holdout stays unopened.
  Only the minimum eligibility mapping needed to identify the 21 eligible ids was read,
  as authorized for this one-purpose provisioning.
- Committed only the public projection + this status doc; the private manifest, salt, and
  mapping never entered Git, logs, diffs, or terminal output.
