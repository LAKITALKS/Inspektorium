# Agent Arena — Project Chronology (through v0.7.7-retire-case042)

*Documentation/audit-prep only. No code, YAML, prompts, or metrics were changed to produce
this dossier. Sections are labelled **[FACT]**, **[INTERPRETATION]**, **[RECOMMENDATION]**,
or **[OPEN]** where the distinction matters.*

This chronology updates and extends the earlier per-phase notes that live in the repo root
(`BASELINE_PHASE_0.md`, `PROVIDER_CONTRACT_PHASE_2.md`, `JUDGE_PARSER_PHASE_2_5.md`,
`CASE_LIBRARY_RUN_HARNESS_PHASE_4.md`, `STUDY_FORENSICS_CASE_LIBRARY_V0_1.md`) and the
Phase-5A bundle (`analysis/phase5a/lib_20260704_134553_55aa66/`). It does not replace them; it
consolidates the timeline v0.6 → v0.7.7.

## Tag → commit map [FACT]

| Tag | Commit | Message |
|---|---|---|
| v0.6-agent-arena-baseline | 3327605 | Baseline: Agent Arena v0.6 pre-hardening freeze (Phase 0) |
| v0.6.1-clean-baseline | 9170703 | Fix: resolve showcase case ID collision before hardening |
| v0.6.2-output-contract | e962e85 | Harden structured-output parsing (Phase 1) |
| v0.6.3-provider-contract | 2346c39 | Normalize provider response contract (Phase 2) |
| v0.6.4-judge-parser | 1818fc5 | Harden judge output parsing (Phase 2.5) |
| v0.7.0-case-library | 0c1b0b9 | Expand study forensics case library (Phase 3) |
| v0.7.1-run-harness | fbf2a0d | Add case library run harness (Phase 4) |
| v0.7.2-case043-gold-fix | 17b05e8 | Fix case043 gold label after live stability review |
| v0.7.3-mechanism-label-review | 5761093 | Refine mechanism fixture labels after live audit |
| v0.7.4-full-baseline-gold-review | b12fc72 | Review full-baseline gold label candidates |
| v0.7.5-case040-label-correction | 2075baa | Flip case040 primary label after curator review |
| v0.7.6-phase5a-diagnostics | b9c30f4 | Add Phase 5A single-model diagnostics report |
| v0.7.7-retire-case042 | 19aa295 | Retire case042 from active metrics with intake-policy filtering |

---

## Phase-by-phase [FACT unless noted]

### v0.6 baseline / Phase 0 — Baseline & rollback prep (tag v0.6-agent-arena-baseline, 3327605)
- **Purpose:** Freeze a working state before any hardening; establish rollback points.
- **Main changes:** First git commit of the engine (it had 0 commits). Added `.env`/`.env.local`
  to `.gitignore`; corrected stale agent model IDs; recorded state in `BASELINE_PHASE_0.md`.
- **Files/modules:** repo-wide initial commit; `agents/*.yaml`; `BASELINE_PHASE_0.md`.
- **Validation:** `pytest` at baseline = 885 passed, **3 failing** (a pre-existing case-ID
  collision, accepted "as-is" per user decision).
- **Completed:** baseline commit + tag. **Deferred:** the collision fix (→ Phase 0.5).
- **Risks introduced:** committing with a known-red test suite (documented).

### Phase 0.5 — Clean baseline (tag v0.6.1-clean-baseline, 9170703)
- **Purpose:** Restore a green suite before hardening.
- **Main changes:** Renamed two showcase cases that collided on number **and** internal id
  (they had reused `034`/`035`) to `case041`/`case042` with ids `study-forensics-041/042`;
  updated hardcoded case counts in `tests/test_study_forensics.py`.
- **Validation:** full suite **green** (888 passed).
- **Note [FACT]:** This is the origin of the current `case041` (GLP-1) and `case042` (Edge-AI)
  ids — both were early "showcase" cases built from the same template.

### Phase 1 — Output Contract Hardening (tag v0.6.2-output-contract, e962e85)
- **Purpose:** Stop the live crash where a truncated `` ```json `` fence raised
  `ValueError: substring not found`.
- **Main changes:** New module `src/agent_arena/output_contract.py` (robust extraction:
  fenced/unfenced, pre/post prose, string-aware brace scan, best-effort truncation repair,
  `ParseDiagnostics`, optional `finish_reason` hint). `runner.parse_agent_output` became a
  thin backward-compatible wrapper.
- **Validation:** +30 tests; full suite green (918).
- **Deferred:** persisting parse diagnostics onto results; the judge parser (→ Phase 2.5).
- **Risk [INTERPRETATION]:** repaired truncated JSON can now be scored where it previously
  failed to parse; `truncation_suspected` is available but not yet gated in scoring.

### Phase 2 — Provider Contract Normalization (tag v0.6.3-provider-contract, 2346c39)
- **Purpose:** Make provider calls observable and consistent.
- **Main changes:** `ModelResponse` (text, provider, model, finish_reason, usage, latency_ms,
  error, error_type) + `BaseProvider.generate`; Anthropic/OpenAI/Ollama map normalized
  finish_reason + usage; `run_agent` threads finish_reason into the parser; `AgentResult`
  gained optional finish_reason/usage/error_type; OpenAI max_tokens 2048→4096.
- **Files:** `providers/*`, `runner.py`, `schemas.py`, `PROVIDER_CONTRACT_PHASE_2.md`.
- **Validation:** +30 tests; suite green (937).
- **Risk [FACT]:** OpenAI sampling became deterministic (temp 0) + higher token cap — a
  behavior change for that provider path (documented).

### Phase 2.5 — Judge Parser Hygiene (tag v0.6.4-judge-parser, 1818fc5)
- **Purpose:** The judge had the same unclosed-fence crash as the pre-Phase-1 agent parser.
- **Main changes:** Extracted a shared `extract_json_object` in `output_contract`; the judge
  now delegates to it; removed a pre-existing unused import. Judge prompt/scoring unchanged.
- **Validation:** +11 tests; suite green (947); all 30 Phase-1 parser tests still pass.

### Phase 3 — Case Library v0.1 (tag v0.7.0-case-library, 0c1b0b9)
- **Purpose:** Expand study_forensics from 29 → 50 curated cases.
- **Main changes:** Added 21 synthetic fixtures (`case043`–`case063`, all
  `origin: synthetic_fixture`, no fabricated citations) across biomedical, market/comms,
  AI/tech, environment/policy patterns, incl. 2 solid positive controls and borderline probes.
  Added `tests/test_case_library.py` and `STUDY_FORENSICS_CASE_LIBRARY_V0_1.md`.
- **Validation:** suite green (963).
- **Deferred/Risk [FACT]:** the 4-value `gold_label` taxonomy is narrower than the intended
  richer classifications (misleading/insufficient/etc.), which are documentation-only.

### Phase 4 — Run Harness + Multi-Run Stability v0.1 (tag v0.7.1-run-harness, fbf2a0d)
- **Purpose:** Make the library runnable/repeatable/measurable.
- **Main changes:** `src/agent_arena/run_library.py` (discovery, batch run, `--runs-per-case`,
  deterministic fake provider, artifacts under `runs/library/<id>/`, descriptive stability
  flags + `HIGH_SCORE_VARIANCE_THRESHOLD`). `CASE_LIBRARY_RUN_HARNESS_PHASE_4.md`.
- **Validation:** +17 tests (fake providers only); suite green (980). A first **live smoke**
  (3 cases ×1) succeeded.
- **Deferred:** calibration/proper scoring; a heterogeneous model panel.

### Phase 4.1 — Gold Review (folded into tags v0.7.2/0.7.3/0.7.4)
- **Purpose:** Resolve cases the live probes flagged as stable-but-wrong.
- **v0.7.2-case043-gold-fix (17b05e8):** case043 (cell→cancer "treats cancer") flipped
  mechanism_vs_evidence → **overclaim** (borderline); live 3/3 overclaim confirmed the intended
  reading per the prompt priority rule.
- **v0.7.3-mechanism-label-review (5761093):** synthetic mechanism fixtures written with
  selling language misclassified: case045/case048 → **overclaim** (borderline); case044
  **reworded** to remain a clean hedged mechanism control. Pre-existing hedged mechanism cases
  (024/028) verified correct.
- **v0.7.4-full-baseline-gold-review (b12fc72):** after the first full 50×1 baseline,
  case044 re-balanced (had over-corrected to "solid"); case040/case042 marked borderline;
  case054 left as documented borderline.
- **Validation:** suite green (980) throughout; targeted live re-checks (3 runs/case) used to
  confirm, not to auto-flip.

### Phase 4.2 — case040 correction (tag v0.7.5-case040-label-correction, 2075baa)
- **Purpose:** case040 (uncontrolled pre/post vocational-training evaluation) was mislabeled.
- **Main changes:** primary label flipped **overclaim → correlation_vs_causation** (clear/high),
  findings/spans reordered, overclaim kept as alternative. Prompt unchanged. Rationale is
  taxonomy-based (the case's own note: "structural, not rhetorical"); model agreement (3/3) was
  corroboration, not the driver.
- **Validation:** suite green (980).

### Phase 5A — Single-Model Diagnostics (tag v0.7.6-phase5a-diagnostics, b9c30f4)
- **Purpose:** Offline diagnostics over the full 50×3 baseline (run `lib_20260704_134553_55aa66`).
- **Main changes:** report bundle in `analysis/phase5a/<run_id>/` (accuracy, confusion matrix,
  per-label metrics, per-case stability, suite-assignment draft, two directional solid-confusion
  metrics, human review queue, single-model ceiling caveat + Phase-5B strategy). No engine code.
- **Validation:** documentation only; suite unchanged.
- **Key facts:** 150/150 successful; 96.0% accuracy; 0 unstable; only case042/case054
  stable-alternative (see current_state_snapshot.md).

### case041 intake metadata cleanup (commit 4566cc3; no tag)
- **Purpose:** Annotate the GLP-1 weight-loss showcase case after an intake audit.
- **Main changes:** additive only — `origin: curated_showcase`, `intake_review: passed`, and a
  curator note. **Prompt byte-identical; label unchanged.** Kept active Core.

### case042 retirement / intake-policy filtering (tag v0.7.7-retire-case042, 19aa295)
- **Purpose:** Make case042's retirement **effective**, not decorative.
- **Main changes:** optional Task schema fields `status`, `excluded_from_active_metrics`;
  `run_library.discover_cases` excludes retired cases by default (`is_retired`), reachable via
  `--include-retired` or explicit `--case-id`; CLI prints active/retired counts. case042
  annotated (`origin: demo_derived`, `status: retired`, `suite_history`) with prompt/label
  byte-identical (no flip, no hard-delete). Added `docs/case_intake_policy.md` + retirement tests.
- **Validation:** suite green (**988**); active discovery 50→**49**.

---

## B. Delta from v0.6 to v0.7.7 [FACT]

- **Provider contract hardening:** raw-text-only providers → normalized `ModelResponse`
  (finish_reason/usage/latency/error_type); consistent max_tokens; observable errors.
- **Parser hygiene:** fragile inline JSON parsing (crashed on unclosed fences) → shared robust
  `output_contract` used by both the agent parser and the judge.
- **Case-library expansion/stabilization:** 29 → 50 curated cases; gold labels reviewed and, where
  taxonomy-justified, corrected (043/044/045/048/040).
- **Multi-run stability harness:** new `run_library` batch runner + descriptive stability flags.
- **Phase 5A diagnostics:** committed offline diagnostic bundle at v0.7.6.
- **case040 label correction:** overclaim → correlation_vs_causation (taxonomy-based).
- **case041 intake-review annotation:** curated_showcase / intake passed; kept active Core.
- **case042 retirement:** demo_derived/task-design confound → retired from active metrics.
- **Active-vs-retired discovery filtering:** real harness support (default excludes retired).
- **Intake-policy documentation:** `docs/case_intake_policy.md`.
- **Tests/validation status:** 885(+3 red) at v0.6 → **988 passed** at v0.7.7; ruff clean on
  changed modules; all live checks were small/targeted (no large live batch after v0.7.7).
