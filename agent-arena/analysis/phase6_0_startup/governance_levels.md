# Phase 6 — Governance Levels (operational)

Purpose: a *simpler but rigorous* operating model. Three levels, chosen by what a
change can influence. The goal is proportional rigor — heavy process only where a
change could affect scientific interpretation, gold, taxonomy, or the holdout.
**Do not create document bureaucracy for ordinary Level 1 work.**

Governance level is determined by the **highest-impact surface a change touches**,
not by effort or line count.

---

## Level 1 — ordinary engineering

**Scope:** changes that cannot alter benchmark semantics, gold, taxonomy, metrics
definitions, or holdout state.

Examples:
- implementation fixes and refactors without semantic change
- tests for existing or new deterministic logic
- internal documentation and comments
- deterministic tooling (e.g. offline integrity checks that only *report*)
- formatting limited to intentionally touched files

**Process:**
- inspect the exact diff before commit
- run relevant tests / validation
- stage only explicit, intended paths (never `git add .`/`-A`/`commit -a`)
- report modified paths

**No checkpoint document required.** A clear commit message suffices.

---

## Level 2 — methodology and evaluation

**Scope:** anything that defines *how we measure or interpret*, on development data.

Examples:
- confidence semantics (range, meaning, handling of missing values)
- calibration methods (e.g. temperature scaling, isotonic) and their fit protocol
- abstention / selective-prediction policy and thresholds
- evaluation metrics (ECE variants, reliability binning, risk–coverage)
- development-set / validation-split protocols and pool definitions
- report interpretation rules

**Requirements:**
- **documented acceptance criteria pre-specified before results** (see
  `phase6_acceptance_criteria.md`)
- **reproducibility:** fixed inputs, fixed seed/config, a manifest binding result →
  (input pool + code commit + parameters)
- **methodology checkpoint** recorded in the relevant phase directory
- **separate preparation and result checkpoints** whenever the operation could
  influence later interpretation (metrics/thresholds must be frozen *before*
  looking at the numbers they will be judged against)

**Level 2 explicitly may NOT:** choose criteria, thresholds, or pool membership
*using the results they will later be evaluated against* (no result-driven
selection); touch the holdout in any way; alter gold or taxonomy.

---

## Level 3 — benchmark, gold, taxonomy, holdout, or public claims

**Scope:** anything that changes the ground truth, the benchmark's meaning, or an
external-facing claim.

Examples:
- taxonomy changes (labels, definitions, precedence, scope)
- gold-label changes; case retirement or un-retirement
- holdout access, holdout evaluation, holdout membership/selection changes
- benchmark membership changes (adding/removing canonical cases)
- final evaluation-protocol changes
- public superiority / performance / product claims

**Requirements (all mandatory):**
- **explicit curator approval** (Lazaros Varvatis) before execution
- **frozen criteria before results** — the decision rule is written and approved
  before any number that could bias it is produced
- **separate preparation and result checkpoints**
- **preserved history** — no rewriting/overwriting of historical Phase-5 artifacts;
  changes are additive with versioning + comparability-impact assessment
- **strict holdout isolation** — the private holdout stays sealed unless a
  dedicated, curator-approved, pre-registered holdout-evaluation protocol is in
  force

**Default for Phase 6.0–6.4:** no Level 3 action is taken. The holdout remains
sealed; taxonomy and gold remain frozen; no public claims are made.

---

## Quick classification table

| change | level |
|--------|-------|
| add offline integrity check that only reports | 1 |
| refactor parser, no behavior change, tests updated | 1 |
| define what `confidence` means / how missing values are handled | 2 |
| choose calibration method + fit on development pool | 2 |
| set an abstention threshold from a development risk–coverage curve | 2 |
| freeze the development pool membership | 2 (prep checkpoint) |
| relabel a case / retire a case | 3 |
| change a taxonomy definition or precedence | 3 |
| open or evaluate the holdout | 3 |
| publish a "we beat prompt-only X" claim | 3 |

**Escalation rule:** when in doubt between two levels, use the higher one. When a
change spans levels, the whole change inherits the highest level it touches.
