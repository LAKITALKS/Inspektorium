# Phase 6.2 — Runtime Selection Review

**Decision:** **THREE_MODEL_PER_MODEL_CALIBRATION** (curator, authoritative). No single
canonical primary model is selected; three separate runtime contracts are frozen —
Haiku, Sonnet, Opus — each receiving the same frozen 27-case pool, identical system
prompt and task-packet construction, one independent execution, run id, anonymized
envelope, and calibration report. **The three models are never pooled into one score.**
The decision rests on the repository's multi-model architecture and the frozen
per-model protocol — **not** on prior performance results.

**Resolved dated snapshots** (authoritative model catalog; no Messages API call, no
newer-family substitution):

| model | agent config alias | exact dated snapshot |
|-------|--------------------|----------------------|
| Haiku 4.5 | `claude-haiku-4-5-20251001` (already dated) | `claude-haiku-4-5-20251001` |
| Sonnet 4.5 | `claude-sonnet-4-5` | **`claude-sonnet-4-5-20250929`** |
| Opus 4.5 | `claude-opus-4-5` | **`claude-opus-4-5-20251101`** |

Each is a dated snapshot of the **same 4.5 family**. The Sonnet and Opus configs were
**pinned to these dated snapshots before results** (Haiku was already dated); each
contract's `exact_model_id` equals its config's `model` — **no moving alias, no implicit
override**. The provider now explicitly enforces the frozen `timeout=120` / `max_retries=2`.

**Governance:** Level 2. No model calls, no network, no private material. Source-code
baseline `327e7690ad53d3de793c074d5aa9137764575fe7`; tracked tree clean at prep.
Contracts frozen and validated below; **pending curator approval before commit**.

---

## 1. Canonical-model determination — NONE established

The repository does **not** establish any one agent config as *the* canonical primary
Agent Arena system whose confidence Phase 6.2 is meant to calibrate:

- **Historical runs are multi-model.** Tracked run manifests evaluate all three
  models together, e.g. `runs/run_e7bc9a74.json` (claude-haiku-4-5-20251001,
  claude-sonnet-4-5, claude-opus-4-5) and `runs/run_e8f2d9e8.json` /
  `runs/run_8ed21427.json` (haiku + opus + sonnet).
- **Reporting is per-model.** `study_forensics_taxonomy.md` reports empirical accuracy
  "avg across models" and per model; `calibration_protocol.md` reports metrics
  "per model"; the Phase 6.2 result envelope carries a single `model` field (one
  envelope per model).
- **No "primary model" designation exists.** The only "primary" references in the
  tracked docs (`phase4_9_retrospective/…`) concern a primary *label* (case054 gold),
  not a primary model.

**Conclusion:** Agent Arena is a multi-model evaluation system. Selecting one config
would be an invented choice → this memo stops for curator selection.

## 2. Candidate comparison

| dimension | Haiku | Sonnet | Opus |
|-----------|-------|--------|------|
| agent config | `agents/claude_haiku.yaml` | `agents/claude_sonnet.yaml` | `agents/claude_opus.yaml` |
| provider | anthropic | anthropic | anthropic |
| exact model id | `claude-haiku-4-5-20251001` | `claude-sonnet-4-5` | `claude-opus-4-5` |
| **model revision pinned?** | **YES (dated)** | **NO (undated alias)** | **NO (undated alias)** |
| config SHA-256 | `d755c07e…3e60` | `6d114d32…530f` | `1a9b3a0c…deb7` |
| scalar confidence exposed | yes — via the shared study-forensics JSON contract (`"confidence"`), identical prompt path for all three | same | same |
| methodological relevance | strong on clear categories; **mechanism_vs_evidence ≈ 40%** (taxonomy) | **best on the hardest category: mechanism_vs_evidence ≈ 80%** (taxonomy); balanced | strong general; **mechanism_vs_evidence ≈ 40%** (taxonomy) |
| cost for 27 cases (1 run) | lowest | middle | highest |
| runtime param support | temp ✓ / top_p (API yes, **runner does not send**) / **seed unsupported (Anthropic)** / max_tokens ✓ | same | same |
| parser/prompt compatibility | identical (same provider + system prompt) | identical | identical |
| used in prior dev runs? | yes | yes | yes |
| risk of changing target after calibration | calibration is model-specific — switching the production model later invalidates it | same | same |

Cost is order-of-magnitude only: ~27 calls × (~1.3–1.7k input + ≤4096 output) tokens
per model; tier ordering Haiku < Sonnet < Opus. Confirm exact figures against current
Anthropic pricing before authorizing — not fabricated here.

## 3. Runtime values already freezable now (model-independent)

Derived from the exact tracked runner/provider code (read-only; deterministic):

| field | value |
|-------|-------|
| provider | `anthropic` |
| endpoint/backend | Anthropic Messages API (`client.messages.create` via `anthropic.Anthropic()`) |
| temperature | `0.0` (all three configs) |
| top_p | **UNSUPPORTED_BY_RUNNER** (runner transmits no top_p; API default applies — gap, §5) |
| seed | **UNSUPPORTED** (Anthropic Messages API exposes no seed) |
| max output tokens | `4096` (`DEFAULT_MAX_TOKENS`) |
| request timeout | **NOT_CONFIGURED** (Anthropic SDK default — gap, §5) |
| concurrency | `1` (sequential `run_library` loop; no threading/async) |
| replication count | `1` (`runs_per_case` default = 1; no fixed replication in the execution contract) |
| transport retry | Anthropic SDK default (transport-level: rate_limit/timeout/connection/5xx); **runner adds none** |
| retry backoff | Anthropic SDK default (exponential) |
| semantic/quality retries | **PROHIBITED** — not implemented; must never be added |
| parser | `output_contract.parse_structured_output`; parse failure recorded (`parse_ok=False`), **never re-run** |
| missing-confidence handling | `confidence_validity.classify_confidence` → MISSING; **never coerced to 0.0** (record raw) |
| invalid-confidence handling | classify → INVALID; **never coerced to 0.0** (record raw) |
| system-prompt SHA-256 | `f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5` (STUDY_FORENSICS_PROMPT, 4644 bytes) |
| task-packet construction SHA-256 | `92972e1825a8b096fb7e0af97748aa2fa098eb3686fd4197f690a58f36d36da4` (descriptor: `system=STUDY_FORENSICS_PROMPT; user=task.prompt(verbatim)`; **no per-case content hashed**) |
| repository commit | `327e7690ad53d3de793c074d5aa9137764575fe7` |
| protocol version | `6.1` |

Model-dependent (pending decision): exact model id, model revision, agent-config path
+ hash, cost.

## 4. Unsupported / not-applicable parameters (explicit)

- **seed** → `UNSUPPORTED` (Anthropic Messages API has no seed).
- **top_p** → `UNSUPPORTED_BY_RUNNER` (not transmitted by the current runner).
- **request timeout / retry counts** → `NOT_CONFIGURED` (Anthropic SDK defaults).

## 5. Reproducibility gaps to resolve before freezing

1. **Undated model aliases.** `claude-sonnet-4-5` and `claude-opus-4-5` are **not**
   pinned to a dated snapshot; only Haiku (`…-20251001`) is. If Sonnet or Opus is
   chosen, pin its config to a dated snapshot first (Level-1 config edit) so
   `model revision` is unambiguous.
2. **top_p / timeout / retry not set by the runner** → API/SDK defaults could drift.
   To fully freeze, either explicitly set them in the runner (Level-1 code change) or
   accept `UNSUPPORTED_BY_RUNNER` / `NOT_CONFIGURED` with a documented caveat.
3. **temperature 0.0** reduces but does not guarantee cross-time determinism; with
   replication = 1 this is the intended near-deterministic setting.

## 6. Direct recommendation (evidence-based; for curator confirmation)

- **Preferred:** treat Phase 6.2 as **per-model calibration** and freeze **one runtime
  contract per candidate model** (Haiku + Sonnet + Opus) — this matches the multi-model
  design, the historical run convention, and the already-frozen per-model protocol,
  and avoids inventing a single "primary." Pin Sonnet/Opus to dated snapshots first.
- **If a single primary system must be named:** **Sonnet** is the most defensible on
  capability grounds (best on the hardest category, mechanism_vs_evidence ≈ 80% vs
  ≈ 40% for Haiku/Opus; balanced tier), **pinned to a dated snapshot** — explicitly
  **not** Haiku-because-cheapest.

## 7. Curator decisions (RESOLVED)

1. **Scope:** per-model set (all three) — THREE_MODEL_PER_MODEL_CALIBRATION.
2. **Model ids:** dated snapshots resolved (table above).
3. **Snapshot pinning:** `agents/claude_sonnet.yaml` and `agents/claude_opus.yaml` were
   pinned to the dated snapshots **before results** (Haiku already dated); each
   contract's `exact_model_id` equals its config's `model` (validated). No moving alias
   remains and no implicit override is used.
4. **Provider enforcement:** `providers/anthropic.py` now constructs
   `anthropic.Anthropic(timeout=120.0, max_retries=2)` explicitly (no SDK-default
   fallback); the contract transport values are tied to those provider constants.
   `top_p: OMITTED_FROM_REQUEST`, `seed: UNSUPPORTED` — no runner gaps remain.

## 8. Status — FROZEN (pending curator approval before commit)

Three runtime contracts built and validated by `runtime_contract.py`
(`phase6_2_runtime_contract_{haiku,sonnet,opus}.json`): all `exact_model_id`s are dated
snapshots that equal their pinned config's `model`, all non-model values identical,
every hash reproduces from source, provider timeout/retry enforcement matches, no
placeholder remains, and all three are `is_executable == True`. Residual limitation:
temperature 0 + no seed reduce but do not guarantee model determinism. No model/network
calls; no private material accessed. Awaiting curator approval to commit; execution
remains separately gated.
