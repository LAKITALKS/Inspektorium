# Phase 7B — First Vertical Slice: Artifact Binding (implementation report)

Implements the first Phase-7B slice only. Not all of Phase 7. Deterministic, offline,
no model call, no holdout access, no LaVita identity in any executable artifact.

## Objective

Prove one end-to-end chain and gate it deterministically:

```
FROZEN CLAIM → FROZEN PROVENANCE → EVIDENCE ITEMS → INTERNAL FINDING
            → CLIENT FINDING → EVIDENCE SYMMETRY CHECK → FINAL BINDING CHECK
```

## Architecture reused (not rebuilt)

- `schemas.EvidenceRole` — reused as the single evidence-direction enum (no second enum).
- `schemas.FailureSeverity` — reused as the QA severity model (BLOCKER ≙ CRITICAL; MAJOR blocks).
- `forensic_report.leakage_findings` — reused to reject private-identity/path leakage in fixtures.
- `hashlib` canonical-digest pattern (as in `forensic_report`) — reused for `content_fingerprint`.
- `run_library.discover_cases` — inspected to derive an **enforceable** isolation invariant.

New components and why they were necessary:
- `schemas.py` (additive section) — typed chain objects (`ClaimProvenance`, `QAEvidenceItem`,
  `InternalFinding`, `ClientFinding`, `ForensicRecord`) with stable ids/cross-references, which
  the dict-based 6.3.0 report contract does not provide. Placed in the domain-model home.
- `src/agent_arena/artifact_binding.py` — the deterministic QA logic (symmetry primitive + final
  binding gate). A focused QA module, **not** a second reporting architecture.

## Schema changes

- **Forensic report 6.3.0: UNCHANGED.** No bump, no field change, zero migration. All existing
  6.3.0 fixtures validate byte-for-byte as before.
- **New additive contract:** `FORENSIC_RECORD_SCHEMA_VERSION = "0.1.0"` (`schemas.py`). Optional
  fields default sensibly; the ids required by the QA gate are mandatory in the QA path only.
- The broader §5.1–§5.8 report-side deltas and any future `6.4.0` bump remain a **later** 7B work
  package (documented in `analysis/phase7_startup/phase7_roadmap_and_acceptance.md`).

## QA fixture isolation (enforceable)

- Fixtures live at `tests/fixtures/pipeline_qa/*.json` (data class C), **outside** `tasks/`.
- `discover_cases` globs `tasks/study_forensics/*.yaml` for `STUDY_FORENSICS` Tasks — a different
  directory, extension, and schema. Triple structural isolation.
- `test_pipeline_qa_isolation.py` asserts: QA dir holds no `*.yaml`; fixtures live outside the
  tasks tree; discovery never yields a QA path; pointing discovery at the QA dir yields **zero**
  cases; a ForensicRecord is not a loadable `Task`. No naming-convention reliance.

## Invariants implemented

- **Symmetry** (`check_evidence_symmetry`, first independent 7B QA primitive): if a whole
  direction (`supports_finding` vs `opposes_or_qualifies_finding`, derived from `EvidenceRole`)
  present in the parent finding's **material** evidence is entirely dropped by the client finding
  → `asymmetric_evidence_selection` (BLOCKER). Direction-neutral: dropping either side fails.
- **Binding** (`final_binding_check` A/B/C/F): client must reference an existing parent finding
  (A); existing evidence (B); evidence bound to that finding's context (C); and the parent's
  frozen provenance (F). Any violation → `artifact_source_binding_drift` (BLOCKER). Encodes
  *NO CLIENT SUMMARY WITHOUT FINDING BINDING* and *downstream must reference frozen provenance*.
- **Monotonicity** (check D, minimal): `rank(client_strength) ≤ rank(allowed_summary_strength)`
  on the ordered `SUMMARY_STRENGTH_ORDER` lattice, else `summary_strength_escalation` (BLOCKER).
  Evidence strength and search completeness are kept as separate dimensions.
- **Release gate:** `releasable = (no finding with severity in {CRITICAL, MAJOR})`; counts exposed.

Pipeline-QA codes (`SYSTEM_QA_CODES`) are asserted **disjoint** from the frozen four-label claim
taxonomy (`CLAIM_LABELS`). No taxonomy expansion.

## Tests added (19)

`test_artifact_binding.py` (13): A complete pass · B favorable omitted → asymmetry+blocked ·
C opposite omitted → asymmetry (neutral) · D unknown evidence → binding drift · E wrong parent →
binding drift · F provenance mismatch + unknown provenance → binding drift · G strength escalation
→ monotonicity, plus equal/weaker passes · QA↔taxonomy disjoint · fingerprint recompute ·
modelled≠literature fingerprint · loader rejects private-path leakage.
`test_pipeline_qa_isolation.py` (6): the isolation invariants above (Test H).

## Backward compatibility

Full suite: **1309 → 1328 passed** (+19, no regression, no existing fixture migrated, no expected
output altered). Ruff clean on all created files and on the modified `schemas.py`. Pre-existing
repo-wide ruff debt (33 `src/` / 132 tree) left untouched, as instructed.

## Known limitations (deliberately out of this slice)

Search-scope gate and Level-D negative-claim logic; omission audit over source categories;
LLM-driven critic / second pass; PDF/HTML post-render extraction; the full §5 report-side field
set and 6.4.0 bump; the remaining real-world regressions R1/R2/R6/R7/R8; full severity taxonomy;
7A boundary/perturbation/adversarial/replication tracks. The strength lattice is a minimal
deterministic ordering, not natural-language entailment.

## Next recommended slice (one)

**R7 — modelled-value provenance state** (from Case 02, isolated): a single low-complexity slice
that exercises `provenance_state ∈ {modelled}` vs `{published_literature}` end-to-end, adding a
binding check that fires when a modelled estimate is represented as a published literature value.
It builds directly on the provenance object shipped here with minimal new surface.
