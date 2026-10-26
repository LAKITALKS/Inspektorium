# Phase 5.05d — Shortcut-Risk Audit (read-only, all 20 packets)

Deterministic descriptive checks on the annotator-facing case material. The audit
separates three tiers of concern; correlation alone is **not** treated as shortcut use.

## Deterministic checks

### Packet length (words) by gold label
| gold label | n | mean | min | max |
|---|---|---|---|---|
| overclaim | 9 | 83.9 | 36 | 254 |
| solid | 6 | 83.8 | 54 | 104 |
| mechanism_vs_evidence | 2 | 75.0 | 64 | 86 |
| correlation_vs_causation | 3 | 188.3 | 86 | 390 |

### Heading structure
19 of 20 packets share the identical 3-heading structure (Task / Case material / Your
annotation). **BIAA-013 is the sole exception**, adding `## Study` and `## Media Coverage`
sub-headings.

### Taxonomy/label words inside the case material
- **BIAA-013** (gold `correlation_vs_causation`): the material's opening instruction line
  reads "…Identify any **overclaims**, unsupported causal inferences, **mechanism** gaps,
  or **correlation**-as-**causation** issues." — i.e. it names *all four* taxonomy
  categories verbatim.
- **BIAA-012** (gold `solid`): contains the word "causation" once, as part of the authors'
  honest caveat ("does not prove causation"). Benign natural-language occurrence; if
  anything it points *away* from the gold (`solid`), so it is not a cue.

### Leakage probes
- References to original/real case IDs (`caseNNN`) in material: **NONE**.
- Verdict-like headings ("verdict", "gold label", "correct answer"): **NONE**.
- Residual curator commentary embedded in material: **only BIAA-013** (the analysis
  instruction line).

## Three-tier interpretation

### Demonstrated leakage
- **None.** No packet exposes its unique gold label, a real case ID, an internal
  taxonomy decision, or a verdict.

### Plausible shortcut risk
- **BIAA-013** — packet-construction defect: (a) an embedded analysis instruction that
  names all four taxonomy terms, (b) a divergent heading structure, (c) length ~4× the
  corpus mean. Because it names *all four* categories it does **not** uniquely signpost
  `correlation_vs_causation`, so it is a *risk*, not demonstrated leakage. It should be
  reworded to match the neutral fixture template before any holdout use.

### Observed structural correlation (no inference of shortcut use)
- `correlation_vs_causation` packets are longer on average (188 vs ~84 words), but n=3 and
  the mean is driven by BIAA-013 (390) and BIAA-015. With the other three labels tightly
  clustered (~75–84), length is **not** a reliable category signal, and there is no
  evidence any model used it.
- Length ordering does not track difficulty; the hardest soft case (BIAA-007) is one of
  the *shortest* packets (49 words).

## Corroborating evidence against broad shortcutting
The only genuinely independent-family rater (Rater 3) did **not** reproduce gold on three
cases. If packets broadly leaked their labels, that rater would also have scored them.
Its divergence on precisely the two-sided borderline cases is what an un-signposted,
genuinely ambiguous sample should produce.

## Audit conclusion
No demonstrated leakage. One packet (**BIAA-013**) carries a real construction defect and
a plausible (non-unique) shortcut risk; recommend rewording before holdout. All other
structural differences are observed correlations only.
