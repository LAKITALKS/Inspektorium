---
title: 'Inspektorium: fail-closed evidence integrity for AI-generated claims and AI evaluation reports'
tags:
  - Python
  - AI assurance
  - LLM evaluation
  - citation verification
  - provenance
authors:
  - name: Lazaros Varvatis
    affiliation: 1
affiliations:
  - name: Independent Researcher, Berlin, Germany
    index: 1
date: 27 October 2026
bibliography: paper.bib
---

> **Draft.** This paper is a draft in the format of the Journal of Open Source Software. It has not been submitted.

# Summary

Inspektorium is a Python package and command-line tool that checks the evidence behind AI-generated claims and the integrity of the reports about them.
An evaluator, human or model, proposes findings: a claim span in an answer, a relation to a source and supporting quotations with character offsets.
Inspektorium does not judge whether the relation is true.
It verifies that each claim span and each quotation matches the supplied text exactly at the stated offsets.
A finding that fails this check is not reportable; the report shows the failure instead of the proposed relation.
Reports render untrusted text as data, so answer, source or evaluator text cannot create report structure or hide warnings.
An audit workflow writes hash-bound bundles, records human review as new immutable revisions and releases artifacts only on an explicit step.

# Statement of need

Language models cite sources that do not exist or that say something else [@ji2023survey; @liu2023verifiability].
Evaluation pipelines therefore check attribution, often with another model as the judge [@rashkin2023attribution; @gao2023alce].
Two gaps remain.
First, a judge's own evidence pointers are rarely checked: a quotation that a judge cites as support may be altered, misplaced or invented.
Second, evaluation reports embed the text they evaluate.
That text can carry injected instructions or display tricks [@perez2022ignore; @greshake2023indirect].
A report can then show a forged status line or hide a warning.

Inspektorium addresses both gaps with deterministic checks that fail closed.
It is meant for researchers and practitioners who audit model outputs or evaluation reports.
They need each reported finding to rest on verifiable evidence pointers.
Typical users are evaluation engineers, auditors of AI-assisted documents and research groups that compare evaluators.

# State of the field

Most related tools *decide support* with a model.
RAGAS computes a faithfulness score with an LLM [@es2024ragas], and FActScore scores atomic facts [@min2023factscore].
MiniCheck and RefChecker classify claim support with small models or LLMs [@tang2024minicheck; @hu2024refchecker].
SelfCheckGPT detects hallucinations from sampling consistency [@manakul2023selfcheckgpt].
LettuceDetect predicts hallucinated character spans with a token classifier [@kovacs2025lettucedetect].
The open-source tool anchor[^anchor] gates on natural language inference and emits offsets for the sentences it matched.
These tools answer whether a claim is supported; Inspektorium answers whether the evidence an evaluator cites is exactly where the evaluator says it is.

Provider features such as the Anthropic Citations API[^citations] return cited text with character locations during generation.
Inspektorium instead checks pointers after the fact, independent of who produced them.
The lexical tool verbatimeter[^verbatimeter] measures verbatim reuse of source text offline but does not bind quotations to offsets or gate reports.

On the security side, garak probes whether a model can be induced to emit harmful output, including terminal escape codes [@derczynski2024garak].
Inspektorium works on the receiving end: it neutralizes such text when it renders reports.
General evaluation frameworks such as Inspect[^inspect] run evaluations and grade them.
Inspektorium complements them as an integrity layer for their evidence and reports, in the spirit of end-to-end audit trails [@raji2020closing].

# Software design

Inspektorium separates *proposals* from *checks*.
The reference checker (`inspektorium inspect`) takes an answer, its sources and a batch of proposals.
It canonicalizes the texts and checks every claim span and quotation for exact equality at the stated offsets.
It decodes JSON input strictly and rejects duplicate keys.
Each finding records the proposed relation, the result of every check and the relation that may be reported.
That reportable relation is empty when a check failed.
Reports are deterministic JSON and Markdown; the Markdown display escapes markup and shows control, bidirectional and zero-width characters as visible markers.

The audit workflow (`inspektorium audit`) runs a case through a recorded or authorized model response, a forensic assessment, disagreement routing and a set of controls.
It writes a candidate bundle: a manifest binds the hash of every file, and the record binds the bytes of the installed audit runtime.
Unresolved cases stop with an open mandatory review.
A human decision creates a new immutable revision, and only an explicit release step produces a released artifact.
Live model calls require a written authorization with a budget ledger; tests and examples run offline.

# Research impact statement

Inspektorium is at an early stage.
Its checks are tested with counter-tests and clean counterparts, and the public evidence package for version 0.1.1 documents the display and parsing guards.
An owner-reported internal pilot found no accuracy difference between its prompt conditions, a null result at a ceiling.
Its structural controls accepted both semantically wrong control answers.
The project documents these results openly.
A preregistered validation study with independent human reviewers is planned but not yet done; scientific efficacy is not established.

# AI usage disclosure

The author directed the development and made every design and release decision.
AI coding assistants, mainly Anthropic's Claude models through Claude Code, drafted code, tests and documentation on the author's instructions.
Separate AI passes reviewed them.
All changes were checked by the test suite and continuous integration; AI review is not presented as human peer review.
Statements about other tools and papers were checked against their primary sources.

[^anchor]: <https://github.com/hnvivek/anchor>
[^citations]: <https://platform.claude.com/docs/en/build-with-claude/citations>
[^verbatimeter]: <https://pypi.org/project/verbatimeter/>
[^inspect]: <https://github.com/UKGovernmentBEIS/inspect_ai>

# References
