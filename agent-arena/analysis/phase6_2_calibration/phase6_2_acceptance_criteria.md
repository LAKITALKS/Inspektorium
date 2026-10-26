# Phase 6.2 — Acceptance Criteria & Stop Conditions

Split into **preparation** criteria (this session) and **execution** criteria (the
later, separately authorized private run). Pre-specified before any results.

## Preparation acceptance (this session)

P-1. Anonymized result contract + schema exist; result records use opaque `DEV-####`
ids and forbid canonical/BIAA/salt fields (`additionalProperties:false`).

P-2. Deterministic offline tooling implements, exactly per the frozen protocol:
result validation; VALID/MISSING/INVALID confidence (no 0.0 coercion); correctness;
**binary top-label Brier (primary)**; 5-bin reliability (all bins retained);
secondary ECE; 10-bin sensitivity; accuracy-by-range; coverage; selective accuracy;
abstention error rate; costed abstention; micro + macro(n≥5); clear/borderline/
development_only strata; small-`n` flags.

P-3. Tooling **rejects or flags**: duplicate opaque ids; malformed labels;
confidence outside `[0,1]`; boolean confidence; missing/invalid confidence coerced to
0.0; unknown strata; impossible/inconsistent correctness; per-model totals ≠ frozen
27 / wrong label aggregate; reports omitting empty bins; threshold optimization on the
eval set. Each is covered by a test.

P-4. Reports are deterministic (idempotent `build_report`), machine-readable +
concise human-readable, marked small-sample; all outputs id-free (opaque/class only).

P-5. Full suite green; lint clean on changed files; no model calls; no private
material accessed; no frozen Phase 6.1 artifact modified.

P-6. **Envelope binding.** The analyzer accepts records only via an envelope whose
`manifest_id` + public salted `commitment` equal the tracked
`development_pool_public_manifest.json`, with matching `protocol_version`,
`expected_record_count = 27`, and `declared_gold_aggregate = 8/15/2/2`; canonical/
BIAA/HLD ids and salt are rejected anywhere. Tested.

P-7. **Gold ≠ predicted.** The 8/15/2/2 aggregate is enforced on `gold_label` only;
predicted labels are never constrained; a valid set whose predicted distribution
differs substantially from 8/15/2/2 passes; predicted-label distribution is reported.
Tested.

P-8. **Denominators.** Accuracy uses all records (valid labels) regardless of
confidence; Brier/reliability/ECE use VALID-confidence records; MISSING/INVALID are
counted, never coerced to 0.0; each metric reports its denominator; a warning fires
when valid coverage `< 100%`. Tested (missing confidence changes the confidence
denominator but not the classification outcome).

P-9. **Status/provenance.** Every report states DEVELOPMENT-NOT-HOLDOUT, small-sample,
no-universal-superiority, no-threshold-optimized, `manifest_id` + commitment, protocol
version, valid/missing/invalid counts, denominators, and `synthetic_fixture` status.
Frozen bins/τ grid/abstention-cost constants appear in report metadata. Tested.

**Preparation stop conditions:** any need for the private manifest/holdout/
`internal_only`; any change to frozen methodology; any real result generation.

## Execution acceptance (LATER — separate authorization; NOT this session)

E-1. Runs only via the trusted private runner against the fingerprint-verified
27-case manifest; emits anonymized records only.

E-2. Metrics computed exactly as pre-registered here; result manifest binds numbers
to (private-manifest salted commitment + code commit + params + seed); reproducible.

E-3. Abstention reported as costed trade-off; adopted only against the frozen
conditional criterion, else "not demonstrated beneficial"; no threshold tuned then
reported as unbiased.

E-4. No holdout; no universal-superiority claim; small-sample caveats present.

**Execution stop conditions:** fingerprint mismatch; any holdout/`internal_only`
need; result-driven re-tuning; any canonical id in an output.

## Remaining execution gate
Phase 6.2 execution is **PENDING SEPARATE CURATOR AUTHORIZATION** (trusted private
run + explicit result-generation approval). Preparation completion does **not**
authorize execution.
