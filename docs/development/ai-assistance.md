# AI assistance

Lazaros Varvatis is the sole author of Inspektorium.
The author directed the work, made every design and release decision and is responsible for every commit.

## How AI was used in development

- **Implementation.** AI coding assistants, mainly Anthropic's Claude models through Claude Code, drafted code, tests, scripts and documentation on the author's instructions.
- **Review.** Separate AI review passes read code, tests and documents and reported findings; the author decided on each finding.
- **Research support.** AI assistants searched and summarized sources. Statements about other tools and papers were checked against their primary sources before use.

AI tools are not authors or contributors. Commits carry the author's identity only.

## Safeguards

- Every change is checked by the test suite, the frozen acceptance and the CI jobs described in [testing](testing.md).
- Status values and numbers come only from checks that were run; skipped or missing checks are not reported as passed.
- Protective controls need a violating counter-test and a clean counterpart.
- AI review is not human peer review and is not presented as such.

## AI in the research itself

The research record contains studies in which language models were the object of evaluation, for example live model runs.
In the owner-reported pilot, an isolated AI reviewer checked most stimuli; this is disclosed with the [results](../research/results.md#study-limitations).
These uses are part of the research design, not of software development.
