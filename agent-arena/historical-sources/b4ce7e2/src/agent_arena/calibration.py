"""Deterministic, offline calibration & abstention analysis engine (Phase 6.2 prep).

Implements the frozen Phase 6.1 protocol
(`analysis/phase6_1_confidence_protocol/`) over an **anonymized result envelope**
whose records use opaque development ids (e.g. ``DEV-0001``) and carry no canonical
case identity. Everything here is pure/deterministic and makes **no model calls**.

Frozen choices honored (never re-tuned here):
- **Brier** (binary top-label correctness) is the primary probabilistic score;
- **five** fixed equal-width reliability bins are primary; a **ten**-bin view is a
  sensitivity report only; empty bins are always retained; confidence ``1.0`` is in
  the last bin;
- **ECE** is secondary/descriptive, denominator = VALID-confidence count;
- confidence validity is VALID / MISSING / INVALID — never silently coerced to 0.0;
- ordinary classification accuracy uses ALL records (valid labels) regardless of
  confidence validity; Brier/reliability/ECE use only VALID-confidence records;
- strata (clear / borderline / development_only) are reported separately;
- all four labels stay visible; per-label figures require ``n >= 5``;
  correlation/mechanism (n = 2) are descriptive only;
- abstention is a **costed** trade-off; optimizing a threshold on the same result
  set is prohibited (encoded in code).

Validated with SYNTHETIC fixtures only; it does not fabricate or imply real Agent
Arena performance. The gold aggregate 8/15/2/2 is the pool's GOLD-label composition;
predicted-label distribution is reported descriptively and is never constrained.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean

from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence
from agent_arena.dev_manifest import FROZEN_AGGREGATE, GOLD_LABELS

# ---------------------------------------------------------------------------
# Frozen parameters (pre-registered; not tunable here)
# ---------------------------------------------------------------------------

LABELS = tuple(GOLD_LABELS)
STRATA = ("clear", "borderline", "development_only")
FIVE_BIN_EDGES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
TEN_BIN_EDGES = tuple(round(i / 10, 1) for i in range(11))
TAU_GRID = tuple(round(i / 10, 1) for i in range(11))
MIN_LABEL_N = 5
EXPECTED_TOTAL = FROZEN_AGGREGATE["total"]           # 27
EXPECTED_LABEL_COUNTS = {k: FROZEN_AGGREGATE[k] for k in LABELS}

PROTOCOL_VERSION = "6.1"
ENVELOPE_VERSION = "6.2.0"
EXPECTED_MANIFEST_ID = "AA-DEVPOOL-6100"
ABSTENTION_COST_MODEL = "coverage_lost_all = 1 - coverage_all (fixed; no tunable cost ratio)"
PUBLIC_MANIFEST_RELPATH = (
    "analysis/phase6_1_confidence_protocol/development_pool_public_manifest.json"
)
REPORT_STATUS_BANNER = (
    "DEVELOPMENT CALIBRATION — NOT HOLDOUT",
    "descriptive small-sample analysis",
    "not evidence of universal superiority",
    "no threshold was optimized on the reported data",
)

ENVELOPE_REQUIRED = (
    "envelope_version", "protocol_version", "manifest_id", "public_commitment",
    "run_id", "model", "provider", "prompt_contract_version", "generated_at",
    "expected_record_count", "declared_gold_aggregate", "records",
)

_DEV_ID_RE = re.compile(r"^DEV-[0-9]{3,}$")
_COMMITMENT_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_CANONICAL_ID_RE = re.compile(r"^study-forensics-[0-9]+$")


class CalibrationError(ValueError):
    """Raised for prohibited operations (e.g. threshold optimization on the eval set)."""


# ---------------------------------------------------------------------------
# Result records + validation
# ---------------------------------------------------------------------------

@dataclass
class ResultRecord:
    dev_id: str
    model: str
    predicted_label: str
    gold_label: str
    stratum: str
    confidence_raw: object
    validity: str = ""
    confidence: float | None = None      # float iff VALID
    correct: int = 0                     # 1 iff predicted == gold

    def finalize(self) -> "ResultRecord":
        self.validity = classify_confidence(self.confidence_raw)
        self.confidence = float(self.confidence_raw) if self.validity == VALID else None
        self.correct = 1 if self.predicted_label == self.gold_label else 0
        return self


@dataclass
class ValidationResult:
    records: list[ResultRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_result_records(raw: list[dict], enforce_aggregate: bool = True) -> ValidationResult:
    """Validate anonymized result records. Messages are structural (index/opaque id).

    The frozen 8/15/2/2 aggregate is checked on **gold_label only**; predicted labels
    are validated to be in the vocabulary but are NEVER constrained to any
    distribution. Missing/invalid confidence is classified (MISSING/INVALID), never
    coerced to 0.0.
    """
    result = ValidationResult()
    seen: set[tuple[str, str]] = set()
    per_model_gold: dict[str, dict[str, int]] = {}
    per_model_count: dict[str, int] = {}

    for i, rec in enumerate(raw):
        if not isinstance(rec, dict):
            result.errors.append(f"record[{i}] must be an object")
            continue
        dev_id = rec.get("dev_id", "")
        model = rec.get("model", "")
        pred = rec.get("predicted_label", "")
        gold = rec.get("gold_label", "")
        stratum = rec.get("stratum", "")
        missing_conf_key = "confidence" not in rec
        conf_raw = None if missing_conf_key else rec.get("confidence")

        if not isinstance(dev_id, str) or not _DEV_ID_RE.match(dev_id):
            result.errors.append(f"record[{i}].dev_id must match ^DEV-[0-9]{{3,}}$ (opaque)")
        if not isinstance(model, str) or not model:
            result.errors.append(f"record[{i}].model must be a non-empty string")
        key = (model, dev_id)
        if key in seen:
            result.errors.append(f"record[{i}] duplicate (model, dev_id)")
        else:
            seen.add(key)
        if pred not in LABELS:
            result.errors.append(f"record[{i}].predicted_label is malformed")
        if gold not in LABELS:
            result.errors.append(f"record[{i}].gold_label is malformed")
        if stratum not in STRATA:
            result.errors.append(f"record[{i}].stratum is unknown")

        # optional explicit correctness must be 0/1 and consistent with predicted==gold
        if "correct" in rec:
            c = rec["correct"]
            if isinstance(c, bool) or c not in (0, 1):
                result.errors.append(f"record[{i}].correct must be 0 or 1")
            elif pred in LABELS and gold in LABELS and c != (1 if pred == gold else 0):
                result.errors.append(f"record[{i}].correct is inconsistent with predicted vs gold")

        # confidence validity (never coerced): flag only genuinely out-of-contract values
        if not missing_conf_key and classify_confidence(conf_raw) == INVALID:
            result.errors.append(
                f"record[{i}].confidence is invalid (non-numeric/boolean/out-of-range)")

        if isinstance(model, str) and model and gold in LABELS:
            per_model_gold.setdefault(model, {lbl: 0 for lbl in LABELS})[gold] += 1
            per_model_count[model] = per_model_count.get(model, 0) + 1

        result.records.append(ResultRecord(
            dev_id=dev_id, model=model, predicted_label=pred, gold_label=gold,
            stratum=stratum, confidence_raw=conf_raw,
        ).finalize())

    if enforce_aggregate:
        for model, count in sorted(per_model_count.items()):
            if count != EXPECTED_TOTAL:
                result.errors.append(
                    f"model {model!r}: {count} records != frozen expected total {EXPECTED_TOTAL}")
            gold_counts = per_model_gold.get(model, {})
            for lbl in LABELS:
                if gold_counts.get(lbl, 0) != EXPECTED_LABEL_COUNTS[lbl]:
                    result.errors.append(
                        f"model {model!r}: gold {lbl} count {gold_counts.get(lbl, 0)} "
                        f"!= frozen {EXPECTED_LABEL_COUNTS[lbl]}")
    return result


# ---------------------------------------------------------------------------
# Anonymized result envelope (binds records to the frozen pool without identities)
# ---------------------------------------------------------------------------

def _iter_strings(obj: object):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k)
            yield from _iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _iter_strings(v)
    elif isinstance(obj, str):
        yield obj


def load_public_manifest_binding(repo_root: str | Path | None = None) -> tuple[str, str]:
    """Read the tracked public manifest → (manifest_id, public_commitment)."""
    root = Path(repo_root).resolve() if repo_root is not None else Path(__file__).resolve().parents[2]
    data = json.loads((root / PUBLIC_MANIFEST_RELPATH).read_text())
    return data.get("manifest_id"), data.get("commitment")


def validate_result_envelope(
    envelope: dict, expected_manifest_id: str, expected_commitment: str,
    enforce_aggregate: bool = True,
) -> ValidationResult:
    """Validate that the envelope is bound to the exact tracked manifest + commitment.

    The offline analyzer verifies the envelope references the exact tracked
    ``manifest_id`` and public salted ``commitment`` (string equality — the salt is
    never needed or present) before accepting any records. Canonical/BIAA/HLD ids and
    salt are rejected anywhere in the envelope.
    """
    result = ValidationResult()
    if not isinstance(envelope, dict):
        result.errors.append("envelope must be an object")
        return result

    # forbidden content anywhere (identities / salt must not appear)
    for s in _iter_strings(envelope):
        if _CANONICAL_ID_RE.match(s):
            result.errors.append("canonical id present in envelope")
        if re.search(r"\bBIAA-[0-9]+", s, re.IGNORECASE):
            result.errors.append("BIAA id present in envelope")
        if re.search(r"\bHLD-[0-9]+", s, re.IGNORECASE):
            result.errors.append("HLD id present in envelope")
    for k in _iter_strings({kk: "" for kk in envelope}):
        if k.lower() in ("salt", "salt_hex", "private_manifest", "canonical_id"):
            result.errors.append(f"forbidden envelope field: {k}")

    for k in ENVELOPE_REQUIRED:
        if k not in envelope:
            result.errors.append(f"envelope missing required field: {k}")

    if envelope.get("manifest_id") != expected_manifest_id:
        result.errors.append("envelope manifest_id does not match the tracked manifest id")
    cv = envelope.get("public_commitment")
    if not (isinstance(cv, str) and _COMMITMENT_HEX_RE.match(cv)):
        result.errors.append("envelope public_commitment must be a 64-hex digest")
    elif cv != expected_commitment:
        result.errors.append("envelope public_commitment does not match the tracked commitment")
    if envelope.get("protocol_version") != PROTOCOL_VERSION:
        result.errors.append(f"envelope protocol_version must be {PROTOCOL_VERSION!r}")
    if envelope.get("expected_record_count") != EXPECTED_TOTAL:
        result.errors.append(f"envelope expected_record_count must be {EXPECTED_TOTAL}")
    if envelope.get("declared_gold_aggregate") != FROZEN_AGGREGATE:
        result.errors.append("envelope declared_gold_aggregate must equal the frozen 8/15/2/2 aggregate")

    records = envelope.get("records")
    if not isinstance(records, list):
        result.errors.append("envelope.records must be a list")
        return result
    if len(records) != EXPECTED_TOTAL:
        result.errors.append(f"envelope has {len(records)} records != expected {EXPECTED_TOTAL}")

    rec_val = validate_result_records(records, enforce_aggregate=enforce_aggregate)
    result.errors.extend(rec_val.errors)
    result.records = rec_val.records
    result.provenance = {
        "envelope_version": envelope.get("envelope_version"),
        "protocol_version": envelope.get("protocol_version"),
        "manifest_id": envelope.get("manifest_id"),
        "public_commitment": envelope.get("public_commitment"),
        "run_id": envelope.get("run_id"),
        "model": envelope.get("model"),
        "provider": envelope.get("provider"),
        "prompt_contract_version": envelope.get("prompt_contract_version"),
        "generated_at": envelope.get("generated_at"),
    }
    return result


# ---------------------------------------------------------------------------
# Confidence audit
# ---------------------------------------------------------------------------

def confidence_audit(records: list[ResultRecord]) -> dict:
    n_valid = sum(1 for r in records if r.validity == VALID)
    n_missing = sum(1 for r in records if r.validity == MISSING)
    n_invalid = sum(1 for r in records if r.validity == INVALID)
    return {"n_total": len(records), "n_valid": n_valid,
            "n_missing": n_missing, "n_invalid": n_invalid,
            "n_excluded": n_missing + n_invalid}


# ---------------------------------------------------------------------------
# Primary score + reliability + ECE
# ---------------------------------------------------------------------------

def _valid(records: list[ResultRecord]) -> list[ResultRecord]:
    return [r for r in records if r.validity == VALID]


def brier_top_label(records: list[ResultRecord]) -> float | None:
    """Primary metric: binary top-label Brier over VALID records. None if no valid."""
    v = _valid(records)
    if not v:
        return None
    return mean((r.confidence - r.correct) ** 2 for r in v)


def _bin_index(conf: float, edges: tuple) -> int:
    for i in range(len(edges) - 1):
        last = i == len(edges) - 2
        if (edges[i] <= conf < edges[i + 1]) or (last and conf == edges[i + 1]):
            return i
    return len(edges) - 2  # defensive; VALID conf is within [0,1]


def reliability_table(records: list[ResultRecord], edges: tuple = FIVE_BIN_EDGES) -> list[dict]:
    """Per-bin table; ALL bins retained (empty bins kept explicitly visible)."""
    v = _valid(records)
    buckets: list[list[ResultRecord]] = [[] for _ in range(len(edges) - 1)]
    for r in v:
        buckets[_bin_index(r.confidence, edges)].append(r)
    table = []
    for i, members in enumerate(buckets):
        n = len(members)
        if n:
            mc = mean(r.confidence for r in members)
            acc = mean(r.correct for r in members)
            gap = abs(acc - mc)
        else:
            mc = acc = gap = None
        table.append({
            "index": i, "low": edges[i], "high": edges[i + 1], "n": n,
            "mean_confidence": mc, "accuracy": acc, "abs_gap": gap,
            "underpowered": n < MIN_LABEL_N,
        })
    return table


def ece_from_table(table: list[dict], n_valid: int) -> float | None:
    """Secondary/descriptive ECE; denominator = number of VALID-confidence records."""
    if n_valid == 0:
        return None
    return sum((b["n"] / n_valid) * b["abs_gap"] for b in table if b["n"] > 0)


def assert_reliability_bins_complete(table: list[dict], edges: tuple = FIVE_BIN_EDGES) -> list[str]:
    """Guard: a reliability report must retain every bin (including empty ones)."""
    errors = []
    if len(table) != len(edges) - 1:
        errors.append(f"reliability table must retain all {len(edges) - 1} bins, got {len(table)}")
    return errors


# ---------------------------------------------------------------------------
# Coverage / selective accuracy / abstention (costed)
# ---------------------------------------------------------------------------

def risk_coverage_curve(records: list[ResultRecord], tau_grid: tuple = TAU_GRID) -> list[dict]:
    """Costed abstention curve over the FIXED tau grid.

    ``coverage_all`` uses ALL records (involuntary MISSING/INVALID abstentions in the
    denominator, per abstention_policy §1); ``coverage_valid`` uses VALID-only (per
    protocol §8 phrasing). Both are reported for transparency. Cost = coverage lost.
    """
    total = len(records)
    v = _valid(records)
    n_valid = len(v)
    n_involuntary = total - n_valid
    baseline_risk = (1 - mean(r.correct for r in v)) if v else None
    curve = []
    for tau in tau_grid:
        covered = [r for r in v if r.confidence >= tau]
        nc = len(covered)
        sel_acc = mean(r.correct for r in covered) if covered else None
        sel_risk = (1 - sel_acc) if sel_acc is not None else None
        benefit = (baseline_risk - sel_risk) if (sel_risk is not None and baseline_risk is not None) else None
        curve.append({
            "tau": tau,
            "n_covered": nc,
            "n_involuntary_abstained": n_involuntary,
            "coverage_all": (nc / total) if total else None,
            "coverage_valid": (nc / n_valid) if n_valid else None,
            "selective_accuracy": sel_acc,
            "selective_risk": sel_risk,
            "abstention_error_rate": sel_risk,
            "benefit_vs_tau0": benefit,
            "coverage_lost_all": (1 - nc / total) if total else None,
            "underpowered": nc < MIN_LABEL_N,
        })
    return curve


def select_operating_threshold(*_args, **_kwargs):
    """Prohibited: choosing an operating threshold from the same evaluation set.

    Encodes the frozen no-optimization rule (`calibration_protocol.md §14`). Any
    operating point must be pre-registered / chosen on separate data, not tuned here.
    """
    raise CalibrationError(
        "threshold optimization on the same result set is prohibited (calibration_protocol.md §14)")


# ---------------------------------------------------------------------------
# Report builder (micro + macro + strata + provenance)
# ---------------------------------------------------------------------------

def _predicted_distribution(records: list[ResultRecord]) -> dict:
    return {lbl: sum(1 for r in records if r.predicted_label == lbl) for lbl in LABELS}


def _subset_metrics(records: list[ResultRecord]) -> dict:
    v = _valid(records)
    n_all = len(records)
    n_valid = len(v)
    table5 = reliability_table(records, FIVE_BIN_EDGES)
    table10 = reliability_table(records, TEN_BIN_EDGES)
    return {
        "n": n_all,
        "n_valid": n_valid,
        "confidence_audit": confidence_audit(records),
        "confidence_valid_coverage": (n_valid / n_all) if n_all else None,
        "confidence_coverage_warning": (n_all > 0 and n_valid < n_all),
        "denominators": {"accuracy": n_all, "brier": n_valid, "ece": n_valid, "reliability": n_valid},
        "accuracy": (mean(r.correct for r in records) if records else None),   # ALL records
        "brier_top_label": brier_top_label(records),                          # VALID only (primary)
        "reliability_5bin": table5,                                           # primary
        "ece_5bin": ece_from_table(table5, n_valid),                          # secondary
        "reliability_10bin_sensitivity": table10,                            # sensitivity only
        "predicted_label_distribution": _predicted_distribution(records),    # descriptive only
        "underpowered": n_all < MIN_LABEL_N,
    }


def build_report(records: list[ResultRecord], provenance: dict | None = None,
                 synthetic: bool = False) -> dict:
    """Deterministic machine-readable calibration/abstention report per model.

    Headline metrics are on the CLEAR stratum; borderline and development_only are
    reported separately; per-label macro uses only clear labels with ``n >= 5`` and
    records exactly which labels were included/excluded and why. All four labels stay
    visible. ``provenance`` (from the validated envelope) and a status banner are
    embedded so every report is self-describing.
    """
    prov = provenance or {}
    models = sorted({r.model for r in records})
    report = {
        "tool": "phase6_2_calibration",
        "status": {
            "banner": list(REPORT_STATUS_BANNER),
            "manifest_id": prov.get("manifest_id"),
            "public_commitment": prov.get("public_commitment"),
            "protocol_version": prov.get("protocol_version") or PROTOCOL_VERSION,
            "run_id": prov.get("run_id"),
            "model": prov.get("model"),
            "provider": prov.get("provider"),
            "prompt_contract_version": prov.get("prompt_contract_version"),
            "generated_at": prov.get("generated_at"),
            "synthetic_fixture": bool(synthetic),
        },
        "params": {
            "primary_score": "binary_top_label_brier",
            "five_bin_edges": list(FIVE_BIN_EDGES),
            "ten_bin_edges": list(TEN_BIN_EDGES),
            "tau_grid": list(TAU_GRID),
            "min_label_n": MIN_LABEL_N,
            "expected_total": EXPECTED_TOTAL,
            "abstention_cost_model": ABSTENTION_COST_MODEL,
        },
        "models": {},
    }
    for model in models:
        mrecs = [r for r in records if r.model == model]
        clear = [r for r in mrecs if r.stratum == "clear"]
        borderline = [r for r in mrecs if r.stratum == "borderline"]
        devonly = [r for r in mrecs if r.stratum == "development_only"]

        per_label = {}
        for lbl in LABELS:
            lr = [r for r in clear if r.gold_label == lbl]
            per_label[lbl] = {
                "n": len(lr),
                "accuracy": (mean(r.correct for r in lr) if lr else None),
                "brier_top_label": brier_top_label(lr),
                "small_n": len(lr) < MIN_LABEL_N,
                "descriptive_only": len(lr) < MIN_LABEL_N,
            }
        included = [lbl for lbl in LABELS
                    if per_label[lbl]["n"] >= MIN_LABEL_N and per_label[lbl]["brier_top_label"] is not None]
        excluded = {lbl: (f"n<{MIN_LABEL_N}" if per_label[lbl]["n"] < MIN_LABEL_N else "no_valid_confidence")
                    for lbl in LABELS if lbl not in included}

        report["models"][model] = {
            "headline_clear": _subset_metrics(clear),
            "stratum_borderline": _subset_metrics(borderline),
            "stratum_development_only": _subset_metrics(devonly),
            "micro_all": _subset_metrics(mrecs),
            "per_label_clear": per_label,
            "macro_brier_clear": (mean(per_label[lbl]["brier_top_label"] for lbl in included)
                                  if included else None),
            "macro_included_labels": included,
            "macro_excluded_labels": excluded,
            "risk_coverage_clear": risk_coverage_curve(clear),
        }
    return report


# ---------------------------------------------------------------------------
# Human-readable rendering
# ---------------------------------------------------------------------------

def render_report_text(report: dict) -> str:
    def fmt(x):
        return "—" if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))

    s = report.get("status", {})
    lines = []
    for b in s.get("banner", []):
        lines.append(f"### {b}")
    if s.get("synthetic_fixture"):
        lines.append("### SYNTHETIC FIXTURE — not real Agent Arena performance")
    lines.append(f"manifest_id={s.get('manifest_id')}  commitment={s.get('public_commitment')}")
    lines.append(f"protocol={s.get('protocol_version')}  run_id={s.get('run_id')}  "
                 f"model={s.get('model')}  prompt_contract={s.get('prompt_contract_version')}  "
                 f"generated_at={s.get('generated_at')}")
    lines.append(f"abstention_cost_model: {report.get('params', {}).get('abstention_cost_model')}")
    lines.append("=" * 78)

    for model, m in report["models"].items():
        h = m["headline_clear"]
        ca = h["confidence_audit"]
        lines.append(f"\nmodel: {model}")
        lines.append(f"  clear n={h['n']} valid={h['n_valid']} missing={ca['n_missing']} invalid={ca['n_invalid']}")
        lines.append(f"  denominators: accuracy/n={h['denominators']['accuracy']} "
                     f"brier/ece/reliability n_valid={h['denominators']['brier']}")
        if h["confidence_coverage_warning"]:
            lines.append(f"  WARNING: confidence-valid coverage < 100% "
                         f"({fmt(h['confidence_valid_coverage'])})")
        lines.append(f"  PRIMARY Brier (top-label) = {fmt(h['brier_top_label'])}   "
                     f"ECE (secondary) = {fmt(h['ece_5bin'])}   accuracy(all) = {fmt(h['accuracy'])}")
        lines.append(f"  macro Brier (clear) = {fmt(m['macro_brier_clear'])}  "
                     f"included={m['macro_included_labels']}  excluded={m['macro_excluded_labels']}")
        lines.append(f"  predicted-label distribution (descriptive): {h['predicted_label_distribution']}")
        lines.append("  reliability (5 fixed bins; empty bins retained):")
        for b in h["reliability_5bin"]:
            flag = "  [n<5]" if b["underpowered"] and b["n"] else ("  [empty]" if b["n"] == 0 else "")
            lines.append(f"    [{b['low']:.1f},{b['high']:.1f}) n={b['n']} "
                         f"conf={fmt(b['mean_confidence'])} acc={fmt(b['accuracy'])} gap={fmt(b['abs_gap'])}{flag}")
        lines.append("  per-label (clear) — all four labels retained:")
        for lbl in LABELS:
            pl = m["per_label_clear"][lbl]
            tag = " [small_n/descriptive-only]" if pl["descriptive_only"] else ""
            lines.append(f"    {lbl}: n={pl['n']} acc={fmt(pl['accuracy'])} brier={fmt(pl['brier_top_label'])}{tag}")
        lines.append(f"  borderline n={m['stratum_borderline']['n']}  "
                     f"development_only n={m['stratum_development_only']['n']} (reported separately)")
        lines.append("  risk–coverage (costed; coverage_all includes involuntary abstentions):")
        for pt in m["risk_coverage_clear"]:
            lines.append(f"    τ={pt['tau']:.1f} cov_all={fmt(pt['coverage_all'])} "
                         f"sel_acc={fmt(pt['selective_accuracy'])} cost(cov_lost)={fmt(pt['coverage_lost_all'])} "
                         f"benefit={fmt(pt['benefit_vs_tau0'])}")
    return "\n".join(lines) + "\n"
