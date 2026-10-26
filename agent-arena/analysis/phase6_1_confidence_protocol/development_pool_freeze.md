# Phase 6.1 — Development-Pool Freeze (aggregate frozen; identities private)

**Governance:** Level 2 preparation checkpoint. This is the single most
leakage-sensitive artifact of Phase 6 (risk R-1). It freezes the **aggregate**
composition publicly while keeping **case identities private**, by curator
directive, because the full 27-case complement would reveal all 21 eligible cases —
and in the correlation/mechanism strata (eligible = holdout = 4) that would reveal
exact holdout membership.

---

## 1. Why identities are not published (resolved blocker)

Investigation this phase established, from public tracked artifacts only:

- `origin` (and every other public per-case field) does **not** encode eligibility:
  `origin: synthetic_fixture` (21 active) distributes overclaim 16 / corr 2 /
  solid 2 / mech 1, which does **not** match the eligible-21 distribution
  (5 / 8 / 4 / 4). Hypothesis falsified.
- No tracked, non-`internal_only` file carries a per-canonical-ID eligibility /
  blind / holdout flag (verified: `active_case_inventory.csv` columns; holdout
  selection docs contain no canonical IDs; annotator-facing `BIAA-*` packets are
  claim-isolated with no source identity).
- Eligibility ("has an approved annotator-facing packet") is resolvable only via
  the **sealed BIAA→canonical mapping**, which is a prohibited blind-ID mapping.

**Therefore the earlier requirement that the case-level manifest be reproducible
entirely from public tracked artifacts is formally revised** — it is incompatible
with holdout secrecy. Resolution: a **curator-controlled private development
manifest** (below).

## 2. Frozen aggregate composition (public)

| gold_label | dev-pool count |
|------------|:--------------:|
| solid | 8 |
| overclaim | 15 |
| correlation_vs_causation | 2 |
| mechanism_vs_evidence | 2 |
| **total** | **27** |

These equal `active − eligible` per label from public aggregates
(active 13/23/6/6 − eligible 5/8/4/4), and match the curator-frozen counts.
**correlation and mechanism are at n = 2 — diagnostic only** in all downstream
calibration (see `calibration_protocol.md §12–13`).

## 3. Eligibility / exclusion rule (frozen)

A canonical case is in the **development pool** iff it is:
- **active** (not `status: retired`, not `excluded_from_active_metrics`), **and**
- **not holdout-eligible** — i.e. it is **not** one of the 21 cases with a latest
  approved annotator-facing blind packet.

Excluded and reported separately:
- **retired** cases (2) — excluded entirely;
- **holdout-eligible** cases (21) — excluded (holdout-safety; sealed);
- the exclusion is applied by the curator against the sealed mapping, off-repo.

## 4. Reporting strata within the pool (frozen)

The 27 dev cases are reported in these separate strata (never pooled into a single
headline): **clear**, **borderline**, and **development-only** (its own stratum).
Exact per-stratum counts are part of the private manifest (they depend on
identities) and are certified at provisioning; only the per-label aggregate above is
frozen publicly now.

## 5. Private development manifest + salted commitment (curator-provisioned; PENDING)

- **Location:** the private manifest **and its salt** live in curator-controlled
  storage **outside Git** (never `internal_only/` in-repo, never committed).
- **Content:** the authoritative `DEV-id → canonical-id` mapping plus per-case
  `gold_label`, `gold_case_type`, stratum. Schema: `private_manifest_schema.json`.
- **Salted commitment (not a plain digest).** Because the canonical universe is
  small and the aggregate is public, an unsalted digest would allow offline
  enumeration. The public commitment is therefore
  `commitment = SHA256(private_random_salt ‖ canonical_manifest_bytes)` with a
  cryptographically random salt of **≥ 32 bytes** kept outside Git. Public
  verification (without the salt) cannot reveal membership; private verification
  (with manifest + salt) confirms integrity. Implemented in `dev_manifest.py`
  (`commitment` / `verify_commitment`); the plain `canonical_fingerprint` was
  removed.
- **Public tracked side (`development_pool_public_manifest.json`)** contains ONLY:
  schema/artifact tags, the **opaque manifest id** (`AA-DEVPOOL-6100`), the
  **commitment algorithm + version** (`salted-sha256` / `v1`), the **commitment
  value**, the **aggregate label counts + total**, and the **provisioning status** —
  **no canonical IDs, no BIAA mapping, no salt, no holdout-reconstruction info.** The
  exclusion rule (§3) is documented here in prose, not in the public manifest.
- **Commitment value:** `PENDING_CURATOR_PROVISIONING` until provisioned.

## 6. Status (frozen)

- Aggregate pool composition: **FROZEN** (public).
- Identity-level membership: **PENDING_CURATOR_PROVISIONING** (private).
- No canonical case IDs were accessed or inferred; no `internal_only` or private
  mapping was opened in this session.
- **Phase 6.2 is BLOCKED** until the curator creates and freezes the private
  manifest and records its SHA-256 fingerprint in
  `development_pool_public_manifest.json` (replacing the PENDING sentinel), verified
  by `dev_manifest.py`.

## 7. Provisioning handoff (a one-purpose, curator-controlled private execution)

The curator does not hand-author the manifest. A deterministic provisioning tool
(`provision_dev_manifest.py`, built and tested this phase with synthetic fixtures
only) performs the private run:

1. read the tracked active canonical library;
2. accept a **private** input listing the 21 eligible canonical ids (from the sealed
   mapping) — supplied only in the private execution;
3. derive `development pool = active − eligible`, excluding retired;
4. validate the derived aggregate equals **solid 8 / overclaim 15 /
   correlation_vs_causation 2 / mechanism_vs_evidence 2 / total 27**;
5. write the private manifest **outside Git**;
6. create (or accept) the **≥ 32-byte private salt** and compute the salted public
   commitment;
7. emit the clean public projection (no case ids, no salt) into
   `development_pool_public_manifest.json`, replacing the PENDING sentinel.

The tool **never** prints canonical / eligible / dev ids or mappings to stdout,
stderr, logs, exceptions, or test output — every diagnostic is id-free (counts /
labels only). This private execution is a **single-purpose curator operation**; its
session and outputs are never reused for model development or holdout evaluation.
Verification is `dev_manifest.verify_public_against_private(public, private, salt)`.
