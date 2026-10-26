# Case Intake Policy — study_forensics library

Historical presence in the library is **not** sufficient for a case to count in
active scoring. Every case — including material derived from demos or pitches —
must pass the intake checklist below before it is included in active metrics.

## Intake checklist (all required)
1. **Isolated exact claim** — the single claim under evaluation is explicit and
   not buried inside surrounding analysis that qualifies or critiques it.
2. **Clear source voice** — the claim-maker is unambiguous (who is asserting it).
3. **Archived source** — the source text/excerpt is captured in the case.
4. **Primary label with rationale** — `gold_label` + `gold_justification`.
5. **Documented strongest alternative reading** — `gold_alternative_reading`.
6. **Expected findings** — at least one, with severity/confidence.
7. **origin field** — one of:
   `curated`, `real_world_intake`, `demo_derived`, `synthetic`, `curated_showcase`.

Demo-derived material (`origin: demo_derived`) is allowed **only** if it passes
this same checklist. Failing an item (e.g. non-isolated claim / ambiguous source
voice) means the material is not benchmark-ready.

## Retirement (not deletion)
- Cases that fail intake **after a retrospective audit** are **retired**, not
  hard-deleted. They remain historically archived (file kept, gold label kept)
  but are **excluded from active metrics**.
- Retirement is recorded on the case via:
  - `status: retired`
  - `excluded_from_active_metrics: true`
  - an `origin` value reflecting provenance (e.g. `demo_derived`)
  - a `suite_history` entry (date, trigger, rationale, `label_flip: false`)
- **Enforcement:** case discovery (`agent_arena.run_library.discover_cases`)
  excludes retired / `excluded_from_active_metrics` cases **by default**. They
  remain loadable and are still discoverable when explicitly requested by
  `--case-id`, or in bulk via `--include-retired`.

## Rewrites vs new case_id
- Do **not** rewrite under the same `case_id` if the evaluated claim or source
  voice changes materially. Instead create a **new case_id** and link the two via
  `supersedes` / `superseded_by`.

## Reporting
- Active library runs report the active case set (retired cases excluded).
- Historical reports (e.g. the Phase-5A bundle) are **not** rewritten; they
  reflect the case set at the time they were produced. Future reports should be
  regenerated against the active set after a retirement takes effect.

## Currently retired cases
| case_id | reason | superseded_by |
|---|---|---|
| study-forensics-042 | demo-origin contamination + task-design confound (target readiness claim embedded in an analytical paper that critiques it; ambiguous source voice) | pending |
