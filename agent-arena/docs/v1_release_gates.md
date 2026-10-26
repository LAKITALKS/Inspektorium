# Agent Arena — v1.0 Release Gates (canonical roadmap requirement)

> **Publication update — 2026-10-26:** technical research prerelease **1.0.1**
> is published with P1–P10 source. See [public scope and provenance](../PUBLICATION.md).
> Historical closeout wording below refers to the original internal 1.0.0.
> The scientific Final v1 gate remains NOT MET. No new live run is authorized.

*Permanent product requirement, recorded by WP-7C. This document **freezes a requirement**; it does
**not** schedule or implement it now, and it creates **no** new phase. The benchmark engine described
here is built only at final v1.0 readiness, after Phases 8, 9, 10 and final real-case/library
validation. Do not create "Phase 11" for it.*

## R1 — v1.0 Harness Efficacy Benchmark (FINAL RELEASE / APPLICATION VALIDATION GATE)

**Purpose.** Measure the value of the **complete Agent Arena v1.0 harness itself** — not merely the raw
performance of an individual LLM. Agent Arena is a *harness*; its quality and the underlying model's
capability are **distinct variables** (see R5). The gate answers: *how much does the full Agent Arena
system add on top of the same model used plainly?*

**Minimum design (record now; do not overengineer, do not build now).** Compare the **same underlying
model** under at least:

- **Condition A —** model **+ complete Agent Arena v1.0 harness** (full package: claim→provenance→
  evidence→finding chain, runtime contract, parser/judge, robustness controls, artifact-binding /
  derived-value / search-scope / symmetry / release gates, end-to-end audit + report).
- **Condition B —** the **same model without the Agent Arena harness** — a controlled prompt-only /
  minimal baseline.

Hold everything else as comparable as reasonably possible (same cases, same gold, same runtime family,
same dataset version).

**The benchmark must measure, at minimum:**
- overall task accuracy / verdict quality
- calibration
- failure topology (e.g. the `mechanism_vs_evidence ↔ overclaim` seam)
- robustness to perturbation
- claim/evidence fidelity
- artifact correctness
- provenance / binding failures
- search-scope failures (where applicable)
- end-to-end audit / report reliability

**Completion criterion is _harness efficacy_, not "did the model pass".** A weak foundation model can
remain the limiting factor even under an excellent harness; a strong foundation model may extract more
value from the same harness. The gate reports the **delta A − B**, per model, never pooled.

## R2 — Why this is NOT Phase 6.4

Phase 6.4 was an **early, package-level contrast** (Agent Arena package vs prompt-only Haiku) and
remains useful **historical** evidence. It does **not** satisfy R1: the v1.0 Harness Efficacy Benchmark
evaluates the **completed** system after Phases 7–10 and final real-case/library validation, across the
full metric set above (artifact correctness, provenance/binding, search-scope, end-to-end audit
reliability) — dimensions that did not exist at 6.4. R1 supersedes 6.4 as the release gate; 6.4 is not
retired, it is reclassified as a historical baseline.

## R3 — Longitudinal version benchmark (permanent baseline)

The first v1.0 Harness Efficacy Benchmark becomes the **historical baseline** for every future release
(v1.1, v1.2, v1.3, v1.5, v2.0, …). The question future runs must answer is **"did the *harness* itself
improve?"** — not merely "did a newer foundation model get stronger." To keep comparisons interpretable,
every benchmark run must preserve and freeze:

- benchmark version
- dataset / version fingerprints (scientific manifest + case/variant fingerprints)
- model identity (exact dated snapshot)
- runtime contract (+ fingerprint)
- harness version (execution-plan version + package fingerprint + driver source hash)
- baseline condition definition (the exact Condition B)
- metrics
- result-set fingerprints

This mirrors the Phase-7A provenance already in use (e.g. `scientific_manifest_fingerprint`,
`runtime_contract_fingerprint`, `aggregate_result_set_fingerprint`, `driver_source_sha256`), so
harness-improvement and model-improvement never get conflated.

## R4 — Case Library growth vs frozen-experiment identity

The Case Library **should grow** over time. However, Case Library expansion is **never** a reason to
invalidate or reopen a frozen experiment (e.g. Phase 7). Future benchmark versions must preserve
**dataset/version identity** so that *old-version comparison* and *expanded-library comparison* are kept
separate and are never conflated. A new library version is a new benchmark dataset fingerprint, not a
retroactive edit of a frozen one.

## R5 — v1.0 model-strategy principle (no production model selected here)

Participation in Phase 7 does **not** designate a production model. Do **not** encode "Haiku is the
production model" merely because it ran in Phase 7. Harness quality and foundation-model capability are
distinct variables: a weak model can bottleneck an excellent harness, and a strong model can gain more
from the same harness. Production-model selection is a separate decision, made elsewhere, on its own
evidence — not fixed by this document.

## Status

| gate | state |
|---|---|
| R1 v1.0 Harness Efficacy Benchmark | **REQUIREMENT FROZEN** — engine not built; scheduled after Phases 8/9/10 + final validation |
| R2 Phase-6.4 distinction | **RECORDED** |
| R3 longitudinal version benchmark | **RECORDED** |
| R4 case-library identity rule | **RECORDED** |
| R5 model-strategy principle | **RECORDED** |

*Note (13.10.2026):* the local tag `v1.0.0` marks the **internal technical v1 closeout** only ([V1_SCOPE.md](../V1_SCOPE.md)). It does not satisfy R1; the efficacy benchmark remains a separate, separately commissioned task.

*Do not implement the benchmark engine now. This is the frozen requirement only.*
