# Phase 5.05e — Targeted Remediation Plan (written before any edit)

**Immutable source checkpoint:** commit `a4027d7a6e67095b91b4af411949b5dbdcd9011d` ·
tag `v0.8.5-proxy-iaa-curator-review` · approved disposition **B — STRONG, MINOR
CURATION REQUIRED FIRST** · holdout frozen: no · gold-label changes approved: no ·
taxonomy revision required: no.

**Taxonomy version:** four-label taxonomy (`solid`, `overclaim`,
`correlation_vs_causation`, `mechanism_vs_evidence`) — **unchanged**. Reference file
`annotator_taxonomy_reference.md` sha256 `c8c9f5c35da6d62e4a9dcffcb6b0c0b3c1604fc66b0e94795832b7f792bc872e`.

## Approved blind IDs, internal real-case mapping, pre-edit hashes, gold labels
*(This file is top-level/internal, not annotator-facing; the mapping is permitted here.)*

| blind | real file | real id | gold (before) | ambiguity (before) | yaml sha256 (pre) | orig packet sha256 (pre) |
|-------|-----------|---------|---------------|--------------------|-------------------|--------------------------|
| BIAA-003 | case009_mindfulness_autism.yaml | study-forensics-009 | overclaim | medium | 8c7556d7eaf0abb7… | d32a4c965ed3b384… |
| BIAA-007 | case043_cell_study_cancer_cure.yaml | study-forensics-043 | overclaim | high | c0813173976639ed… | 8ac2f3a5457795ea… |
| BIAA-013 | case_public_001_exercise_intensity.yaml | study-forensics-public-001 | correlation_vs_causation | low | 3478f17ef1843dc6… | d01cb9c4f7e650af… |
| BIAA-016 | case037_mindfulness_app.yaml | study-forensics-037 | overclaim | medium | 326d73193f614c27… | 8ec356bec8e0993e… |
| BIAA-019 | case031_rapamycin_longevity.yaml | study-forensics-031 | solid | medium | 719ccc8b537c3e1e… | 87199a67d6b6b910… |

## Approved action, expected changes, and revised-packet need per case
| case | approved action | fields/files expected to change | revised packet? |
|------|-----------------|--------------------------------|-----------------|
| BIAA-003 | retain gold · re-designate borderline · clarify gold rationale | YAML `ambiguity_level` (medium→high), `gold_justification` (append precedence), `curator_notes` (append) | No (no packet-visible change) |
| BIAA-007 | retain gold · add precedence explanation · request independent human review | YAML `gold_justification`/`curator_notes` (append precedence + holdout-ineligible note); new human-review request file | No |
| BIAA-013 | revise packet construction · remove embedded instruction · normalize · exclude from holdout | New `BIAA-013_v2.md` only | **Yes** |
| BIAA-016 | isolate exact claim · mark borderline · revise packet · revalidate | YAML `ambiguity_level` (medium→high), `curator_notes` (append); new `BIAA-016_v2.md` | **Yes** |
| BIAA-019 | clarify source voice · decide revision-vs-retirement · exclude from holdout | Decision record only (proposed **RETIREMENT**, see case_decisions/BIAA-019.md) | No (pending curator) |

## Explicitly prohibited (must NOT change)
- Any primary **gold_label** (all five identical before/after).
- The four-label **taxonomy** definitions.
- The **public claim** or **evidence** text of any case (`prompt`/`context` semantic content).
- The **original blind packets** under `.../annotator_facing/packets/` (byte-identical).
- Historical **Phase 5.05c** and **Phase 5.05d** artifacts.
- Private **response sheets / manifests**; providers, prompts (pipeline), schemas,
  evaluator, judge, scoring, parser.
- The historical **blind_case_index.csv** run provenance (left unchanged; forward
  designation recorded in the case YAML + this phase's `revision_map.csv`).

## Standing statements
- **No gold-label change is authorized** and none is made; gold before == gold after for all five.
- **All revised packets require targeted blind revalidation** before any holdout eligibility.
- **Original packets remain historical evidence** and are never overwritten; revised
  packets are versioned (`_v2`) under `revised_packets/`.
- No holdout is created or frozen. No live model calls. No metrics computed.
