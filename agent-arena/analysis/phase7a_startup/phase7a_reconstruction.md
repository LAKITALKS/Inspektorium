# Phase 7A — Reconstruction & Audit (startup, pre-registration)

Read-only reconstruction of repository state, the frozen taxonomy/precedence, the Phase-6
analytical findings, and the existing robustness infrastructure. **No** model was called, **no**
gold/taxonomy/case was changed, **no** holdout was accessed, and nothing was committed. Every
number below is quoted from a committed artifact and is attributed; none is newly computed.

---

## A. Repository state (verified)

| item | expected (brief) | observed | match |
|---|---|---|---|
| branch | `feat/case-library-run-harness` | `feat/case-library-run-harness` | ✅ |
| HEAD | `aa71c4a2…debe05` | `aa71c4a2efd7735142448e2477d54bcfd0debe05` | ✅ |
| HEAD parent | `596f5301…29c18a` | `596f5301966b65ca882e72e366bbaa3fa529c18a` | ✅ |
| HEAD subject | consolidate phase 7B artifact release gate | identical | ✅ |
| Phase-6 tag | `v0.9.0-phase6-closeout` → `ec57472…` | tag resolves to `ec57472c188f801cf223c46faf027ae8bb97588d` | ✅ |
| Phase-6 ancestry | closeout is ancestor of HEAD | `merge-base --is-ancestor` = YES | ✅ |
| working tree | no tracked modifications | only untracked pre-existing files (`??`), zero tracked diffs | ✅ |
| baseline suite | 1414 passed | `pytest --collect-only` = **1414 tests collected** (imports clean; not executed — docs-only session) | ✅ (size) |

**Phase-7B commit chain (all seven verified, in order, as the exact `ec57472..HEAD` set):**

```
fad82bc  feat: add phase 7 artifact binding vertical slice        (Evidence Symmetry / Artifact Binding)
40093c6  feat: preserve derived-value provenance in phase 7 QA    (Derived-Value Provenance)
0b93666  fix:  make value-origin provenance fail closed           (Fail-Closed Value-Origin)
d68aa19  fix:  enforce categorical value-origin binding           (Categorical Value-Origin)
f7e1804  feat: bind negative evidence claims to search scope      (Search-Scope Gate)
596f530  fix:  require evidence basis for narrowed search scope    (Search-Scope Basis)
aa71c4a  feat: consolidate phase 7B artifact release gate         (Final Artifact-QA / Release Gate)
```

**Untracked, out-of-scope, left exactly as found (not opened, staged, moved, or deleted):**
`research/`, `Dataset *.pdf`, `Dataset 5.json`, `pilot_dataset_6_cases (1).json`, `run_*.py`
probes, `.agent_arena/`, `.DS_Store`, `analysis/phase4_9_retrospective/fable_audit_input_combined.md`.

**Conclusion:** repository equals the approved starting checkpoint. No STOP condition from §1.

---

## B. Phase-6 closeout status (frozen, unconditional)

- Closeout commit `ec57472…`, tag `v0.9.0-phase6-closeout`.
- Decision (`phase6_closeout/phase6_go_no_go_review.md`): **GO FOR PHASE 7 — final curator
  decision, "This is not conditional."** All ten Phase-6 objectives **PASS**
  (`phase6_objective_acceptance_matrix.md`).
- The Phase-7 entry safeguards are **standing governance requirements**, *not* unresolved Phase-6
  defects. They are **not** reopened or re-litigated here, and Phase 6 is **not** described as
  conditional anywhere in this package.

---

## C. Phase-6 analytical findings reconstructed (from committed reports)

Source: `phase6_closeout/phase6_integrated_findings.md`, quoting
`phase6_2_results/cross_model_descriptive_comparison.json` and
`phase6_4_prompt_only_results/paired_comparison_report.json`. **Development material — NOT holdout.
Not pooled.** The 81 / 54 predictions are **not** independent cases.

### C.1 — Phase 6.2, three-model development calibration (same 27 dev cases per model)

| model | accuracy (27) | Brier (all 27) | ECE 5-bin (clear) | high-conf errors | mean conf |
|---|---|---|---|---|---|
| Haiku | 27/27 = 1.000 | 0.00930 | 0.0912 | 0 | 0.910 |
| Sonnet | 24/27 = 0.889 | 0.10533 | **0.00115** | **3** | 0.923 |
| Opus | 27/27 = 1.000 | 0.00968 | 0.0927 | 0 | 0.908 |

- **Sonnet's 3 errors are all gold `overclaim`**, each predicted as a *more specific* label:
  DEV-0011 → `correlation_vs_causation`; DEV-0013 → `mechanism_vs_evidence`;
  DEV-0024 → `mechanism_vs_evidence`.
- **Brier is primary.** **ECE is secondary and sparse-bin / potentially misleading**: confidences
  concentrate in the top range, so Sonnet had the *lowest* ECE while being the *only* model with
  errors; Brier exposed the high-confidence errors appropriately.
- **No abstention threshold approved** — simple confidence-threshold abstention was not
  established as a reliable operating rule.
- Haiku and Opus at 27/27 → a plausible **ceiling effect** on this development pool.

### C.2 — Phase 6.4, package-level paired pilot (Haiku snapshot `claude-haiku-4-5-20251001`)

| metric | Agent Arena | prompt-only |
|---|---|---|
| accuracy (27) | 27/27 = 1.000 | 24/27 = 0.889 |
| Brier top-label (27, VALID) | 0.0093 | 0.0814 |
| high-conf errors | 0 | 1 |
| parser completion | 27/27 | 27/27 |

- Accuracy difference (AA − prompt-only) = **+0.111**; Brier difference (prompt-only − AA) = **+0.0721**.
- Paired outcomes: **both correct 24 · Agent-Arena-only 3 · prompt-only-only 0 · both wrong 0**.
- Three asymmetric cases, **all gold `overclaim`**: **DEV-0011, DEV-0013, DEV-0018** — prompt-only
  chose a *more specific* label instead of `overclaim` on each.
- **Package-level** contrast (system prompt + response contract + parser differ **together**;
  `prompt_only_baseline.py` docstring). It does **not** isolate a single prompt string. Parser
  completion is reported **separately** from classification quality.

### C.3 — Cross-phase convergence (HYPOTHESIS only)

| failing DEV id | 6.2 Sonnet | 6.4 prompt-only Haiku |
|---|---|---|
| DEV-0011 | ✗ → correlation_vs_causation | ✗ → correlation_vs_causation |
| DEV-0013 | ✗ → mechanism_vs_evidence | ✗ → mechanism_vs_evidence |
| DEV-0018 | (correct) | ✗ → mechanism_vs_evidence |
| DEV-0024 | ✗ → mechanism_vs_evidence | (correct) |

- **DEV-0011 and DEV-0013 recur across both** runs; every error in both phases is a gold
  `overclaim` case relabeled to a *more specific* category.
- The **overclaim → over-specific** pattern is a **Phase-7 hypothesis / diagnostic signal**, *not*
  a proven taxonomy defect. At this n it is indistinguishable between (a) genuine boundary
  ambiguity, (b) a prioritization-scaffold gap, or (c) dataset-specific phrasing. **Frozen for
  Phase 7A: RESULT PATTERN ≠ TAXONOMY DEFECT.** Phase 7A *tests* it and *searches for
  counterevidence*; it must not assume it true.

---

## D. Taxonomy & precedence (frozen; exact model found)

Four labels, unchanged and unextended: **`solid`, `overclaim`, `correlation_vs_causation`,
`mechanism_vs_evidence`**. `mechanism_vs_evidence` is **biologically scoped**
(animal/preclinical mechanism → implied human clinical benefit).

**Precedence rule (`docs/taxonomy_precedence.md`), reconstructed verbatim in intent:**

1. `overclaim` is the **generic / residual** category (core signal = *rhetorical inflation*).
2. `correlation_vs_causation` and `mechanism_vs_evidence` are **specific** structural failure
   modes, each with a documented definitional trigger:
   - `correlation_vs_causation` — causal claim from a non-causal / uncontrolled / confounded
     design (missing counterfactual / comparison arm).
   - `mechanism_vs_evidence` — a **described biological mechanism** (animal/preclinical pathway)
     used to imply human clinical benefit not demonstrated. **Explicitly excludes** the
     biomarker/surrogate-to-clinical gap ("Shape B"); **surrogate endpoints framed as clinical
     outcomes route to `overclaim`.**
3. A specific label outranks `overclaim` **only if** its trigger is *genuinely present* **and** it
   *captures the core error*. Otherwise the primary stays `overclaim` and the specific label is
   recorded as `gold_alternative_reading`.
4. Governance: do **not** stretch a specific label to match a model's preferred reading; stable
   model disagreement is a **review trigger**, not a label-change reason; a flip requires an
   **independent taxonomy justification**; historical metrics stay frozen.

Worked precedents: **case040** (specific trigger PRESENT → flip `overclaim → correlation_vs_causation`,
overclaim kept secondary) and **case054** (stable 3/3 model reading of `mechanism_vs_evidence`
**rejected** as primary — no biological mechanism described; in-vitro dissolution is a surrogate →
routes to `overclaim`). case054 is the deliberate anti-co-evolution reference: the *rule*, not
model behavior, controls gold.

### D.1 — Documentation ↔ executable-logic audit (§7)

- **The precedence rule is a governance / gold-freeze rule, not executable code.** No `precedence`
  logic exists in `src/` or `tests/`; it is applied by curators when assigning gold, model-independently.
- `study_forensics_checker._detect_label()` is a **parser** that extracts the *model's own stated
  label* from free text. Its ordering (compound labels `mechanism_vs_evidence` /
  `correlation_vs_causation` checked before the single-word `overclaim` / `solid`) is an
  **unambiguous-substring tie-break for parsing output**, on a *different object* than gold
  precedence. **No contradiction** exists between the precedence documentation and executable logic.
- **Noted as a robustness-relevant surface (not a defect):** because the parser resolves a
  multi-label mention toward the compound labels first, an adversarial or perturbed model *output*
  that names several labels could be parsed toward a specific label. This is a legitimate thing for
  the 7A adversarial/perturbation tracks to probe at the *output-parsing* layer; it is **not** a
  taxonomy-precedence conflict and requires no change in this startup session.

**Conclusion:** no doc/code/Phase-6 contradiction found → no STOP condition from §7.

---

## E. Existing robustness infrastructure (inventory)

**Reusable as-is (no build needed):**

| module | capability relevant to 7A |
|---|---|
| `run_library.py` | **Batch case-library run harness with a multi-run stability surface.** `--runs-per-case N` replication; retirement-aware `discover_cases` (honors `status: retired` / `excluded_from_active_metrics`, `--include-retired`, explicit `--case-id`); deterministic offline `FakeLibraryProvider` (`--fake`) for zero-cost structural dry-runs; per-run flat records (detected_label, label_correct, score, confidence, parse_ok, finish_reason, truncation_suspected, error/error_type, latency, usage, timestamp); `CaseStability` (unique_labels, `label_consistency_rate` = modal fraction, score mean/min/max/range, confidence_mean, flags) + `LibrarySummary`; JSON + Markdown artifact writer. **This is the 7A.4 replication backbone.** |
| `runner.py` | Single-agent execution; the **Agent Arena package** `SYSTEM_PROMPT` (~11 structured forensic fields); structured-output parse. |
| `providers/{anthropic,openai,ollama,response}.py` | Model adapters + response normalization. |
| `evaluator.py` + `study_forensics_checker.py` | Scoring + `_detect_label` (output label extraction) + failure-mode detection. |
| `calibration.py` | Frozen calibration engine: **Brier primary**, **5 fixed bins** (10-bin sensitivity only, empty bins retained), **ECE secondary**, VALID/MISSING/INVALID confidence (never coerced to 0.0), per-label figures require **n ≥ 5**, strata separated, **costed** abstention with threshold-optimization prohibited in code. Operates on an anonymized `DEV-####` envelope (no canonical identity). |
| `runtime_contract.py` | **Configuration fingerprints**: `system_prompt_sha256`, `task_packet_construction_sha256`, `parser_contract_sha256`, `agent_config_sha256`, `repository_commit`; freeze + verify. Phase-6.2 dated snapshots (`analysis/phase6_2_runtime_freeze/phase6_2_runtime_contract_*.json`) give the **exact** model ids — Haiku `claude-haiku-4-5-20251001`, Sonnet `claude-sonnet-4-5-20250929`, Opus `claude-opus-4-5-20251101` — with temp 0.0, top_p OMITTED, seed UNSUPPORTED, timeout 120 s, ≤2 transport retries, semantic retries PROHIBITED. The Phase-7A primary condition freezes **Haiku + Sonnet** (Opus excluded). |
| `confidence_validity.py` | VALID/MISSING/INVALID confidence classification. |
| `packet_integrity.py` | `check_contamination` leak guard (reused by baseline). |
| `prompt_only_baseline.py` | Frozen Phase-6.4A **package-level** prompt-only arm (offline, deterministic) — available if a baseline contrast is authorized. |
| `disagreement_lab.py` | Cross-model divergence → structured report; surfaces alternative readings, "taxonomically unstable" model behavior, category-boundary root-cause, gold-review flags. **Does not resolve disagreement or change gold.** Useful for boundary-confusion analysis. |
| `dev_manifest.py` | Salted-sha256 development-pool commitment machinery. |
| `journal.py` / `audit_trail.py` / `schemas.py` | `RunJournalEntry`, provenance/audit, typed objects. |
| `caseforge.py` | Case-candidate generation (marks `pending_human_review`; sha256 fingerprints). **Not run this session.** |

**Thin, additive extensions that Phase 7A would need (design only; not built this session):**

1. A **stability-aggregation extension** over `run_library`/`calibration` outputs: explicit
   `modal_label` field, `label_switch_count`, `confidence_spread` (stdev), and **per-replication
   Brier** — additive to existing `CaseStability` (which already has the modal *fraction* and
   variance flags).
2. A **cluster/family metadata + pseudoreplication-aware reporter**: `base_case_id`,
   `perturbation_cluster_id`, `boundary_family_id`, `adversarial_family_id`, plus reporting that
   separates **N independent bases** from **N total evaluated variants**.
3. A **boundary-confusion / transition-matrix diagnostic** (a small helper over the existing
   confusion output) for the overclaim → over-specific hypothesis **with counterevidence** (full
   4×4 transition matrix, both directions).
4. A **per-case content fingerprint** helper (reuse `runtime_contract._sha256_hex`).
5. A **robustness-failure-type** reporting vocabulary (§ robustness_design) kept strictly out of
   the 4-label gold taxonomy.

**Assessment:** the execution/measurement backbone already exists and is mature. Phase 7A is
mostly **case authoring + gold freeze + thin additive reporting**, not new-harness construction.

---

## F. Data-class & Phase-7B separation (attested)

- **Class A — Case library / existing evaluation data:** `tasks/study_forensics/*.yaml` (~48 active,
  1 retired = `study-forensics-042`); Phase-6 development pool (`DEV-####` envelope).
- **Class B — Phase-7A robustness evaluation cases:** to be authored (boundary / perturbation /
  adversarial). **Do not merge with A or C.**
- **Class C — Pipeline-QA regression fixtures:** Phase-7B R1–R8 synthetic fixtures + the artifact
  release gate. **Contribute 0** to any Phase-7A accuracy / Brier / ECE / stability / difficulty /
  case-count statistic. The Phase-7B release gate is a **pipeline-control layer**, a separate
  namespace; 7B QA findings ≠ 7A model errors.
- **Real commercial pilot material (incl. LaVita-derived lessons) must NOT become Phase-7A cases.**
  No LaVita robustness case will be created.

---

## G. Security / holdout attestation for this session

- Holdout: **not touched** — no holdout case, gold, manifest, identity map, mapping, salt,
  envelope, private raw response, hidden alias, or private canonical id was opened, listed, or
  inferred. No broad traversal of private/untracked directories was performed.
- Only read: git metadata; `docs/*.md`; `analysis/phase6_closeout/*.md`;
  `analysis/phase7_startup/*.md`; tracked `src/agent_arena/*.py`; one tracked **Class-A** dev case
  (`case040`) as the gold-field template.
- No unrelated untracked dataset, `run_*.py` probe, `research/`, `.agent_arena/`, or client
  material was inspected.
