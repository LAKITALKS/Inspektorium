# RUN_CONFIG — ASA 25/261 · RUN 001

| Field | Value |
|---|---|
| CASE | ASA_25_261_PREMIUM_GROUNDING |
| RUN | run_001 |
| DATE | 23 August 2026 |
| AGENT ARENA VERSION | agent-arena 0.1.0 (package metadata); internal contracts: forensic_report 6.3.0, ForensicRecord 0.1.0, release gate 0.1.0 |
| GIT BRANCH | feat/case-library-run-harness |
| GIT COMMIT | 84d75d4b3d931090500151a23c3ef939e910cde0 |
| GIT STATUS (before run) | DIRTY — untracked scratch files and datasets present before the run; no tracked file was modified by this run |
| MODEL | claude-opus-5 |
| MODEL VARIANT | claude-opus-5 (single-model run; the pipeline is not multi-agent) |
| PROVIDER | anthropic |
| REASONING / EFFORT SETTING | NOT EXPOSED |
| CONTEXT / MODE | NOT EXPOSED |
| TEMPERATURE | NOT EXPOSED |
| SEED | NOT EXPOSED |
| INPUT FREEZE | `input/01_FINAL_EVIDENCE_FREEZE_v1.md` |
| INPUT FREEZE SHA-256 | `530f8fdf33715f59f86e10df6a9329ad5ccce4c4f0befc219341563b36600069` |
| INPUT FREEZE BYTES | 119130 |
| HANDOFF FILE | Not present in the local package; the epistemic routing it carries was supplied directly in the run instruction and is recorded verbatim per proposition under `routing` (see `INPUT_INTEGRITY_REPORT.md`) |
| RESEARCH | CLOSED |
| WEB / NEW LITERATURE DISCOVERY | PROHIBITED — none performed |
| ASA OUTCOME AS SCIENTIFIC GOLD LABEL | PROHIBITED — quarantined |
| DESIRED VERDICT | NONE |
| EVIDENCE CUT-OFF | 2026-08-22 |
| REPORT CONTRACT | forensic_report schema 6.3.0 (frozen, unmodified) |
| RECORD CONTRACT | ForensicRecord 0.1.0 (frozen, unmodified) |
| RELEASE GATE | Phase-7B 0.1.0 |
| TEST SUITE | PASS — 1484 passed (full suite, run before adjudication) |
| CODE CHANGES | NONE |

## Pipeline stages executed

| # | Stage | Implementation |
|---|---|---|
| 0 | Input integrity | SHA-256 verification against the expected canonical hash |
| 1 | Frozen claim ingestion | 26 active atomic propositions, exact wording, freeze sections 12/48/88 |
| 2 | Claim-forensics adjudication | `agent_arena.forensic_report.build_forensic_report` |
| 3 | Report validation | `agent_arena.forensic_report.validate_forensic_report` |
| 4 | Representation record | `agent_arena.schemas.ForensicRecord` |
| 5 | Release gate | `agent_arena.artifact_binding.evaluate_artifact_release` |
| 6 | Cross-proposition consistency | this harness |
| 7 | Output freeze + manifest | SHA-256 over every artifact |

Stage 2 covers, within the frozen report contract: evidence-to-claim binding,
evidence authority and study-quality constraints, endpoint fidelity, population
fidelity, timeframe fidelity, product transfer, causality boundaries, numerical
fidelity, counterevidence, evidence independence and cohort overlap,
author-network independence, adversarial challenge, Steelman review, and
uncertainty calibration. Stage 5 adds deterministic finding binding,
summary-strength monotonicity, evidence symmetry, value-origin provenance and
search-scope binding. No stage was skipped.

## Firewalls in force

- Scientific research firewall — no PubMed, Europe PMC, OpenAlex, Crossref,
  Scholar, registry, product-page or citation-network access. No new evidence.
- Regulatory firewall — the ASA outcome is procedural provenance only, is never
  used as a gold label, and no verdict is calibrated toward or away from it.
- Strategic firewall — outreach, commercial goals, demonstrator quality and
  third-party audiences played no part in any verdict.
