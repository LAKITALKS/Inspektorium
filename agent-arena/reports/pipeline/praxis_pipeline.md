# Agent Arena — Pipeline Report

**Generated:** 2026-04-07T08:04:16.745749+00:00  

**Journal:** `.agent_arena`  

**Entries analyzed:** 57

## Steps Executed

| Step | Status | Detail |
|------|--------|--------|
| load_journal | [+] completed | Loaded 57 entries (19 tasks, 3 models) |
| insights | [+] completed | 3 model profiles, 4 category maturity assessments, 4 disagreement cases, 6 borderline signals |
| calibrate | [+] completed | 23 proposals (gold_review: 6, data_gap: 1, cat_refinement: 3, model_confusion: 7, fp_reduction: 6) |
| router | [+] completed | 4 routing recommendations |
| disagreement_lab | [+] completed | 4 disagreement cases, 4 borderline signals, 3 gold-review signals |
| caseforge | [+] completed | 6 candidates generated |
| audit_trail | [+] completed | Workflow note logged: dec_20260407_080416_7ea363 |

## Insights Summary

**Model profiles:** 3

- **claude-haiku-4-5-20251001**: avg score 61.6, 19 runs

- **claude-opus-4-20250514**: avg score 61.1, 19 runs

- **claude-sonnet-4-20250514**: avg score 63.0, 19 runs

### Category Maturity

| Category | Correctness | Maturity | Runs |
|----------|-------------|----------|------|
| correlation_vs_causation | 67% | developing | 9 |
| mechanism_vs_evidence | 47% | unstable | 15 |
| overclaim | 80% | mature | 15 |
| solid | 100% | mature | 18 |

## Calibration Summary

**Total proposals:** 23

### Gold Review Candidates

- **study-forensics-007**: All models incorrect with high confidence — unanimous wrong answer

- **study-forensics-013**: Stable cross-model disagreement on classification

- **study-forensics-024**: Stable cross-model disagreement on classification

- **study-forensics-030**: Stable cross-model disagreement on classification

- **study-forensics-031**: All models incorrect with high confidence — unanimous wrong answer

- **study-forensics-public-001**: Stable cross-model disagreement on classification

### Data Gaps

- **solid**: Category 'solid' has 100% correctness — may lack borderline / challenging cases

### Category Refinement

- **mechanism_vs_evidence**: Low correctness rate (47%) suggests category instability

- **mechanism_vs_evidence**: High disagreement rate (60%) in 5 multi-model cases

- **mechanism_vs_evidence**: Label scatter: family label 'mechanism_vs_evidence' appears in only 47% of runs

## Routing Recommendations

| Target | Mode | Confidence | Models | Cost |
|--------|------|------------|--------|------|
| correlation_vs_causation | multi | medium | claude-sonnet-4-20250514, claude-opus-4-20250514, claude-haiku-4-5-20251001 | standard |
| mechanism_vs_evidence | disagreement | medium | claude-sonnet-4-20250514, claude-opus-4-20250514, claude-haiku-4-5-20251001 | invest_in_quality |
| overclaim | multi | medium | claude-sonnet-4-20250514, claude-opus-4-20250514, claude-haiku-4-5-20251001 | standard |
| solid | multi | medium | claude-sonnet-4-20250514, claude-opus-4-20250514, claude-haiku-4-5-20251001 | standard |

## Disagreement Findings

**Cases analyzed:** 19

**Disagreement cases:** 4

**Borderline signals:** 4

**Gold-review signals:** 3

### Disagreement Cases

- **study-forensics-013**: solid(2), mechanism_vs_evidence(1) — entropy 0.92, root issue: category_boundary

- **study-forensics-024**: overclaim(2), mechanism_vs_evidence(1) — entropy 0.92, root issue: category_boundary

- **study-forensics-030**: overclaim(1), mechanism_vs_evidence(2) — entropy 0.92, root issue: model_limitation

- **study-forensics-public-001**: overclaim(2), solid(1) — entropy 0.92, root issue: gold_label

## Caseforge Candidates

**Candidates generated:** 6

- **cf_soli_88ea560b**: solid (data_gap) — solid

- **cf_soli_3829553a**: solid (confusion_probe) — solid

- **cf_over_d7dcea82**: overclaim (confusion_probe) — overclaim

- **cf_soli_3829553a**: solid (confusion_probe) — solid

- **cf_mech_ef995897**: mechanism_vs_evidence (calibration_signal) — mechanism_vs_evidence

- **cf_mech_ef995897**: mechanism_vs_evidence (calibration_signal) — mechanism_vs_evidence

## Audit Trail

Workflow note logged: `dec_20260407_080416_7ea363`

## Items Requiring Human Review

- [insights] Borderline candidate: study-forensics-013 — High cross-model disagreement on classification
- [insights] Borderline candidate: study-forensics-024 — High cross-model disagreement on classification
- [insights] Borderline candidate: study-forensics-030 — High cross-model disagreement on classification
- [insights] Borderline candidate: study-forensics-public-001 — High cross-model disagreement on classification
- [insights] Borderline candidate: study-forensics-007 — All models incorrect with high confidence — possible gold label issue
- [insights] Borderline candidate: study-forensics-031 — All models incorrect with high confidence — possible gold label issue
- [calibrate] Gold review: study-forensics-007 — All models incorrect with high confidence — unanimous wrong answer
- [calibrate] Gold review: study-forensics-013 — Stable cross-model disagreement on classification
- [calibrate] Gold review: study-forensics-024 — Stable cross-model disagreement on classification
- [calibrate] Gold review: study-forensics-030 — Stable cross-model disagreement on classification
- [calibrate] Gold review: study-forensics-031 — All models incorrect with high confidence — unanimous wrong answer
- [calibrate] Gold review: study-forensics-public-001 — Stable cross-model disagreement on classification
- [calibrate] Category refinement: mechanism_vs_evidence — Low correctness rate (47%) suggests category instability
- [calibrate] Category refinement: mechanism_vs_evidence — High disagreement rate (60%) in 5 multi-model cases
- [calibrate] Category refinement: mechanism_vs_evidence — Label scatter: family label 'mechanism_vs_evidence' appears in only 47% of runs
- [disagreement_lab] Gold review signal: study-forensics-013 — root issue: category_boundary
- [disagreement_lab] Borderline: study-forensics-013 — entropy 0.92
- [disagreement_lab] Gold review signal: study-forensics-024 — root issue: category_boundary
- [disagreement_lab] Borderline: study-forensics-024 — entropy 0.92
- [disagreement_lab] Borderline: study-forensics-030 — entropy 0.92
- [disagreement_lab] Gold review signal: study-forensics-public-001 — root issue: gold_label
- [disagreement_lab] Borderline: study-forensics-public-001 — entropy 0.92
- [caseforge] 6 case candidate(s) pending review

## Recommended Next Actions

1. Review 6 gold-review candidate(s) via `agent-arena audit-log add`
2. Address 1 data gap(s) — consider `agent-arena caseforge`
3. Investigate 3 gold-review signal(s) from disagreement analysis
4. Review 6 caseforge candidate(s) — all pending human review

---
*Gen 7 Pipeline — orchestration only. No decisions made, no data modified. All items require human review.*
