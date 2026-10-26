# Phase 7B — Final Artifact-QA / Release-Gate Consolidation (implementation report)

Bounded Phase-7B slice. Deterministic, offline, no model call, no holdout access, no LaVita
identity in any executable artifact. Consolidates the already-implemented Phase-7B QA
primitives into ONE authoritative release decision. No new evidence dimension, no new claim
taxonomy, no post-render / PDF work, no search infrastructure.

## Objective

```
EXISTING PHASE-7B CONTROLS
→ ONE QA ENTRYPOINT
→ COMPLETE QA FINDINGS (no early exit)
→ DETERMINISTIC SEVERITY ROLL-UP
→ RELEASABLE / NOT RELEASABLE
→ MACHINE-READABLE RELEASE REPORT
```

## Existing controls consolidated (reused, not redesigned)

All five primitives already existed in `src/agent_arena/artifact_binding.py`; the inline
A/B/C/D/F logic previously living inside `final_binding_check` was extracted into two named,
independently callable functions so the mandatory set is explicit and testable:

| Control | Function | Codes |
|---|---|---|
| Finding / artifact binding (A,B,C,F) | `check_finding_binding` *(extracted)* | `artifact_source_binding_drift` |
| Summary-strength monotonicity (D) | `check_summary_strength` *(extracted)* | `summary_strength_escalation`, `artifact_source_binding_drift` |
| Evidence symmetry | `check_evidence_symmetry` | `asymmetric_evidence_selection` |
| Value-origin provenance | `check_value_origin` | `model_output_to_literature_fact`, `source_reported_to_modelled_fact`, `unresolved_value_origin`, `artifact_source_binding_drift` |
| Search-scope binding | `check_search_scope` | `search_scope_to_world_generalization`, `unresolved_search_scope`, `artifact_source_binding_drift` |

Leakage / private-identity integrity is enforced UPSTREAM at `load_forensic_record`
(fail-closed raise reusing the `forensic_report` leakage vocabulary), so the gate operates
on an already leak-checked record — not duplicated into the gate.

## Mandatory-check set (explicit, ordered registry)

```python
MANDATORY_PHASE7B_CHECKS = (
    ("finding_artifact_binding",      check_finding_binding),
    ("summary_strength_monotonicity", check_summary_strength),
    ("evidence_symmetry",             check_evidence_symmetry),
    ("value_origin_provenance",       check_value_origin),
    ("search_scope_binding",          check_search_scope),
)
```

A static ordered tuple (no plugin framework). A future release path invokes this registry;
a control cannot be silently forgotten (Test S asserts `checks_run == registry`). Completeness
audit: the set of registry callables equals the set of public `check_*` functions — no orphan
validator, and `final_binding_check` delegates to the SAME path so the two cannot diverge.

## Central entrypoint

`evaluate_artifact_release(record) -> ReleaseReport`. Deterministic flow: run every registry
control in order → collect all findings → sort findings canonically → severity roll-up →
release decision → build report bound to the input fingerprint. No model call, no I/O, no
wall-clock in the canonical payload. `final_binding_check` is retained as a backward-compatible
`BindingResult` shim over the identical execution path.

## Release-report contract (`ReleaseReport`, internal QA object)

Defined in `artifact_binding.py` alongside the existing `BindingResult` (the local convention
for QA *result* objects). Fields: `release_report_id` (deterministic: `RR-<record_id>-<fp[:12]>`),
`forensic_record_id`, `qa_contract_version`, `record_fingerprint`, `checks_run[]`
(`CheckRun{name,status,finding_count}`), `findings[]` (existing `BindingFinding`),
`severity_counts{critical,major,moderate,minor,stylistic}`, `releasable`, `blocking_codes[]`
(sorted), `decision_reason`. A deliberate **no timestamp** — the report is fully canonical so
determinism needs no field exclusion.

`PHASE7B_RELEASE_GATE_VERSION = "0.1.0"` — compact internal contract version, NOT a public API
guarantee and NOT the frozen Forensic Report 6.3.0.

## Severity policy (existing enum; no second taxonomy)

Reuses `FailureSeverity`. Frozen release rule (identical to the pre-existing
`BLOCKING_SEVERITIES` convention — not newly invented):

```
releasable == (critical_count == 0 AND major_count == 0)
```

`moderate` / `minor` / `stylistic` are non-blocking. **All eight current Phase-7B QA codes map
to `critical`** (audited — see below); no code currently maps to `major` or below, so the
sub-critical branches are exercised by the roll-up unit tests (C, D) with typed synthetic
findings, documented honestly rather than by fabricating a major classification.

### QA-code / severity audit

| QA code | severity | blocking? | originating check |
|---|---|---|---|
| `artifact_source_binding_drift` | critical | yes | binding / value-origin / search-scope |
| `summary_strength_escalation` | critical | yes | summary_strength |
| `asymmetric_evidence_selection` | critical | yes | evidence_symmetry |
| `model_output_to_literature_fact` | critical | yes | value_origin |
| `source_reported_to_modelled_fact` | critical | yes | value_origin |
| `unresolved_value_origin` | critical | yes | value_origin |
| `search_scope_to_world_generalization` | critical | yes | search_scope |
| `unresolved_search_scope` | critical | yes | search_scope |

No inconsistency found: every `SYSTEM_QA_CODES` member has exactly one severity, no orphan
severity entries, no typo variants, no QA/claim-label overlap. No severity was changed (would
require curator review per Section 27).

## Deterministic decision & failure aggregation

- **No early exit.** Every control runs regardless of earlier failures; one record may report
  binding + symmetry + value-origin + search-scope failures simultaneously (Tests E, F).
- **No dependency false pass.** Controls are total functions: an unresolvable parent surfaces
  as a finding (binding drift, critical) and blocks; dependent checks (strength, symmetry)
  abstain (0 findings) rather than fabricate a pass — never a silent success (Test G). No
  top-level check is ever skipped, so `CheckRun.status` is always `"ran"` (no workflow-status
  taxonomy introduced).
- **Deterministic ordering.** Findings are sorted by a content-based key
  `(severity_rank, code, check, client_finding_id, refs, detail)` → identical output for
  identical input (Test Q) and stable under irrelevant input-collection reordering (Test R).
  `blocking_codes` sorted; `severity_counts` fixed key order.

## Input fingerprint

`record_fingerprint(record)` = `sha256(canonical_report_bytes(record.model_dump(mode="json")))`,
reusing the existing `forensic_report` canonical-bytes convention (sorted keys, fixed
serialization) and the module's `hashlib.sha256` convention — no new hashing algorithm. Binds a
report to the exact record it evaluated; changes when any release-relevant field changes
(Test P).

## Dataset isolation

One new generic synthetic fixture `tests/fixtures/pipeline_qa/qa_release_gate_consolidated.json`
(generic intervention-vs-comparator; no commercial / LaVita identity, no gold label).
Structurally isolated (data class C): contributes **0** to case library / development pool /
holdout / evaluation counts (Test T + `test_pipeline_qa_isolation.py`).

## Scope / limitations (precise terminology)

- **Structured / pre-render QA only.** The gate verifies the structured client representation.
  It does NOT parse or verify any rendered PDF/HTML (Section 22, 32). No post-render source
  matching, no OCR, no literature-search automation (Section 33).
- **Structured source-binding depth.** Uses the deepest binding already available
  (`evidence_id → source_id → exact_reference`) where present; e.g. a source-reported value
  requires source id + locator. No new source database / parser is built (Section 21).
- **No aggregate score.** The gate answers RELEASABLE / NOT RELEASABLE plus explicit findings —
  never a quality/trust/forensic score (Section 18).

```
PASSING THIS GATE DOES NOT CERTIFY SCIENTIFIC TRUTH OR EVIDENCE COMPLETENESS.
```

A release-gate PASS means the structured artifact satisfies the implemented Phase-7B QA
contract — NOT scientific truth, source quality, exhaustive literature, causal validity, or
external expert validation.

## Schema versioning

Forensic report **6.3.0 unchanged**. `FORENSIC_RECORD_SCHEMA_VERSION` kept at **0.1.0** (no
record fields added). New internal `PHASE7B_RELEASE_GATE_VERSION = "0.1.0"` introduced for the
serialized `ReleaseReport` contract (tested as a stable deterministic structure).

## Tests (1393 → 1414, +21)

`test_release_gate_consolidation.py` (+20, Tests A–T): A clean releases · B single critical
blocks · C single major blocks (roll-up) · D sub-major non-blocking · E multiple failures all
reported · F binding failure does not mask others · G unresolvable dependency no false pass · H
symmetry · I value-origin derived→source · J reverse value-origin · K unresolved value origin ·
L search-scope globalization · M narrowed scope without basis · N summary-strength escalation ·
O clean mixed-evidence releases · P fingerprint tracks input · Q determinism · R canonical
finding order · S mandatory-check coverage · T pipeline-QA isolation.
`test_pipeline_qa_isolation.py` (+1): consolidated fixture contributes 0 cases. All prior
Phase-7B regressions remain green (full suite): **1414 passed**.

## Known remaining 7B gaps (classification only — not implemented here)

- **Post-render artifact verification** — OPEN / BELONGS LATER (separately scoped; not required
  to open 7A).
- **Renderer-generated novel scientific claims** — OPEN / BELONGS LATER (a post-render concern).
- Immutable claim provenance · evidence symmetry · client-finding binding · summary-strength
  monotonicity · derived-value provenance · search-scope binding · final structured artifact
  binding · release gate — **CLOSED** (structured layer).
- Compression preserving material exceptions — **PARTIAL** (evidence-symmetry covers material
  omission at the structured level; free-text compression is out of scope).
