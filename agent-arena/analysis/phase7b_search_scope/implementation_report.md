# Phase 7B — Third Vertical Slice: Search-Scope Gate (implementation report)

Bounded Phase-7B slice. Deterministic, offline, no model call, no holdout access, no LaVita
identity in any executable artifact. Builds on the frozen symmetry / binding / strength /
value-origin controls (unchanged).

## Problem

A bounded search result must not become a global world claim:

```
"No head-to-head study was identified in the reviewed sources."   (bounded)
→ "No head-to-head study exists."                                 (global — forbidden)
```

Freeze: **NOT FOUND ≠ DOES NOT EXIST.** The assertion breadth of a negative claim may not
exceed its documented search basis. Agent Arena **does not claim that a structured search proves
global absence.**

## Semantic placement (separate dimension)

Search scope is its own epistemic dimension — *what universe of material was searched before a
negative assertion* — kept separate from claim provenance, value origin, evidence strength and
confidence. Traceability: `CLIENT NEGATIVE ASSERTION → internal NegativeEvidenceAssertion →
SearchScope OR source-local evidence basis`. No free-floating global negatives.

## Minimal contract (additive; no existing scope concept existed — verified)

Three small models on `ForensicRecord` / `ClientFinding`:
- `SearchScope{ search_scope_id, scope_type ∈ {reviewed_set, documented_search},
  reviewed_source_ids, resources, query_terms, date_cutoff, search_completeness ∈
  {targeted, structured} }`. `source_local` is direct inspection, **not** a SearchScope type.
- `NegativeEvidenceAssertion{ assertion_id, finding_id, proposition, assertion_scope,
  search_scope_id?, source_local_evidence_ids[] }` — its **basis is derived from actual support**,
  not a self-declared label.
- `ClientNegativeAssertion{ assertion_id, client_scope }` on `ClientFinding` — the scope the
  client statement claims.

Completeness stays modest (`targeted` / `structured`) — no `complete` / `exhaustive`, so a label
cannot manufacture false certainty.

## Assertion-scope model & compatibility (categorical containment, not a rank)

`ASSERTION_SCOPES = source_local · reviewed_set · documented_search · global_nonexistence`.

```
ALLOWED_CLIENT_SCOPES = {
  source_local      → {source_local},
  reviewed_set      → {source_local, reviewed_set},
  documented_search → {source_local, reviewed_set, documented_search},
}
# global_nonexistence: supported by NO basis by default (fail closed).
```

A client may keep or **narrow** scope, never **broaden** it. This is a scope-containment relation
(legitimately nested), distinct from the categorical Value-Origin rule.

## Curator hardening — narrower scope requires a resolvable narrower basis

The initial implementation correctly prevented epistemic **broadening**, but allowed a narrower
client scope based **solely on scope containment**. Curator review identified that this is not
always valid: a narrower assertion also makes a **more specific provenance claim** whose evidence
basis must actually resolve. The gate was hardened from

```
scope containment
```

to

```
scope containment + basis resolution.
```

Freeze: **SCOPE MAY NARROW ONLY IF THE NARROWER EVIDENCE BASIS RESOLVES.** A narrower scope label
must never silently invent a new evidence basis — **NARROWER SCOPE WITHOUT NARROWER BASIS =
INVENTED PROVENANCE.**

The two-question check the gate now answers per client negative assertion:

1. Is the client scope no broader than the internal epistemic basis? *(containment — unchanged)*
2. Does the concrete evidence basis the client's chosen scope asserts actually exist? *(new)*

Required narrower bases (structured, reusing existing fields; no parallel evidence model):

- **`source_local`** — a client "the cited source does not contain X" claim requires a resolvable
  concrete source-local basis: `NegativeEvidenceAssertion.source_local_evidence_ids` non-empty and
  each id → an existing `QAEvidenceItem` with a non-empty `source_id` (evidence → source binding).
- **`reviewed_set`** — a client "in the reviewed sources, X was not identified" claim requires an
  actual represented reviewed set: the assertion's `SearchScope.reviewed_source_ids` non-empty. A
  `documented_search` scope substantiated only by resources / query terms / date cutoff does **not**
  by itself prove an explicit reviewed set exists.
- **`documented_search`** — unchanged: a substantiated documented search (Section 18); reachable
  only when the resolved basis is itself `documented_search`.
- **`global_nonexistence`** — unchanged: supported by no basis, always blocked.

A missing narrower basis is reported as **`artifact_source_binding_drift`** (BLOCKER): the client
binds to a source / reviewed set that is not represented. This is deliberately distinct from
`unresolved_search_scope` (which keeps its prior meaning: the assertion resolves **no** basis of any
kind) and from `search_scope_to_world_generalization` (broadening). No new QA code was required.

Non-goals preserved (Section 15): the rule is *never fabricate the narrower basis*, **not** *never
narrow*. A documented search that genuinely enumerates a reviewed source set, or an assertion with
genuine source-local evidence, narrows legitimately and passes (Tests B, D, F, G, I). Confidence and
evidence strength remain unread (Tests N, O). Binding depth stays structural only — no PDF/OCR/free-
text verification (Section 16).

## Fail-closed behavior

- **Missing / unsubstantiated basis** → `unresolved_search_scope` (BLOCKER). Missing search scope
  is not a global search. A `documented_search` scope with an empty search record (no resources /
  queries / date / reviewed sources) is treated as unsubstantiated → fail closed (Section 18).
- **Broadening** (incl. any `global_nonexistence` claim, or reviewed_set → documented_search) →
  `search_scope_to_world_generalization` (BLOCKER). Level D never passes by default; no arbitrary
  "N databases = global absence" rule exists.
- **Source-local** assertions are supported directly by frozen source evidence and need **no**
  fabricated SearchScope.

Both new codes are pipeline-QA codes (namespace disjoint from the frozen four claim labels).
Binding failures (assertion → finding, client → internal assertion) reuse
`artifact_source_binding_drift`. Confidence and evidence strength are never read by the gate.

## Tests (1359 → 1374, +15; curator hardening 1374 → 1393, +19)

`test_artifact_binding_search_scope.py` (original slice, unchanged, all green): A source-local safe ·
B source-local→world blocked · C reviewed-set safe · D reviewed-set→structured blocked · E
documented-search safe · F documented-search→global blocked (core) · G missing scope→unresolved · H
source-local needs no search metadata · I client may narrow · J client may not broaden · K
independent of confidence · L independent of evidence strength · documented-search-without-record→
unresolved · codes-not-labels.

`test_artifact_binding_search_scope_basis.py` (curator hardening matrix, +19): A documented→documented ·
B documented→reviewed_set **with** set (pass) · **C documented→reviewed_set without set (blocked —
key regression)** · D documented→source_local with basis (pass) · E documented→source_local without
basis (blocked) · F reviewed_set→reviewed_set · G reviewed_set→source_local with basis · H
reviewed_set→source_local without basis (blocked) · I source_local with basis · J source_local with
missing source binding (blocked) · K bounded→global (blocked) · L unresolved scope (blocked) · M
narrower label does not create provenance (blocked, not unresolved) · N missing basis unsaved by
confidence · O missing basis unsaved by evidence strength · P base record clean (no over-block) · Q
value-origin primitive clean · R evidence-symmetry primitive clean · S fixture stays class-C.

`test_pipeline_qa_isolation.py`: slice-3 fixture contributes 0 cases. Prior symmetry, binding,
strength, and value-origin regressions remain green (full suite): 1393 passed.

## Dataset isolation

`tests/fixtures/pipeline_qa/qa_search_scope_negative_language.json` — fully synthetic, generic
(A-vs-B comparison), no commercial/LaVita identity. Structurally isolated (data class C);
contributes **0** to case library / development / holdout / evaluation counts.

## Schema versioning

Forensic report **6.3.0 unchanged**. `FORENSIC_RECORD_SCHEMA_VERSION` kept at **0.1.0**: all
additions are optional with defaults; existing records (slices 1–2) remain valid; nothing
version-gates the string, so a bump would carry no meaning. Backward-compatible extension. The
curator hardening adds **no new fields** — it strengthens the deterministic gate logic only over
existing `SearchScope` / `NegativeEvidenceAssertion` / `QAEvidenceItem` fields — so the serialized
contract is untouched and neither version moves.

## Known limitations (out of this slice)

No systematic-review / PRISMA / database-API / automated-search / screening infrastructure; no
free-text NLP classification of prose "sounds global" (the gate reads structured
`client_scope`); no rendered-artifact (PDF/HTML) post-render verification; no operational
"complete/exhaustive" definition. An `evidence_of_absence` contract that could ever justify
`global_nonexistence` does not exist and is deliberately not introduced.

## Next recommended step (one)

**Final artifact-QA expansion / release-gate consolidation** — the individual QA primitives
(symmetry, binding, strength, value-origin, search-scope) now exist; the natural next step is a
consolidated release view (severity roll-up + a single machine-readable release report), rather
than opening a new representation dimension. Justification in the final report §R.
