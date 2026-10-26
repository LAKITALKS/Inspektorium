# Phase 7 — Existing-Control Inventory (STEP 2 + F)

Coverage legend: **PRESENT** (works today) · **PARTIAL** (data/mechanism exists, enforcement or
scope missing) · **ABSENT** (no equivalent) · **REDUNDANT** (prompt proposes what already exists).

All file references are concrete and verified this session.

## D. Existing components we can reuse (named)

| component | file | what it already gives Phase 7 |
|---|---|---|
| Deterministic report builder + 2 renderers | `src/agent_arena/forensic_report.py` | pure, no-network, no-wall-clock builder; **one report object → JSON + full MD + executive MD** (single source of truth); failure modes **echoed, never inferred**; leakage scan; recomputable input/report digests |
| Frozen report contract | `analysis/phase6_3_report_prototype/forensic_report_schema.json` | `report_schema_version` const **6.3.0**; `additionalProperties:false`; frozen label/tier/role/confidence vocabularies; `x_forbidden_anywhere` leak list |
| Numeric rewrite guard | `forensic_report._rewrite_guard` | every number in a rewrite must exist in the input corpus, else blocked → *no safe rewrite* (embryonic monotonicity, **numeric only**) |
| Evidence direction | `schemas.EvidenceRole` (+ `EvidenceSpan.role`, report `evidence_items[].role`, `supporting` / `contradicting_or_limiting`) | supporting / weakening / contradictory / missing_expected — the **data model for symmetry already exists** |
| Internal evidence spans | `schemas.EvidenceSpan` (`text`, `source_field`, `char_start/char_end`, `relevance`, `role`) | span binding to the **agent response** (`steps[2]`, `final_answer`) |
| Gold/adjudication metadata | `schemas.Task` (`gold_label`, `gold_alternative_reading`, `gold_case_type` clear/borderline, `gold_confidence`, `gold_justification`) | boundary/primary-label test scaffolding for 7A |
| Taxonomy checker | `src/agent_arena/study_forensics_checker.py` | 4 frozen labels; negation-aware FP suppression; hedge/decorative-uncertainty detection |
| Frozen precedence rule | `docs/taxonomy_precedence.md`, `docs/study_forensics_taxonomy.md` | `overclaim` = generic/residual; specific label only on **definitional trigger**; anti-co-evolution; `mechanism_vs_evidence` excludes surrogate/in-vitro (case054) — governs the overclaim→over-specific hypothesis **without** a taxonomy change |
| Leakage / contamination guard | `src/agent_arena/packet_integrity.py`, `forensic_report.leakage_findings` | deterministic offline private-id/path/gold detection; reused as baseline leak guard |
| Confidence semantics | `src/agent_arena/confidence_validity.py` | VALID / MISSING / INVALID; **never coerced to 0.0**; reused everywhere |
| Calibration engine | `src/agent_arena/calibration.py` | Brier primary, ECE secondary, costed abstention, small-n flags |
| Governance provenance chain | `schemas.DecisionEntry` / `UpstreamStep` / `AuditSummary` / `DependencySummary`; `src/agent_arena/audit_trail.py`; `.agent_arena/decisions.jsonl` | human-decision provenance + **propagation-risk** chain — the natural spine of an *audit manifest* |
| Client-facing renderers | `src/agent_arena/reporting.py` (MD/HTML/PDF), `src/agent_arena/reporter.py` (forensic dossier) | existing artifact surface = the object the final binding check must guard |
| Canonical bytes / digests | `forensic_report.canonical_*_bytes`, `report_digest` | reusable fingerprinting for provenance freeze |

## Requirement → coverage → gap → action

| # | requirement | existing component | coverage | gap | recommended action |
|---|---|---|---|---|---|
| 1 | Claim → source binding | `claim.claim_source_reference`; `EvidenceSpan.source_field` | PARTIAL | free-text string; not an immutable object; no exact quote/URL/retrieved_at | add optional `claim.provenance` sub-object; keep string for back-compat |
| 2 | Immutable **web-claim** provenance (URL, retrieved_at, exact_span, snapshot, fingerprint) | report `provenance` block (but it is **run/model** provenance: digests, commit, parser_status) | ABSENT (for web claim) | no page state, no exact span, no snapshot, no `archived vs live` state | new `claim.provenance` with `provenance_state`; reuse digest machinery for `content_fingerprint` |
| 3 | Search-scope / negative-evidence discipline (Levels A–D) | none (grep: no real `search_scope`) | ABSENT | "not found" freely generalizes to "does not exist" | new optional `evidence.search_scope` + validator gating `negative_evidence_level` (D forbidden by default) |
| 4 | Evidence direction | `EvidenceRole` + role fields + `contradicting_or_limiting` | PRESENT (data) / ABSENT (enforcement) | nothing forces both directions from the **same source** to survive | symmetry **contract test**, not a new field |
| 5 | Evidence IDs / finding→evidence binding | `failure_modes.detected[].evidence_refs` (free strings) | PARTIAL | items have no stable id; refs not validated to resolve | add optional `evidence_items[].evidence_id`; validator: refs must resolve when ids used |
| 6 | Self-critique (steelman / prosecution / critic-overreach / counterevidence) | `uncertainty.alternative_plausible_label` (+rationale); `GroundingAudit`; `postmortem`; anti-co-evolution rule | PARTIAL | alt-label check exists; no explicit steelman/prosecution/failed-criticisms; no counterevidence-search pass | add optional `self_audit` block; do **not** build 10 agents — one structured pass |
| 7 | Omission / evidence-symmetry audit over source categories | evidence roles + `contradicting_or_limiting` | PARTIAL→ABSENT | no independent pass over favorable/unfavorable/null/mixed/limitations/subgroup/AE | add optional `evidence.source_symmetry`; drive Fantacone regression |
| 8 | Summary strength / semantic monotonicity | `_rewrite_guard` (numeric); renderer renders only from report object; exec summary preserves material uncertainty | PARTIAL | numeric-only, not semantic; no parent→client strength lattice | add `allowed_summary_strength` + strength lattice + monotonicity validator |
| 9 | Client-finding binding (no new proposition) | single-source-of-truth builder; renderer adds no claims | PARTIAL | no explicit `client_finding` bound to a parent `finding_id`; no cross-summary "no new proposition" check | add optional `client_finding` block bound to finding id |
| 10 | Final artifact binding check (A–G) + release gate | none as a gate (leak scan + rewrite guard are partial) | ABSENT | no BLOCKER/MAJOR/MINOR gate over the finished artifact | new deterministic `artifact_binding_check` → release condition |
| 11 | System-QA reason codes (separate from 4 labels) | claim-level `failure_modes` vocabulary (11 modes) | PARTIAL | those are **claim-level**; pipeline-QA codes absent and must not touch the 4 labels | new small `system_qa` vocabulary (deduped — see postmortem §STEP 4) |
| 12 | Deterministic checks / digests | `forensic_report` digests; `packet_integrity`; canonical bytes | PRESENT | — | reuse for artifact QA |
| 13 | Confidence handling | `confidence_validity` | PRESENT | — | reuse unchanged |
| 14 | Audit manifest | `audit_trail` + `DecisionEntry`/`UpstreamStep` | PARTIAL | not yet emitted per client operation | reuse chain as the manifest spine (governance-efficiency, 7A.6) |

## F. Redundant proposals — already handled, do NOT rebuild

The Phase-7 prompt proposes several things the repo already has. Extend these; do not create a
parallel system.

- **Run/model provenance fields** (`input_digest`, `report_generation_digest`,
  `repository_commit`, `parser_status`, `audit_trail`, `warnings`) — already in the report
  `provenance` block. Add **web-claim** fields alongside; don't duplicate the run-provenance block.
- **"Renderer must not invent facts"** — the renderer already renders **only** from the validated
  report object (single source of truth); `_rewrite_guard` already blocks unsupported *numeric*
  facts. Extend to **semantic** monotonicity; don't rebuild the renderer.
- **Evidence-direction enum** — `EvidenceRole` exists; reuse it. Do not add a second direction enum.
- **A frozen failure-mode vocabulary** — 11 claim-level modes already exist in
  `forensic_report.FAILURE_MODES`. The new system-QA codes are a **separate** small set, not
  additions here and **not** additions to the four labels.
- **Confidence VALID/MISSING/INVALID** — done (`confidence_validity`).
- **Leakage detection** — done (`packet_integrity` + `leakage_findings`); reuse.
- **Governance/decision provenance chain** — done (`DecisionEntry`/`UpstreamStep`); reuse as the
  audit manifest, don't invent a new chain.
- **Overclaim→over-specific "fix"** — governed by `docs/taxonomy_precedence.md` already; this is a
  **hypothesis tested with cases** (7A), never a taxonomy edit.

## G. Minimal schema changes (STEP 5 summary — full deltas in roadmap doc)

Home: the existing `forensic_report` input/report contract (bump `6.3.0 → 6.4.0`), **all additions
optional and back-compatible** so every current 6.3.0 fixture stays valid. Minimal set:

1. `claim.provenance` — immutable web-claim object: `canonical_url`, `page_title`, `retrieved_at`,
   `exact_span`, `context_before/after`, `content_fingerprint`, `snapshot_reference`,
   `provenance_state ∈ {archived_snapshot, current_live, modelled, published_literature}`.
2. `evidence.search_scope` — `scope_id`, `sources_reviewed[]`, `queries[]`, `date_cutoff`,
   `completeness ∈ {single_source, reviewed_set, documented_search}`; each negative claim carries
   `negative_evidence_level ∈ {A,B,C,D}`; **D forbidden** unless explicit evidence-of-absence.
3. `evidence.evidence_items[].evidence_id` (optional) + resolve-check for `evidence_refs`.
4. `evidence.source_symmetry` — per-source omission audit over the material categories.
5. `verdict.allowed_summary_strength` + `client_finding{ display_claim, client_verdict,
   client_explanation, finding_id }` + a `summary_strength` lattice + monotonicity validator.
6. `system_qa{ checks[]{ code, severity, detail } }` — deduped codes, **separate** from the 4 labels.
7. `artifact_binding_check{ findings[]{ check, severity }, release_status }` — BLOCKER/MAJOR/MINOR.
