# Phase 5.1a — Contamination Audit (annotator-facing packets)

Scanned BIAA-021_v1.md, BIAA-022_v1.md, BIAA-023_v1.md for: canonical case IDs, source YAML
filenames, real author/institution/journal/outlet names, BIAA mapping info, gold_label, expected
label, correct answer, taxonomy verdict, curator decision, prior response/vote, agreement, majority,
kappa, model names, holdout selection, candidate ranking, internal_only, source URLs, packet-local
annotation schemas.

## Result: **clean — NONE found.**
- No canonical case ID (case030/063/036, study-forensics-*), no source YAML filename, no real
  names/institutions/journals/outlets, no URLs.
- No gold_label, no snake_case taxonomy token (correlation_vs_causation / mechanism_vs_evidence /
  overclaim / solid), no expected/correct answer, no taxonomy verdict.
- No curator decision, prior response/vote, agreement/majority/kappa, model name, holdout/selection
  info, candidate ranking, or internal_only reference.
- **No `## Your annotation` section and no packet-local response-field list** in any packet (single
  authoritative external response schema only).

### Confirmed per packet
- Exactly **one** evaluated claim · one explicit source voice · complete, independently evaluable
  evidence context · no multiple competing evaluated claims · no stale/competing response schema ·
  no answer leakage.

### Ordinary terminology (not leakage)
- Generic scientific terms retained as evidence (e.g. "apelin/APJ pathway", "HbA1c", "natural
  antioxidants", "recycling policy") are ordinary domain language, not cues to any label.
- Each packet displays its own opaque blind ID (BIAA-021/022/023) — the intended identifier, not
  leakage of any mapping.
