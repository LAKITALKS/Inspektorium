# Phase 5.05f — Targeted Revalidation Result-Analysis Plan (frozen before mapping/gold)

**run_id:** reval_20260802_145257  ·  **written_at (UTC):** 2026-08-02T14:52:57Z
**repository_commit:** 902fea74bf00b85f1effe0dbef2c9f3b7aa5e75e
**repository_tag:** v0.8.7-targeted-revalidation-prep
**study_designation:** targeted_versioned_blind_model_revalidation
**acceptance_criteria_version:** 5.05f/1.0

> This plan is written **before** the internal RVAL→case mapping or any gold label is
> accessed, and before any result is calculated. This is a fresh run; the earlier aborted
> partial run (which stopped at input verification with X missing) is **not** reused or
> continued. This analysis is a targeted three-family blind **model** revalidation of two
> revised packets — **not** human IAA.

## Scope (two cases)
- RVAL-001, RVAL-002 only. No human review performed. No holdout action authorized.

## Original model assignments (fixed before collection)
| revalidator | model_family | displayed_model_name | inference_mode |
|-------------|--------------|----------------------|----------------|
| X | Anthropic | Opus 5 | (default) |
| Y | GLM | GLM 5.2 | (default) |
| Z | Gemini | Gemini 3.5 Flash | Extra Thinking |

## Inputs — all three preserved and structurally validated BEFORE any comparison
| revalidator | canonical CSV sha256 | validation |
|-------------|----------------------|------------|
| X | 44b06ba132439bb82295da09d6835b71c9e6053b110cf5682275bb42ea9cbe50 | PASSED |
| Y | 0c68ab39e4f11d66f0a901ba8b1c481ffe3f17359d53d922291528fa1cdc0283 | PASSED |
| Z | 2299ea9f5aa7cd046b4ead2e6f62b6134184c75284908fde5be24db814d239ae | PASSED |

- All three responses were independently collected and preserved (raw + manifest) **before**
  this comparison. No result had been calculated before this plan was written.
- No revalidator is excluded. No response is altered.

## Frozen acceptance criteria (copied verbatim from committed revalidation_plan.md — not reinterpreted, relaxed, or added to)
A revised packet passes targeted revalidation only if **all** hold:
1. At least **two of three** independent revalidators assign the existing gold label as their **primary** label.
2. **No majority** assigns a different primary label.
3. At least **two of three** mark `source_voice_clear = yes`, `claim_isolated = yes`, and `evidence_context_understandable = yes`.
4. **No majority** identifies `material_packet_defect = yes`.
5. **No individual** material-defect report remains unresolved after curator inspection.
6. **No serious disagreement** reveals a new taxonomy-boundary problem.
7. Any remaining disagreement is explicitly documented and curator-reviewed.

If only two independent revalidators are ultimately collected: both must assign the existing gold label as primary; both must mark source voice, claim isolation, and evidence context as clear; neither may identify a material packet defect; otherwise the packet does not pass. (Not applicable here — all three were collected.)

These criteria must not be relaxed or changed after observing results.

## Statistical note
- Cohen's / Fleiss' kappa are **not** computed or promoted as a reliability estimate for a
  two-case targeted sample. Only simple descriptive agreement is reported, explicitly
  labelled two-case descriptive evidence.

Only after this file exists may the internal RVAL mapping and current gold labels be accessed.
