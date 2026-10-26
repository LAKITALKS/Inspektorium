# Documentation decisions for v0.1.1

**Status: PREPARED for the maintainer's publication review. Not approved.**
These decisions were prepared on 2026-10-13 together with the v0.1.1
candidate. They become effective only if the maintainer approves publication;
the diff against public `main` `4bd0ba9` is part of that decision.

## 1. Historical numbers

Rule applied: current public performance claims rest on publicly attributable
evidence. Where an owner-reported number has no public evidence package, the
front-facing README describes it qualitatively. The original records and
values stay unchanged where they are documented as historical or
owner-reported. No historical value is changed, and no new rate is pooled
across incompatible phases or case sets. The v0.1.1 evidence package concerns
report display and input parsing; it does not retroactively support any of
these numbers.

| Number(s) | File and location | Before | After | Reason |
| --- | --- | --- | --- | --- |
| 4/12 → 12/12 blocked; 6/6 clean accepted | `README.md`, capability table, row "OWNER-REPORTED INTERNAL EXPERIMENT" | "Artifact-fault pilot: 4/12 versus 12/12 blocked; 6/6 clean counterparts accepted" | "Artifact-fault pilot: full controls blocked more injected artifact faults than baseline processing and accepted all clean counterparts"; boundary adds "Small constructed set" | No public evidence package; qualitative statement keeps direction and limits without presenting a current public figure. |
| 24/24 (A/B/C), B−A = 0 points | `README.md`, "Evidence and limitations" | "In the internal pilot, A/B/C each achieved 24/24 main-case accuracy: B−A was zero percentage points." | "found no main-case accuracy difference between its conditions, all of which were at ceiling"; adds a pointer to the historical records and states that v0.1.1 evidence does not support them | Same reason; the null result and the ceiling caveat are kept. |
| 61/84 → 78/84 (Haiku), 65/84 → 70/84 (Sonnet) | `README.md` | Not shown | Not shown; mentioned only as "an earlier contract study" kept as a historical record | Was never a README figure; no change of substance. |
| I01–I07 values | `CLAIMS.md`, owner-reported table | Values as of 2026-09-15 | Unchanged; a note marks the rows as a historical owner-reported record that v0.1.1 evidence does not support | Historical record must stay intact. |
| Pilot and contract-study values | `RESEARCH_RESULTS.md`, owner-reported sections | Values as of 2026-09-15 | Unchanged; a "Historical record" note is added to each section | Same. |
| `SCOPE.md` pilot summary | `SCOPE.md`, broader research direction | Qualitative ("zero observed A/B accuracy gain") | Unchanged | Already qualitative. |
| Internal technical v1.0.0 counts (tests, checks, pages) | All public docs | Not present | Not added; `RESEARCH_RESULTS.md` states why | No public evidence package; they are not measurements of public v0.1.1. |
| Historical public measurements (74 tests; 88.11% / 89.10% branch coverage) | `RELEASE_CHECKLIST.md`, `RESEARCH_RESULTS.md` | Present, dated | Unchanged | Publicly attributable, dated software-quality measurements. |

Alternative for the maintainer: keep the original counts in the README
table, each marked "owner-reported, historical, not supported by v0.1.1
evidence". Reverting the two README rows restores the 2026-09-15 wording.

## 2. Version names

- **public v0.1.0**: tag `v0.1.0` (object `648e24a…`, commit `a376c40`).
- **public v0.1.1**: this candidate; package 0.1.1, report schema 0.1.
- **internal technical v1.0.0**: described as the owner-reported technical
  closeout of a separate, non-public codebase. The internal project name,
  internal commit IDs and internal counts are deliberately not published; the
  maintainer may add a provenance note.
- **Final v1 gate** (`ROADMAP.md`): marked "Not met".

## 3. Status of R08–R10

R08–R10 changed from "roadmap" to "implemented internally (owner-reported);
public roadmap". Every mention states that the phases were checked offline and
live-tested in a limited way on earlier internal states, that the closeout
code was not live-tested again, that no scientific efficacy is demonstrated
and that the implementation is not part of the public package. Source: the
owner's statement for this release preparation; not inspected or reproduced
in this repository. `RESEARCH_PLAN.md` states that the falsifiable questions
remain open.

## 4. Claim ledger structure

Rows P01–P11 keep their original wording; only the version cells of P06 and
P07 gained a cross-reference to the new rows. New rows:

- P12 Markdown display of untrusted text as data (v0.1.1);
- P13 strict `--input` parsing (v0.1.1), including the new report-model
  invariant that a verified citation requires a complete evidence reference;
  it is documented in this row rather than in a new one so that the IDs
  P14–P17 stay stable;
- P14 an exact excerpt can distort meaning, for example by omitting a negation;
- P15 a reportable `not_established` is not a scientifically examined
  refutation;
- P16 schema validity of a report is neither a re-check against sources nor
  proof of origin; evaluator provenance and a `verify` command are later work;
- P17 strict offsets: correct text with a wrong offset is rejected, no
  repositioning, no general false-alarm rate.

P14–P17 document limits of both 0.1.0 and 0.1.1; no new model logic is
proposed.

## 5. Citation metadata and changelog

- `CITATION.cff` changes only `version: 0.1.0` → `version: 0.1.1`. The file
  has never had `date-released`, and none is added: the release date is
  unknown until publication, and a 0.1.0 date must not be paired with 0.1.1.
  The publication-day step in `RELEASE_CHECKLIST.md` (section C) adds the date
  in the commit to be tagged, if wanted. No DOI and no repository URL are
  added; the v0.1.0 checklist recorded both as absent.
- `CHANGELOG.md` is new. The 0.1.1 entry is "Unreleased (candidate)" without
  a date. The 0.1.0 entry uses the tagger date of `v0.1.0` (2026-08-11) and
  lists the later `main` commits, which changed no source, test or example
  file.

## 6. Release checklist

The v0.1.0 checklist and the 2026-09-15 documentation review remain byte-for-
byte unchanged, including the title "v0.1.0 Release Checklist". The new
v0.1.1 section separates facts, local preparation and publication. The
2026-09-15 review's open approval boxes are noted as a fact (that change is on
public `main`), not back-filled.

## 7. Working rules

`AGENTS.md` is new and binding for agent-assisted changes; `CONTRIBUTING.md`
points to it and applies its evidence, status and untrusted-text rules to
every contribution. The publication rule in `AGENTS.md` is limited to agents,
so it does not conflict with ordinary pull requests by contributors. The
model or tooling used to prepare this release is not a product requirement and
is not named in either file.

## 8. Wording of the display rule and labels

- The documentation states the display rule by Unicode general category (Cc,
  Cf, Cs, Zl and Zp, plus code points unassigned (Cn) in the running Python's
  Unicode database) instead of "control, bidirectional and invisible
  characters", because private-use characters, combining marks, variation
  selectors and other invisible characters outside these categories are not
  marked. It says "displayed as data", not "safe display", and ties the
  evidence to the synthetic catalog and the named renderers.
- Marking unassigned code points was added after the independent display
  review, so that format characters assigned in a later Unicode version are
  not shown raw on an older Python. The documentation states the trade-off
  (newer characters such as recent emoji appear as markers on older Pythons)
  and the Python and Unicode versions of the recorded evidence runs.
- Wording that embedded text "cannot imitate a marker" is narrowed to the
  exact marker brackets U+27E6/U+27E7; look-alike brackets are a known limit.
  No document claims that warnings can never be covered visually: the
  `AGENTS.md` rule against hiding warnings is a working rule for
  contributors, and the visual overlap by combining marks is a known limit.
- The known display limits (cmark-gfm e-mail autolinks, including `mailto:`
  and `xmpp:` forms; combining marks drawn over neighbouring lines; look-alike
  marker brackets; GitHub web-service features and other viewers not tested;
  Python-Markdown tested only with `tables` and `fenced_code`; tools that
  strip trailing spaces) are listed in `CHANGELOG.md`, `README.md` and
  `METHODOLOGY.md`; claim P12 names the main ones and links the full list.
  The first three were observed in the independent display review and are not
  measured by the catalog.
- Library users are told to parse untrusted JSON with
  `parse_inspection_input_json` or `parse_proposal_json`, because the
  Pydantic `model_validate_json` methods keep last-duplicate-key-wins
  behaviour; the strictness claim (P13) is limited to `--input` and
  `--proposals` files and these functions.
- `CHANGELOG.md` lists every changed Markdown label with its 0.1.0 wording.
  The scope limitation "Citation validation confirms exact text and offsets,
  not semantic truth." keeps its wording, because it is part of the JSON
  report, which stays byte-identical.

## 9. Unchanged

`LICENSE` (PolyForm Noncommercial 1.0.0, described as source-available, not
OSI open source), report schema 0.1, the tag `v0.1.0`, Git history and the
website are not changed by these documentation decisions.
