#!/usr/bin/env python3
"""Deterministic Phase 6.2 calibration report generator (offline, no model calls).

Reads the three anonymized result envelopes (Haiku / Sonnet / Opus), independently
validates each against the tracked public manifest binding and the frozen runtime
contracts, then renders the per-model calibration reports, the cross-model descriptive
comparison, and the input-integrity report — using **only** the frozen engine in
``agent_arena.calibration`` (Brier primary, 5 fixed bins, secondary ECE, costed
abstention). Nothing here re-tunes any bin/threshold/cost.

Privacy: the envelopes live OUTSIDE the repository and are never copied into it. This
script takes their directory as a runtime argument; the artifacts it writes carry only
opaque ``DEV-####`` ids, class labels, aggregated metrics, and run/model provenance —
no canonical/BIAA/HLD ids, no salt, no private paths.

Determinism: no wall-clock timestamps are injected; every value derives from the frozen
engine and the envelope provenance, so repeated runs are byte-for-byte identical.

Usage::

    PYTHONPATH=src .venv/bin/python analysis/phase6_2_results/build_calibration_reports.py \
        --envelope-dir <PRIVATE_ENVELOPE_DIR> --out-dir analysis/phase6_2_results
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
    build_report,
    load_public_manifest_binding,
    render_report_text,
    validate_result_envelope,
)
from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence

# --- expected runs (from the authoritative Phase 6.2 checkpoint) -------------------
EXPECTED_RUNS = {
    "haiku": {
        "envelope": "haiku_result_envelope.json",
        "run_id": "AA-6.2-RUN-6a3b93a24af7431e",
        "model": "claude-haiku-4-5-20251001",
        "contract_id": "AA-RTC-6.2-HAIKU-001",
    },
    "sonnet": {
        "envelope": "sonnet_result_envelope.json",
        "run_id": "AA-P62-SONNET-23f5dcc25de6",
        "model": "claude-sonnet-4-5-20250929",
        "contract_id": "AA-RTC-6.2-SONNET-001",
    },
    "opus": {
        "envelope": "opus_result_envelope.json",
        "run_id": "opus-878636c64fc8",
        "model": "claude-opus-4-5-20251101",
        "contract_id": "AA-RTC-6.2-OPUS-001",
    },
}
MODEL_ORDER = ("haiku", "sonnet", "opus")

# system_prompt_sha256 pinned by all three frozen runtime contracts (shared prompt).
CONTRACT_SYSTEM_PROMPT_SHA256 = "f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5"

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
# Independent input-integrity validation (supplements the engine's envelope check)
# ---------------------------------------------------------------------------

def validate_one(short: str, envelope: dict, manifest_id: str, commitment: str) -> dict:
    """Independent per-envelope integrity checks; returns a structured result."""
    exp = EXPECTED_RUNS[short]
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    # 1. structural: no unexpected top-level or record fields (schema additionalProperties:false)
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

    # 3. expected run/model/contract
    check("run_id_matches_expected", envelope.get("run_id") == exp["run_id"],
          f"{envelope.get('run_id')} vs {exp['run_id']}")
    check("model_matches_expected", envelope.get("model") == exp["model"],
          f"{envelope.get('model')} vs {exp['model']}")
    pcv = envelope.get("prompt_contract_version", "") or ""
    contract_id_present = exp["contract_id"] in pcv
    sha_present = CONTRACT_SYSTEM_PROMPT_SHA256 in pcv
    # contract binding is satisfied if the literal contract id is echoed, OR (schema
    # permits a bare hash) the pinned system_prompt_sha256 is present AND the exact
    # model id maps uniquely to this contract.
    contract_bound = contract_id_present or (sha_present and envelope.get("model") == exp["model"])
    check("contract_binding_satisfied", contract_bound,
          f"contract_id_present={contract_id_present} sha_present={sha_present}")

    # 4. records: exactly 27, unique dev ids, gold aggregate, confidence validity
    check("record_count_27", len(records) == 27, str(len(records)))
    dev_ids = [r.get("dev_id") for r in records]
    check("dev_ids_unique", len(set(dev_ids)) == len(dev_ids), f"n_unique={len(set(dev_ids))}")
    gold_counts = {lbl: sum(1 for r in records if r.get("gold_label") == lbl) for lbl in LABELS}
    check("gold_aggregate_8_15_2_2",
          gold_counts == {"solid": 8, "overclaim": 15,
                          "correlation_vs_causation": 2, "mechanism_vs_evidence": 2},
          json.dumps(gold_counts, sort_keys=True))
    conf_states = [classify_confidence(r.get("confidence")) for r in records]
    n_valid = conf_states.count(VALID)
    n_missing = conf_states.count(MISSING)
    n_invalid = conf_states.count(INVALID)
    check("confidence_all_valid", n_invalid == 0,
          f"valid={n_valid} missing={n_missing} invalid={n_invalid}")
    # no raw confidence is a literal 0.0 that could have been a coercion artifact
    zero_conf = [r.get("dev_id") for r in records if r.get("confidence") == 0.0]
    check("no_zero_coercion_artifact", not zero_conf, f"zero_conf_dev_ids={zero_conf}")
    # optional explicit correctness consistency (if present)
    inconsistent = [r.get("dev_id") for r in records if "correct" in r
                    and r.get("correct") != (1 if r.get("predicted_label") == r.get("gold_label") else 0)]
    check("explicit_correct_consistent", not inconsistent, f"inconsistent={inconsistent}")

    # 5. leakage scan on the raw envelope
    leak = leakage_scan(json.dumps(envelope))
    check("no_identity_leakage", not leak, "; ".join(leak))

    # 6. engine-side envelope validation (authoritative binding + vocab + dup + no coercion)
    ev = validate_result_envelope(envelope, manifest_id, commitment, enforce_aggregate=True)
    check("engine_validate_result_envelope_clean", ev.ok,
          "; ".join(ev.errors[:6]) + (" …" if len(ev.errors) > 6 else ""))

    dev_id_set = sorted(dev_ids)
    return {
        "model_short": short,
        "run_id": envelope.get("run_id"),
        "model": envelope.get("model"),
        "contract_id": exp["contract_id"],
        "prompt_contract_version": pcv,
        "contract_id_echoed_in_pcv": contract_id_present,
        "system_prompt_sha256_present": sha_present,
        "generated_at": envelope.get("generated_at"),
        "confidence_counts": {"valid": n_valid, "missing": n_missing, "invalid": n_invalid},
        "gold_counts": gold_counts,
        "dev_id_set": dev_id_set,
        "checks": checks,
        "all_pass": all(c["pass"] for c in checks),
        "leakage": leak,
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


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _fmt(x, nd=4):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def render_derived_md(short: str, run_id: str, model: str, derived: dict) -> str:
    lines = []
    lines.append("\n## Derived descriptive (items 2 / 6 / 16 / 17 — not new frozen metrics)\n")
    d = derived["definitions"]
    lines.append(f"- high_conf_error := {d['high_conf_error']}")
    lines.append(f"- low_conf_correct := {d['low_conf_correct']}")
    lines.append(f"- _{d['note']}_\n")
    lines.append("| stratum | n | correct | incorrect | mean conf | min conf | max conf |")
    lines.append("|---|---|---|---|---|---|---|")
    for key in ("all_27", "clear", "development_only", "borderline"):
        s = derived[key]
        lines.append(
            f"| {key} | {s['n']} | {s['correct']} | {s['incorrect']} | "
            f"{_fmt(s['mean_reported_confidence'])} | {_fmt(s['min_reported_confidence'])} | "
            f"{_fmt(s['max_reported_confidence'])} |")
    lines.append("")
    errs = derived["all_27"]["all_errors"]
    if errs:
        lines.append("### High-confidence / all errors (item 16)\n")
        lines.append("| dev_id | predicted | gold | stratum | confidence |")
        lines.append("|---|---|---|---|---|")
        for e in errs:
            lines.append(f"| {e['dev_id']} | {e['predicted_label']} | {e['gold_label']} | "
                         f"{e['stratum']} | {e['confidence']} |")
        lines.append("")
    else:
        lines.append("### Errors (item 16)\n\n_No incorrect predictions in this run._\n")
    lcc = derived["all_27"]["low_conf_correct"]
    if lcc:
        lines.append("### Low-confidence correct predictions (item 17)\n")
        lines.append("| dev_id | gold | stratum | confidence |")
        lines.append("|---|---|---|---|")
        for c in lcc:
            lines.append(f"| {c['dev_id']} | {c['gold_label']} | {c['stratum']} | {c['confidence']} |")
        lines.append("")
    else:
        lines.append("### Low-confidence correct predictions (item 17)\n\n"
                     f"_None: no correct prediction had VALID confidence < {LOW_CONF_CEIL} "
                     "(all observed confidences lie in the top primary bin [0.8, 1.0])._\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Cross-model descriptive comparison
# ---------------------------------------------------------------------------

def cross_model(per_model: dict) -> dict:
    """Build the SECONDARY descriptive cross-model comparison. Same 27 cases; no pooling."""
    table = {}
    for short in MODEL_ORDER:
        pm = per_model[short]
        report = pm["report"]
        model_key = pm["model"]
        m = report["models"][model_key]
        clear = m["headline_clear"]
        allm = m["micro_all"]
        der = pm["derived"]
        # selective accuracy / coverage at tau=0.9 (a reporting point, NOT a chosen operator)
        rc = {round(pt["tau"], 1): pt for pt in m["risk_coverage_clear"]}
        pt09 = rc.get(0.9, {})
        table[short] = {
            "model": model_key,
            "run_id": pm["run_id"],
            "accuracy_all_27": allm["accuracy"],
            "accuracy_clear": clear["accuracy"],
            "brier_top_label_clear": clear["brier_top_label"],
            "brier_top_label_all_27": allm["brier_top_label"],
            "ece_5bin_clear": clear["ece_5bin"],
            "confidence_valid_coverage_all_27": allm["confidence_valid_coverage"],
            "mean_reported_confidence_all_27": der["all_27"]["mean_reported_confidence"],
            "macro_brier_clear": m["macro_brier_clear"],
            "n_errors_all_27": der["all_27"]["incorrect"],
            "n_high_conf_errors_all_27": len(der["all_27"]["high_conf_errors"]),
            "selective_accuracy_clear_tau_0.9": pt09.get("selective_accuracy"),
            "coverage_all_clear_tau_0.9": pt09.get("coverage_all"),
            "coverage_lost_all_clear_tau_0.9": pt09.get("coverage_lost_all"),
        }

    # per-DEV disagreement across the three models (predicted label)
    preds = {}
    golds = {}
    strata = {}
    for short in MODEL_ORDER:
        for r in per_model[short]["records"]:
            preds.setdefault(r.dev_id, {})[short] = r.predicted_label
            golds[r.dev_id] = r.gold_label
            strata[r.dev_id] = r.stratum
    disagreements = []
    for dev_id in sorted(preds):
        labels = {preds[dev_id][s] for s in MODEL_ORDER}
        if len(labels) > 1:
            disagreements.append({
                "dev_id": dev_id,
                "gold_label": golds[dev_id],
                "stratum": strata[dev_id],
                "haiku": preds[dev_id]["haiku"],
                "sonnet": preds[dev_id]["sonnet"],
                "opus": preds[dev_id]["opus"],
            })
    # paired correctness pattern per dev id (H,S,O) correct flags
    correctness = {}
    for short in MODEL_ORDER:
        for r in per_model[short]["records"]:
            correctness.setdefault(r.dev_id, {})[short] = r.correct
    pattern_counts: dict[str, int] = {}
    for dev_id in preds:
        pat = "".join(str(correctness[dev_id][s]) for s in MODEL_ORDER)  # HSO order
        pattern_counts[pat] = pattern_counts.get(pat, 0) + 1

    return {
        "banner": [
            "DEVELOPMENT CALIBRATION — NOT HOLDOUT",
            "SECONDARY descriptive cross-model comparison",
            "all three models evaluated the SAME 27 development cases",
            "no pooling into an 81-case benchmark; the 81 predictions are NOT independent cases",
            "no single pooled calibration score; no universal-superiority inference",
            "no threshold optimized on these results; holdout remained sealed",
            "model outputs may remain nondeterministic despite frozen request parameters",
        ],
        "model_count": 3,
        "cases_per_model": 27,
        "column_order": list(MODEL_ORDER),
        "per_model": table,
        "disagreements": disagreements,
        "n_disagreements": len(disagreements),
        "correctness_pattern_counts_HSO": pattern_counts,
    }


def render_cross_model_md(cm: dict) -> str:
    lines = []
    for b in cm["banner"]:
        lines.append(f"### {b}")
    lines.append("")
    lines.append(f"Models: {cm['model_count']} · cases per model: {cm['cases_per_model']} "
                 f"· **the SAME 27 development cases across all three** (paired, not independent).\n")
    lines.append("## Descriptive per-model summary\n")
    lines.append("| metric | haiku | sonnet | opus |")
    lines.append("|---|---|---|---|")
    rows = [
        ("accuracy (all 27)", "accuracy_all_27"),
        ("accuracy (clear, n=26)", "accuracy_clear"),
        ("Brier top-label (clear) — primary", "brier_top_label_clear"),
        ("Brier top-label (all 27)", "brier_top_label_all_27"),
        ("ECE 5-bin (clear) — secondary", "ece_5bin_clear"),
        ("macro Brier (clear; solid+overclaim only)", "macro_brier_clear"),
        ("confidence-valid coverage (all 27)", "confidence_valid_coverage_all_27"),
        ("mean reported confidence (all 27)", "mean_reported_confidence_all_27"),
        ("errors (all 27)", "n_errors_all_27"),
        ("high-conf errors (all 27)", "n_high_conf_errors_all_27"),
        ("selective acc @τ=0.9 (clear)", "selective_accuracy_clear_tau_0.9"),
        ("coverage_all @τ=0.9 (clear)", "coverage_all_clear_tau_0.9"),
        ("cost=coverage lost @τ=0.9 (clear)", "coverage_lost_all_clear_tau_0.9"),
    ]
    for label, key in rows:
        h = cm["per_model"]["haiku"][key]
        s = cm["per_model"]["sonnet"][key]
        o = cm["per_model"]["opus"][key]
        lines.append(f"| {label} | {_fmt(h)} | {_fmt(s)} | {_fmt(o)} |")
    lines.append("")
    lines.append(f"## Cross-model disagreements (predicted label): "
                 f"{cm['n_disagreements']} of 27 DEV ids\n")
    if cm["disagreements"]:
        lines.append("| dev_id | gold | stratum | haiku | sonnet | opus |")
        lines.append("|---|---|---|---|---|---|")
        for d in cm["disagreements"]:
            lines.append(f"| {d['dev_id']} | {d['gold_label']} | {d['stratum']} | "
                         f"{d['haiku']} | {d['sonnet']} | {d['opus']} |")
    else:
        lines.append("_No cross-model prediction disagreements._")
    lines.append("")
    lines.append("## Paired correctness patterns (Haiku,Sonnet,Opus → 1=correct)\n")
    lines.append("| pattern H,S,O | count |")
    lines.append("|---|---|")
    for pat in sorted(cm["correctness_pattern_counts_HSO"], reverse=True):
        lines.append(f"| {pat[0]},{pat[1]},{pat[2]} | {cm['correctness_pattern_counts_HSO'][pat]} |")
    lines.append("")
    lines.append("> These are paired outcomes on identical cases: a difference reflects "
                 "the two models' behavior on the *same* item, not two independent samples. "
                 "n is far too small (27; corr/mech at n=2) to claim universal superiority.\n")
    return "\n".join(lines)


def render_integrity_md(binding: dict, results: list, dev_set_identical: bool,
                        common_dev_set: list) -> str:
    lines = []
    lines.append("# Phase 6.2 — Input Integrity Report\n")
    lines.append("### DEVELOPMENT CALIBRATION — NOT HOLDOUT\n")
    lines.append("Independent validation of the three anonymized result envelopes **before** "
                 "any performance analysis. The holdout remained sealed; no private mapping, "
                 "salt, or canonical identity was accessed.\n")
    lines.append("## Tracked binding\n")
    lines.append(f"- manifest_id: `{binding['manifest_id']}`")
    lines.append(f"- public_commitment: `{binding['commitment']}`\n")
    lines.append(f"## DEV-ID set identical across all three models: "
                 f"**{'YES' if dev_set_identical else 'NO'}** "
                 f"({len(common_dev_set)} ids, {common_dev_set[0]}…{common_dev_set[-1]})\n")
    overall = all(r["all_pass"] for r in results) and dev_set_identical
    lines.append(f"## Overall integrity: **{'PASS' if overall else 'FAIL'}**\n")
    for r in results:
        lines.append(f"### {r['model_short']} — {r['model']}")
        lines.append(f"- run_id: `{r['run_id']}`  ·  expected contract: `{r['contract_id']}`")
        lines.append(f"- prompt_contract_version: `{r['prompt_contract_version']}`")
        lines.append(f"- contract_id echoed in prompt_contract_version: "
                     f"**{r['contract_id_echoed_in_pcv']}**  ·  "
                     f"system_prompt_sha256 present: **{r['system_prompt_sha256_present']}**")
        cc = r["confidence_counts"]
        lines.append(f"- confidence: valid={cc['valid']} missing={cc['missing']} invalid={cc['invalid']}")
        lines.append(f"- gold aggregate: {json.dumps(r['gold_counts'], sort_keys=True)}")
        lines.append(f"- leakage: {'none' if not r['leakage'] else '; '.join(r['leakage'])}")
        lines.append(f"- per-envelope result: **{'PASS' if r['all_pass'] else 'FAIL'}**")
        lines.append("")
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--envelope-dir", required=True,
                    help="directory holding the three *_result_envelope.json files (outside the repo)")
    ap.add_argument("--out-dir", required=True, help="directory to write reports into")
    args = ap.parse_args()

    env_dir = Path(args.envelope_dir).expanduser()
    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_id, commitment = load_public_manifest_binding()
    binding = {"manifest_id": manifest_id, "commitment": commitment}

    integrity_results = []
    per_model = {}
    for short in MODEL_ORDER:
        exp = EXPECTED_RUNS[short]
        envelope = json.loads((env_dir / exp["envelope"]).read_text())
        integ = validate_one(short, envelope, manifest_id, commitment)
        integrity_results.append(integ)
        ev = validate_result_envelope(envelope, manifest_id, commitment, enforce_aggregate=True)
        if not ev.ok:
            print(f"[{short}] ENVELOPE INTEGRITY FAILED — stopping:")
            for e in ev.errors:
                print(f"    - {e}")
            return 2
        report = build_report(ev.records, provenance=ev.provenance, synthetic=False)
        der = derived_descriptive(ev.records)
        per_model[short] = {"model": integ["model"], "run_id": integ["run_id"],
                            "report": report, "derived": der, "records": ev.records}

    # DEV-ID set identical across models?
    dev_sets = [r["dev_id_set"] for r in integrity_results]
    dev_set_identical = all(s == dev_sets[0] for s in dev_sets)
    common_dev_set = dev_sets[0]

    # write per-model reports (JSON = engine report + additive derived/integrity keys)
    for short in MODEL_ORDER:
        pm = per_model[short]
        integ = next(r for r in integrity_results if r["model_short"] == short)
        json_obj = dict(pm["report"])
        json_obj["derived_descriptive"] = pm["derived"]
        json_obj["input_integrity"] = {
            "run_id": integ["run_id"], "model": integ["model"],
            "contract_id": integ["contract_id"],
            "contract_id_echoed_in_pcv": integ["contract_id_echoed_in_pcv"],
            "system_prompt_sha256_present": integ["system_prompt_sha256_present"],
            "confidence_counts": integ["confidence_counts"],
            "gold_counts": integ["gold_counts"],
            "all_pass": integ["all_pass"],
            "dev_id_set_identical_across_models": dev_set_identical,
        }
        _dump_json(json_obj, out_dir / f"{short}_calibration_report.json")
        md = render_report_text(pm["report"])
        md += render_derived_md(short, integ["run_id"], integ["model"], pm["derived"])
        (out_dir / f"{short}_calibration_report.md").write_text(md)

    # cross-model comparison
    cm = cross_model(per_model)
    _dump_json(cm, out_dir / "cross_model_descriptive_comparison.json")
    (out_dir / "cross_model_descriptive_comparison.md").write_text(render_cross_model_md(cm))

    # input integrity report (json + md)
    integrity_obj = {
        "banner": ["DEVELOPMENT CALIBRATION — NOT HOLDOUT",
                   "input integrity — validated before any performance analysis"],
        "tracked_binding": binding,
        "dev_id_set_identical_across_models": dev_set_identical,
        "common_dev_id_set": common_dev_set,
        "overall_pass": all(r["all_pass"] for r in integrity_results) and dev_set_identical,
        "per_envelope": integrity_results,
    }
    _dump_json(integrity_obj, out_dir / "input_integrity_report.json")
    (out_dir / "input_integrity_report.md").write_text(
        render_integrity_md(binding, integrity_results, dev_set_identical, common_dev_set))

    print(f"wrote reports to {out_dir}")
    print(f"overall integrity pass: {integrity_obj['overall_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
