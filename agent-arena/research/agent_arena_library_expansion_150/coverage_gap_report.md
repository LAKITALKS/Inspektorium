# Coverage Gap Report — Initial (pre-Batch-001)

**Date:** 2026-08-03
**Baseline:** 48 active canonical cases (Phase 5 closeout ledger, v0.8.13-phase5-closeout)
**Taxonomy verified:** `docs/study_forensics_taxonomy.md` v0.6.5 — four labels confirmed unchanged.

---

## 1. Ledger reconciliation (resolved)

Two in-repo sources disagreed:

| Source | Active | Retired |
|---|---:|---:|
| `analysis/phase5_0_active_library_diagnostics/` | 49 | 1 |
| `analysis/phase5_2_closeout/` (authoritative) | 48 | 2 |

**Cause:** `study-forensics-031` (rapamycin_longevity, gold label `solid`,
`gold_case_type: borderline`) was retired *after* the Phase 5.0 snapshot was
generated. Its case file carries `status: retired` /
`excluded_from_active_metrics: true`.

**Resolution:** Phase 5.2 closeout figures adopted. The Phase 5.0 CSVs are a
stale historical artifact and were **not modified** (protected under §2).

This was assessed against the §30 stop condition *"the public case ledger is
inconsistent."* It does not trigger a stop: the discrepancy has a single
identifiable cause and an unambiguous authoritative resolution. Curators should
nonetheless be aware that `label_distribution_active.csv` overstates `solid` by
one.

---

## 2. Label distribution — the dominant gap

| Label | Active | Share | Assessment |
|---|---:|---:|---|
| `overclaim` | 23 | 47.9% | **Heavily over-represented** |
| `solid` | 13 | 27.1% | Adequate |
| `correlation_vs_causation` | 6 | 12.5% | **Thin** |
| `mechanism_vs_evidence` | 6 | 12.5% | **Thin** |

The taxonomy document itself already flags this: `correlation_vs_causation` is
described as *"mature but thin"* (2 clear cases at the time of writing), and
`mechanism_vs_evidence` as *"Developing"* with the weakest model accuracy
(53% avg; Haiku and Opus at 40%).

This matters more than the raw counts suggest. `mechanism_vs_evidence` is both
the thinnest **and** the hardest category — it is the one where added cases buy
the most discriminative power, and where the taxonomy has already had to narrow
its own scope (Shape B explicitly excluded, Shape D marked borderline).

**Implication for the 150-case target.** §7 of the operating protocol sets an
even 35–40 per label across new candidates. Applied to this baseline, an even
split would land the merged library at roughly:

| Label | Merged (48 + 150 even) | Share |
|---|---:|---:|
| overclaim | ~61 | 30.8% |
| solid | ~51 | 25.8% |
| correlation_vs_causation | ~44 | 22.2% |
| mechanism_vs_evidence | ~44 | 22.2% |

That is a substantial improvement and stays inside the §7 band (30–45 per label
among new cases). No deviation from §7 is needed. But if curators want the
*merged* library closer to even, new-case allocation would need to skew toward
the two thin labels — which would require an explicit §7 exception. **Flagged
for curator decision; not assumed.**

---

## 3. Domain distribution

Approximate primary-domain assignment across 48 active cases:

| Domain | Count | Status |
|---|---:|---|
| Clinical medicine | 11 | Saturated |
| Biomedical research | 7 | Well covered |
| AI / machine learning | 7 | Well covered |
| Nutrition & supplements | 5 | Adequate |
| Environmental & climate | 4 | Adequate |
| Public health & epidemiology | 4 | Adequate |
| Pharmaceuticals & biotech | 3 | Light |
| Economics & social policy | 3 | Light |
| Education | 3 | Light |
| Psychology & behavioral | 2 | **Under-represented** |
| Energy & sustainability | 1 | **Under-represented** |
| Software & cybersecurity | 0 | **Empty** |
| Agriculture & food systems | 0 | **Empty** |
| Consumer products & advertising | 0 | **Empty (as primary domain)** |
| Business & market claims | 0 | **Empty** |

**Concentration finding:** the biomedical cluster (clinical + biomedical +
pharma + nutrition) accounts for ~26 of 48 cases (~54%), far above the §7
guideline of no single domain above ~20%. Even treating those as four separate
domains, clinical medicine alone is at 23%.

Four of the fifteen target domains are entirely empty.

---

## 4. Structural / provenance gap

This is the finding with the largest consequence for the operation.

| Origin | Count |
|---|---:|
| `synthetic_fixture` | 21 |
| legacy, no `origin` field | 26 |
| `curated_showcase` | 1 |

Only about **two** active cases (`case_public_001`, `case041`) are traceable to
a named real-world primary source. Roughly 44% of the active library is
explicitly constructed vignettes, and a further ~54% is legacy material whose
provenance is undocumented at case level — `active_case_inventory.csv` flags all
26 as `missing: origin,intake_review`.

Two consequences:

1. **Duplicate control (§15) is weaker than it appears.** Fingerprinting a new
   real-world candidate against a synthetic vignette compares a real claim to an
   invented one. Forensic-shape collision is still detectable and still matters;
   source-level collision is not meaningful against ~44% of the baseline.

2. **Source-voice diversity cannot be measured from the baseline.** §20 requires
   the batch plan to record current source-voice distribution. For 47 of 48
   active cases there is no recorded source voice to distribute. That field is
   reported as *unavailable* rather than fabricated.

---

## 5. Schema mismatch between research output and canonical format

The canonical case format (e.g. `case_public_001_exercise_intensity.yaml`) is a
**self-contained evaluation task**:

```
id, title, domain, difficulty, task_type, task_family, trap_type,
ambiguity_level, prompt, context, expected_answer, reference_solution,
gold_label, gold_confidence, gold_case_type, gold_justification,
gold_alternative_reading, gold_summary, expected_findings,
gold_evidence_spans, evaluation, key_insights, common_errors,
expected_failure_modes, discriminative_dimensions, diagnostic_focus
```

It contains **no** `canonical_url`, `archive_url`, `persistent_identifier`,
`source_sha256`, or `access_date` field. Source material is embedded as text in
`prompt`, not linked.

The §19 research record required by this operation is a different artifact: a
sourcing-and-verification dossier built around URLs, hashes, archive snapshots,
quality scores, and adversarial review.

These are complementary, not interchangeable. A §19 record does not drop into
`tasks/study_forensics/` — a curator would have to re-author each one into task
format (writing `prompt`, `gold_evidence_spans`, `key_insights`,
`common_errors`, `diagnostic_focus`). That is real per-case curator work, and it
should be budgeted rather than discovered at handoff.

---

## 6. Open blocking decision

Before Batch 001 research begins, one decision is required, because it changes
what gets produced and cannot be reversed cheaply after ten candidates exist.

**The question:** should expansion candidates be *real-world-sourced* (per §10–§13:
verified exact quote, canonical URL, archive URL, DOI, publication date, access
date, contrary-evidence search) or *constructed fixtures* in the house style of
cases 043–063?

The protocol text assumes the former throughout. The existing library is ~44%
the latter. Both are defensible; they are not the same deliverable.

A capability constraint bears on this. Under the real-world-sourced route, three
§19 fields are partly beyond this agent:

- `archive_url` — this agent cannot create Wayback snapshots. It can record an
  existing snapshot if one exists.
- `source_sha256` — computable only for content actually retrievable. A number
  of publisher and journal domains are not fetchable by this agent.
- `persistent_identifier_verified` — DOI can be read from metadata but not
  always resolved end-to-end.

§16 makes `source_stability >= 4` a hard gate for CURATOR_READY. If those fields
are treated as strict requirements, a meaningful share of otherwise strong
candidates will land in HOLD_FOR_REVIEW on archival grounds rather than forensic
ones, and ten-per-batch may not be reachable. If they are best-effort with
explicit `unavailable_to_agent` markers, throughput is realistic but the curator
inherits an archival backlog.

**Recommendation:** real-world-sourced, with archive/hash fields best-effort and
explicitly marked. Rationale: the library's thinnest and hardest categories
(`mechanism_vs_evidence`, `correlation_vs_causation`) are exactly where real
claims outperform constructed ones, because real mechanism-to-outcome leaps
carry authentic hedging language that synthetic fixtures tend to caricature. The
existing synthetic block already covers the clean, textbook shapes well.

---

## 7. Recommended priorities for Batch 001

Conditional on §6 being resolved:

1. **Label priority:** `mechanism_vs_evidence` and `correlation_vs_causation`
   weighted above `overclaim`. Do not force labels to hit a ratio (§7).
2. **Domain priority:** software/cybersecurity, agriculture/food systems,
   business/market claims, energy — the four empty or near-empty domains.
3. **Explicit avoid-list for Batch 001:** further clinical-medicine and
   general-`overclaim` cases, absent unusually strong forensic value.
4. **Solid-case discipline (§28):** at least two `solid` candidates that could
   plausibly have been overclaims. The baseline's `solid` cases skew toward
   clean reporting; adversarially-survivable solids are the scarcer good.
