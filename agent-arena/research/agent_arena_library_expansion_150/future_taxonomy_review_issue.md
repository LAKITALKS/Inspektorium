# Future Taxonomy Review Issue — deferred, do not resolve during this expansion run

**Opened:** 2026-08-03
**Status:** DEFERRED BY CURATOR DECISION — recorded for a later taxonomy cycle
**Do not act on this during the library-expansion operation.**

---

## Summary

The operating research protocol for this expansion used a **broader,
domain-general** interpretation of `mechanism_vs_evidence` than the **frozen
taxonomy** authorises. The two definitions were reconciled in favour of the
frozen taxonomy. This issue records the divergence so it is not silently lost.

## The divergence

**Frozen taxonomy — `docs/study_forensics_taxonomy.md` v0.6.5 (authoritative):**

> "A biological mechanism is described and used to imply human clinical
> benefit, but the evidence for that benefit does not exist."

Validated shapes are biomedical only:

- Shape A — mechanism demonstrated in mice / rodents / animals
- Shape C — molecular pathway with preclinical results framed as future therapy
- Shape B (biomarker-to-clinical) — **explicitly excluded**
- Shape D (strong preclinical + cautious reporting) — borderline only

**Operating research protocol §8 (broader):**

> "mechanistic, preclinical, surrogate, simulation, or theoretical evidence"

explicitly including "simulations, technical mechanisms, laboratory-only
performance, theoretical models," with unsupported outcomes including
"operational superiority, consumer benefit, environmental benefit."

## Curator resolution (2026-08-03)

The frozen biological definition **stands**. Non-biological cases —technical
mechanisms, simulations, laboratory-only software performance, benchmark
behaviour, cybersecurity defenses — do **not** automatically receive
`mechanism_vs_evidence`. They are classified under the label matching the actual
dominant defect, normally `overclaim`, `correlation_vs_causation`, or `solid`.

Consequence accepted by the curator: the `mechanism_vs_evidence` portfolio
target was reduced from 44 to 15. The smaller total is a consequence of the
frozen taxonomy, **not** grounds to misclassify cases or to overconcentrate the
library in biomedical domains.

## Why this is worth revisiting later

Non-biological claims do exist with the same *structural* defect the category
describes — a mechanism or laboratory-only demonstration standing in for
evidence of the claimed real-world outcome. Under the frozen taxonomy these are
absorbed into `overclaim`, which is already the library's largest category
(47.9% of active cases at baseline).

Two consequences a future taxonomy cycle may wish to weigh:

1. **Signal dilution.** `overclaim` accumulates structurally distinct failure
   modes. The taxonomy's own key discriminator for `overclaim` is that "the
   *framing* of the results is the problem, not the results themselves" — which
   does not describe a lab-to-deployment evidence gap especially well.
2. **A growing annotated record.** Candidates carrying
   `future_taxonomy_review.possible_domain_general_mechanism_analogue: true`
   will accumulate across the 15 batches. That set is the natural evidence base
   for deciding whether a domain-general category (or an explicit Shape E within
   the existing one) is warranted.

## Cases flagged so far

| Candidate | Assigned label | Domain | Analogue rationale |
|---|---|---|---|
| AAEXP-0001 | `overclaim` | software & cybersecurity | Representation-control mechanism carries a generality claim; lab-only benchmark performance substitutes for demonstrated robustness against adaptive adversaries |

*(Table appended as further candidates are flagged.)*

## Related minor observation

The v0.6.5 maturity table records `correlation_vs_causation` as having "only 2
cases in current pool." The active library now holds 6. The table is a
v0.6.5-era snapshot that has not tracked library growth. Non-blocking; noted so
it is not mistaken for current truth.

## Explicit non-actions

- `docs/study_forensics_taxonomy.md` — **not modified**
- No existing gold label — **not modified**
- No fifth label created
- `future_taxonomy_review` is research metadata only and carries no label force
