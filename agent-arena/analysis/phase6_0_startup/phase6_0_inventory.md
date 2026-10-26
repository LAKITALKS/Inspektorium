# Phase 6.0 — Technical Inventory

**Status:** development-only inspection. No model calls. No gold/taxonomy/holdout
changes. Read-only reconstruction of the current system plus identified gaps and
risks. Authoritative baseline: commit `cfb78de` / tag `v0.8.13-phase5-closeout`.

---

## 1. Authoritative inputs vs. historical snapshots

| artifact | role | authority |
|----------|------|-----------|
| `tasks/study_forensics/*.yaml` (50 files) | canonical case sources incl. gold labels | **authoritative** |
| `docs/study_forensics_taxonomy.md` (v0.6.5) | frozen 4-label taxonomy | **authoritative (frozen)** |
| `docs/taxonomy_precedence.md`, `docs/case_intake_policy.md` | label precedence + intake rules | **authoritative** |
| `analysis/phase5_2_closeout/` | Phase 5 closeout (ledger, handoff, entry criteria) | **authoritative current** |
| `analysis/phase5_1_holdout_freeze/holdout_public_manifest.json` | public holdout manifest (opaque HLD IDs + hashes) | **authoritative (public)** |
| `analysis/phase5_0_active_library_diagnostics/` | Phase 5.0 snapshot (49 active / 1 retired) | **historical — do not "fix"** |
| `runs/`, `reports/` | prior run outputs / rendered reports | historical evidence |
| `research/agent_arena_library_expansion_150/` | concurrent external operation | **out of scope — do not touch** |
| `analysis/**/internal_only/` | IAA internal_only (blind maps, private gold) | **sealed — do not open** |
| `__LOCAL_HOME__/Documents/AgentArena_IAA_Private/` | private holdout (gold, mapping, packets) | **sealed — outside repo** |

**Known historical discrepancy (documented, not a defect):** Phase 5.0 diagnostics
report 49 active / 1 retired; Phase 5.2 closeout reports 48 active / 2 retired. The
Phase 5.2 closeout is authoritative. The difference is the retirement of
`study-forensics-031` after the Phase 5.0 snapshot. The two retired cases in the
current library are `study-forensics-031` (rapamycin) and `study-forensics-042`
(edge-AI energy). Do not modify the protected Phase 5.0 files.

**Documentation-consistency observation (non-blocking, do NOT fix in 6.0):** the
taxonomy borderline table (`study_forensics_taxonomy.md`) still lists case 031 as
`mechanism_vs_evidence`, whereas the retired YAML carries `gold_label: solid`,
`gold_case_type: borderline`. Case 031 is retired and excluded from active metrics,
so this has no effect on Phase 6 development metrics. Any reconciliation touches the
frozen taxonomy and retired gold → **Level 3**, out of Phase 6.0 scope. Logged in the
risk register (R-11) as a maintenance item only.

---

## 2. Case library aggregates (reconstructed from `tasks/study_forensics/*.yaml`)

Matches the Phase 5.2 ledger exactly:

| dimension | value |
|-----------|-------|
| total known canonical cases | 50 |
| active (not retired) | 48 |
| retired (`status: retired`) | 2 — study-forensics-031, study-forensics-042 |
| gold_label: solid / overclaim / correlation_vs_causation / mechanism_vs_evidence | 14 / 24 / 6 / 6 |
| gold_case_type: clear / borderline | 39 / 11 |

Holdout eligibility (from `phase5_1_holdout_freeze/eligibility_summary.md`):

| pool | count |
|------|-------|
| eligible (active, non-dev-only, latest approved annotator-facing packet) | 21 (solid 5 / overclaim 8 / corr 4 / mech 4) |
| sealed holdout ⊂ eligible | 16 (4 per label) |
| active w/o approved annotator-facing packet | 26 |
| development-only | 1 (holdout-ineligible) |

**Leakage-critical consequence:** the sealed holdout is a subset of the 21 eligible
cases, and the specific membership is not disclosed inside the repo. Therefore the
21 eligible cases must be treated as **potentially holdout** and are unavailable for
Phase 6 development. The holdout-safe development pool identifiable from public data
is `{active} \ {eligible-21}` = the 26 non-blind active cases + 1 dev-only case
(27 cases), further filtered by borderline status for standard-accuracy metrics.
Exact pool freeze is a **Phase 6.1 preparation checkpoint** (see execution plan).

---

## 3. Input → output pipeline map

```
canonical case YAML (tasks/study_forensics/*.yaml)
  └─ load_task()  ──────────────────────────────►  Task (schemas.py)
       │                                              fields incl. prompt, context,
       │                                              gold_label, gold_* (curator-only)
       ▼
  discover_cases() (run_library.py)  ── filters retired/label/family
       ▼
  run_single() ─► run_agent() (runner.py)
       │            ├─ _select_system_prompt(task) → STUDY_FORENSICS_PROMPT (static)
       │            └─ provider.generate(task, system_prompt)
       │                 model-facing message = {system: STUDY_FORENSICS_PROMPT,
       │                                          user: task.prompt}          ◄── LEAKAGE BOUNDARY
       ▼
  raw model output ─► parse_structured_output() (output_contract.py)
       │                 → AgentResponse{final_answer, …, confidence:float}
       ▼
  evaluate_result() ─► study_forensics_checker.py
       │                 detected_label, label_correct (vs task.gold_label)
       ▼
  flat record {case_id, gold_label, label, label_correct, score, confidence, …}
       ▼
  run_library aggregation ─► LibrarySummary + CaseStability
       ▼
  _write_artifacts() → JSON records + rendered markdown summary
```

### Component reference

| stage | module | notes |
|-------|--------|-------|
| case schema | `schemas.py` (`Task`, 1099 LOC) | gold_* fields are curator metadata, never model-facing |
| discovery/harness | `run_library.py` (537) | `discover_cases`, `run_single`, `run_library`, stability |
| system prompt select | `runner.py` (`_select_system_prompt`) | static per task_type; no gold content |
| provider contract | `providers/{anthropic,openai,ollama}.py`, `__init__.py` | user content = `task.prompt` verbatim |
| output parsing | `output_contract.py` (321) | `confidence` coerced to float, **defaults 0.0** |
| scoring/labeling | `study_forensics_checker.py` (813), `evaluator.py` (1890) | compares detected vs gold |
| reporting | `reporter.py`, `reporting.py` | client/summary rendering |
| "calibration" | `calibrate.py` (876) | **heuristic proposal generator, NOT probability calibration** |
| audit trail | `audit_trail.py`, `journal.py`, CLI `audit-log …` | decision journal |
| consistency | `consistency.py` (740) | cross-run/label consistency checks |
| CLI | `cli.py` (859) | click groups incl. `iaa`, `disagreement-lab`, `client-report`, `audit-log` |
| tests | `tests/` (1008 collected) | `python3 -m pytest` |

---

## 4. Leakage surface analysis

**Live model path (clean):** the only content reaching the model is the static
`STUDY_FORENSICS_PROMPT` plus `task.prompt`. None of `gold_label`,
`expected_answer`, `gold_justification`, `gold_evidence_spans`, `gold_summary`,
`gold_alternative_reading`, `curator_notes`, `expected_findings`,
`gold_case_type`, `gold_confidence` is serialized into the model message
(verified in `providers/*.generate`). Filenames/`case_id` (which can encode the
label, e.g. `case046_..._correlation.yaml`) are **not** sent to the model.

**Residual leakage vectors to guard (packet-integrity scope):**
1. Any future packet/report builder that serializes more of the `Task` than
   `task.prompt` into a model-facing artifact.
2. Any prompt template that embeds `case_id`/filename verbatim.
3. `internal_only/` and private-holdout material must never enter a
   development-facing packet or report.
4. Gold/answer tokens appearing in the *system* prompt (currently none).

These are exactly the checks operationalized by the Phase 6.0 packet-integrity
tool (§6), which runs offline and development-only.

---

## 5. Confidence & abstention readiness

- **Confidence already emitted:** models return a numeric `confidence`; the parser
  exposes `AgentResponse.confidence: float`, captured per run in the flat record.
- **Semantic gaps (must be pinned in 6.1):**
  - Range/scale is unspecified (0–1 vs 0–100) and unenforced.
  - Missing/non-numeric confidence **silently degrades to 0.0**, indistinguishable
    from a genuine minimal-confidence report (parse failure masquerades as extreme
    confidence). Directly biases any reliability curve.
  - No mapping from self-reported confidence to empirical accuracy exists.
- **Abstention:** no selective-prediction / risk-coverage mechanism exists yet.
  There is a categorical finding-confidence label system
  (`HIGH/MEDIUM/HEURISTIC`) in the checker, but it is heuristic and not calibrated
  to accuracy; it must not be conflated with model confidence.
- **No statistical calibration exists.** `calibrate.py` proposes methodology
  changes (FP reduction, gold review, category refinement, model-confusion, data
  gaps); it does not compute ECE, reliability diagrams, or selective-prediction
  curves. → primary Phase 6.1/6.2 build target.

---

## 6. Packet-integrity automation (Phase 6.0 deliverable — design)

Reuses existing infrastructure rather than rebuilding: reconstructs the exact
model-facing packet via `runner._select_system_prompt` + the provider user-content
rule (`task.prompt`), **without any model call** (fully deterministic/offline).

Two separately reported checks (never collapsed into one verdict):

1. **Semantic preservation** — the reconstructed model-facing packet preserves the
   canonical claim (`task.prompt`) verbatim, is non-empty, and carries the required
   structural scaffold (the study-forensics system contract). Reports per-case
   diagnostics.
2. **Contamination / leakage** — the model-facing packet contains none of the
   forbidden gold/answer fields, no `case_id`/filename label encoding, no
   `internal_only`/private identifiers, no HLD/BIAA/RVAL/FXR tokens.

Output: machine-readable JSON (per-case + aggregate, both checks separate) plus a
concise human-readable summary. Development material only; explicitly refuses paths
under `internal_only/`, `research/`, or the private holdout.

---

## 7. Gaps, fragilities, and missing coverage

| # | item | class | Phase 6 relevance |
|---|------|-------|-------------------|
| G1 | No statistical confidence calibration (ECE/reliability/selective prediction) | missing capability | core 6.1/6.2 build |
| G2 | Confidence silently defaults to 0.0 on missing/non-numeric | fragile assumption | 6.1 semantics + guard |
| G3 | Confidence range/scale unspecified & unenforced | undefined semantics | 6.1 decision |
| G4 | Holdout membership sealed → dev pool not cleanly separable without discipline | leakage risk | 6.1 pool freeze |
| G5 | No automated packet-integrity gate (Phase 5.1 audit was manual markdown) | missing deterministic tool | built in 6.0 |
| G6 | `calibrate.py` name collides semantically with "calibration" | naming/clarity | document, avoid confusion |
| G7 | Many `run_*.py` scripts at repo root (ad-hoc, untracked) | reproducibility | prefer versioned entry points in 6.x |
| G8 | Taxonomy borderline table vs. retired 031 gold mismatch | doc-consistency (Level 3) | non-blocking, logged R-11 |
| G9 | No manifest binding a calibration result to input pool + code commit | reproducibility | 6.2 manifest requirement |

---

## 8. Explicit non-actions (isolation preserved during this inventory)

- Did **not** open `internal_only/`, `research/…expansion_150/`, or the private
  holdout.
- Did **not** read per-HLD gold, HLD→source mappings, or private packets.
- Did **not** modify taxonomy, gold labels, schemas, retired status, or the holdout
  definition/selection.
- Did **not** run model evaluations.
