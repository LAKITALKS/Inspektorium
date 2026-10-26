# BASELINE — Phase 0 (Freeze before Phase 1 hardening)

**Timestamp:** 2026-07-01T07:17:34Z
**Branch:** `main`
**Last commit hash:** *(none — repository has 0 commits)*
**Working tree status:** **DIRTY** (no baseline commit exists yet)

---

## 1. Git status snapshot

| Category | Count |
|---|---|
| Commits in repo | **0** |
| Staged files | 98 |
| Untracked files | 24 |
| Staged-then-modified (AM) | 4 |

### Staged-then-modified (AM) files — changes made earlier in this session
These were staged, then further edited (all from earlier session phases, **not** Phase 0):
- `.gitignore` — added `.env` / `.env.local` ignore rules
- `agents/claude_opus.yaml` — model id `claude-opus-4-20250514` → `claude-opus-4-5`
- `agents/claude_sonnet.yaml` — model id `claude-sonnet-4-20250514` → `claude-sonnet-4-5`
- `src/agent_arena/providers/anthropic.py` — `max_tokens` 2048 → 4096

### Untracked files of note
- `tasks/study_forensics/case034_glp1_aleniglipron.yaml` — **new showcase case (this session)**
- `tasks/study_forensics/case035_edge_ai_energy_blind_spot.yaml` — **new showcase case (this session)**
- `.agent_arena/journal.jsonl` (57 lines), `.agent_arena/decisions.jsonl` (7 lines) — evaluation journal
- `run_*.py` (12 ad-hoc runner scripts), `Dataset *.pdf/json`, `.DS_Store`

Nothing was deleted, reset, cleaned, or overwritten. All uncommitted work is intact.

---

## 2. ⚠️ Blocker to a clean baseline — case ID collision

My two showcase cases added earlier this session **reuse case numbers and internal IDs that were already taken**:

| Number | Pre-existing (staged) | New this session (untracked) | Shared `id:` |
|---|---|---|---|
| 034 | `case034_gas_stoves_asthma.yaml` | `case034_glp1_aleniglipron.yaml` | `study-forensics-034` |
| 035 | `case035_ai_tutoring.yaml` | `case035_edge_ai_energy_blind_spot.yaml` | `study-forensics-035` |

This raises the study-forensics case count from 27 → 29 and creates 2 duplicate IDs. It is the **sole cause of the 3 failing tests** below.

**Recommended resolution (requires user confirmation; NOT done in Phase 0):** renumber the two showcase files to `case036_glp1_aleniglipron.yaml` (`id: study-forensics-036`) and `case037_edge_ai_energy_blind_spot.yaml` (`id: study-forensics-037`), and bump the hardcoded `27` counts in `tests/test_study_forensics.py`. This restores a green baseline.

---

## 3. Test run

**Command:** `.venv/bin/python -m pytest -q`

| Result | Count |
|---|---|
| Passed | **885** |
| Failed | 3 |
| Duration | ~2.4s |
| Live API required | **No** — fixtures only, ran fully offline |

**Failing tests (all in `tests/test_study_forensics.py::TestTaskLoading`):**
- `test_task_files_exist` — asserts exactly 27 case files (now 29)
- `test_all_tasks_load` — asserts exactly 27 tasks (now 29)
- `test_task_ids_unique` — 29 ids, 27 unique → 2 duplicates (the collision above)

All three are direct consequences of the ID collision, not pre-existing defects.

---

## 4. Baseline description — what Agent Arena currently does

Local-first AI-agent evaluation engine for biomedical/reasoning claim forensics. A (provider, model) agent answers a task prompt once as strict JSON; the evaluator scores it across 10 diagnostic dimensions, all evidence-bound.

- **Providers:** `anthropic`, `openai`, `ollama` (behind `BaseProvider` ABC + `get_provider` registry). Optional LLM-`judge` as a second model path.
- **Task types:** rubric-based, forecasting_decision, study_forensics.
- **Report/PDF output paths:** `reports/run_<id>.md` (internal dossier), `reports/client/<id>_report.{md,html,pdf}` (client report, PDF via optional `weasyprint`). **Note:** `runs/` and `reports/` are git-ignored — run artifacts are local-only.
- **Meta-stack:** `insights`, `calibrate`, `route`, `disagreement-lab`, `caseforge`, `audit-log`, `pipeline` — all driven from `.agent_arena/journal.jsonl`.
- **Tests:** 888 total, fixture-based, no network.

---

## 5. Important artifacts to preserve as baseline

| Path | Contents | Preserve as baseline? |
|---|---|---|
| `src/agent_arena/**` | Full engine source | **Yes** (code baseline) |
| `tasks/**`, `agents/**` | Cases + agent configs | **Yes** |
| `tests/**` | 888 tests | **Yes** |
| `.agent_arena/journal.jsonl` (57), `decisions.jsonl` (7) | Evaluation history for calibrate/insights | **Yes** — needed for Phase-1 before/after calibration |
| `reports/run_e7bc9a74.md` + `runs/run_e7bc9a74.json` | GLP-1 multi-agent run (all agree `overclaim`) | **Yes** — before/after reference |
| `reports/run_39f41f2c.md` + `runs/run_39f41f2c.json` | Edge-AI run (models diverge; only Haiku correct) | **Yes** — before/after reference |
| `reports/walde_glp1_agent_arena_onepager*.md` | External one-pager deliverables | Yes (deliverable, not baseline logic) |
| `Dataset *.pdf/json`, `run_*.py`, `.DS_Store` | Ad-hoc scripts / data / OS cruft | Optional — not engine baseline |

---

## 6. Known audit findings (from Phase-−1 audits)

- **Fragile JSON parsing** — `parse_agent_output` throws `substring not found` on unclosed ```` ```json ```` fences; `parse_ok=False` → hard 0/100. (Observed live this session.)
- **Truncation via `finish_reason="length"`** — not inspected; caused truncated Haiku JSON at `max_tokens=2048`.
- **Thin provider contract** — `send_prompt` returns raw text; no normalized errors/retries/rate-limits; inconsistent `max_tokens` across providers.
- **Claude dependency: low-to-medium**, not severe — clean `BaseProvider` abstraction already exists; only hardcoded model defaults + judge default + router cost table.
- **Scoring** — linear weighted heuristics (`DIAGNOSTIC_WEIGHTS`) + normalized Shannon entropy for disagreement. **No** Bayesian updating, **no** Brier/Log proper scoring, **no** evidence-hierarchy weighting, **no** ensemble aggregator (winner = argmax score).

---

## 7. Git baseline decision

**User decision (2026-07-01): commit AS-IS.** The baseline is frozen with the 3 known-failing
tests from the case ID collision (see §2 and §3) accepted as a documented known issue. The
collision is intentionally **not** resolved in Phase 0; it may be addressed later.

**Baseline commit + tag `v0.6-agent-arena-baseline` created in this Phase-0 step.**

### What was committed
- The 98 deliberately-staged project files (engine, `tasks/`, `agents/`, `tests/`, `docs/`, `pyproject.toml`)
- Latest edits to the 4 AM files (model ids → `*-4-5`, `max_tokens` 4096, `.gitignore`)
- The 2 new showcase cases (`case034_glp1_aleniglipron.yaml`, `case035_edge_ai_energy_blind_spot.yaml`)
- `BASELINE_PHASE_0.md`

### What was intentionally left untracked (not part of baseline)
- OS cruft: `.DS_Store`
- Ad-hoc data / scripts never staged: `Dataset *.pdf/json`, `pilot_dataset_6_cases (1).json`, `run_*.py`
- Runtime journal: `.agent_arena/journal.jsonl`, `.agent_arena/decisions.jsonl` (local eval history)
- Git-ignored local artifacts: `runs/`, `reports/`, `.env`

> Known issue carried into the baseline: `tests/test_study_forensics.py::TestTaskLoading`
> (3 failures) — hardcoded count 27 vs. actual 29 + 2 duplicate ids (`study-forensics-034/035`).

---

## 8. Rollback instructions

*(Valid once the baseline commit + tag `v0.6-agent-arena-baseline` exist.)*

**Return to the baseline (discard uncommitted work — destructive):**
```bash
git stash            # optional: park current changes first
git checkout v0.6-agent-arena-baseline
```

**Compare a future branch against baseline:**
```bash
git diff v0.6-agent-arena-baseline..feat/output-contract-hardening --stat
git diff v0.6-agent-arena-baseline..HEAD -- src/agent_arena/runner.py
```

**Abandon a failed feature branch (baseline untouched):**
```bash
git checkout main
git branch -D feat/output-contract-hardening
```

**Revert a single bad commit (keeps history, safe on shared branches):**
```bash
git revert <bad_commit_hash>
```

**Hard reset a branch back to baseline (local only, destructive):**
```bash
git reset --hard v0.6-agent-arena-baseline
```

---

## 9. Next recommended branch for Phase 1

```
feat/output-contract-hardening
```
Scope (Phase 1, not started): harden `parse_agent_output` (graceful degradation on unclosed fences) + handle `finish_reason="length"`. No scoring/prompt/provider/report changes.
