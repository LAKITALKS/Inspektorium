# Phase 7A — Neutral Perturbation Anchor Candidate & Source-Intake Log (7A.2, WP-3)

Only the **four new independent neutral anchors** (contract §5) require scientific source intake; the
other six perturbation bases are inherited from the already-approved Boundary (checkpoint `3bdabaf`)
and Adversarial (checkpoint `e9e13e3`) pools via the deterministic §6 selection and are **not**
re-adjudicated here. Per the v1.0 closure principle (§28) this log records four strong accepted cases
plus the material alternatives considered and rejected — it does not manufacture 30 candidates.

**Gold frozen before any model output. 0 model/evaluation calls.** Each accepted anchor is one clean,
representative case per frozen label with a defensible gold and no adversarial trick structure
("neutral" = not drawn from a Boundary/Adversarial stress family; §9 — neutral ≠ easy/synthetic).

---

## Accepted anchors (4)

| id | target gold | claim (decisive proposition) | claim source (public-facing) | load-bearing evidence | accept | reason |
|---|---|---|---|---|---|---|
| **P7A-NEU-001** | `solid` | Periconceptional folic acid substantially reduces neural-tube-defect risk (400 µg/day) | CDC public-health guidance (`cdc.gov/folic-acid`), same recommendation NHS/USPSTF | MRC Vitamin Study RCT (Lancet 1991, ~72% recurrence reduction); USPSTF Grade A | ✅ | Faithful, scoped benefit claim backed by a randomised clinical-endpoint trial + replication + Grade A; clean `solid` with a genuine-but-weak `overclaim` alternate. Distinct domain from the two Boundary solids (Shingrix, SPRINT). |
| **P7A-NEU-002** | `overclaim` | Sensa "sprinkle it on and lose ~30 lb without dieting/exercise", "clinically studied" | FTC deceptive-advertising action (`ftc.gov`, 2014, $26.5M) | FTC: no competent & reliable evidence; invoked studies not adequately controlled | ✅ | Generic unsupported-efficacy inflation — **no** decorative-citation/subgroup/surrogate/superiority/technically-true structure (those are adversarial families). Distinct proposition from brain-training (BND-014) and all A-family overclaims. |
| **P7A-NEU-003** | `correlation_vs_causation` | "Coffee causes cancer" (coffee drinkers have more bladder cancer → coffee raises risk) | Popular health media; documented + re-evaluated by IARC/WHO (Monographs Vol 116, 2016) | IARC 2016: coffee Group 3; prior association attributable to **confounding by smoking** | ✅ | Causal claim from a confounded observational association with a crisp named confounder (smoking) and an authoritative resolution. Distinct confounder/proposition from alcohol J-curve (BND-004), dog ownership (BND-005), breakfast (ADV-005), video games (ADV-006). |
| **P7A-NEU-004** | `mechanism_vs_evidence` | Whole-body cryotherapy "triggers an anti-inflammatory response / reduces tissue damage, so it speeds recovery, relieves pain, improves wellbeing" | Cryotherapy-studio marketing; documented + assessed by FDA consumer update (2016) | FDA 2016: no cleared device, lack of evidence for marketed benefits; Cochrane 2015: evidence insufficient | ✅ | Plausible physiological mechanism (cold blunts acute inflammation) used to imply an **unproven** human clinical benefit, with a genuine outcome-evidence *gap* (not a refuting RCT — avoids the trap that retired ADV-014). Distinct domain from senolytics (BND-009), ginkgo (BND-016), red-light (ADV-013), nattokinase (ADV-017), metformin/spermidine (ADV-003/004). |

All four provenance packets pass the structural `claim_provenance_status` check (real `claim_source_url`,
bounded `claim_exact_span`, declared claim + evidence source roles). Fingerprints frozen pre-model.

---

## Alternatives considered and rejected (independence / cleanliness screen, §10)

| candidate | target gold | reject reason |
|---|---|---|
| Lumosity brain-training "improves everyday cognition / staves off dementia" | overclaim | **Duplicate decisive proposition** with Boundary `P7A-BND-014` ("brain-training games make you smarter and prevent dementia"). Rejected → Sensa. |
| "A daily glass of red wine protects your heart" (alcohol J-curve) | correlation_vs_causation | **Already an active Boundary base** (`P7A-BND-004`). Rejected → coffee/smoking. |
| Night-light in a child's room "causes myopia" (Quinn 1999) | correlation_vs_causation | Clean confounding case, but the public-facing causal claim's durable single-source provenance is weaker than IARC's authoritative coffee re-evaluation. Rejected in favour of the better-anchored coffee case. |
| Blue-light-blocking glasses "improve sleep / protect eyes" | mechanism_vs_evidence | The mechanism (blue light suppresses melatonin) is real, but Cochrane 2023 provides **outcome trials** (uncertain/null) — risks making `overclaim` equally defensible and undermining a unique `mechanism_vs_evidence` gold (the failure mode that retired ADV-014). Rejected → cryotherapy (genuine evidence *gap*, not refutation). |
| Resveratrol/sirtuins "extends healthy human lifespan" | mechanism_vs_evidence | Clean mechanism→benefit gap, but thematically close to the anti-aging/longevity supplement space of ADV-003/004 and BND-009. Rejected to keep the anchor set obviously distinct → cryotherapy. |

**No holdout / client / LaVita material consulted. No demo-derived material. No error-driven selection.**
