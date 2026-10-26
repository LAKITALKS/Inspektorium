# Phase Status Table (v0.6 → v0.7.7)

Legend: **Done** = completed & tagged; **Done (no tag)** = committed without a tag;
**Open** = not started / unresolved.

| Phase | Name | Tag | Commit | Status | Tests at end | Key deferral / risk |
|---|---|---|---|---|---|---|
| 0 | Baseline & rollback prep | v0.6-agent-arena-baseline | 3327605 | Done | 885 pass / 3 fail | committed red (collision) |
| 0.5 | Clean baseline | v0.6.1-clean-baseline | 9170703 | Done | 888 pass | — |
| 1 | Output Contract Hardening | v0.6.2-output-contract | e962e85 | Done | 918 pass | repaired-JSON now scorable |
| 2 | Provider Contract Normalization | v0.6.3-provider-contract | 2346c39 | Done | 937 pass | OpenAI sampling change |
| 2.5 | Judge Parser Hygiene | v0.6.4-judge-parser | 1818fc5 | Done | 947 pass | — |
| 3 | Case Library v0.1 (29→50) | v0.7.0-case-library | 0c1b0b9 | Done | 963 pass | 4-label taxonomy only |
| 4 | Run Harness + Multi-Run Stability | v0.7.1-run-harness | fbf2a0d | Done | 980 pass | descriptive-only stability |
| 4.1a | Gold review — case043 | v0.7.2-case043-gold-fix | 17b05e8 | Done | 980 pass | — |
| 4.1b | Gold review — mechanism fixtures | v0.7.3-mechanism-label-review | 5761093 | Done | 980 pass | mechanism set thinned |
| 4.1c | Full-baseline gold review | v0.7.4-full-baseline-gold-review | b12fc72 | Done | 980 pass | 042/054 left borderline |
| 4.2 | case040 label correction | v0.7.5-case040-label-correction | 2075baa | Done | 980 pass | — |
| 5A | Single-Model Diagnostics | v0.7.6-phase5a-diagnostics | b9c30f4 | Done | 980 pass | single-model ceiling only |
| — | case041 intake annotation | (none) | 4566cc3 | Done (no tag) | 980 pass | — |
| 5R | case042 retirement + filtering | v0.7.7-retire-case042 | 19aa295 | Done | 988 pass | active-set metric not re-measured |
| 4.9 | External audit (Fable 5) | — | — | **Open** | — | this dossier is the input |
| — | case054 adjudication | — | — | **Open** | — | taxonomy precedence undecided |
| 5B | Model-panel discrimination probe | — | — | **Open** | — | needs weak/mid models |

## Live-run history (targeted, cost-controlled) [FACT]
- Phase 4 smoke: 3 cases ×1.
- Mixed probes: several 3-run per-case checks (007/043/046/053/058/061; 044/045/048; 048/024/028;
  040/042/054; case044 re-check).
- Full baseline: 50×3 = 150 runs (Phase 5A input).
- **No live run after v0.7.7.**
