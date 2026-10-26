# Quality Control Log

## QC-001 — Taxonomy scope conflict: `mechanism_vs_evidence`

**Raised:** 2026-08-03, during Batch 001 verification of AAEXP-0001
**Status:** OPEN — escalated to curator, blocks Batch 001 target mix
**Severity:** HIGH — affects 4 of the 10 Batch 001 targets and 44 of the 150 portfolio targets

### The conflict

Two governing documents define `mechanism_vs_evidence` incompatibly.

**Frozen taxonomy `docs/study_forensics_taxonomy.md` v0.6.5:**

> "A biological mechanism is described and used to imply human clinical
> benefit, but the evidence for that benefit does not exist."
>
> Core signal: "Animal or preclinical mechanism presented as basis for human
> therapeutic claims."

Both empirically validated shapes are biomedical:

- Shape A — "A study demonstrates a mechanism in mice/rodents/animals"
- Shape C — "A molecular pathway is described with impressive preclinical results"

Shape B (biomarker-to-clinical) is *explicitly excluded*. Shape D is borderline-only.
All five cited examples (013, 024, 028, 030, 031) are biomedical.

**Operating protocol §8:**

> "mechanistic, preclinical, surrogate, simulation, or theoretical evidence"
>
> including "simulations, technical mechanisms, laboratory-only performance,
> theoretical models" — with unsupported outcomes including "operational
> superiority, consumer benefit, environmental benefit."

§8 is domain-general. v0.6.5 is biological.

### Why this blocks the batch

Two curator instructions now pull in opposite directions:

1. Batch 001 targets **4 `mechanism_vs_evidence`** cases (the largest single target).
2. Batch 001 must prioritize **software/cybersecurity, agriculture, business/market,
   consumer, energy, psychology** and "avoid overloading Batch 001 with
   biomedical cases."

Under frozen v0.6.5, `mechanism_vs_evidence` **only exists in biomedical form**.
So the two instructions cannot both be satisfied:

- Sourcing mechanism cases from the priority domains requires extending the
  frozen category to non-biological mechanisms — which §2 forbids ("Do not
  modify existing taxonomy definitions") and §8 forbids ("Do not change this
  taxonomy").
- Staying inside frozen v0.6.5 forces all 4 mechanism cases to be biomedical —
  directly against the domain-diversification instruction, and into the domain
  already at ~54% saturation.

§30 lists "continuation would require changing existing gold or taxonomy" as a
formal stop condition, and instructs: *"Do not resolve governance conflicts by
improvisation."* Hence this escalation rather than an agent-side ruling.

### Interim handling applied

AAEXP-0001 (LLM jailbreak-defense robustness claim) was labelled **`overclaim`**,
not `mechanism_vs_evidence`, to stay strictly inside frozen v0.6.5 — even though
under §8's broader definition `mechanism_vs_evidence` is arguably the better
fit. `label_confidence` is set to `medium` and the disagreement is documented in
`adversarial_review.reasonable_reviewer_disagreement`.

This interim choice is conservative but **not** a precedent. If the curator rules
that the category extends to non-biological mechanisms, AAEXP-0001 should be
re-examined for relabelling.

### Options for the curator

| Option | Effect | Cost |
|---|---|---|
| **A. Extend the category** to non-biological mechanisms (simulation, lab-only performance, theoretical models) | Unblocks the 44-case portfolio target across all domains | A taxonomy revision. v0.6.5 would need a version bump and the existing 6 mechanism cases re-examined for consistency. Prior IAA/model-accuracy results were measured against the narrower definition |
| **B. Keep the category biological** | Taxonomy untouched | Mechanism cases must be biomedical. The 44-case target then forces heavy biomedical concentration, worsening the ~54% saturation the expansion was partly meant to fix |
| **C. Keep it biological, cut the mechanism target** and reallocate to `correlation_vs_causation` / `solid` | Taxonomy untouched, domain diversity preserved | The thinnest and hardest category stays thin — the original reason for the skew decision |
| **D. Add a new sibling category** (e.g. `lab_vs_deployment`) for non-biological mechanism-style gaps | Preserves both the frozen category and domain breadth | Breaks the frozen four-label taxonomy; large downstream impact on gold labels, packets, and all prior validation |

**Agent recommendation:** Option A or C. Option A if the curator wants the
category to do domain-general work (which §8 clearly envisages); Option C if
taxonomy stability outranks category growth this cycle. Option D is flagged for
completeness but is the most disruptive and is not recommended.

### Note on a related observation

The frozen taxonomy also records `correlation_vs_causation` as having "only 2
cases in current pool" — but the current active library holds 6. The taxonomy
doc's maturity table is a v0.6.5-era snapshot and has not been updated as the
library grew. Not blocking; flagged so it is not mistaken for current truth.

---

## QC-002 — Secondary-source figure discrepancy caught during verification

**Raised:** 2026-08-03 · **Status:** CLOSED — no error propagated

During AAEXP-0001 verification, a secondary summary reported Circuit Breakers
attack-success figures of "28% static / 99% adaptive / 95% human red-teaming."
Direct reading of §5.2 of the primary paper gives **100% ASR** via the RL-based
method on HarmBench.

The secondary figures were discarded and only the directly-read primary text was
used. Logged as a concrete instance justifying the §12 prohibition on relying on
secondary reporting, and as a standing reminder for later batches.
