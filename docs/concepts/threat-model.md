# Threat model

This page names the attacks Inspektorium is built to contain and those it does not address.
Claim IDs refer to the [claim ledger](../research/claims.md).
Mechanisms are described in [methodology](methodology.md). Limits are listed in [limitations](../evaluation/limitations.md).

## Trust boundary

Threats are scoped to the declared trusted code, state store and execution boundary.
Evaluator output, answer text and source text are untrusted data.
Hashes cannot protect against an adversary who replaces all trusted state and code.
Evidence for each covered attack is software-regression or offline technical evidence, not a measured detection rate.

## Covered attacks

### Fabricated or altered quotations

**Attack.** An evaluator proposes a quotation that is truncated, altered, misattributed or invented.

**Control.** The reference checker requires the source span to equal the quotation exactly (P02).
A failed check sets that finding's `reportable_relation` to null and keeps the proposal visible (P03).
Nothing is repaired, searched for or substituted.

**Evidence.** [Citation regressions](../../tests/unit/test_validation.py) and [example 05](../../examples/inspect/05_mixed_and_fabricated_quote/expected_report.json), where an `8 p.m.` quotation fails against a `6 p.m.` source.

### Offset tricks

**Attack.** A proposal cites real source text at offsets that point elsewhere, or a claim span that differs from the claim text.

**Control.** Claim text must equal the answer at its span (P01).
A quotation must sit at its proposed offsets; real text at a wrong offset fails (P17).
Offsets are Python character indices on LF/NFC-canonical text, not byte offsets (P05).

**Evidence.** [Span and wrong-offset regressions](../../tests/unit/test_validation.py) and [LF/NFC tests](../../tests/unit/test_normalization.py).

### Ambiguous input JSON

**Attack.** A file carries duplicate keys, nonstandard constants or other ambiguous JSON, so different parsers read different values.

**Control.** `inspect` decodes `--input` and `--proposals` with one strict decoder (P07, P13).
Rejected input ends with exit code 2 before any provider call, analysis or output.
This control belongs to `inspect` only.

**Evidence.** [CLI rejection tests](../../tests/integration/test_cli_input_rejection.py).
On the v0.1.1 candidate, 12 of 12 input-rejection catalog cases hold ([evidence package](../../evidence/v0.1.1/README.md)).

### Report forgery through embedded text

**Attack.** Untrusted text tries to write report lines, headings, tables, links, images or HTML into the Markdown report.
Examples are a forged status line, a hidden warning or a remote image request.

**Control.** Each untrusted value is encoded once for its embedding context (P12).
Line terminators other than LF inside quotations become markers on the same line.
Markdown- and HTML-significant characters are escaped; the at sign is marked to stop e-mail autolinks.
In the audit workflow, model and source text cannot supply trusted HTML or status markup.

**Evidence.** On the v0.1.1 candidate, 0 of 280 renderings were `RENDERED_MANIPULATED`, against 165 of 280 on the baseline ([evidence package](../../evidence/v0.1.1/README.md#results)).
No rendered candidate page made a request other than loading itself.

### Display attacks with invisible characters

**Attack.** Control characters, bidirectional overrides or zero-width characters reorder or hide text in the displayed report.

**Control.** Characters of the categories Cc, Cf, Cs, Zl and Zp are shown as `⟦U+XXXX⟧` markers (P12).
So are code points unassigned in the running Python's Unicode database, and the exact marker brackets.
Long combining-mark runs are capped at four raw characters.
Audit reports show control, bidirectional and invisible format characters as the same kind of token.
JSON and `record.json` keep the exact characters.

**Evidence.** [Render safety tests](../../tests/unit/test_render_safety.py), [display tests](../../tests/unit/test_display.py) and the [2026-10-24 addendum](../../evidence/v0.1.1/addendum-20261024/README.md).

### Manipulated or tampered bundles

**Attack.** Someone edits a report, record or decision file after a run, or presents an altered candidate for release.

**Control.** Each audit bundle carries a fingerprint chain across record, reports, decision and manifest (R10).
`audit inspect` recomputes the controls from raw-bound history under the installed code.
Invalid or tampered bundles exit 2. Old green fields alone cannot authorize a changed artifact.
`audit release` rechecks the candidate and writes a new immutable revision. There is no force-release switch.

**Evidence.** The [acceptance driver](../../scripts/run_acceptance.py) and the [2026-10-26 offline checks][validation].

### Unauthorized live runs

**Attack.** A run calls a paid model provider without authorization, or exceeds its budget.

**Control.** Offline mode accepts only the built-in recording provider and never falls back to a network call.
Live and replay need an authorization directory, a ledger and a registered profile.
Every provider call first reserves its maximal exposure; unknown billing stays reserved.
Raw responses are written before interpretation, and answered slots are never resent.
Credentials are read only from `ANTHROPIC_API_KEY` and never stored.
Historical owner-reported pilot checks blocked 4/4 pre-execution failures (I04, [historical results][rr-pilot]).

**Evidence.** The [2026-10-26 offline checks][validation]. General prevention performance is research question Q2 in the [research plan](../research/plan.md).

## Not covered

| Area | Why it is outside the model | Claims |
| --- | --- | --- |
| Semantic truth | Exact binding confirms where words are, not what a relation means. A true quote with a false relation stays reportable. | P09, P14 |
| Source quality | Sources are not checked for accuracy, authority, currency or completeness. A hash is not evidence of source authority. | P02, P05 |
| Completeness | Empty findings are accepted. Zero failures do not show that all relevant claims were found. | P10 |
| Model honesty | Rationale and certainty are reported evaluator output, not verified. Model/host agreement is not independent corroboration. | R08, R09 |
| Report origin | A schema-valid report is not re-checked against its sources and is not proof of origin. | P16 |
| Historical state | Fingerprints identify current content, not an authenticated earlier state. Hashes are not signatures. | P05 |
| Reviewer identity | Reviewer names are recorded provenance, not identity authentication. | R09 |
| OS-level network isolation | Offline mode makes no provider call, but Inspektorium provides no operating-system sandbox. The evidence harness guard covers Python sockets only, not native code. | — |

The evidence harness guard is described in the [network measurement](../../evidence/v0.1.1/README.md#network-and-provider-measurement).

[validation]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/publication/2026-10-26/VALIDATION.md
[rr-pilot]: https://github.com/LAKITALKS/inspektorium-research-record/blob/record-2026-10-27/historical-docs/RESEARCH_RESULTS.md#owner-reported-internal-pilot
