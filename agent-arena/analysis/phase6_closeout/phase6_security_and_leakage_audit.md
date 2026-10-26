# Phase 6 — Security & Leakage Audit

A public-repository audit confirming Phase 6 introduced **no** private identity, mapping, raw
response, salt, or holdout material into Git, and that the proposed closeout artifacts embed
no private path. Performed with tracked material only; the private tree was not accessed.

## Access-boundary attestation

- The private development tree, private envelopes, raw responses, DEV→canonical mappings,
  private manifests, salt, candidate-eligibility data, holdout maps/gold/results, and
  annotator private responses were **not** accessed this session.
- Where a committed generator requires private envelopes (Phase 6.2 `build_calibration_reports.py`,
  Phase 6.4C `build_paired_comparison.py`), integrity was verified via **git blob equality**
  and **tests**, never by re-accessing private inputs.

## Tracked-content scan (Phase 6 surface)

| check | result |
|---|---|
| private result envelope tracked (`*_result_envelope.json`) | **NONE** |
| raw-response or retry-ledger file tracked | **NONE** |
| salt value / private-manifest content tracked | **NONE** (only detector *vocabulary*, below) |
| holdout map / gold / result tracked | **NONE** |
| DEV→canonical mapping tracked | **NONE** |
| absolute private path in Phase 6 artifacts | **NONE** as data (only detector *vocabulary*, below) |
| canonical `study-forensics-*` identity in Phase 6 artifacts | **NONE** (only synthetic high-number test placeholders) |
| BIAA / HLD identity in Phase 6 artifacts | **NONE** (only synthetic `901` test placeholders) |

## 64-hex values across tracked Phase 6 artifacts — all public

Every 64-hex token is a **public reproducible hash / commitment / synthetic-fixture digest** —
no salt, no private digest:

- `679233c6…4332` — public salted-sha256 **commitment** (`AA-DEVPOOL-6100`).
- `f7704fa5…` — shared **system-prompt** SHA-256 (Phase 6.2 contracts + envelopes).
- `85e7b929…` — prompt-only **baseline prompt** digest; `3aef083b…` / `62e62ef1…` — prompt-only
  **projection / parser** contract digests.
- `25ff2e83…` — Phase 6.2 **parser** contract; `92972e18…` — **task-packet-construction**
  digest; `d755c07e…` / `36a7d3b9…` / `e24e077d…` — **agent-config** SHA-256 (Haiku / Opus /
  Sonnet).
- `67b8df9d…` / `8b1cbb8b…` — Phase 6.3 **example report / input digests**, reproducible from
  the committed **synthetic** fixture (public, not private).

## Detector-vocabulary (benign, not leaks)

Two classes of forbidden-token *literals* appear by design and are **not** private data:

1. **Leakage-detector vocabulary** in generators — e.g. `_SALTY_KEYS = ("salt", "salt_hex",
   …)` in `build_paired_comparison.py` (byte-identical to the committed Phase 6.2 generator)
   and the regexes in `forensic_report.py`.
2. **Schema/documentation boundary lists** — e.g. `forensic_report_schema.json`
   `x_forbidden_anywhere` enumerates the absolute-home-path marker, the private-tree marker,
   and the internal-only marker as tokens a report must **never** contain. This is a guardrail
   declaration, not an embedded path.

Synthetic test placeholders use the documented high-number (`9xx`) range — well outside any
real identity range — to prove the detectors fire, matching the existing tracked test
convention.

## Pre-existing Phase 5 `internal_only/` (out of Phase 6 scope)

Tracked `internal_only/` directories exist **only under `analysis/phase5_*`** (blind-IAA /
revalidation / holdout-augmentation ID maps and audits). These are **pre-existing Phase 5
artifacts**, committed under the Phase 5 tags; Phase 6 neither created nor modified them, and
this closeout does not touch them. No `internal_only/` path exists anywhere under
`analysis/phase6_*`. (Their handling is a Phase 5 governance matter, noted here only for
completeness, not reopened by this closeout.)

## Proposed closeout artifacts

The new `analysis/phase6_closeout/` markdown files embed **no** absolute private path, canonical
id, BIAA/HLD id, salt/private digest, raw response, mapping, input envelope, or holdout
content. A final leakage scan over every proposed closeout blob is recorded in
`phase6_closeout_status.md`.

## Verdict

**Phase 6 introduced no private-identity, mapping, raw-response, salt, or holdout material
into Git.** The leakage posture is clean.
