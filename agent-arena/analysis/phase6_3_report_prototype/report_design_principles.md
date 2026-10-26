# Phase 6.3 — Report Design Principles

The claim-forensics report exists to make one Agent Arena analysis **legible and
auditable**: a non-specialist can read the verdict, and an expert can check every step.
These principles are enforced in `src/agent_arena/forensic_report.py` and its tests.

## 1. One validated object, two views

`build_forensic_report(input)` returns a single validated report object. The full
Markdown, the executive summary, and the canonical JSON all derive from **that one
object** — there is never a second source of truth. The executive summary omits detail,
never material verdict/confidence/limitation content.

## 2. Evidence-first, claim-specific

The report is organized around the **specific claim** and the **cited evidence**, not
around decorative prose. Every failure mode carries a rationale tied to the analysis;
evidence items carry a tier and a role. Prose never exceeds the supporting evidence.

## 3. Explicit about uncertainty; safe against overclaiming

- Confidence is `VALID / MISSING / INVALID` (Phase 6.1) — **never coerced to 0.0**.
- Missing evidence, missing comparison group / causal chain / human evidence, and
  missing reader-impact information are stated as **missing / unknown**, never invented.
- A classification is explicitly **not** presented as proof of factual falsity
  (`classification_note` on every verdict).
- Reader-impact risk is a **qualitative** category, never a computed harm probability.

## 4. Clear separation of registers

The report distinguishes, in separate fields and Markdown sections:

| register | where |
|---|---|
| the public **claim** | `claim.*` / "Claim" |
| available **evidence** | `evidence.*` / "Evidence assessment" |
| inferred **forensic issue** | `verdict` + `failure_modes` / "Verdict", "Why this verdict" |
| **missing** evidence | `evidence.missing_*`, `uncertainty.missing_evidence` / "What is missing" |
| **uncertainty** | `uncertainty.*` / "Uncertainty" |
| **reader-impact risk** | `reader_impact.*` / "Reader-impact risk" |
| recommended **revision** | `recommended_revision.*` / "Safer rewrite" |

## 5. Deterministic and auditable

- Canonical JSON uses sorted keys and fixed serialization; a report digest
  (`report_generation_digest_sha256`) and an `input_digest_sha256` bind the report to
  its input. A one-character input change changes the digest.
- No wall-clock timestamp is injected at build time (`generated_at` is a passthrough).
- `warnings` and the `audit_trail` are always visible; empty lists stay visible.

## 6. No invented facts in a rewrite

The `defensible_rewrite` is **copied verbatim from validated input — never synthesized**
by the builder or renderers. It passes a **numeric-containment guard**: every number in
the rewrite must already appear in the claim/context/evidence corpus. If it introduces an
unsupported number, the rewrite is **blocked** (dropped to "no safe rewrite available")
and a warning is recorded — the report never ships a fabricated statistic.

Crucially, **passing the numeric guard is not verification.** A present rewrite is always
marked `rewrite_verification = "unverified_proposal"` and carries a note that its factual
and semantic support still requires human review; both the full report and the executive
summary render it as an unverified proposal. This is a deterministic guard, **not** a
natural-language entailment checker, and it is intentionally conservative — it never
labels a rewrite as evidence-verified.

## 7. Independent of private identities

No canonical case id, `BIAA-*`, `HLD-*`, private `DEV-####` id, salt, or private path
may appear in an input or a report; such content is rejected at validation. The report
is about a **claim**, not a private case identity.

## 8. Failure cannot masquerade as success

A parser failure (`parser.parse_ok = false`) always produces an
`analysis_status = "parser_failure"` failure report with `predicted_label = null` — it
can never be rendered as a confident verdict, even if the input also carried an
optimistic `analysis_status`.

## 9. Prototype honesty

Every example is **synthetic** and labelled `SYNTHETIC EXAMPLE — not real Agent Arena
performance`; the development caveat is attached in development mode. The prototype makes
no production, ranking, or threshold-adoption claim.
