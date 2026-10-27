# Inspektorium documentation

Inspektorium checks the evidence behind AI-generated claims and the integrity of the reports about them.
Evaluators propose findings; Inspektorium verifies their quotations and offsets exactly and blocks by default.

## Start here

- [Getting started](getting-started.md): install, a first `inspect` run and a first `audit` run.
- [How it works](concepts/how-it-works.md): proposals, deterministic checks, bundles, review and release.

## Concepts

- [How it works](concepts/how-it-works.md)
- [Methodology](concepts/methodology.md): the rules behind each check.
- [Threat model](concepts/threat-model.md): which attacks are covered and which are not.

## Guides

- [Reference checker](guides/reference-checker.md): check one answer against its sources with `inspektorium inspect`.
- [Audit workflow](guides/audit-workflow.md): validate, run, inspect, review and release with `inspektorium audit`.

## Reference

- [Command line](reference/cli.md)
- [Report and bundle formats](reference/report-schema.md)
- [Python API](reference/python-api.md)

## Evaluation

- [Evidence](evaluation/evidence.md): what was measured, evidence packages and CI.
- [Reproducibility](evaluation/reproducibility.md): how to recompute results, including historical versions.
- [Limitations](evaluation/limitations.md): every known limit, stated once.

## Research

- [Research plan](research/plan.md): questions Q1–Q5, fault catalog and baselines.
- [Results](research/results.md): observations, including the null result.
- [Claim ledger](research/claims.md): every capability claim with its evidence and status.
- [History](research/history.md): how the project developed, and the research record.

## Project

- [Roadmap](roadmap.md): proposed milestones, subject to funding.
- [Architecture](development/architecture.md), [testing](development/testing.md) and [release process](development/release-process.md).
- [AI assistance](development/ai-assistance.md): how AI was used in development.
- [Migrating from 0.2.0](development/migration-0.3.md).
