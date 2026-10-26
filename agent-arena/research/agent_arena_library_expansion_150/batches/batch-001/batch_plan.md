# Batch 001 — Plan

**Batch:** 001 of 015
**Date planned:** 2026-08-03
**Status:** ACTIVE — blocking decisions resolved 2026-08-03 (see §8)

Per §20, this plan exists before candidate selection. No predetermined cases are
named.

---

## 1. Current totals at plan time

| Metric | Value |
|---|---:|
| Curator-ready expansion candidates completed | 0 / 150 |
| Completed batches | 0 / 15 |
| Next candidate ID | AAEXP-0001 |
| Active canonical baseline | 48 |

## 2. Aggregate distributions at plan time

**Provisional label distribution (expansion candidates):** empty — this is the
first batch.

**Canonical active label distribution (baseline for gap targeting):**
solid 13 (27.1%) · overclaim 23 (47.9%) · correlation_vs_causation 6 (12.5%) ·
mechanism_vs_evidence 6 (12.5%)

**Canonical domain distribution:** see `coverage_gap_report.md` §3.

**Canonical source-voice distribution:** **unavailable.** 47 of 48 active cases
record no source voice. Not fabricated; reported as a known gap.

## 3. Underrepresented categories

**Labels:** `mechanism_vs_evidence`, `correlation_vs_causation` (6 each, and the
two weakest categories by model accuracy — 53% and the thinnest pool).

**Domains (empty):** software & cybersecurity · agriculture & food systems ·
business & market claims · consumer products as a primary domain.

**Domains (thin):** energy & sustainability (1) · psychology & behavioral (2).

## 4. Intended target mix for Batch 001

Ten curator-ready candidates, targeted as:

**REVISED 2026-08-03 following the QC-001 taxonomy ruling.** Supersedes the
pre-QC-001 mix (mech 4 / corr 3 / solid 2 / overclaim 1).

| Label | Target | Filled | Note |
|---|---:|---:|---|
| `correlation_vs_causation` | 4 | 0 | Thin category, domain-general — now the main growth path |
| `solid` | 3 | 0 | Must be adversarially survivable (§28) |
| `overclaim` | 2 | **1** | AAEXP-0001 |
| `mechanism_vs_evidence` | 1 | 0 | Frozen biological scope only — must be biomedical/preclinical |

Four labels represented, satisfying the §7 three-label minimum.

Derived from the revised 150-case portfolio target:
solid 46 · overclaim 37 · correlation_vs_causation 52 · mechanism_vs_evidence 15.

**QC-001 ruling (2026-08-03):** the frozen biological definition of
`mechanism_vs_evidence` stands. Non-biological cases — technical mechanisms,
simulations, laboratory-only software performance, benchmark behaviour,
cybersecurity defenses — do **not** automatically receive that label; they are
classified under the label matching the actual dominant defect. Such cases carry
`future_taxonomy_review.possible_domain_general_mechanism_analogue: true` as
research metadata only. See `future_taxonomy_review_issue.md` (deferred — not to
be resolved during this run).

The earlier §7 exception under BD-003 is superseded by this revised allocation.

**Surplus handling:** an excellent candidate whose label target is already full
goes to the documented **reserve queue**, not to rejection or reclassification.

**These are targets, not quotas.** §7 is explicit that a label must not be
assigned to satisfy balance. If the evidence supports a different label, the
label follows the evidence and the mix moves.

## 5. Planned search domains

Priority order, weighted to empty and thin domains:

1. Software & cybersecurity — vulnerability severity vs exploitability, lab vs
   production benchmarks, vendor efficacy claims
2. Agriculture & food systems — yield/sustainability claims, greenhouse vs field
   trials, regenerative-practice carbon claims
3. Energy & sustainability — lifecycle boundary claims, grid-scale storage,
   carbon-neutrality wording
4. Business & market claims — advertising-standards and consumer-protection
   adjudications (ASA, FTC, EU equivalents)
5. Psychology & behavioral — intervention effect sizes, replication status
6. Secondary fill: biomedical *only* where the forensic shape is genuinely novel
   relative to the 26 existing biomedical cases

## 6. Planned source types

Claim sources, in §14 preference order: official publications and technical
reports · official press releases · company/institution pages · system and model
cards · regulatory and advertising-standards decisions · verified official
accounts.

Evidence sources: primary studies · regulatory assessments · systematic reviews
and meta-analyses · trial registries · benchmark documentation · independent
replications and reanalyses.

## 7. Known duplicate risks

| Risk | Mitigation |
|---|---|
| Forensic-shape collision with synthetic fixtures 043–063 (which already cover textbook shapes: relative-vs-absolute risk, subgroup generalization, surrogate endpoints, no-adverse-events-means-safe, best-in-class without head-to-head) | Fingerprint on forensic shape, not just source. A real-world instance of an already-covered textbook shape is a near-duplicate unless it adds distinct forensic value (§15) |
| AI/ML benchmark cases colliding with 025, 027, 039, 058, 060, 061 | Six AI cases already exist. Require a distinct evidence-mismatch type, not just a different model or vendor |
| Mechanism-to-human-benefit collision with 013, 024, 028, 030, 036, 044 | Existing mechanism cases are all animal/preclinical biomedical. Prefer non-biomedical mechanism cases (engineering, environmental, materials) to widen the shape |
| Single-source clustering | Max 5 cases per company/institution/campaign/underlying study across all 150 (§7) |

## 8. Blocking decisions — RESOLVED 2026-08-03

**BD-001 — Artifact type: real-world-sourced.** Verified public claims with
verified claim sources and sufficient evidence context. Existing synthetic
fixtures remain canonical but are not the template. Dossiers are produced in §19
format and are *not* rewritten into canonical task YAML; house-format conversion
is a separate curator step. Each accepted dossier records
`conversion_suitability`: `canonical_case` | `blind_packet` | `both` | `neither`.
Curator conversion workload is estimated in the batch report.

**BD-002 — Archival fields: best-effort, not hard gates.** `archive_url`,
`source_sha256`, and `persistent_identifier` may carry `unavailable_to_agent`,
`not_applicable`, or `source_does_not_provide_identifier`. Identifiers and hashes
are never invented. A strong case is not rejected because an external archive
service is unavailable — but a case *is* held or rejected when the underlying
claim is itself unstable, unverifiable, or unlikely to remain recoverable.

CURATOR_READY still requires: exact claim verified · canonical URL stable ·
exact source location recorded · access date recorded · source voice verified ·
primary evidence verified · contrary-evidence search complete · duplicate control
passed · source recoverable for curator review.

**BD-003 — Label allocation: skew to thin labels.** See §4.

## 9. Quality threshold

Per §16, unchanged: total ≥ 40/50; claim verifiability ≥ 4; source-voice clarity
≥ 4; evidence completeness ≥ 4; source stability ≥ 4; clean duplicate status;
contrary-evidence search complete; label confidence medium or high.

No threshold relaxation is authorized to reach ten (§6, §21).

## 10. Stop conditions for this batch

- Duplicate rate exceeds 50% of researched leads
- The same critical source-verification error repeats across the batch
- `mechanism_vs_evidence` cannot be populated without weak cases
- Two of two deterministically audited candidates materially fail (§22)
- Any §30 condition triggers

On any of these: halt, persist state, write the RESUME BLOCK, request curator
guidance.
