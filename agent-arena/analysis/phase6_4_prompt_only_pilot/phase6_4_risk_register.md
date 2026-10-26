# Phase 6.4A — Risk Register

Risks specific to preparing a fair prompt-only comparison pilot, with mitigations encoded
in `prompt_only_baseline.py`, the frozen artifacts, and the tests.

| id | risk | L | I | mitigation | status |
|----|------|---|---|-----------|--------|
| **Q-1** | **Unfair (weak) baseline** — a strawman makes any Agent Arena advantage meaningless | med | high | competent, neutral prompt with claim/evidence + accurate 4-label definitions + biological scope + strict output; `baseline_design_principles.md` | mitigated |
| **Q-2** | **Answer leakage into the baseline prompt** — gold/expected/canonical/DEV/strata reaching the model | low | critical | projection = `task.prompt` only; `validate_no_forbidden_fields` reuses `check_contamination` + explicit id/path checks; leak fixture proves the guard fires | mitigated |
| **Q-3** | **Confidence corruption** — missing/invalid confidence coerced to 0.0 | med | high | `classify_baseline_confidence` = Phase 6.1 classifier; no coercion; bool/out-of-range → INVALID; tested | mitigated |
| **Q-4** | **Parser failure masquerading as a verdict** — malformed/repaired JSON accepted | low | high | malformed OR repaired/truncated → `parse_ok=false`, never a verdict, never retried; tested | mitigated |
| **Q-5** | **Ceiling effect misread** — both arms 27/27 read as "equivalent" | **high** | med | interpretation rules: report ceiling, do NOT call equivalent, examine Brier/confidence cautiously | mitigated (documented) |
| **Q-6** | **54-case pooling** — treating 54 predictions as independent | med | high | protocol forbids pooling; paired-by-DEV only; forbidden-language list; tested (no 54-independent interpretation) | mitigated |
| **Q-7** | **Post-hoc threshold/metric tuning** | med | high | metrics/bins/thresholds/costs frozen before results; reuse Phase 6.1/6.2; no new threshold after results | mitigated |
| **Q-8** | **Model swap after results** — changing the model once baseline is seen | low | high | model fixed (`claude-haiku-4-5-20251001`) before results; contract binds the dated id | mitigated |
| **Q-9** | **Premature/over-privileged execution** — private session reading completed predictions or holdout | low | critical | one-purpose least-privilege handoff; explicit must-not-read list; execution not performed here | mitigated (documented) |
| **Q-10** | **Residual nondeterminism** — `temperature=0` + unsupported seed still varies | med | low | documented in the contract (`residual_nondeterminism_note`); only the analysis is deterministic, not the sampling | disclosed |
| **Q-11** | **Prompt drift** — silent change to the frozen prompt | low | high | prompt bytes SHA-256-hashed into the contract; one-char change → digest change; tested | mitigated |
| **Q-12** | **Small-n over-interpretation** — 27 cases; corr/mech n=2 read as validated | **high** | high | development small-sample banner; `small_n`/`descriptive_only`; per-label/per-bin `n`; holdout stays sealed | mitigated |
| **Q-13** | **Universal-superiority framing** — pilot generalized beyond the pool | med | high | interpretation rules forbid it; rationale states operational-only model choice | mitigated |
| **Q-14** | **Single-prompt-string misframing** — describing the contrast as merely a swapped prompt string when the **response contract** (~11 vs 3 fields) and **parser** (truncation-repair vs strict no-repair) also differ | **high** | high | all artifacts state a **package-level** contrast; contract carries `treatment_contrast` and `validate_runtime_contract` rejects a single-prompt-string claim in the metadata; a test scans every doc for the false phrasing; parser/confidence completion reported separately from accuracy | mitigated |
| **Q-15** | **Response-burden asymmetry** — the baseline's lighter 3-field response may favor it vs Agent Arena's ~11-field structured output | med | med | documented as a **conservative asymmetry** (an Agent Arena advantage despite the heavier burden is conservative; a baseline advantage may be partly explained by it); stated in rationale, protocol, and limitations | disclosed |
| **Q-16** | **Arm-specific no-repair parser** — the baseline rejects repaired/truncated output while the completed Agent Arena arm accepts repaired output | low | med | disclosed as an **arm-specific design choice**; a parse-completion gap is interpreted in that light, never as model behavior or accuracy; visible here and in the limitations | disclosed |

**Note on scope:** the completed Agent Arena arm is **not** redesigned and the baseline
parser is **not** weakened; Q-14…Q-16 are addressed by accurate framing and separate
reporting, not by changing either arm's frozen endpoints.

**Review:** re-read before authorizing the private execution; add any risk surfaced
during execution before comparison metrics are produced.
