# Security policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.3.x | Yes |
| Earlier than 0.3 | No |

## Report a vulnerability

Report vulnerabilities privately through GitHub Private Vulnerability Reporting:
[open a private report](https://github.com/LAKITALKS/Inspektorium/security/advisories/new).
Do not open a public issue for a vulnerability.

Please include:

- the affected version or commit;
- the command or API call and the input files that reproduce the problem;
- what you expected and what happened;
- the impact you see.

Reports are handled confidentially until a fix or an advisory is published.
Reporters are credited in the advisory unless they ask not to be.

## What counts as a vulnerability

Inspektorium is a fail-closed integrity layer. A vulnerability is any way to make it pass what it must block:

- a fabricated or altered quotation, or a wrong offset, reported as an exact match;
- untrusted text that creates report structure, forges a status line or hides a warning;
- a tampered bundle that `inspektorium audit inspect` reports as valid;
- a release of a candidate that is blocked or has an open mandatory review;
- a live model call through the `inspektorium` command without a valid authorization, or a write outside the chosen output directory.

Documented limits are not vulnerabilities. They are listed in [limitations](docs/evaluation/limitations.md).
An evaluator's wrong semantic judgment is such a limit: Inspektorium does not check meaning.
