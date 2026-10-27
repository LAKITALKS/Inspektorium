# Roadmap

**Status: proposed, subject to funding.** The milestones below are planned work. None of them is part of 0.3.0.

## Where 0.3.0 stands

- One package and one command: `inspektorium inspect` and `inspektorium audit`.
- `inspect` binds claim spans and quotations to exact offsets and gates reportability on them (report schema 0.1).
- Reports show untrusted text as data; it cannot create report structure or hide warnings.
- `audit` writes hash-bound bundles, records human review and releases only on an explicit step.
- Scientific efficacy is not established; the owner-reported pilot is a [null result](research/results.md#outcomes-including-the-null-result).

## M1 — Evaluator provenance and `inspektorium verify`

**Months 1–2.** Goal: anyone can check a saved report or bundle without trusting the installation that produced it.

Work packages:

- Record evaluator identity, prompt version and model in the report, in a new report schema version.
- Add `inspektorium verify`: re-check a saved report against its sources and recompute bundle hashes.
- Publish counter-tests: altered report, swapped source, foreign or truncated bundle.

Acceptance: `verify` rejects every altered artifact of the published counter-test set and accepts each unchanged original.
This closes the documented limit P16 ([claim ledger](research/claims.md)).

Not claimed: a verified report does not show that the evaluator's judgments are correct.

## M2 — Report-integrity catalog

**Months 2–4.** Goal: a public, repeatable method to test whether model output can forge evaluation reports or hide warnings.

Work packages:

- A catalog of attack inputs with clean counterparts: control, bidirectional and zero-width characters, Markdown and HTML injection, terminal escape codes, forged status lines.
- Adapters for two to three widely used open-source evaluation tools that render model output in reports.
- A responsible-disclosure process for findings in third-party tools.

Acceptance: the catalog runs offline with one command; every attack has a clean counterpart; results per tool and version are published after disclosure.

Not claimed: a tool that passes the catalog is safe in every viewer or font.

## M3 — Integration

**Months 3–5.** Goal: use Inspektorium as a gate in existing pipelines.

Work packages:

- A PyPI package.
- A GitHub Action and a pre-commit hook that fail when a finding is not reportable.
- A published JSON Schema for reports and bundles.

Acceptance: an example repository runs the Action and the hook, and the JSON Schema validates every committed example report.
The PyPI package passes the installation check in [testing](development/testing.md).

Not claimed: a passing gate certifies the content of the checked answer.

## M4 — Validation study

**Months 2–6.** Goal: answer research questions Q1 and Q4 of the [research plan](research/plan.md) with a preregistered design.

Work packages:

- Preregister hypotheses, analysis units, baselines and stopping rules before any data collection.
- Use a licensed public corpus and independent human reviewers.
- Run live models only within an approved budget.

Acceptance: the preregistration is public before data collection; results, data and code are published, including null results.

Not claimed: any outcome before the study runs. H01 stays an untested hypothesis until then.

## M5 — Adoption and publication

**Months 4–6.** Goal: real use and a citable publication.

Work packages:

- Pilot users in law, health communication and journalism, using their own material.
- A submission to the Journal of Open Source Software, based on the [paper draft](../paper/paper.md).
- A Zenodo DOI for the release.

Acceptance: three pilot users document use on their own material, with their permission; the JOSS submission is filed; the release has a DOI.

Not claimed: endorsement by pilot users or reviewers before they give it.

Each milestone has a GitHub issue with the label `roadmap`.
