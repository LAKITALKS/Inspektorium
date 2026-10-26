"""Phase 5.05c — multi-annotator response import + agreement analysis.

Deterministic, offline, stdlib-only. Parses the strongly anonymized blind response
sheets (annotators A/B/C), validates them, resolves the internal-only gold mapping,
and computes inter-annotator agreement statistics + a soft/serious disagreement
review queue. No live model calls. Never mutates gold labels, case YAMLs, prompts,
or historical Phase-5A metrics.

Design note — reuse, not duplication:
- The canonical 4-label taxonomy set is imported from ``disagreement_lab`` (single
  source of truth) rather than re-declared.
- ``disagreement_lab`` operates on model-run journal entries and produces forensic
  divergence narratives; it does NOT parse annotator CSV sheets nor compute Cohen's/
  Fleiss' kappa. This module is a distinct, focused analyzer for annotator sheets and
  intentionally reuses the label set + the run-id/manifest pattern from ``run_library``.

Study framing: this is a **strongly anonymized, model-assisted PROXY IAA**, not a
human IAA. Annotator ``confidence`` values are uncalibrated self-reports.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from agent_arena.disagreement_lab import _KNOWN_LABELS as KNOWN_LABELS

STUDY_TYPE = "strongly_anonymized_model_assisted_proxy_iaa"
METRIC_VERSION = "iaa_analysis/1.0"

# Response-sheet schema
RESPONSE_COLUMNS = [
    "blind_case_id", "primary_label", "secondary_label", "confidence",
    "rationale", "ambiguity_notes", "source_voice_clear", "claim_isolated",
    "evidence_matches_claim_strength", "missing_evidence_notes",
    "recommended_human_review", "freeform_notes",
]
_TERNARY = {"yes", "no", "uncertain"}
_BINARY = {"yes", "no"}
CATEGORICAL_ALLOWED = {
    "source_voice_clear": _TERNARY,
    "claim_isolated": _TERNARY,
    "evidence_matches_claim_strength": _TERNARY,
    "recommended_human_review": _BINARY,
}
LABEL_ORDER = ["solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"]

# Gate thresholds (documented framework; never the sole criterion — see propose_disposition)
STRONG_FLEISS = 0.80
MODERATE_FLEISS = 0.60


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class ResponseRow:
    blind_case_id: str
    primary_label: str = ""
    secondary_label: str = ""
    confidence: float | None = None
    rationale: str = ""
    ambiguity_notes: str = ""
    source_voice_clear: str = ""
    claim_isolated: str = ""
    evidence_matches_claim_strength: str = ""
    missing_evidence_notes: str = ""
    recommended_human_review: str = ""
    freeform_notes: str = ""

    @property
    def is_completed(self) -> bool:
        return bool(self.primary_label.strip())


@dataclass
class SheetValidation:
    annotator_id: str
    path: str
    is_blank_template: bool = False
    completed: bool = False
    n_rows: int = 0
    n_completed: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rows: list[ResponseRow] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


# ---------------------------------------------------------------------------
# A. Parser + validation
# ---------------------------------------------------------------------------
def _norm(v: str | None) -> str:
    return (v or "").strip()


def parse_response_sheet(path: str | Path) -> tuple[list[ResponseRow], list[str]]:
    """Parse a response sheet into rows. Raises no exceptions on content; header
    problems are returned as errors by ``validate_sheet``."""
    p = Path(path)
    rows: list[ResponseRow] = []
    errors: list[str] = []
    with p.open(newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        missing_cols = [c for c in RESPONSE_COLUMNS if c not in header]
        if missing_cols:
            errors.append(f"missing columns: {missing_cols}")
            return rows, errors
        for i, raw in enumerate(reader, start=2):  # row 1 = header
            conf_raw = _norm(raw.get("confidence"))
            conf: float | None = None
            if conf_raw:
                try:
                    conf = float(conf_raw)
                except ValueError:
                    conf = math.nan  # flagged in validation
            rows.append(ResponseRow(
                blind_case_id=_norm(raw.get("blind_case_id")),
                primary_label=_norm(raw.get("primary_label")).lower(),
                secondary_label=_norm(raw.get("secondary_label")).lower(),
                confidence=conf,
                rationale=_norm(raw.get("rationale")),
                ambiguity_notes=_norm(raw.get("ambiguity_notes")),
                source_voice_clear=_norm(raw.get("source_voice_clear")).lower(),
                claim_isolated=_norm(raw.get("claim_isolated")).lower(),
                evidence_matches_claim_strength=_norm(raw.get("evidence_matches_claim_strength")).lower(),
                missing_evidence_notes=_norm(raw.get("missing_evidence_notes")),
                recommended_human_review=_norm(raw.get("recommended_human_review")).lower(),
                freeform_notes=_norm(raw.get("freeform_notes")),
            ))
    return rows, errors


def _blank_secondary(v: str) -> bool:
    return v == "" or v == "none"


def validate_sheet(path: str | Path, expected_ids: set[str], annotator_id: str = "?") -> SheetValidation:
    """Validate one response sheet against the expected blind-case ids."""
    rows, header_errors = parse_response_sheet(path)
    sv = SheetValidation(annotator_id=annotator_id, path=str(path), rows=rows, n_rows=len(rows))
    sv.errors.extend(header_errors)
    if header_errors:
        return sv

    ids = [r.blind_case_id for r in rows]
    id_set = set(ids)
    # exact-set / duplicate / unknown checks
    dups = [x for x, c in Counter(ids).items() if c > 1]
    if dups:
        sv.errors.append(f"duplicate blind_case_id: {sorted(dups)}")
    unknown = sorted(id_set - expected_ids)
    if unknown:
        sv.errors.append(f"unknown blind_case_id: {unknown}")
    missing_ids = sorted(expected_ids - id_set)
    if missing_ids:
        sv.errors.append(f"missing expected blind_case_id rows: {missing_ids}")

    n_completed = sum(1 for r in rows if r.is_completed)
    sv.n_completed = n_completed
    sv.is_blank_template = (n_completed == 0 and len(rows) > 0)
    sv.completed = (n_completed == len(rows) and len(rows) > 0)

    if sv.is_blank_template:
        # Recognized as a template — not treated as completed data; no per-row errors.
        return sv

    # Per-row validation for any completed row
    for r in rows:
        if not r.is_completed:
            if not sv.completed:
                sv.warnings.append(f"{r.blind_case_id}: row not completed (no primary_label)")
            continue
        if r.primary_label not in KNOWN_LABELS:
            sv.errors.append(f"{r.blind_case_id}: invalid primary_label '{r.primary_label}'")
        if not _blank_secondary(r.secondary_label) and r.secondary_label not in KNOWN_LABELS:
            sv.errors.append(f"{r.blind_case_id}: invalid secondary_label '{r.secondary_label}'")
        if not _blank_secondary(r.secondary_label) and r.secondary_label == r.primary_label:
            sv.errors.append(f"{r.blind_case_id}: primary_label equals secondary_label")
        if r.confidence is None:
            sv.errors.append(f"{r.blind_case_id}: missing confidence")
        elif r.confidence != r.confidence:  # NaN
            sv.errors.append(f"{r.blind_case_id}: non-numeric confidence")
        elif not (0.0 <= r.confidence <= 1.0):
            sv.errors.append(f"{r.blind_case_id}: confidence out of range [0,1]: {r.confidence}")
        for fieldname, allowed in CATEGORICAL_ALLOWED.items():
            val = getattr(r, fieldname)
            if val and val not in allowed:
                sv.errors.append(f"{r.blind_case_id}: {fieldname}='{val}' not in {sorted(allowed)}")
            if not val:
                sv.warnings.append(f"{r.blind_case_id}: {fieldname} not filled")
        if not r.rationale:
            sv.warnings.append(f"{r.blind_case_id}: rationale missing (completeness)")
    return sv


# ---------------------------------------------------------------------------
# B. Internal gold mapping (never written to annotator-facing paths)
# ---------------------------------------------------------------------------
ANNOTATOR_FACING_MARKER = "annotator_facing"


def load_expected_ids(index_path: str | Path) -> set[str]:
    """Expected in-study blind ids = rows with included_in_iaa_stats == 'yes'."""
    out = set()
    with Path(index_path).open(newline="") as f:
        for row in csv.DictReader(f):
            if _norm(row.get("included_in_iaa_stats")).lower() == "yes":
                out.add(_norm(row.get("blind_case_id")))
    return out


def load_gold_mapping(index_path: str | Path, tasks_dir: str | Path) -> dict[str, dict]:
    """Resolve blind_case_id -> {real_case_id, gold_label} from the internal index
    and the case YAML files. INTERNAL ONLY — the returned mapping must never be
    written under an ``annotator_facing`` path."""
    import yaml  # local import; pyyaml is a project dependency

    tasks = Path(tasks_dir)
    mapping: dict[str, dict] = {}
    with Path(index_path).open(newline="") as f:
        for row in csv.DictReader(f):
            if _norm(row.get("included_in_iaa_stats")).lower() != "yes":
                continue
            bid = _norm(row.get("blind_case_id"))
            filename = _norm(row.get("filename"))
            gold = ""
            fp = tasks / filename
            if fp.exists():
                data = yaml.safe_load(fp.read_text())
                gold = _norm(data.get("gold_label")).lower()
            mapping[bid] = {"real_case_id": _norm(row.get("real_case_id")), "gold_label": gold}
    return mapping


def _assert_internal_path(out_dir: str | Path) -> None:
    if ANNOTATOR_FACING_MARKER in Path(out_dir).parts:
        raise ValueError(
            f"refusing to write internal gold-linked results under an annotator-facing path: {out_dir}"
        )


# ---------------------------------------------------------------------------
# C. Agreement metrics (deterministic)
# ---------------------------------------------------------------------------
def raw_agreement(a: list[str], b: list[str]) -> float:
    if not a:
        return float("nan")
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


def all_agree_rate(labels_by_rater: list[list[str]]) -> float:
    if not labels_by_rater or not labels_by_rater[0]:
        return float("nan")
    n = len(labels_by_rater[0])
    agree = sum(1 for i in range(n) if len({r[i] for r in labels_by_rater}) == 1)
    return agree / n


def cohen_kappa(a: list[str], b: list[str], categories: list[str] | None = None) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    cats = categories or sorted(set(a) | set(b))
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca.get(c, 0) / n) * (cb.get(c, 0) / n) for c in cats)
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else 0.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(label_rows: list[list[str]], categories: list[str] | None = None) -> float:
    """Fleiss' kappa over items × raters (complete data, fixed rater count).

    ``label_rows``: one list of rater labels per item (all same length = n_raters).
    Chosen over Krippendorff's alpha because the study is a fixed 3-rater, complete-
    data design, which Fleiss handles exactly with stdlib only (no new dependency).
    If variable rater counts / missing data become common, switch to Krippendorff's
    alpha (documented trade-off).
    """
    items = [r for r in label_rows if r]
    N = len(items)
    if N == 0:
        return float("nan")
    n = len(items[0])
    if any(len(r) != n for r in items) or n < 2:
        return float("nan")
    cats = categories or sorted({lbl for r in items for lbl in r})
    # n_ij: count of raters assigning category j to item i
    counts = [[Counter(r).get(c, 0) for c in cats] for r in items]
    p_j = [sum(counts[i][j] for i in range(N)) / (N * n) for j in range(len(cats))]
    P_i = [(sum(c * c for c in counts[i]) - n) / (n * (n - 1)) for i in range(N)]
    P_bar = sum(P_i) / N
    P_e = sum(pj * pj for pj in p_j)
    if P_e >= 1.0:
        return 1.0 if P_bar >= 1.0 else 0.0
    return (P_bar - P_e) / (1 - P_e)


def per_label_agreement(annotator: list[str], gold: list[str]) -> dict[str, dict]:
    """Annotator-vs-gold reproduction by label. NOT model benchmark accuracy:
    ``gold_reproduction_rate`` = recall-like (of gold-L items, how many the annotator
    also called L); ``annotator_label_purity`` = precision-like (of annotator-L calls,
    how many were gold L)."""
    out: dict[str, dict] = {}
    for lbl in LABEL_ORDER:
        gold_l = [i for i, g in enumerate(gold) if g == lbl]
        ann_l = [i for i, a in enumerate(annotator) if a == lbl]
        exact = sum(1 for i in gold_l if annotator[i] == lbl)
        out[lbl] = {
            "gold_count": len(gold_l),
            "annotator_count": len(ann_l),
            "exact_match_count": exact,
            "gold_reproduction_rate": (exact / len(gold_l)) if gold_l else float("nan"),
            "annotator_label_purity": (exact / len(ann_l)) if ann_l else float("nan"),
        }
    return out


def disagreement_matrix(a: list[str], b: list[str], categories: list[str] | None = None) -> dict:
    cats = categories or LABEL_ORDER
    m = {ra: {cb: 0 for cb in cats} for ra in cats}
    for x, y in zip(a, b):
        if x in m and y in m[x]:
            m[x][y] += 1
    return {"categories": cats, "matrix": m}


# ---------------------------------------------------------------------------
# C.6 Soft vs serious disagreement (never mutates gold)
# ---------------------------------------------------------------------------
def classify_disagreements(
    rows: list[ResponseRow],
    gold_map: dict[str, dict],
    alt_reading_labels: dict[str, set[str]] | None = None,
) -> dict[str, list[dict]]:
    """Split annotator disagreements into soft vs serious. Deterministic; does NOT
    change any gold label — it only produces a review queue.

    soft   = primary != gold AND (gold == secondary_label OR primary in documented
             alternative-reading labels for that case).
    serious= primary != gold AND gold != secondary AND primary not in alt labels.
    """
    alt = alt_reading_labels or {}
    soft: list[dict] = []
    serious: list[dict] = []
    for r in rows:
        if not r.is_completed:
            continue
        gold = gold_map.get(r.blind_case_id, {}).get("gold_label", "")
        if not gold or r.primary_label == gold:
            continue
        gold_is_secondary = (r.secondary_label == gold and not _blank_secondary(r.secondary_label))
        primary_in_alt = r.primary_label in alt.get(r.blind_case_id, set())
        rec = {
            "blind_case_id": r.blind_case_id,
            "annotator_primary": r.primary_label,
            "annotator_secondary": r.secondary_label,
            "gold_label": gold,
            "confidence": r.confidence,
        }
        if gold_is_secondary or primary_in_alt:
            rec["soft_reason"] = "gold==secondary" if gold_is_secondary else "primary in documented alternative"
            soft.append(rec)
        else:
            serious.append(rec)
    return {"soft": soft, "serious": serious}


# ---------------------------------------------------------------------------
# C.7 Confidence + ambiguity (uncalibrated self-report)
# ---------------------------------------------------------------------------
def _median(xs: list[float]) -> float:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return float("nan")
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def confidence_ambiguity_analysis(rows: list[ResponseRow], gold_map: dict[str, dict]) -> dict:
    completed = [r for r in rows if r.is_completed]
    correct = [r for r in completed if r.primary_label == gold_map.get(r.blind_case_id, {}).get("gold_label", "")]
    disagree = [r for r in completed if r not in correct]

    def conf(rs):
        vals = [r.confidence for r in rs if isinstance(r.confidence, float) and r.confidence == r.confidence]
        return {"mean": (sum(vals) / len(vals)) if vals else float("nan"),
                "median": _median(vals), "n": len(vals)}

    by_label: dict[str, dict] = {}
    for lbl in LABEL_ORDER:
        rs = [r for r in completed if r.primary_label == lbl]
        by_label[lbl] = conf(rs)

    n = len(completed) or 1
    return {
        "note": "confidence values are uncalibrated self-reports, NOT calibrated probabilities",
        "confidence_when_matches_gold": conf(correct),
        "confidence_when_disagrees_gold": conf(disagree),
        "confidence_by_label": by_label,
        "human_review_recommendation_rate": sum(1 for r in completed if r.recommended_human_review == "yes") / n,
        "ambiguity_note_presence_rate": sum(1 for r in completed if r.ambiguity_notes) / n,
        "source_voice_uncertain_rate": sum(1 for r in completed if r.source_voice_clear == "uncertain") / n,
        "claim_isolated_uncertain_rate": sum(1 for r in completed if r.claim_isolated == "uncertain") / n,
    }


# ---------------------------------------------------------------------------
# G. Gate disposition (documented framework; requires data)
# ---------------------------------------------------------------------------
def propose_disposition(metrics: dict) -> dict:
    """Multi-signal disposition. Never a single statistic as sole criterion.
    Requires computed metrics; callers must not invoke on blank/partial data."""
    fleiss = metrics.get("multi_rater", {}).get("fleiss_kappa")
    pairwise = list(metrics.get("pairwise_kappa", {}).values())
    serious = metrics.get("serious_disagreement_count", 0)
    raw = metrics.get("raw_agreement_all_three")
    signals = {
        "fleiss_kappa": fleiss,
        "min_pairwise_kappa": min(pairwise) if pairwise else None,
        "raw_all_three": raw,
        "serious_disagreement_count": serious,
    }
    if fleiss is None:
        return {"level": "UNDETERMINED", "signals": signals,
                "rationale": "no multi-rater statistic available (incomplete data)"}
    strong = fleiss >= STRONG_FLEISS and (not pairwise or min(pairwise) >= MODERATE_FLEISS) and serious == 0
    moderate = fleiss >= MODERATE_FLEISS
    level = "STRONG" if strong else ("MODERATE" if moderate else "WEAK")
    return {
        "level": level,
        "signals": signals,
        "rationale": ("consider multi-rater + pairwise kappas + raw agreement + serious "
                      "disagreement count + per-label/borderline concentration together; "
                      "this is a proxy-IAA gate, not a benchmark-validity claim"),
    }


# ---------------------------------------------------------------------------
# D/E. Orchestration + artifacts + manifest
# ---------------------------------------------------------------------------
def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def build_input_manifest(sheet_paths: dict[str, str], expected_count: int,
                         validations: dict[str, SheetValidation], used_gold: bool) -> dict:
    missing = sum(max(0, expected_count - v.n_completed) for v in validations.values())
    warnings = {aid: v.warnings for aid, v in validations.items() if v.warnings}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_tag": _git("describe", "--tags"),
        "study_type": STUDY_TYPE,
        "metric_version": METRIC_VERSION,
        "expected_blind_case_count": expected_count,
        "annotators": sorted(sheet_paths.keys()),  # identifiers only (A/B/C)
        "inputs": {aid: {"filename": Path(p).name, "sha256": _sha256(Path(p))}
                   for aid, p in sheet_paths.items()},
        "missing_response_count": missing,
        "validation_warnings": warnings,
        "gold_mapping_used": used_gold,
    }


def analyze(
    sheet_paths: dict[str, str],
    index_path: str | Path,
    tasks_dir: str | Path,
    out_dir: str | Path,
    allow_partial: bool = False,
    alt_reading_labels: dict[str, set[str]] | None = None,
) -> dict:
    """Full analysis path. Refuses final analysis on incomplete data unless
    ``allow_partial=True`` (which produces a STRUCTURE-VALIDATION-ONLY output with no
    gate disposition). Writes artifacts under ``out_dir`` (must be internal-only).
    """
    _assert_internal_path(out_dir)
    expected = load_expected_ids(index_path)
    validations = {aid: validate_sheet(p, expected, aid) for aid, p in sheet_paths.items()}
    all_completed = all(v.completed and v.ok for v in validations.values())

    out = Path(out_dir)

    if not all_completed:
        if not allow_partial:
            # Refuse: do not create an output dir or any artifacts from incomplete data.
            return {
                "status": "REFUSED",
                "reason": "final analysis requires all sheets completed and valid; "
                          "pass allow_partial=True for a structure-validation-only report",
                "validations": {aid: {"errors": v.errors, "completed": v.completed,
                                       "is_blank_template": v.is_blank_template,
                                       "n_completed": v.n_completed} for aid, v in validations.items()},
            }
        # partial / structure-validation-only
        out.mkdir(parents=True, exist_ok=True)
        banner = "STRUCTURE VALIDATION ONLY — NO ANNOTATOR RESULTS."
        report = [f"# IAA Structure Validation\n", f"> **{banner}**\n"]
        for aid, v in validations.items():
            report.append(f"## Annotator {aid}\n")
            report.append(f"- path: `{Path(v.path).name}`")
            report.append(f"- blank_template: {v.is_blank_template} · completed: {v.completed} · "
                          f"rows: {v.n_rows} · completed_rows: {v.n_completed}")
            report.append(f"- errors: {v.errors or 'none'}")
            report.append(f"- warnings: {len(v.warnings)}\n")
        (out / "response_validation_report.md").write_text("\n".join(report))
        manifest = build_input_manifest(sheet_paths, len(expected), validations, used_gold=False)
        manifest["mode"] = "structure_validation_only"
        (out / "input_manifest.json").write_text(json.dumps(manifest, indent=2))
        return {"status": "STRUCTURE_VALIDATION_ONLY", "banner": banner,
                "validations": validations, "out_dir": str(out)}

    # --- completed data: compute metrics ---
    out.mkdir(parents=True, exist_ok=True)
    gold_map = load_gold_mapping(index_path, tasks_dir)
    aids = sorted(sheet_paths.keys())
    rows_by = {aid: {r.blind_case_id: r for r in validations[aid].rows} for aid in aids}
    order = sorted(expected)
    labels = {aid: [rows_by[aid][b].primary_label for b in order] for aid in aids}
    gold = [gold_map.get(b, {}).get("gold_label", "") for b in order]

    pairwise_kappa: dict[str, float] = {}
    pairwise_raw: dict[str, float] = {}
    for i in range(len(aids)):
        for j in range(i + 1, len(aids)):
            k = f"{aids[i]}_vs_{aids[j]}"
            pairwise_kappa[k] = cohen_kappa(labels[aids[i]], labels[aids[j]], LABEL_ORDER)
            pairwise_raw[k] = raw_agreement(labels[aids[i]], labels[aids[j]])
    for aid in aids:
        pairwise_kappa[f"{aid}_vs_gold"] = cohen_kappa(labels[aid], gold, LABEL_ORDER)
        pairwise_raw[f"{aid}_vs_gold"] = raw_agreement(labels[aid], gold)

    fleiss = fleiss_kappa([[labels[aid][i] for aid in aids] for i in range(len(order))], LABEL_ORDER)
    disagreements = {aid: classify_disagreements(validations[aid].rows, gold_map, alt_reading_labels) for aid in aids}
    serious_count = sum(len(d["serious"]) for d in disagreements.values())

    metrics = {
        "run_id": out.name,
        "study_type": STUDY_TYPE,
        "n_items": len(order),
        "annotators": aids,
        "raw_agreement_pairwise": pairwise_raw,
        "raw_agreement_all_three": all_agree_rate([labels[aid] for aid in aids]),
        "pairwise_kappa": pairwise_kappa,
        "multi_rater": {"statistic": "fleiss_kappa", "fleiss_kappa": fleiss,
                        "note": "Fleiss chosen for fixed 3-rater complete data; Krippendorff alpha "
                                "is the documented alternative for missing/variable-rater data"},
        "per_label_agreement": {aid: per_label_agreement(labels[aid], gold) for aid in aids},
        "serious_disagreement_count": serious_count,
        "soft_disagreement_count": sum(len(d["soft"]) for d in disagreements.values()),
        "confidence_ambiguity": {aid: confidence_ambiguity_analysis(validations[aid].rows, gold_map) for aid in aids},
    }
    metrics["disposition"] = propose_disposition(metrics)

    manifest = build_input_manifest(sheet_paths, len(expected), validations, used_gold=True)
    (out / "input_manifest.json").write_text(json.dumps(manifest, indent=2))
    (out / "iaa_summary.json").write_text(json.dumps(metrics, indent=2, default=str))
    (out / "iaa_summary.md").write_text(render_summary_md(metrics))
    return {"status": "COMPLETE", "metrics": metrics, "disagreements": disagreements, "out_dir": str(out)}


def render_summary_md(m: dict) -> str:
    d = m["disposition"]
    lines = [
        f"# IAA Summary — `{m['run_id']}`\n",
        f"**Study type:** {m['study_type']} — a model-assisted PROXY IAA, **not** human IAA.  ",
        f"**Items:** {m['n_items']} · **Annotators:** {', '.join(m['annotators'])}\n",
        f"**Proposed disposition:** {d['level']}  ",
        f"> {d['rationale']}\n",
        "## Multi-rater",
        f"- Fleiss' kappa: {m['multi_rater']['fleiss_kappa']}",
        f"- All-three exact agreement: {m['raw_agreement_all_three']}\n",
        "## Pairwise Cohen's kappa",
    ]
    for k, v in m["pairwise_kappa"].items():
        lines.append(f"- {k}: {v}")
    lines.append(f"\n## Disagreements\n- soft: {m['soft_disagreement_count']} · serious: {m['serious_disagreement_count']}")
    lines.append("\n*Confidence values are uncalibrated self-reports. No gold label is changed by this analysis; "
                 "disagreements route to a curator review queue only.*")
    return "\n".join(lines)
