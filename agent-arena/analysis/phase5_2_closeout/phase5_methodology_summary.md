# Phase 5 — Methodology Summary

## What was done
- **Blind packet construction:** claim-forensics items rendered as anonymized annotator-facing
  packets (BIAA-###) with neutral placeholders, one evaluated claim, explicit source voice, and
  evidence context — judged only on claim/evidence structure.
- **Four-label annotation taxonomy:** `solid`, `overclaim`, `correlation_vs_causation`,
  `mechanism_vs_evidence`, with a precedence rule (specific labels outrank generic `overclaim` only
  when their trigger genuinely captures the core error).
- **Proxy / model revalidation methodology:** independent model families annotated the blind packets
  in isolated sessions; agreement statistics were computed by the committed deterministic analyzer.
- **Frozen criteria before result access:** acceptance criteria and analysis plans were written and
  committed **before** the internal gold mapping or results were opened.
- **Isolated response collection:** each rater/revalidator worked in a fresh session; raw responses
  were preserved (with SHA-256 + manifests) **before** comparison.
- **Hash and manifest preservation:** every input/packet/bundle carries recorded hashes; nothing is
  compared or reported until preserved.
- **Versioned packet remediation:** defects were fixed by new versions (BIAA-013_v2 → v3;
  BIAA-016_v2) — originals never overwritten.
- **Curator decision layering:** provisional analyses remain immutable; curator decisions are a
  separate, subsequent governance layer.
- **Retirement rather than deletion:** unsuitable cases are flagged `status: retired` /
  `excluded_from_active_metrics` and excluded by default, but preserved and loadable.
- **Fail-stop behavior:** the Phase 5.1 preflight correctly stopped when a stratum had <4 eligible
  cases, rather than forcing a partial holdout.
- **Deterministic candidate selection:** blind-pool augmentation (Phase 5.1a) and holdout selection
  (Phase 5.1) used frozen seeds + SHA-256 ranking; no manual swaps; no model-performance inputs.
- **Prospective holdout freeze:** a 16-case, four-per-label holdout was sealed with public
  cryptographic commitments and private mapping/gold kept outside Git.
- **Separation of public commitments from private sealed material:** committed artifacts carry only
  policies, aggregate summaries, and hashes.

## Explicit scope statements
- **Model revalidation is NOT human inter-annotator agreement (IAA).**
- The Phase 5 evidence **does not prove universal model superiority**.
- **No holdout performance result exists.**
- **No direct Agent-Arena-versus-optimized-prompt baseline result exists yet.**
- Later performance claims require **separate evaluation evidence** under a precommitted protocol.
