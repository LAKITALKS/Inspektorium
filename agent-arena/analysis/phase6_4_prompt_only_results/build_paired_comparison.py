#!/usr/bin/env python3
"""Deterministic Phase 6.4 paired comparison generator (offline, no model calls).

Reads exactly the **two** anonymized result envelopes of the Phase 6.4 paired pilot —
the completed Agent Arena forensic-package Haiku arm (Phase 6.2 run) and the completed
competent-minimal prompt-only Haiku arm (Phase 6.4B run) — independently validates each
against the tracked public-manifest binding, then renders:

- the input-integrity report (JSON + MD);
- one per-arm calibration report (JSON + MD) using **only** the frozen engine in
  ``agent_arena.calibration`` (Brier primary, 5 fixed bins, secondary ECE, costed
  abstention) — nothing re-tuned;
- the descriptive **paired** comparison (JSON + MD): the same 27 opaque ``DEV-####``
  cases contrasted pairwise across the two arms, with frozen sign conventions.

**This is a development pilot, NOT a holdout.** The two arms are a *package-level*
contrast (system prompt + model-facing response contract + parser differ together), not
the causal effect of one system-prompt string. Parser completion is reported separately
from classification accuracy. The 54 predictions are two paired outputs on 27 cases — they
are **never** pooled into a 54-case benchmark and no pooled score is ever computed.

Privacy & determinism (identical guarantees to the Phase 6.2 generator):

- the two envelopes live OUTSIDE the repository and are never copied into it; this script
  takes their paths as runtime arguments;
- every tracked artifact carries only opaque ``DEV-####`` ids, class labels, aggregated
  metrics, and run/model provenance — no canonical/BIAA/HLD id, no salt, no private path;
- no wall-clock timestamp is injected — every value derives from the frozen engine and the
  envelope provenance, so repeated runs are byte-for-byte identical.

Usage::

    PYTHONPATH=src .venv/bin/python \
        analysis/phase6_4_prompt_only_results/build_paired_comparison.py \
        --agent-arena-envelope <PRIVATE_DIR>/phase6_2_envelopes/haiku_result_envelope.json \
        --prompt-only-envelope <PRIVATE_DIR>/phase6_4_envelopes/haiku_prompt_only_result_envelope.json \
        --out-dir analysis/phase6_4_prompt_only_results
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import mean

from agent_arena.calibration import (
    FIVE_BIN_EDGES,
    LABELS,
    brier_top_label,
    build_report,
    load_public_manifest_binding,
    render_report_text,
    validate_result_envelope,
)
from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence

# --- the two expected runs (authoritative Phase 6.4 checkpoint) --------------------
AGENT_ARENA = "agent_arena"
PROMPT_ONLY = "prompt_only"
ARM_ORDER = (AGENT_ARENA, PROMPT_ONLY)
ARM_TITLE = {
    AGENT_ARENA: "Agent Arena (forensic package)",
    PROMPT_ONLY: "prompt-only (competent minimal package)",
}
EXPECTED_RUNS = {
    AGENT_ARENA: {
        "run_id": "AA-6.2-RUN-6a3b93a24af7431e",
        "model": "claude-haiku-4-5-20251001",
        "contract_id": "AA-RTC-6.2-HAIKU-001",
        # system_prompt_sha256 pinned by the Phase 6.2 Haiku runtime contract.
        "system_prompt_sha256": "f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5",
    },
    PROMPT_ONLY: {
        "run_id": "AA-6.4B-HAIKU-PROMPTONLY-f44d734f00162c03",
        "model": "claude-haiku-4-5-20251001",
        "contract_id": "AA-RTC-6.4-HAIKU-PROMPT-ONLY-001",
        # prompt-only runtime contract pins the baseline prompt digest.
        "system_prompt_sha256": "85e7b929253e37d2600a055e7212ffd755cf03fccdd3ddea40a745297eebbff6",
    },
}
SHARED_MODEL = "claude-haiku-4-5-20251001"

ENVELOPE_ALLOWED_KEYS = {
    "envelope_version", "protocol_version", "manifest_id", "public_commitment",
    "run_id", "model", "provider", "prompt_contract_version", "generated_at",
    "expected_record_count", "declared_gold_aggregate", "records",
}
RECORD_ALLOWED_KEYS = {
    "dev_id", "model", "predicted_label", "gold_label", "stratum",
    "confidence", "gold_case_type", "correct",
}

# Descriptive-only thresholds for error highlighting (NOT tuned operating points; the
# primary reliability presentation's top bin is [0.8, 1.0]).
HIGH_CONF_FLOOR = FIVE_BIN_EDGES[-2]   # 0.8 — top primary bin lower edge
LOW_CONF_CEIL = FIVE_BIN_EDGES[3]      # 0.6 — below the top two bins

PILOT_BANNER = (
    "DEVELOPMENT PILOT — NOT HOLDOUT",
    "same 27 paired development cases; one run per arm; same exact model",
    "package-level contrast (system prompt + response contract + parser differ together)",
    "descriptive small-sample analysis; no universal-superiority inference",
    "no threshold optimized after results; small-n label limitations (corr/mech at n=2)",
    "the 54 predictions are two paired outputs on 27 cases — never pooled into 54 cases",
    "holdout remained sealed; residual model nondeterminism possible despite temperature=0",
    "parser/response-contract asymmetry; the baseline's lighter response burden may favor it",
)

_CANON = re.compile(r"study-forensics-[0-9]+", re.IGNORECASE)
_BIAA = re.compile(r"\bBIAA-[0-9]+", re.IGNORECASE)
_HLD = re.compile(r"\bHLD-[0-9]+", re.IGNORECASE)
_SALTY_KEYS = ("salt", "salt_hex", "private_manifest", "canonical_id", "case_id")


def _iter_strings(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k)
            yield from _iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _iter_strings(v)
    elif isinstance(obj, str):
        yield obj


def leakage_scan(text: str) -> list[str]:
    """Return leakage findings (canonical/BIAA/HLD/salt tokens) in a text blob."""
    hits = []
    if _CANON.search(text):
        hits.append("canonical study-forensics id token")
    if _BIAA.search(text):
        hits.append("BIAA id token")
    if _HLD.search(text):
        hits.append("HLD id token")
    for key in _SALTY_KEYS:
        if re.search(rf"\b{re.escape(key)}\b", text, re.IGNORECASE):
            hits.append(f"forbidden key token: {key}")
    return hits


# ---------------------------------------------------------------------------
# Parser completion (reported SEPARATELY from classification accuracy)
# ---------------------------------------------------------------------------

def parse_completion(records: list[dict]) -> dict:
    """Parser-completion audit for one arm, kept strictly separate from accuracy.

    The anonymized envelope schema represents a *completed* parse as a record carrying a
    valid ``predicted_label`` (in the frozen vocabulary); there is no separate
    parse-failure marker. A record whose label is absent/out-of-vocabulary is counted as a
    parser failure and is NEVER silently dropped. Missing/invalid confidence is a
    confidence-validity fact (reported elsewhere), not a parse failure.
    """
    n = len(records)
    parsed = [r for r in records if r.get("predicted_label") in LABELS]
    failures = [r.get("dev_id") for r in records if r.get("predicted_label") not in LABELS]
    return {
        "expected": 27,
        "records_present": n,
        "parse_ok": len(parsed),
        "parse_failures": len(failures),
        "parse_failure_dev_ids": failures,
        "parse_completion_rate": (len(parsed) / n) if n else None,
        "note": ("parse completion is reported separately from classification accuracy; "
                 "the envelope schema marks a completed parse by a valid predicted_label"),
    }


# ---------------------------------------------------------------------------
# Independent per-arm input-integrity validation
# ---------------------------------------------------------------------------

def validate_one(arm: str, envelope: dict, manifest_id: str, commitment: str) -> dict:
    """Independent per-envelope integrity checks for one arm; structured result."""
    exp = EXPECTED_RUNS[arm]
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    # 1. structural: no unexpected top-level or record fields
    env_keys = set(envelope.keys())
    check("envelope_no_unexpected_fields", env_keys <= ENVELOPE_ALLOWED_KEYS,
          f"unexpected={sorted(env_keys - ENVELOPE_ALLOWED_KEYS)}")
    records = envelope.get("records", [])
    bad_rec_keys = sorted({k for r in records if isinstance(r, dict)
                           for k in r.keys() if k not in RECORD_ALLOWED_KEYS})
    check("records_no_unexpected_fields", not bad_rec_keys, f"unexpected={bad_rec_keys}")

    # 2. binding metadata
    check("envelope_version_6.2.0", envelope.get("envelope_version") == "6.2.0",
          str(envelope.get("envelope_version")))
    check("protocol_version_6.1", envelope.get("protocol_version") == "6.1",
          str(envelope.get("protocol_version")))
    check("manifest_id_matches_tracked", envelope.get("manifest_id") == manifest_id,
          f"{envelope.get('manifest_id')} vs {manifest_id}")
    check("public_commitment_matches_tracked", envelope.get("public_commitment") == commitment,
          f"{envelope.get('public_commitment')}")
    check("provider_anthropic", envelope.get("provider") == "anthropic",
          str(envelope.get("provider")))
    check("expected_record_count_27", envelope.get("expected_record_count") == 27,
          str(envelope.get("expected_record_count")))
    check("declared_gold_aggregate_8_15_2_2",
          envelope.get("declared_gold_aggregate") == {
              "solid": 8, "overclaim": 15, "correlation_vs_causation": 2,
              "mechanism_vs_evidence": 2, "total": 27},
          json.dumps(envelope.get("declared_gold_aggregate"), sort_keys=True))

    # 3. expected run / model / contract / shared model
    check("run_id_matches_expected", envelope.get("run_id") == exp["run_id"],
          f"{envelope.get('run_id')} vs {exp['run_id']}")
    check("model_matches_expected", envelope.get("model") == exp["model"],
          f"{envelope.get('model')} vs {exp['model']}")
    check("model_is_shared_pilot_model", envelope.get("model") == SHARED_MODEL,
          str(envelope.get("model")))
    pcv = envelope.get("prompt_contract_version", "") or ""
    contract_id_present = exp["contract_id"] in pcv
    sha_present = exp["system_prompt_sha256"] in pcv
    # contract binding is satisfied if the literal contract id is echoed, OR the pinned
    # system_prompt_sha256 is present AND the exact model maps uniquely to this contract.
    contract_bound = contract_id_present or (sha_present and envelope.get("model") == exp["model"])
    check("contract_binding_satisfied", contract_bound,
          f"contract_id_present={contract_id_present} sha_present={sha_present}")

    # 4. records: exactly 27, unique dev ids, gold aggregate, confidence validity
    check("record_count_27", len(records) == 27, str(len(records)))
    dev_ids = [r.get("dev_id") for r in records]
    check("dev_ids_unique_opaque",
          len(set(dev_ids)) == len(dev_ids)
          and all(isinstance(d, str) and re.fullmatch(r"DEV-[0-9]{3,}", d) for d in dev_ids),
          f"n_unique={len(set(dev_ids))}")
    gold_counts = {lbl: sum(1 for r in records if r.get("gold_label") == lbl) for lbl in LABELS}
    check("gold_aggregate_8_15_2_2",
          gold_counts == {"solid": 8, "overclaim": 15,
                          "correlation_vs_causation": 2, "mechanism_vs_evidence": 2},
          json.dumps(gold_counts, sort_keys=True))
    conf_states = [classify_confidence(r.get("confidence")) for r in records]
    n_valid = conf_states.count(VALID)
    n_missing = conf_states.count(MISSING)
    n_invalid = conf_states.count(INVALID)
    check("confidence_no_invalid", n_invalid == 0,
          f"valid={n_valid} missing={n_missing} invalid={n_invalid}")
    check("confidence_validity_preserved", n_valid + n_missing + n_invalid == len(records),
          f"valid={n_valid} missing={n_missing} invalid={n_invalid}")
    # no raw confidence is a literal 0.0 that could be a missing/invalid coercion artifact
    zero_conf = [r.get("dev_id") for r in records if r.get("confidence") == 0.0]
    check("no_zero_coercion_artifact", not zero_conf, f"zero_conf_dev_ids={zero_conf}")
    # optional explicit correctness consistency (if present)
    inconsistent = [r.get("dev_id") for r in records if "correct" in r
                    and r.get("correct") != (1 if r.get("predicted_label") == r.get("gold_label") else 0)]
    check("explicit_correct_consistent", not inconsistent, f"inconsistent={inconsistent}")

    # 5. parser completion preserved (separate from accuracy)
    pc = parse_completion(records)
    check("parser_completion_state_preserved", pc["parse_failures"] == 0,
          f"parse_ok={pc['parse_ok']}/{pc['records_present']} failures={pc['parse_failures']}")

    # 6. synthetic-fixture guard: a real run must not be flagged synthetic and must carry a
    #    real run id + generation timestamp (no synthetic fixture masquerading as a real run)
    real_run = bool(envelope.get("run_id")) and bool(envelope.get("generated_at")) \
        and "synthetic_fixture" not in envelope and envelope.get("run_id") == exp["run_id"]
    check("not_synthetic_fixture_mislabeled_as_real", real_run,
          f"run_id={envelope.get('run_id')} generated_at={envelope.get('generated_at')}")

    # 7. leakage scan on the raw envelope
    leak = leakage_scan(json.dumps(envelope))
    check("no_identity_leakage", not leak, "; ".join(leak))

    # 8. engine-side envelope validation (authoritative binding + vocab + dup + no coercion)
    ev = validate_result_envelope(envelope, manifest_id, commitment, enforce_aggregate=True)
    check("engine_validate_result_envelope_clean", ev.ok,
          "; ".join(ev.errors[:6]) + (" …" if len(ev.errors) > 6 else ""))

    dev_id_set = sorted(dev_ids)
    return {
        "arm": arm,
        "arm_title": ARM_TITLE[arm],
        "run_id": envelope.get("run_id"),
        "model": envelope.get("model"),
        "contract_id": exp["contract_id"],
        "prompt_contract_version": pcv,
        "contract_id_echoed_in_pcv": contract_id_present,
        "system_prompt_sha256_present": sha_present,
        "generated_at": envelope.get("generated_at"),
        "confidence_counts": {"valid": n_valid, "missing": n_missing, "invalid": n_invalid},
        "gold_counts": gold_counts,
        "parser_completion": pc,
        "dev_id_set": dev_id_set,
        "gold_by_dev": {r.get("dev_id"): r.get("gold_label") for r in records},
        "stratum_by_dev": {r.get("dev_id"): r.get("stratum") for r in records},
        "checks": checks,
        "all_pass": all(c["pass"] for c in checks),
        "leakage": leak,
    }


def cross_arm_pairing(aa: dict, po: dict) -> dict:
    """Cross-arm pairing integrity: identical DEV set / gold / stratum per paired DEV."""
    dev_set_identical = aa["dev_id_set"] == po["dev_id_set"]
    gold_mismatches = sorted(
        d for d in aa["dev_id_set"]
        if aa["gold_by_dev"].get(d) != po["gold_by_dev"].get(d))
    stratum_mismatches = sorted(
        d for d in aa["dev_id_set"]
        if aa["stratum_by_dev"].get(d) != po["stratum_by_dev"].get(d))
    return {
        "dev_id_set_identical_across_arms": dev_set_identical,
        "n_common_dev_ids": len(set(aa["dev_id_set"]) & set(po["dev_id_set"])),
        "gold_label_identical_per_paired_dev": not gold_mismatches,
        "gold_mismatch_dev_ids": gold_mismatches,
        "stratum_identical_per_paired_dev": not stratum_mismatches,
        "stratum_mismatch_dev_ids": stratum_mismatches,
        "all_pass": (dev_set_identical and not gold_mismatches and not stratum_mismatches),
    }


# ---------------------------------------------------------------------------
# Derived descriptive (items the frozen engine does not itself emit)
# ---------------------------------------------------------------------------

def _subset_derived(records: list) -> dict:
    valid = [r for r in records if r.validity == VALID]
    correct = sum(r.correct for r in records)
    errors = [r for r in records if r.correct == 0]
    low_conf_correct = [r for r in valid if r.correct == 1 and r.confidence < LOW_CONF_CEIL]
    high_conf_errors = [r for r in valid if r.correct == 0 and r.confidence >= HIGH_CONF_FLOOR]
    return {
        "n": len(records),
        "n_valid": len(valid),
        "correct": correct,
        "incorrect": len(records) - correct,
        "mean_reported_confidence": (round(mean(r.confidence for r in valid), 6) if valid else None),
        "min_reported_confidence": (min(r.confidence for r in valid) if valid else None),
        "max_reported_confidence": (max(r.confidence for r in valid) if valid else None),
        "all_errors": [
            {"dev_id": r.dev_id, "predicted_label": r.predicted_label,
             "gold_label": r.gold_label, "stratum": r.stratum, "confidence": r.confidence}
            for r in errors
        ],
        "high_conf_errors": [
            {"dev_id": r.dev_id, "predicted_label": r.predicted_label,
             "gold_label": r.gold_label, "stratum": r.stratum, "confidence": r.confidence}
            for r in high_conf_errors
        ],
        "low_conf_correct": [
            {"dev_id": r.dev_id, "gold_label": r.gold_label,
             "stratum": r.stratum, "confidence": r.confidence}
            for r in low_conf_correct
        ],
    }


def derived_descriptive(records: list) -> dict:
    clear = [r for r in records if r.stratum == "clear"]
    borderline = [r for r in records if r.stratum == "borderline"]
    devonly = [r for r in records if r.stratum == "development_only"]
    return {
        "definitions": {
            "high_conf_error": f"incorrect prediction with VALID confidence >= {HIGH_CONF_FLOOR}",
            "low_conf_correct": f"correct prediction with VALID confidence < {LOW_CONF_CEIL}",
            "note": "descriptive highlighting only; NOT a tuned operating threshold",
        },
        "all_27": _subset_derived(records),
        "clear": _subset_derived(clear),
        "borderline": _subset_derived(borderline),
        "development_only": _subset_derived(devonly),
    }


def by_gold_label_all27(records: list) -> dict:
    """Descriptive per-gold-label accuracy/Brier over ALL 27 records (all strata).

    All four labels stay visible; correlation/mechanism (n=2) carry small_n /
    descriptive_only and are unsuitable for label-level calibration claims.
    """
    out = {}
    for lbl in LABELS:
        lr = [r for r in records if r.gold_label == lbl]
        out[lbl] = {
            "n": len(lr),
            "correct": sum(r.correct for r in lr),
            "incorrect": len(lr) - sum(r.correct for r in lr),
            "accuracy": (mean(r.correct for r in lr) if lr else None),
            "brier_top_label": brier_top_label(lr),
            "small_n": len(lr) < 5,
            "descriptive_only": len(lr) < 5,
        }
    return out


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _fmt(x, nd=4):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def render_arm_md(arm: dict) -> str:
    """Full per-arm markdown: pilot banner + engine render + parser/derived/by-gold."""
    integ = arm["integrity"]
    lines = [f"# Phase 6.4 — {ARM_TITLE[arm['arm']]} Haiku arm report\n"]
    for b in PILOT_BANNER:
        lines.append(f"### {b}")
    lines.append("")
    lines.append(f"- run_id: `{integ['run_id']}`  ·  contract: `{integ['contract_id']}`  ·  "
                 f"model: `{integ['model']}`")
    lines.append(f"- generated_at (envelope provenance): `{integ['generated_at']}`\n")

    pc = integ["parser_completion"]
    cc = integ["confidence_counts"]
    lines.append("## Parser completion & confidence validity (reported SEPARATELY from accuracy)\n")
    lines.append(f"- parser completion: **{pc['parse_ok']}/{pc['records_present']}** "
                 f"(parser failures: **{pc['parse_failures']}**)")
    lines.append(f"- confidence: VALID={cc['valid']}  MISSING={cc['missing']}  INVALID={cc['invalid']} "
                 f"(no missing/invalid coerced to 0.0)\n")
    lines.append("_" + pc["note"] + "._\n")

    lines.append("## Denominators (frozen)\n")
    lines.append("- accuracy → all records (valid labels), regardless of confidence validity")
    lines.append("- Brier / reliability / ECE → VALID-confidence records only")
    lines.append("- MISSING/INVALID counted, never coerced; here all 27 are VALID so every "
                 "denominator = 27\n")

    lines.append("## Frozen calibration engine output\n")
    lines.append("```")
    lines.append(render_report_text(arm["report"]).rstrip())
    lines.append("```\n")

    lines.append("## Descriptive by gold label — ALL 27 (all four labels visible)\n")
    lines.append("| gold label | n | correct | incorrect | accuracy | Brier | flag |")
    lines.append("|---|---|---|---|---|---|---|")
    for lbl in LABELS:
        g = arm["by_gold_label_all27"][lbl]
        flag = "small_n/descriptive-only" if g["small_n"] else ""
        lines.append(f"| {lbl} | {g['n']} | {g['correct']} | {g['incorrect']} | "
                     f"{_fmt(g['accuracy'])} | {_fmt(g['brier_top_label'])} | {flag} |")
    lines.append("")

    der = arm["derived"]
    d = der["definitions"]
    lines.append("## Derived descriptive (mean confidence, errors, low-conf-correct)\n")
    lines.append(f"- high_conf_error := {d['high_conf_error']}")
    lines.append(f"- low_conf_correct := {d['low_conf_correct']}")
    lines.append(f"- _{d['note']}_\n")
    lines.append("| stratum | n | correct | incorrect | mean conf | min conf | max conf |")
    lines.append("|---|---|---|---|---|---|---|")
    for key in ("all_27", "clear", "development_only", "borderline"):
        s = der[key]
        lines.append(
            f"| {key} | {s['n']} | {s['correct']} | {s['incorrect']} | "
            f"{_fmt(s['mean_reported_confidence'])} | {_fmt(s['min_reported_confidence'])} | "
            f"{_fmt(s['max_reported_confidence'])} |")
    lines.append("")
    errs = der["all_27"]["all_errors"]
    if errs:
        lines.append("### Errors (all 27) — high-confidence errors flagged\n")
        lines.append("| dev_id | predicted | gold | stratum | confidence | high_conf(≥0.8) |")
        lines.append("|---|---|---|---|---|---|")
        for e in errs:
            hi = "YES" if e["confidence"] is not None and e["confidence"] >= HIGH_CONF_FLOOR else "no"
            lines.append(f"| {e['dev_id']} | {e['predicted_label']} | {e['gold_label']} | "
                         f"{e['stratum']} | {e['confidence']} | {hi} |")
        lines.append("")
    else:
        lines.append("### Errors (all 27)\n\n_No incorrect predictions in this arm._\n")
    lcc = der["all_27"]["low_conf_correct"]
    if lcc:
        lines.append("### Low-confidence correct predictions (VALID conf < 0.6)\n")
        lines.append("| dev_id | gold | stratum | confidence |")
        lines.append("|---|---|---|---|")
        for c in lcc:
            lines.append(f"| {c['dev_id']} | {c['gold_label']} | {c['stratum']} | {c['confidence']} |")
        lines.append("")
    else:
        lines.append("### Low-confidence correct predictions (VALID conf < 0.6)\n\n"
                     "_None: no correct prediction had VALID confidence < 0.6._\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Paired comparison (descriptive; frozen sign conventions; NEVER pooled)
# ---------------------------------------------------------------------------

def _micro(report: dict, model: str) -> dict:
    return report["models"][model]["micro_all"]


def _rc_point(report: dict, model: str, tau: float) -> dict:
    rc = {round(pt["tau"], 1): pt for pt in report["models"][model]["risk_coverage_clear"]}
    return rc.get(round(tau, 1), {})


def paired_comparison(aa: dict, po: dict) -> dict:
    """Frozen descriptive paired comparison. Same 27 cases; NO pooling; NO pooled score."""
    aa_recs = {r.dev_id: r for r in aa["records"]}
    po_recs = {r.dev_id: r for r in po["records"]}
    dev_ids = sorted(aa_recs)

    aa_micro = _micro(aa["report"], aa["model"])
    po_micro = _micro(po["report"], po["model"])

    aa_acc = aa_micro["accuracy"]
    po_acc = po_micro["accuracy"]
    aa_brier = aa_micro["brier_top_label"]
    po_brier = po_micro["brier_top_label"]

    # per-DEV disagreement (predicted label) + paired correctness quadrants
    disagreements = []
    quadrants = {"both_correct": [], "agent_arena_only": [],
                 "prompt_only_only": [], "both_incorrect": []}
    paired_rows = []
    for dev_id in dev_ids:
        a = aa_recs[dev_id]
        b = po_recs[dev_id]
        if a.predicted_label != b.predicted_label:
            disagreements.append({
                "dev_id": dev_id, "gold_label": a.gold_label, "stratum": a.stratum,
                "agent_arena": a.predicted_label, "prompt_only": b.predicted_label,
            })
        if a.correct and b.correct:
            quadrants["both_correct"].append(dev_id)
        elif a.correct and not b.correct:
            quadrants["agent_arena_only"].append(dev_id)
        elif not a.correct and b.correct:
            quadrants["prompt_only_only"].append(dev_id)
        else:
            quadrants["both_incorrect"].append(dev_id)
        paired_rows.append({
            "dev_id": dev_id, "gold_label": a.gold_label, "stratum": a.stratum,
            "agent_arena_pred": a.predicted_label, "agent_arena_conf": a.confidence,
            "agent_arena_correct": a.correct,
            "prompt_only_pred": b.predicted_label, "prompt_only_conf": b.confidence,
            "prompt_only_correct": b.correct,
        })

    aa_hce = aa["derived"]["all_27"]["high_conf_errors"]
    po_hce = po["derived"]["all_27"]["high_conf_errors"]

    # fixed-threshold selective behavior (clear stratum, over the frozen tau grid)
    selective = {}
    for tau in (round(i / 10, 1) for i in range(11)):
        a_pt = _rc_point(aa["report"], aa["model"], tau)
        b_pt = _rc_point(po["report"], po["model"], tau)
        selective[f"{tau:.1f}"] = {
            "agent_arena": {"coverage_all": a_pt.get("coverage_all"),
                            "selective_accuracy": a_pt.get("selective_accuracy"),
                            "selective_risk": a_pt.get("selective_risk"),
                            "coverage_lost_all": a_pt.get("coverage_lost_all"),
                            "benefit_vs_tau0": a_pt.get("benefit_vs_tau0")},
            "prompt_only": {"coverage_all": b_pt.get("coverage_all"),
                            "selective_accuracy": b_pt.get("selective_accuracy"),
                            "selective_risk": b_pt.get("selective_risk"),
                            "coverage_lost_all": b_pt.get("coverage_lost_all"),
                            "benefit_vs_tau0": b_pt.get("benefit_vs_tau0")},
        }

    ceiling = (aa_acc == 1.0 and po_acc == 1.0)

    return {
        "banner": list(PILOT_BANNER),
        "comparison_unit": "27 paired DEV-#### cases; two arms; paired (per-case), never pooled",
        "arms": {
            "agent_arena": {"run_id": aa["run_id"], "model": aa["model"],
                            "contract_id": EXPECTED_RUNS[AGENT_ARENA]["contract_id"]},
            "prompt_only": {"run_id": po["run_id"], "model": po["model"],
                            "contract_id": EXPECTED_RUNS[PROMPT_ONLY]["contract_id"]},
        },
        "denominators": {
            "accuracy_all_records_per_arm": 27,
            "brier_ece_reliability_valid_records_per_arm": {
                "agent_arena": aa_micro["n_valid"], "prompt_only": po_micro["n_valid"]},
        },
        "parser_completion": {
            "agent_arena": aa["integrity"]["parser_completion"],
            "prompt_only": po["integrity"]["parser_completion"],
        },
        "confidence_valid_coverage": {
            "agent_arena": aa_micro["confidence_valid_coverage"],
            "prompt_only": po_micro["confidence_valid_coverage"],
        },
        "accuracy": {
            "agent_arena_all27": aa_acc,
            "prompt_only_all27": po_acc,
            # frozen sign convention: accuracy(Agent Arena) - accuracy(prompt-only)
            "difference_agent_arena_minus_prompt_only": aa_acc - po_acc,
        },
        "brier_top_label_valid": {
            "agent_arena": aa_brier,
            "prompt_only": po_brier,
            # frozen sign convention: Brier(prompt-only) - Brier(Agent Arena)
            "difference_prompt_only_minus_agent_arena": (
                po_brier - aa_brier if (po_brier is not None and aa_brier is not None) else None),
        },
        "ece_5bin_all27_secondary": {
            "agent_arena": aa_micro["ece_5bin"],
            "prompt_only": po_micro["ece_5bin"],
        },
        "mean_reported_confidence_all27": {
            "agent_arena": aa["derived"]["all_27"]["mean_reported_confidence"],
            "prompt_only": po["derived"]["all_27"]["mean_reported_confidence"],
        },
        "predicted_label_distribution_all27": {
            "agent_arena": aa_micro["predicted_label_distribution"],
            "prompt_only": po_micro["predicted_label_distribution"],
        },
        "prediction_disagreements": {
            "n": len(disagreements),
            "detail": disagreements,
        },
        "paired_correctness_table": {
            "both_correct": len(quadrants["both_correct"]),
            "agent_arena_correct_prompt_only_incorrect": len(quadrants["agent_arena_only"]),
            "agent_arena_incorrect_prompt_only_correct": len(quadrants["prompt_only_only"]),
            "both_incorrect": len(quadrants["both_incorrect"]),
            "dev_ids": quadrants,
        },
        "high_confidence_errors": {
            "agent_arena": {"n": len(aa_hce), "detail": aa_hce},
            "prompt_only": {"n": len(po_hce), "detail": po_hce},
            # frozen sign convention: prompt-only minus Agent Arena
            "difference_prompt_only_minus_agent_arena": len(po_hce) - len(aa_hce),
        },
        "by_gold_label_all27": {
            "agent_arena": aa["by_gold_label_all27"],
            "prompt_only": po["by_gold_label_all27"],
        },
        "by_stratum": {
            arm_key: {
                "clear": {"n": arm["derived"]["clear"]["n"],
                          "correct": arm["derived"]["clear"]["correct"],
                          "incorrect": arm["derived"]["clear"]["incorrect"]},
                "development_only": {"n": arm["derived"]["development_only"]["n"],
                                     "correct": arm["derived"]["development_only"]["correct"],
                                     "incorrect": arm["derived"]["development_only"]["incorrect"]},
                "borderline": {"n": arm["derived"]["borderline"]["n"],
                               "correct": arm["derived"]["borderline"]["correct"],
                               "incorrect": arm["derived"]["borderline"]["incorrect"]},
            }
            for arm_key, arm in (("agent_arena", aa), ("prompt_only", po))
        },
        "fixed_threshold_selective_clear": selective,
        "abstention_cost_note": (
            "coverage_lost_all = 1 - coverage_all (fixed; no tunable cost ratio). Any point "
            "showing benefit is development-selected and NOT an unbiased operating guarantee."
        ),
        "accuracy_ceiling": ceiling,
        "paired_rows": paired_rows,
        "prohibitions_upheld": {
            "no_54_case_pool": True,
            "no_pooled_accuracy_brier_or_ece": True,
            "no_statistical_proof_claim": True,
            "no_universal_winner": True,
            "no_case_excluded_or_altered_after_results": True,
        },
    }


def render_paired_md(cmp: dict) -> str:
    lines = ["# Phase 6.4 — Paired Haiku package-level development comparison\n"]
    for b in cmp["banner"]:
        lines.append(f"### {b}")
    lines.append("")
    lines.append(f"**Comparison unit:** {cmp['comparison_unit']}.\n")
    a = cmp["arms"]["agent_arena"]
    p = cmp["arms"]["prompt_only"]
    lines.append(f"- Agent Arena arm — run `{a['run_id']}`, contract `{a['contract_id']}`")
    lines.append(f"- prompt-only arm — run `{p['run_id']}`, contract `{p['contract_id']}`")
    lines.append(f"- shared model: `{a['model']}`\n")

    lines.append("## Headline (descriptive; frozen sign conventions)\n")
    lines.append("| metric | Agent Arena | prompt-only | difference (frozen sign) |")
    lines.append("|---|---|---|---|")
    acc = cmp["accuracy"]
    lines.append(f"| accuracy (all 27) | {_fmt(acc['agent_arena_all27'])} | "
                 f"{_fmt(acc['prompt_only_all27'])} | "
                 f"AA − PO = **{_fmt(acc['difference_agent_arena_minus_prompt_only'])}** |")
    br = cmp["brier_top_label_valid"]
    lines.append(f"| Brier top-label (VALID) — primary | {_fmt(br['agent_arena'])} | "
                 f"{_fmt(br['prompt_only'])} | "
                 f"PO − AA = **{_fmt(br['difference_prompt_only_minus_agent_arena'])}** |")
    ece = cmp["ece_5bin_all27_secondary"]
    lines.append(f"| ECE 5-bin (all 27) — secondary | {_fmt(ece['agent_arena'])} | "
                 f"{_fmt(ece['prompt_only'])} | — |")
    mc = cmp["mean_reported_confidence_all27"]
    lines.append(f"| mean reported confidence (all 27) | {_fmt(mc['agent_arena'])} | "
                 f"{_fmt(mc['prompt_only'])} | — |")
    cov = cmp["confidence_valid_coverage"]
    lines.append(f"| confidence-valid coverage | {_fmt(cov['agent_arena'])} | "
                 f"{_fmt(cov['prompt_only'])} | — |")
    pcc = cmp["parser_completion"]
    lines.append(f"| parser completion | {pcc['agent_arena']['parse_ok']}/27 | "
                 f"{pcc['prompt_only']['parse_ok']}/27 | — |")
    hce = cmp["high_confidence_errors"]
    lines.append(f"| high-confidence errors (≥0.8) | {hce['agent_arena']['n']} | "
                 f"{hce['prompt_only']['n']} | "
                 f"PO − AA = **{hce['difference_prompt_only_minus_agent_arena']}** |")
    lines.append("")
    if cmp["accuracy_ceiling"]:
        lines.append("> **Accuracy ceiling:** both arms reached 27/27; the pilot could not "
                     "distinguish classification accuracy. The arms are NOT called equivalent; "
                     "Brier / confidence / parser completion are examined cautiously.\n")
    else:
        lines.append("> **No accuracy ceiling:** the arms differ in classification accuracy on "
                     "this pilot. This is a paired development observation for this 27-case pool "
                     "only — not a general advantage, and not attributed solely to the system "
                     "prompt (the arms differ as whole packages).\n")

    pt = cmp["paired_correctness_table"]
    q = pt["dev_ids"]
    lines.append("## Paired correctness table (same 27 cases; NOT 54 independent cases)\n")
    lines.append("| quadrant | count | DEV ids |")
    lines.append("|---|---|---|")
    lines.append(f"| both correct | {pt['both_correct']} | "
                 f"{', '.join(q['both_correct']) if q['both_correct'] else '—'} |")
    lines.append(f"| Agent Arena correct / prompt-only incorrect | "
                 f"{pt['agent_arena_correct_prompt_only_incorrect']} | "
                 f"{', '.join(q['agent_arena_only']) if q['agent_arena_only'] else '—'} |")
    lines.append(f"| Agent Arena incorrect / prompt-only correct | "
                 f"{pt['agent_arena_incorrect_prompt_only_correct']} | "
                 f"{', '.join(q['prompt_only_only']) if q['prompt_only_only'] else '—'} |")
    lines.append(f"| both incorrect | {pt['both_incorrect']} | "
                 f"{', '.join(q['both_incorrect']) if q['both_incorrect'] else '—'} |")
    lines.append("")

    dis = cmp["prediction_disagreements"]
    lines.append(f"## Predicted-label disagreements: {dis['n']} of 27 DEV ids\n")
    if dis["detail"]:
        lines.append("| dev_id | gold | stratum | Agent Arena | prompt-only |")
        lines.append("|---|---|---|---|---|")
        for d in dis["detail"]:
            lines.append(f"| {d['dev_id']} | {d['gold_label']} | {d['stratum']} | "
                         f"{d['agent_arena']} | {d['prompt_only']} |")
    else:
        lines.append("_No predicted-label disagreements._")
    lines.append("")

    lines.append("## High-confidence errors (incorrect with VALID confidence ≥ 0.8)\n")
    for arm_key, title in (("agent_arena", "Agent Arena"), ("prompt_only", "prompt-only")):
        h = cmp["high_confidence_errors"][arm_key]
        if h["detail"]:
            lines.append(f"- **{title}**: {h['n']}")
            for e in h["detail"]:
                lines.append(f"  - {e['dev_id']} — predicted `{e['predicted_label']}`, "
                             f"gold `{e['gold_label']}`, {e['stratum']}, conf {e['confidence']}")
        else:
            lines.append(f"- **{title}**: 0")
    lines.append("")

    lines.append("## By gold label — ALL 27 (all four labels visible)\n")
    lines.append("| gold label | AA acc | AA Brier | PO acc | PO Brier | flag |")
    lines.append("|---|---|---|---|---|---|")
    for lbl in LABELS:
        g_a = cmp["by_gold_label_all27"]["agent_arena"][lbl]
        g_p = cmp["by_gold_label_all27"]["prompt_only"][lbl]
        flag = "small_n/descriptive-only" if g_a["small_n"] else ""
        lines.append(f"| {lbl} (n={g_a['n']}) | {_fmt(g_a['accuracy'])} | {_fmt(g_a['brier_top_label'])} | "
                     f"{_fmt(g_p['accuracy'])} | {_fmt(g_p['brier_top_label'])} | {flag} |")
    lines.append("")

    lines.append("## By stratum (clear / development_only / borderline; reported separately)\n")
    lines.append("| stratum | AA n | AA correct | PO n | PO correct |")
    lines.append("|---|---|---|---|---|")
    for st in ("clear", "development_only", "borderline"):
        sa = cmp["by_stratum"]["agent_arena"][st]
        sp = cmp["by_stratum"]["prompt_only"][st]
        lines.append(f"| {st} | {sa['n']} | {sa['correct']} | {sp['n']} | {sp['correct']} |")
    lines.append("")

    lines.append("## Fixed-threshold selective behavior (clear stratum; frozen τ grid)\n")
    lines.append("_Reporting the pre-declared risk–coverage curve; no threshold is chosen or "
                 "tuned on these results. " + cmp["abstention_cost_note"] + "_\n")
    lines.append("| τ | AA cov | AA sel-acc | AA cost | AA benefit | PO cov | PO sel-acc | PO cost | PO benefit |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for tau in (f"{i/10:.1f}" for i in range(11)):
        s = cmp["fixed_threshold_selective_clear"][tau]
        aq = s["agent_arena"]
        pq = s["prompt_only"]
        lines.append(
            f"| {tau} | {_fmt(aq['coverage_all'])} | {_fmt(aq['selective_accuracy'])} | "
            f"{_fmt(aq['coverage_lost_all'])} | {_fmt(aq['benefit_vs_tau0'])} | "
            f"{_fmt(pq['coverage_all'])} | {_fmt(pq['selective_accuracy'])} | "
            f"{_fmt(pq['coverage_lost_all'])} | {_fmt(pq['benefit_vs_tau0'])} |")
    lines.append("")
    lines.append("> Paired outcomes on identical cases: a difference reflects the two packages' "
                 "behavior on the *same* item, not two independent samples. n is far too small "
                 "(27; corr/mech at n=2) for any universal-superiority claim. The 54 predictions "
                 "are never pooled into a 54-case benchmark and no pooled score is computed.\n")
    return "\n".join(lines)


def render_integrity_md(binding: dict, results: list, pairing: dict) -> str:
    lines = ["# Phase 6.4 — Input Integrity Report\n"]
    lines.append("### DEVELOPMENT PILOT — NOT HOLDOUT\n")
    lines.append("Independent validation of the two anonymized result envelopes **before** any "
                 "paired performance analysis. The holdout remained sealed; no private mapping, "
                 "salt, or canonical identity was accessed.\n")
    lines.append("## Tracked binding\n")
    lines.append(f"- manifest_id: `{binding['manifest_id']}`")
    lines.append(f"- public_commitment: `{binding['commitment']}`\n")
    overall = all(r["all_pass"] for r in results) and pairing["all_pass"]
    lines.append(f"## Overall integrity: **{'PASS' if overall else 'FAIL'}**\n")

    lines.append("## Cross-arm pairing\n")
    lines.append(f"- DEV-ID set identical across arms: "
                 f"**{'YES' if pairing['dev_id_set_identical_across_arms'] else 'NO'}** "
                 f"({pairing['n_common_dev_ids']} common ids)")
    lines.append(f"- gold label identical per paired DEV: "
                 f"**{'YES' if pairing['gold_label_identical_per_paired_dev'] else 'NO'}** "
                 f"(mismatches: {pairing['gold_mismatch_dev_ids'] or 'none'})")
    lines.append(f"- stratum identical per paired DEV: "
                 f"**{'YES' if pairing['stratum_identical_per_paired_dev'] else 'NO'}** "
                 f"(mismatches: {pairing['stratum_mismatch_dev_ids'] or 'none'})\n")

    for r in results:
        lines.append(f"### {r['arm_title']} — {r['model']}")
        lines.append(f"- run_id: `{r['run_id']}`  ·  expected contract: `{r['contract_id']}`")
        lines.append(f"- prompt_contract_version: `{r['prompt_contract_version']}`")
        lines.append(f"- contract_id echoed in prompt_contract_version: "
                     f"**{r['contract_id_echoed_in_pcv']}**  ·  "
                     f"system_prompt_sha256 present: **{r['system_prompt_sha256_present']}**")
        pc = r["parser_completion"]
        lines.append(f"- parser completion: **{pc['parse_ok']}/{pc['records_present']}** "
                     f"(failures: {pc['parse_failures']}) — reported separately from accuracy")
        cc = r["confidence_counts"]
        lines.append(f"- confidence: valid={cc['valid']} missing={cc['missing']} invalid={cc['invalid']}")
        lines.append(f"- gold aggregate: {json.dumps(r['gold_counts'], sort_keys=True)}")
        lines.append(f"- leakage: {'none' if not r['leakage'] else '; '.join(r['leakage'])}")
        lines.append(f"- per-envelope result: **{'PASS' if r['all_pass'] else 'FAIL'}**\n")
        lines.append("| check | pass | detail |")
        lines.append("|---|---|---|")
        for c in r["checks"]:
            detail = c["detail"].replace("|", "\\|") if c["detail"] else ""
            lines.append(f"| {c['check']} | {'✓' if c['pass'] else '✗'} | {detail} |")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def _dump_json(obj, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def build_all(aa_envelope: dict, po_envelope: dict, manifest_id: str, commitment: str) -> dict:
    """Validate both envelopes and build every report object (pure; no I/O)."""
    envelopes = {AGENT_ARENA: aa_envelope, PROMPT_ONLY: po_envelope}
    integrity = {arm: validate_one(arm, envelopes[arm], manifest_id, commitment)
                 for arm in ARM_ORDER}
    pairing = cross_arm_pairing(integrity[AGENT_ARENA], integrity[PROMPT_ONLY])

    arms = {}
    for arm in ARM_ORDER:
        ev = validate_result_envelope(envelopes[arm], manifest_id, commitment, enforce_aggregate=True)
        if not ev.ok:
            raise SystemExit(f"[{arm}] ENVELOPE INTEGRITY FAILED:\n  - "
                             + "\n  - ".join(ev.errors))
        model = ev.provenance["model"]
        arms[arm] = {
            "arm": arm,
            "run_id": integrity[arm]["run_id"],
            "model": model,
            "report": build_report(ev.records, provenance=ev.provenance, synthetic=False),
            "derived": derived_descriptive(ev.records),
            "by_gold_label_all27": by_gold_label_all27(ev.records),
            "records": ev.records,
            "integrity": integrity[arm],
        }
    cmp = paired_comparison(arms[AGENT_ARENA], arms[PROMPT_ONLY])
    return {"integrity": integrity, "pairing": pairing, "arms": arms, "paired": cmp}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agent-arena-envelope", required=True,
                    help="path to the completed Agent Arena Haiku result envelope (outside repo)")
    ap.add_argument("--prompt-only-envelope", required=True,
                    help="path to the completed prompt-only Haiku result envelope (outside repo)")
    ap.add_argument("--out-dir", required=True, help="directory to write reports into")
    args = ap.parse_args()

    aa_envelope = json.loads(Path(args.agent_arena_envelope).expanduser().read_text())
    po_envelope = json.loads(Path(args.prompt_only_envelope).expanduser().read_text())
    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_id, commitment = load_public_manifest_binding()
    binding = {"manifest_id": manifest_id, "commitment": commitment}

    built = build_all(aa_envelope, po_envelope, manifest_id, commitment)
    integrity = built["integrity"]
    pairing = built["pairing"]
    arms = built["arms"]
    cmp = built["paired"]

    overall = all(integrity[arm]["all_pass"] for arm in ARM_ORDER) and pairing["all_pass"]

    # integrity report (json + md) — strip cross-arm helper maps from the tracked JSON
    integ_public = []
    for arm in ARM_ORDER:
        r = dict(integrity[arm])
        r.pop("gold_by_dev", None)
        r.pop("stratum_by_dev", None)
        integ_public.append(r)
    integrity_obj = {
        "banner": list(PILOT_BANNER),
        "tracked_binding": binding,
        "cross_arm_pairing": pairing,
        "overall_pass": overall,
        "per_envelope": integ_public,
    }
    _dump_json(integrity_obj, out_dir / "input_integrity_report.json")
    (out_dir / "input_integrity_report.md").write_text(
        render_integrity_md(binding, integ_public, pairing))

    if not overall:
        print("INPUT INTEGRITY FAILED — stopping before paired performance analysis.")
        return 2

    # per-arm reports (json + md)
    filename = {AGENT_ARENA: "agent_arena_haiku_arm_report",
                PROMPT_ONLY: "prompt_only_haiku_arm_report"}
    for arm in ARM_ORDER:
        a = arms[arm]
        json_obj = dict(a["report"])
        json_obj["phase6_4_status"] = {"banner": list(PILOT_BANNER), "arm": arm,
                                       "arm_title": ARM_TITLE[arm]}
        json_obj["parser_completion"] = a["integrity"]["parser_completion"]
        json_obj["derived_descriptive"] = a["derived"]
        json_obj["by_gold_label_all27"] = a["by_gold_label_all27"]
        json_obj["input_integrity"] = {
            "run_id": a["integrity"]["run_id"], "model": a["integrity"]["model"],
            "contract_id": a["integrity"]["contract_id"],
            "confidence_counts": a["integrity"]["confidence_counts"],
            "gold_counts": a["integrity"]["gold_counts"],
            "all_pass": a["integrity"]["all_pass"],
        }
        _dump_json(json_obj, out_dir / f"{filename[arm]}.json")
        (out_dir / f"{filename[arm]}.md").write_text(render_arm_md(a))

    # paired comparison (json + md)
    _dump_json(cmp, out_dir / "paired_comparison_report.json")
    (out_dir / "paired_comparison_report.md").write_text(render_paired_md(cmp))

    print(f"wrote reports to {out_dir}")
    print(f"overall integrity pass: {overall}")
    print(f"accuracy: agent_arena={cmp['accuracy']['agent_arena_all27']} "
          f"prompt_only={cmp['accuracy']['prompt_only_all27']} "
          f"diff(AA-PO)={cmp['accuracy']['difference_agent_arena_minus_prompt_only']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
