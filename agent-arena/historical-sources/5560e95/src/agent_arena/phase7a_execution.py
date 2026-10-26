"""Phase-7A thin execution + reporting layer (WP-4 readiness).

This module does **not** create a second execution platform. It reuses the existing case-library
harness (:func:`agent_arena.run_library.run_single` / :class:`FakeLibraryProvider`), the frozen
per-model runtime contracts (:mod:`agent_arena.runtime_contract`), and the confidence-validity /
calibration primitives. It adds only the thin Phase-7A-specific pieces that were genuinely absent:

* deterministic resolution of the **84 evaluated units** (34 independent bases + 50 clustered
  perturbation variants) into runnable :class:`~agent_arena.schemas.Task` objects with unit metadata;
* a deterministic **execution manifest** + **call plan** (840 planned analytical calls) bound by
  reproducible SHA-256 fingerprints (reusing ``runtime_contract._sha256_hex``);
* a **fail-closed pre-run fingerprint gate** (:func:`verify_pre_run`);
* replication-level result **enrichment** (unit type / base / cluster / family / fingerprints /
  confidence validity / Brier contribution) on top of the existing flat run record;
* per-model **aggregation + stability tiers** and the frozen **Boundary / Adversarial / Perturbation /
  Replication** systematic-failure computations (facts only — WP-4 does not decide results);
* per-model report families (never a pooled headline score).

**No real analytical model call is made here.** The CLI is dry-run only (fake provider). The real
Phase-7A launch is a separate, explicitly-guarded invocation documented in the readiness artifact.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from agent_arena import preflight_integrity as pi
from agent_arena import runtime_contract as rc
from agent_arena.confidence_validity import INVALID, MISSING, VALID, classify_confidence
from agent_arena.robustness_pool import (
    GOLD_LABELS,
    case_fingerprint,
    load_active_adversarial_cases,
    load_active_boundary_cases,
    load_active_neutral_cases,
    load_perturbation_variants,
    stored_fingerprint,
    stored_variant_fingerprint,
    variant_fingerprint,
)
from agent_arena.run_library import FakeLibraryProvider, run_single
from agent_arena.schemas import Task

# --- Frozen Phase-7A execution constants ------------------------------------
EXECUTION_PLAN_VERSION = "7A.1"
PRIMARY_MODEL_KEYS = ("haiku", "sonnet")
PRIMARY_MODELS = tuple(rc.MODELS[k]["exact_model_id"] for k in PRIMARY_MODEL_KEYS)
N_REPLICATIONS = 5

EXPECTED_INDEPENDENT_BASES = 34
EXPECTED_EVALUATED_UNITS = 84
EXPECTED_PERTURBATION_VARIANTS = 50
EXPECTED_PERTURBATION_CLUSTERS = 10
EXPECTED_PLANNED_CALLS = EXPECTED_EVALUATED_UNITS * N_REPLICATIONS * len(PRIMARY_MODELS)  # 840

UNIT_TYPES = ("boundary_base", "adversarial_base", "neutral_base", "perturbation_variant")

# Frozen replication stability tiers (design §5 / §19).
TIER_UNANIMOUS = "unanimous"          # 5/5
TIER_STABLE_MAJORITY = "stable_majority"  # 4/5
TIER_FRAGILE = "fragile"              # 3/5
TIER_UNSTABLE = "unstable"           # <=2 modal support / no majority
MAJORITY_FAILURE_MIN_SUPPORT = 3      # "wrong modal label >= 3/5"

_ARTIFACT_DIR = Path("analysis/phase7a_execution")
_RUNTIME_FREEZE_DIR = Path("analysis/phase6_2_runtime_freeze")
EXECUTION_MANIFEST_FILE = "phase7a_execution_manifest.json"
CALL_PLAN_FILE = "phase7a_call_plan.json"
QA_RECORD_FILE = "phase7a_qa_execution.json"
RUNTIME_CONTRACT_FILES = {
    "haiku": "phase6_2_runtime_contract_haiku.json",
    "sonnet": "phase6_2_runtime_contract_sonnet.json",
}

# Execution-provenance types (WP-4.1 §7): a real model batch is an INDEPENDENT MODEL ADJUDICATION;
# a later replay/rerender of frozen records is a DETERMINISTIC REPRODUCTION and must never be
# presented as a new independent model judgment. The fake dry run is neither (synthetic).
EXEC_TYPE_ADJUDICATION = "independent_model_adjudication"
EXEC_TYPE_REPRODUCTION = "deterministic_reproduction_existing_records"
EXEC_TYPE_DRY_RUN = "dry_run_synthetic"
EXECUTION_TYPES = (EXEC_TYPE_ADJUDICATION, EXEC_TYPE_REPRODUCTION, EXEC_TYPE_DRY_RUN)


# ---------------------------------------------------------------------------
# Deterministic canonical fingerprints (reuse the SHA-256 primitive)
# ---------------------------------------------------------------------------

def _canon(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _fp(obj: object) -> str:
    return rc._sha256_hex(_canon(obj).encode("utf-8"))


def package_fingerprint() -> str:
    """Frozen prompt/package fingerprint: binds system prompt + packet construction + parser."""
    return _fp({
        "system_prompt_sha256": rc.system_prompt_sha256(),
        "task_packet_construction_sha256": rc.task_packet_construction_sha256(),
        "parser_contract_sha256": rc.parser_contract_sha256(),
    })


def runtime_contract_fingerprint(model_key: str, repo_root: str | Path | None = None) -> str:
    """SHA-256 over the canonical per-model runtime contract (deterministic, offline)."""
    return _fp(rc.build_contract(model_key, repo_root))


# ---------------------------------------------------------------------------
# Evaluated units (84 = 34 bases + 50 variants)
# ---------------------------------------------------------------------------

@dataclass
class EvaluatedUnit:
    unit_id: str
    unit_type: str                # one of UNIT_TYPES
    gold_label: str
    unit_fingerprint: str
    base_case_id: str             # a base's own id; a variant's cluster-root id
    cluster_root_id: str | None   # variants only (== base_case_id); None for bases
    perturbation_family: str | None
    family_id: str | None         # B1/B2/B3 | A1-A8 | neutral label | perturbation family
    difficulty_tier: str | None
    competing_label: str | None
    task: Task = field(repr=False)

    def meta(self) -> dict:
        """Serializable unit metadata (no Task, no model output)."""
        return {
            "unit_id": self.unit_id,
            "unit_type": self.unit_type,
            "gold_label": self.gold_label,
            "unit_fingerprint": self.unit_fingerprint,
            "base_case_id": self.base_case_id,
            "cluster_root_id": self.cluster_root_id,
            "perturbation_family": self.perturbation_family,
            "family_id": self.family_id,
            "difficulty_tier": self.difficulty_tier,
            "competing_label": self.competing_label,
        }


def _task_from_case(case: dict) -> Task:
    return Task(**{k: v for k, v in case.items() if k != "robustness"})


def _competing(case: dict) -> str | None:
    return ((case.get("robustness") or {}).get("hypothesis_map") or {}).get(
        "most_plausible_competing_label"
    )


def resolve_evaluated_units(repo_root: str | Path | None = None) -> list[EvaluatedUnit]:
    """Deterministically resolve the 84 evaluated units. Retired cases resolve to 0 units."""
    units: list[EvaluatedUnit] = []

    for _, c in load_active_boundary_cases(repo_root):
        rob = c["robustness"]
        units.append(EvaluatedUnit(
            unit_id=c["id"], unit_type="boundary_base", gold_label=c["gold_label"],
            unit_fingerprint=stored_fingerprint(c), base_case_id=c["id"], cluster_root_id=None,
            perturbation_family=None, family_id=rob["boundary_family_id"],
            difficulty_tier=rob.get("difficulty_tier"), competing_label=_competing(c),
            task=_task_from_case(c),
        ))
    for _, c in load_active_adversarial_cases(repo_root):
        rob = c["robustness"]
        units.append(EvaluatedUnit(
            unit_id=c["id"], unit_type="adversarial_base", gold_label=c["gold_label"],
            unit_fingerprint=stored_fingerprint(c), base_case_id=c["id"], cluster_root_id=None,
            perturbation_family=None, family_id=rob["adversarial_family_id"],
            difficulty_tier=rob.get("difficulty_tier"), competing_label=_competing(c),
            task=_task_from_case(c),
        ))
    for _, c in load_active_neutral_cases(repo_root):
        rob = c["robustness"]
        units.append(EvaluatedUnit(
            unit_id=c["id"], unit_type="neutral_base", gold_label=c["gold_label"],
            unit_fingerprint=stored_fingerprint(c), base_case_id=c["id"], cluster_root_id=None,
            perturbation_family=None, family_id=rob["neutral_anchor_label"],
            difficulty_tier=rob.get("difficulty_tier"), competing_label=_competing(c),
            task=_task_from_case(c),
        ))

    # 50 perturbation variants (synthesized Tasks; prompt = perturbed_claim; gold inherited)
    for v in load_perturbation_variants(repo_root):
        if v.get("status") != "active":
            continue
        task = Task(
            id=v["variant_id"], title=f"perturbation variant {v['variant_id']}",
            domain="study_forensics", difficulty="medium", task_type="study_forensics",
            prompt=v["perturbed_claim"], gold_label=v["gold_label"], task_family=v["gold_label"],
            origin="perturbation_variant",
        )
        units.append(EvaluatedUnit(
            unit_id=v["variant_id"], unit_type="perturbation_variant", gold_label=v["gold_label"],
            unit_fingerprint=stored_variant_fingerprint(v), base_case_id=v["base_case_id"],
            cluster_root_id=v["base_case_id"], perturbation_family=v["perturbation_family"],
            family_id=v["perturbation_family"], difficulty_tier=None, competing_label=None,
            task=task,
        ))

    return units


def unit_type_breakdown(units: list[EvaluatedUnit]) -> dict:
    c = Counter(u.unit_type for u in units)
    return {t: c.get(t, 0) for t in UNIT_TYPES}


# ---------------------------------------------------------------------------
# Execution manifest + call plan (deterministic; no model output)
# ---------------------------------------------------------------------------

def scientific_manifest_fingerprint(units: list[EvaluatedUnit]) -> str:
    rows = sorted(
        (u.unit_id, u.unit_type, u.gold_label, u.unit_fingerprint,
         u.cluster_root_id or "", u.family_id or "")
        for u in units
    )
    return _fp(rows)


def build_execution_manifest(repo_root: str | Path | None = None) -> dict:
    units = resolve_evaluated_units(repo_root)
    breakdown = unit_type_breakdown(units)
    n_bases = sum(v for k, v in breakdown.items() if k != "perturbation_variant")
    clusters = sorted({u.cluster_root_id for u in units if u.unit_type == "perturbation_variant"})
    doc = {
        "execution_plan_version": EXECUTION_PLAN_VERSION,
        "phase": "7A",
        "data_class": "B",
        "model_calls": 0,
        "holdout_touched": False,
        "approved_checkpoints": {
            "boundary": "3bdabaf", "adversarial": "e9e13e3", "perturbation": "84d75d4",
        },
        "accounting": {
            "n_independent_bases": n_bases,
            "n_evaluated_units": len(units),
            "n_perturbation_variants": breakdown["perturbation_variant"],
            "n_perturbation_clusters": len(clusters),
            "unit_type_breakdown": breakdown,
            "note": ("50 perturbation variants are nested in 10 independent bases; "
                     "NEVER report 84 independent cases or 50 independent perturbation cases."),
        },
        "units": [u.meta() for u in units],
        "scientific_manifest_fingerprint": scientific_manifest_fingerprint(units),
    }
    doc["execution_manifest_fingerprint"] = _fp(
        {k: doc[k] for k in ("execution_plan_version", "accounting", "units",
                             "scientific_manifest_fingerprint")}
    )
    return doc


def build_call_plan(repo_root: str | Path | None = None) -> dict:
    units = resolve_evaluated_units(repo_root)
    rt_fps = {rc.MODELS[k]["exact_model_id"]: runtime_contract_fingerprint(k, repo_root)
              for k in PRIMARY_MODEL_KEYS}
    doc = {
        "execution_plan_version": EXECUTION_PLAN_VERSION,
        "phase": "7A",
        "model_calls": 0,
        "holdout_touched": False,
        "primary_models": list(PRIMARY_MODELS),
        "n_replications": N_REPLICATIONS,
        "package_condition": "agent_arena_package",
        "prompt_only_baseline": False,
        "n_evaluated_units": len(units),
        "planned_analytical_calls": len(units) * N_REPLICATIONS * len(PRIMARY_MODELS),
        "max_transport_retries_per_call": rc.SHARED_RUNTIME[
            "max_transport_retries_after_initial_request"],
        "max_transport_retry_exposure": (
            len(units) * N_REPLICATIONS * len(PRIMARY_MODELS)
            * rc.SHARED_RUNTIME["max_transport_retries_after_initial_request"]
        ),
        "runtime": {
            "temperature": rc.SHARED_RUNTIME["temperature"],
            "top_p": rc.SHARED_RUNTIME["top_p"],
            "seed": rc.SHARED_RUNTIME["seed"],
            "request_timeout_seconds": rc.SHARED_RUNTIME["request_timeout_seconds"],
            "semantic_or_quality_retries": rc.SHARED_RUNTIME["semantic_or_quality_retries"],
        },
        "runtime_contract_fingerprints": rt_fps,
        "package_fingerprint": package_fingerprint(),
        "scientific_manifest_fingerprint": scientific_manifest_fingerprint(units),
        "unit_ids": [u.unit_id for u in units],
    }
    doc["call_plan_fingerprint"] = _fp({k: v for k, v in doc.items()
                                        if k not in ("model_calls", "holdout_touched")})
    return doc


# ---------------------------------------------------------------------------
# Fail-closed pre-run gate (§15)
# ---------------------------------------------------------------------------

def _read_required_json(path: Path, label: str, errors: list[str]) -> dict | None:
    try:
        if not path.is_file():
            errors.append(f"required artifact missing: {label}: {path}")
            return None
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"required artifact unreadable: {label}: {type(exc).__name__}: {exc}")
        return None
    if not raw:
        errors.append(f"required artifact empty: {label}: {path}")
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"required artifact malformed: {label}: {type(exc).__name__}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"required artifact structurally invalid: {label}: expected JSON object")
        return None
    return value


def verify_pre_run(
    repo_root: str | Path | None = None,
    frozen_dir: str | Path | None = None,
    runtime_frozen_dir: str | Path | None = None,
) -> dict:
    """Recompute everything and fail closed on any drift or accounting violation. [] errors == GO."""
    errors: list[str] = []
    units = resolve_evaluated_units(repo_root)
    manifest = build_execution_manifest(repo_root)
    plan = build_call_plan(repo_root)
    breakdown = unit_type_breakdown(units)
    n_bases = sum(v for k, v in breakdown.items() if k != "perturbation_variant")
    clusters = {u.cluster_root_id for u in units if u.unit_type == "perturbation_variant"}

    # accounting
    if n_bases != EXPECTED_INDEPENDENT_BASES:
        errors.append(f"independent bases {n_bases} != {EXPECTED_INDEPENDENT_BASES}")
    if len(units) != EXPECTED_EVALUATED_UNITS:
        errors.append(f"evaluated units {len(units)} != {EXPECTED_EVALUATED_UNITS}")
    if breakdown["perturbation_variant"] != EXPECTED_PERTURBATION_VARIANTS:
        errors.append(f"variants {breakdown['perturbation_variant']} != {EXPECTED_PERTURBATION_VARIANTS}")
    if len(clusters) != EXPECTED_PERTURBATION_CLUSTERS:
        errors.append(f"clusters {len(clusters)} != {EXPECTED_PERTURBATION_CLUSTERS}")
    if breakdown["boundary_base"] != 14:
        errors.append(f"boundary bases {breakdown['boundary_base']} != 14")
    if breakdown["adversarial_base"] != 16:
        errors.append(f"adversarial bases {breakdown['adversarial_base']} != 16")
    if breakdown["neutral_base"] != 4:
        errors.append(f"neutral bases {breakdown['neutral_base']} != 4")

    # models / N / planned calls
    if list(PRIMARY_MODELS) != ["claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"]:
        errors.append(f"primary models drifted: {PRIMARY_MODELS}")
    if N_REPLICATIONS != 5:
        errors.append(f"N != 5 ({N_REPLICATIONS})")
    if plan["planned_analytical_calls"] != EXPECTED_PLANNED_CALLS:
        errors.append(f"planned calls {plan['planned_analytical_calls']} != {EXPECTED_PLANNED_CALLS}")

    # runtime contracts executable + reproduce
    for k in PRIMARY_MODEL_KEYS:
        if not rc.is_executable(rc.build_contract(k, repo_root)):
            errors.append(f"runtime contract not executable: {k}")

    # unit fingerprints reproduce (bases: case_fingerprint; variants: variant_fingerprint)
    by_id = {c["id"]: c for _, c in (load_active_boundary_cases(repo_root)
             + load_active_adversarial_cases(repo_root) + load_active_neutral_cases(repo_root))}
    for u in units:
        if u.unit_type != "perturbation_variant":
            c = by_id.get(u.unit_id)
            if c is None or u.unit_fingerprint != case_fingerprint(c):
                errors.append(f"base fingerprint drift: {u.unit_id}")
    for v in load_perturbation_variants(repo_root):
        if v.get("status") == "active" and stored_variant_fingerprint(v) != variant_fingerprint(v):
            errors.append(f"variant fingerprint drift: {v['variant_id']}")

    # isolation: no retired / Class-A / Phase-7B / holdout / client / Stacy
    for u in units:
        if not (u.unit_id.startswith("P7A-BND-") or u.unit_id.startswith("P7A-ADV-")
                or u.unit_id.startswith("P7A-NEU-") or u.unit_id.startswith("P7A-PRT-")):
            errors.append(f"foreign unit id in execution universe: {u.unit_id}")
    blob = _canon([u.meta() for u in units]).lower()
    for term in ("holdout", "lavita", "salt", "envelope", "stacy", "inspektorium", "identity_map"):
        if term in blob:
            errors.append(f"forbidden term in execution universe: {term}")

    # Required frozen artifacts: absence, unreadability, malformed/partial content,
    # or drift is always a failure.  These are the active Phase-7A manifest/call
    # plan plus the two primary-model runtime contracts referenced by that plan.
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    fdir = Path(frozen_dir).resolve() if frozen_dir else root / _ARTIFACT_DIR
    runtime_dir = (
        Path(runtime_frozen_dir).resolve()
        if runtime_frozen_dir else root / _RUNTIME_FREEZE_DIR
    )
    mpath, ppath = fdir / EXECUTION_MANIFEST_FILE, fdir / CALL_PLAN_FILE
    fm = _read_required_json(mpath, "phase7a_execution_manifest", errors)
    fpn = _read_required_json(ppath, "phase7a_call_plan", errors)
    runtime_artifacts: dict[str, dict | None] = {}
    for model_key, filename in RUNTIME_CONTRACT_FILES.items():
        runtime_artifacts[model_key] = _read_required_json(
            runtime_dir / filename, f"runtime_contract_{model_key}", errors
        )

    if fm is not None:
        if fm.get("execution_manifest_fingerprint") != manifest["execution_manifest_fingerprint"]:
            errors.append("execution manifest fingerprint differs from frozen artifact")
        if fm.get("scientific_manifest_fingerprint") != manifest["scientific_manifest_fingerprint"]:
            errors.append("scientific manifest fingerprint differs from frozen artifact")
        if fm != manifest:
            errors.append("execution manifest is partial or differs from the canonical manifest")
    if fpn is not None:
        if fpn.get("call_plan_fingerprint") != plan["call_plan_fingerprint"]:
            errors.append("call plan fingerprint differs from frozen artifact")
        if fpn.get("scientific_manifest_fingerprint") != plan["scientific_manifest_fingerprint"]:
            errors.append("call plan scientific manifest differs from the canonical plan")
        if fpn.get("runtime_contract_fingerprints") != plan["runtime_contract_fingerprints"]:
            errors.append("call plan runtime-contract fingerprints differ from canonical plan")
        if fpn != plan:
            errors.append("call plan is partial or differs from the canonical plan")

    for model_key, stored_contract in runtime_artifacts.items():
        if stored_contract is None:
            continue
        contract_errors = rc.validate_contract(stored_contract, root)
        errors.extend(
            f"stored {model_key} runtime contract invalid: {error}"
            for error in contract_errors
        )
        canonical_contract = rc.build_contract(model_key, root)
        if stored_contract != canonical_contract:
            errors.append(f"stored {model_key} runtime contract differs from canonical contract")
        model_id = rc.MODELS[model_key]["exact_model_id"]
        if _fp(stored_contract) != plan["runtime_contract_fingerprints"].get(model_id):
            errors.append(f"stored {model_key} runtime-contract fingerprint differs from call plan")

    frozen_present = all(
        artifact is not None for artifact in (fm, fpn, *runtime_artifacts.values())
    )

    return {
        "passes": not errors,
        "errors": errors,
        "frozen_artifacts_present": frozen_present,
        "n_independent_bases": n_bases,
        "n_evaluated_units": len(units),
        "n_perturbation_variants": breakdown["perturbation_variant"],
        "n_perturbation_clusters": len(clusters),
        "unit_type_breakdown": breakdown,
        "primary_models": list(PRIMARY_MODELS),
        "n_replications": N_REPLICATIONS,
        "planned_analytical_calls": plan["planned_analytical_calls"],
        "execution_manifest_fingerprint": manifest["execution_manifest_fingerprint"],
        "call_plan_fingerprint": plan["call_plan_fingerprint"],
        "package_fingerprint": plan["package_fingerprint"],
        "runtime_contract_fingerprints": plan["runtime_contract_fingerprints"],
        "required_artifacts_verified": frozen_present and not any(
            "required artifact" in error or "manifest" in error
            or "call plan" in error or "runtime contract" in error
            for error in errors
        ),
        "required_artifacts": {
            "execution_manifest": str(mpath),
            "call_plan": str(ppath),
            **{
                f"runtime_contract_{key}": str(runtime_dir / filename)
                for key, filename in RUNTIME_CONTRACT_FILES.items()
            },
        },
    }


# ---------------------------------------------------------------------------
# Execution (dry-run capable; provider supplied by caller — never a real call here)
# ---------------------------------------------------------------------------

def _brier_contribution(rec: dict) -> float | None:
    """Top-label Brier contribution for a classification- and calibration-valid record."""
    correct = rec.get("label_correct")
    if correct is None or not is_calibration_valid(rec):
        return None
    return round((float(rec["confidence"]) - (1.0 if correct else 0.0)) ** 2, 6)


def _enrich(rec: dict, unit: EvaluatedUnit, model_id: str, rt_fp: str, dry_run: bool,
            execution_type: str, *, package_fp: str | None = None) -> dict:
    out = dict(rec)
    out.update({
        "model": model_id,
        "unit_id": unit.unit_id,
        "unit_type": unit.unit_type,
        "base_case_id": unit.base_case_id,
        "cluster_root_id": unit.cluster_root_id,
        "perturbation_family": unit.perturbation_family,
        "family_id": unit.family_id,
        "gold_label": unit.gold_label,
        "unit_fingerprint": unit.unit_fingerprint,
        "runtime_contract_fingerprint": rt_fp,
        "package_fingerprint": package_fp or package_fingerprint(),
        "confidence_state": record_confidence_state(rec),
        "execution_type": execution_type,
        "dry_run": bool(dry_run),
    })
    state = analytical_state(out)
    out.update(state)
    out["brier_contribution"] = _brier_contribution(out)
    return out


def execute(units, provider_factory, models=PRIMARY_MODEL_KEYS, n=N_REPLICATIONS,
            dry_run=True, repo_root=None, execution_type: str | None = None) -> list[dict]:
    """Run each unit ``n`` times per model, returning enriched replication-level records.

    ``provider_factory(model_id)`` supplies the provider. WP-4/4.1 pass the fake provider only; a real
    Phase-7A run passes a factory building the frozen Anthropic provider (a separate, guarded
    invocation) with ``execution_type=EXEC_TYPE_ADJUDICATION``. Every record carries an
    ``execution_type`` so an independent model adjudication is never confused with a later
    deterministic reproduction of frozen records (§7). Dry runs default to the synthetic type.
    """
    if execution_type is None:
        execution_type = EXEC_TYPE_DRY_RUN if dry_run else EXEC_TYPE_ADJUDICATION
    if execution_type not in EXECUTION_TYPES:
        raise ValueError(f"execution_type must be one of {EXECUTION_TYPES}")
    records: list[dict] = []
    for model_key in models:
        model_id = rc.MODELS[model_key]["exact_model_id"] if model_key in rc.MODELS else str(model_key)
        rt_fp = runtime_contract_fingerprint(model_key, repo_root) if model_key in rc.MODELS \
            else "NON_CONTRACT_FAKE"
        provider = provider_factory(model_id)
        for u in units:
            for i in range(n):
                rec = run_single(provider, Path(f"{u.unit_id}.yaml"), u.task, i,
                                 f"phase7a_{'dryrun' if dry_run else 'run'}_{model_key}",
                                 prompt_version="study_forensics_prompt/v1-historical-phase7")
                records.append(_enrich(rec, u, model_id, rt_fp, dry_run, execution_type))
    return records


# ---------------------------------------------------------------------------
# Executable QA provenance — production and diagnostic evidence are separate
# ---------------------------------------------------------------------------

def execute_qa(pytest_args: list[str] | None = None, repo_root: str | Path | None = None,
               timeout: int = 3600) -> dict:
    """Run caller-selected diagnostic QA; never authorizes real adjudication."""
    return pi.execute_diagnostic_qa(pytest_args, repo_root, timeout)


def classify_qa(qa: dict | None) -> str:
    """Classify diagnostic/stored evidence without granting production authority."""
    return pi.classify_diagnostic_qa(qa)


def diagnostic_preflight(
    repo_root: str | Path | None = None,
    run_qa: bool = False,
    qa_record: dict | None = None,
    qa_pytest_args: list[str] | None = None,
) -> dict:
    """Offline/dry-run inspection path; its QA result is explicitly non-authorizing."""
    gate = verify_pre_run(repo_root)
    qa = execute_qa(qa_pytest_args, repo_root) if run_qa else qa_record
    qa_status = classify_qa(qa)
    diagnostic_ready = bool(gate["passes"] and qa_status == pi.QA_NON_AUTHORIZING)
    return {
        "go": diagnostic_ready,
        "production_authorizing": False,
        "gate_passes": gate["passes"],
        "gate_errors": gate["errors"],
        "qa_status": qa_status,
        "qa": qa,
        "qa_record_fingerprint": (qa or {}).get("qa_record_fingerprint"),
    }


def _production_preflight(
    repo_root: str | Path | None = None,
    *,
    qa_executor=pi.execute_canonical_qa,
    source_inspector=pi.inspect_source_state,
    gate_verifier=verify_pre_run,
) -> dict:
    """Internal test seam around the concrete production authorization sequence."""
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    source_before = source_inspector(root)
    if not source_before.get("valid"):
        return {
            "go": False,
            "production_authorizing": True,
            "gate_passes": False,
            "gate_errors": list(source_before.get("errors") or []),
            "qa_status": pi.QA_NOT_EXECUTED,
            "qa_errors": ["canonical QA not launched against invalid source state"],
            "qa": None,
            "qa_record_fingerprint": None,
            "source_binding": source_before,
            "post_qa_source": None,
        }

    gate = gate_verifier(root)
    if not gate["passes"]:
        return {
            "go": False,
            "production_authorizing": True,
            "gate_passes": False,
            "gate_errors": gate["errors"],
            "qa_status": pi.QA_NOT_EXECUTED,
            "qa_errors": ["canonical QA not launched because required artifact gate failed"],
            "qa": None,
            "qa_record_fingerprint": None,
            "source_binding": source_before,
            "post_qa_source": None,
        }

    qa = qa_executor(root, source_before)
    qa_status, qa_errors = pi.validate_canonical_qa_record(qa, source_before)
    source_after = source_inspector(root)
    source_errors = pi.compare_source_binding(source_before, source_after)
    go = bool(gate["passes"] and qa_status == pi.QA_PASSED and not source_errors)
    return {
        "go": go,
        "production_authorizing": True,
        "gate_passes": gate["passes"],
        "gate_errors": gate["errors"] + source_errors,
        "qa_status": qa_status,
        "qa_errors": qa_errors,
        "qa": qa,
        "qa_record_fingerprint": qa.get("qa_record_fingerprint"),
        "source_binding": source_before,
        "post_qa_source": source_after,
    }


def real_run_preflight(repo_root: str | Path | None = None) -> dict:
    """Run fresh, internally selected canonical QA; no caller QA controls exist."""
    return _production_preflight(repo_root)


def run_metadata(execution_type: str, repo_root: str | Path | None = None) -> dict:
    """Three-layer execution provenance (§8): model vs harness vs report/render, plus exec type."""
    if execution_type not in EXECUTION_TYPES:
        raise ValueError(f"execution_type must be one of {EXECUTION_TYPES}")
    units = resolve_evaluated_units(repo_root)
    return {
        "execution_type": execution_type,
        "reproduction_of_frozen_records": execution_type == EXEC_TYPE_REPRODUCTION,
        "layers": {
            "model_execution": {
                "models": list(PRIMARY_MODELS),
                "runtime_contract_fingerprints": {
                    rc.MODELS[k]["exact_model_id"]: runtime_contract_fingerprint(k, repo_root)
                    for k in PRIMARY_MODEL_KEYS},
            },
            "harness_execution": {
                "harness": "agent_arena.phase7a_execution",
                "execution_plan_version": EXECUTION_PLAN_VERSION,
                "package_fingerprint": package_fingerprint(),
            },
            "report_render": {
                "reporter": "agent_arena.phase7a_execution.build_phase7a_report",
                "report_contract_version": EXECUTION_PLAN_VERSION,
            },
        },
        "scientific_manifest_fingerprint": scientific_manifest_fingerprint(units),
    }


# ---------------------------------------------------------------------------
# Resume / dedup safety (§34) — no distributed infra, just the minimum guards
# ---------------------------------------------------------------------------

def replication_key(rec: dict) -> tuple[str, str, int]:
    """The unique identity of one analytical call: (model, unit_id, run_index)."""
    return (rec["model"], rec["unit_id"], int(rec.get("run_index", 0)))


def record_confidence_state(rec: dict) -> str:
    """Return preserved raw-confidence validity, falling back for legacy records only."""
    state = rec.get("confidence_state")
    if "confidence_state" not in rec or state is None:
        return classify_confidence(rec.get("confidence"))
    if state == VALID:
        # Fail closed if a stored state and its numeric representation disagree.
        return VALID if classify_confidence(rec.get("confidence")) == VALID else INVALID
    if state in (MISSING, INVALID):
        return state
    return INVALID


def is_terminal_attempt(rec: dict) -> bool:
    """True once the provider attempt returned without a transport/provider error.

    Terminal semantic output is never automatically re-run, even when parsing or
    analytical validation later fails.
    """
    return not rec.get("error")


def is_classification_valid(rec: dict) -> bool:
    """True only for a terminal, non-truncated, unambiguous parse yielding an allowed label.

    ``parse_multiple_objects`` exists only in records written after Package B (P1-F1);
    older frozen records lack it and are evaluated exactly as before.
    """
    return bool(
        is_terminal_attempt(rec)
        and rec.get("parse_ok") is True
        and not rec.get("truncation_suspected")
        and not rec.get("parse_multiple_objects")
        and rec.get("label") in GOLD_LABELS
    )


def is_calibration_valid(rec: dict) -> bool:
    """True only when classification and the preserved raw confidence are valid."""
    return is_classification_valid(rec) and record_confidence_state(rec) == VALID


def model_call_again_allowed(rec: dict) -> bool:
    """Whether the outer resume loop may retry this slot after a provider error.

    This does not expand the provider SDK's frozen transport retry policy and is
    deliberately false for every terminal semantic response.
    """
    return not is_terminal_attempt(rec)


def analytical_state(rec: dict) -> dict[str, bool]:
    """Materialize the three independent state dimensions on a record."""
    terminal = is_terminal_attempt(rec)
    classification = is_classification_valid(rec)
    calibration = is_calibration_valid(rec)
    return {
        "terminal_attempt": terminal,
        "classification_valid": classification,
        "calibration_valid": calibration,
        "model_call_again_allowed": not terminal,
    }


def is_completed(rec: dict) -> bool:
    """Legacy completion predicate: terminal attempt only, not analytical validity.

    Retained so historical resume semantics are not silently repurposed. New
    analytical decisions must use ``is_classification_valid`` /
    ``is_calibration_valid`` or their explicit aggregate completeness fields.
    """
    return is_terminal_attempt(rec)


def merge_records(existing: list[dict], new: list[dict]) -> dict:
    """Resume-safe merge keyed on (model, unit_id, run_index).

    A **completed** existing record is never silently overwritten; a duplicate completed key is
    rejected (not appended twice). A previously errored record may be replaced by a later completed
    retry for the same key. Provider errors stay distinguishable from analytical outcomes.
    """
    merged: dict[tuple, dict] = {replication_key(r): r for r in existing}
    added, skipped_completed, replaced_error = 0, 0, 0
    for r in new:
        k = replication_key(r)
        prev = merged.get(k)
        if prev is None:
            merged[k] = r
            added += 1
        elif is_completed(prev):
            skipped_completed += 1  # never overwrite a completed replication
        elif is_completed(r):
            merged[k] = r
            replaced_error += 1
    return {
        "records": [merged[k] for k in sorted(merged)],
        "added": added,
        "skipped_completed": skipped_completed,
        "replaced_error": replaced_error,
        "n_total": len(merged),
    }


# ---------------------------------------------------------------------------
# Aggregation → per (model, unit) stability
# ---------------------------------------------------------------------------

@dataclass
class UnitStability:
    model: str
    unit_id: str
    unit_type: str
    base_case_id: str
    cluster_root_id: str | None
    family_id: str | None
    gold_label: str
    n_runs: int
    n_labelled: int
    n_provider_errors: int
    n_parse_failures: int
    modal_label: str | None
    modal_support: int
    modal_correct: bool | None
    unique_labels: list[str]
    label_switch_count: int
    confidence_mean: float | None
    confidence_spread: float | None
    brier_mean: float | None
    per_replication_correct: list[bool]
    stability_tier: str

    def as_dict(self) -> dict:
        return asdict(self)


def _tier(modal_support: int) -> str:
    if modal_support >= 5:
        return TIER_UNANIMOUS
    if modal_support == 4:
        return TIER_STABLE_MAJORITY
    if modal_support == 3:
        return TIER_FRAGILE
    return TIER_UNSTABLE


def aggregate(records: list[dict]) -> list[UnitStability]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        groups[(r["model"], r["unit_id"])].append(r)

    out: list[UnitStability] = []
    for (model, unit_id), recs in sorted(groups.items()):
        recs = sorted(recs, key=lambda r: r.get("run_index", 0))
        labelled = [r for r in recs if is_classification_valid(r)]
        labels = [r["label"] for r in labelled]
        provider_errors = sum(1 for r in recs if r.get("error"))
        parse_failures = sum(1 for r in recs if not r.get("parse_ok"))
        modal_label, modal_support = (None, 0)
        if labels:
            modal_label, modal_support = Counter(labels).most_common(1)[0]
        gold = recs[0]["gold_label"]
        modal_correct = None if modal_label is None else (modal_label == gold)
        switches = sum(1 for a, b in zip(labels, labels[1:]) if a != b)
        confs = [r["confidence"] for r in labelled if is_calibration_valid(r)]
        conf_mean = round(sum(confs) / len(confs), 4) if confs else None
        conf_spread = round(max(confs) - min(confs), 4) if len(confs) >= 2 else (0.0 if confs else None)
        briers = [
            r["brier_contribution"] for r in labelled
            if is_calibration_valid(r) and r.get("brier_contribution") is not None
        ]
        brier_mean = round(sum(briers) / len(briers), 6) if briers else None
        per_rep_correct = [bool(r.get("label_correct")) for r in labelled]
        out.append(UnitStability(
            model=model, unit_id=unit_id, unit_type=recs[0]["unit_type"],
            base_case_id=recs[0]["base_case_id"], cluster_root_id=recs[0].get("cluster_root_id"),
            family_id=recs[0].get("family_id"), gold_label=gold, n_runs=len(recs),
            n_labelled=len(labelled), n_provider_errors=provider_errors,
            n_parse_failures=parse_failures, modal_label=modal_label, modal_support=modal_support,
            modal_correct=modal_correct, unique_labels=sorted(set(labels)),
            label_switch_count=switches, confidence_mean=conf_mean, confidence_spread=conf_spread,
            brier_mean=brier_mean, per_replication_correct=per_rep_correct,
            stability_tier=_tier(modal_support),
        ))
    return out


def _majority_failure(s: UnitStability) -> bool:
    """Wrong modal label with >= 3/5 support (frozen 'majority failure')."""
    return s.modal_correct is False and s.modal_support >= MAJORITY_FAILURE_MIN_SUPPORT


# ---------------------------------------------------------------------------
# Frozen systematic-failure computations (facts only; WP-4 does not decide results)
# ---------------------------------------------------------------------------

def boundary_assessment(stabs: list[UnitStability]) -> dict:
    """Same directional confusion on >=2 independent boundary cases within a priority boundary."""
    bnd = [s for s in stabs if s.unit_type == "boundary_base"]
    directional: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for s in bnd:
        if _majority_failure(s):
            directional[(s.family_id, s.gold_label, s.modal_label)].append(s.unit_id)
    blocking = {f"{fam}:{gold}->{pred}": ids for (fam, gold, pred), ids in directional.items()
                if len(ids) >= 2}
    investigate = {f"{fam}:{gold}->{pred}": ids for (fam, gold, pred), ids in directional.items()
                   if len(ids) == 1}
    return {
        "status": "BLOCK" if blocking else ("INVESTIGATE" if investigate else "OK"),
        "blocking_directions": blocking,
        "investigate_directions": investigate,
        "n_majority_failures": sum(1 for s in bnd if _majority_failure(s)),
    }


def adversarial_assessment(stabs: list[UnitStability]) -> dict:
    adv = [s for s in stabs if s.unit_type == "adversarial_base"]
    by_family: dict[str, list[UnitStability]] = defaultdict(list)
    for s in adv:
        by_family[s.family_id].append(s)
    families = {}
    status = "OK"
    for fam, members in sorted(by_family.items()):
        fails = sum(1 for s in members if _majority_failure(s))
        verdict = "PASS" if fails == 0 else ("INVESTIGATE" if fails == 1 else "BLOCK")
        families[fam] = {"n_cases": len(members), "majority_failures": fails, "verdict": verdict}
        if verdict == "BLOCK":
            status = "BLOCK"
        elif verdict == "INVESTIGATE" and status != "BLOCK":
            status = "INVESTIGATE"
    return {"status": status, "families": families}


def perturbation_assessment(stabs: list[UnitStability]) -> dict:
    """Cluster-aware flip detection vs each cluster root's modal label (same model)."""
    root_modal = {s.unit_id: s.modal_label for s in stabs if s.unit_type != "perturbation_variant"}
    variants = [s for s in stabs if s.unit_type == "perturbation_variant"]
    flips_by_family: dict[str, set[str]] = defaultdict(set)   # family -> set of flipped clusters
    flips_by_cluster: dict[str, set[str]] = defaultdict(set)  # cluster -> set of flipping families
    flipped_variants = []
    for s in variants:
        root = s.cluster_root_id
        root_label = root_modal.get(root)
        is_flip = (root_label is not None and s.modal_label is not None
                   and s.modal_label != root_label and s.modal_support >= MAJORITY_FAILURE_MIN_SUPPORT)
        if is_flip:
            flips_by_family[s.family_id].add(root)
            flips_by_cluster[root].add(s.family_id)
            flipped_variants.append(s.unit_id)
    family_trigger = {fam: sorted(cl) for fam, cl in flips_by_family.items() if len(cl) >= 2}
    cluster_trigger = {cl: sorted(fam) for cl, fam in flips_by_cluster.items() if len(fam) >= 2}
    return {
        "status": "BLOCK" if (family_trigger or cluster_trigger) else "OK",
        "family_multi_cluster_flips": family_trigger,
        "cluster_multi_family_flips": cluster_trigger,
        "flipped_variants": sorted(flipped_variants),
    }


def replication_assessment(stabs: list[UnitStability]) -> dict:
    """>=2 independent same-family cases fragile-or-worse (infra failures excluded)."""
    bases = [s for s in stabs if s.unit_type != "perturbation_variant"]
    by_family: dict[str, list[str]] = defaultdict(list)
    for s in bases:
        if s.n_provider_errors == 0 and s.stability_tier in (TIER_FRAGILE, TIER_UNSTABLE):
            by_family[s.family_id].append(s.unit_id)
    blocking = {fam: ids for fam, ids in by_family.items() if len(ids) >= 2}
    return {
        "status": "BLOCK" if blocking else "OK",
        "fragile_or_worse_by_family": {k: sorted(v) for k, v in by_family.items()},
        "blocking_families": {k: sorted(v) for k, v in blocking.items()},
    }


# ---------------------------------------------------------------------------
# Per-model report families (never pooled)
# ---------------------------------------------------------------------------

def _confusion_matrix(stabs: list[UnitStability]) -> dict:
    matrix: dict[str, Counter] = defaultdict(Counter)
    for s in stabs:
        if s.modal_label is not None:
            matrix[s.gold_label][s.modal_label] += 1
    return {gold: dict(preds) for gold, preds in matrix.items()}


def _analytical_accounting(records: list[dict], expected_calls: int) -> dict:
    terminal = sum(1 for r in records if is_terminal_attempt(r))
    classification_valid = sum(1 for r in records if is_classification_valid(r))
    calibration_valid = sum(1 for r in records if is_calibration_valid(r))
    provider_failures = sum(1 for r in records if not is_terminal_attempt(r))
    classification_invalid = terminal - classification_valid
    calibration_invalid = terminal - calibration_valid
    terminal_complete = terminal == expected_calls
    classification_complete = classification_valid == expected_calls
    calibration_complete = calibration_valid == expected_calls
    return {
        "expected_calls": expected_calls,
        "observed_records": len(records),
        "terminal_attempts": terminal,
        "provider_failures": provider_failures,
        "classification_valid_calls": classification_valid,
        "classification_invalid_calls": classification_invalid,
        "classification_unavailable_calls": max(expected_calls - classification_valid, 0),
        "calibration_valid_calls": calibration_valid,
        "calibration_invalid_calls": calibration_invalid,
        "calibration_unavailable_calls": max(expected_calls - calibration_valid, 0),
        "terminal_attempt_complete": terminal_complete,
        "classification_complete": classification_complete,
        "calibration_complete": calibration_complete,
        "analytical_complete": classification_complete and calibration_complete,
        "analysis_status": (
            "COMPLETE" if classification_complete and calibration_complete
            else "PARTIAL_INCOMPLETE"
        ),
    }


def build_model_report(model_id: str, records: list[dict], *,
                       expected_units: int | None = None,
                       expected_calls: int | None = None) -> dict:
    model_records = [r for r in records if r["model"] == model_id]
    stabs = [s for s in aggregate(model_records) if s.model == model_id]
    bases = [s for s in stabs if s.unit_type != "perturbation_variant"]
    variants = [s for s in stabs if s.unit_type == "perturbation_variant"]
    expected_units = len(stabs) if expected_units is None else expected_units
    expected_calls = len(model_records) if expected_calls is None else expected_calls
    accounting = _analytical_accounting(model_records, expected_calls)

    def acc(group):
        graded = [s for s in group if s.modal_correct is not None]
        value = round(sum(1 for s in graded if s.modal_correct) / len(graded), 4) if graded else None
        return value, len(graded)

    acc_all, acc_all_n = acc(stabs)
    acc_bases, acc_bases_n = acc(bases)
    acc_variants, acc_variants_n = acc(variants)
    briers = [s.brier_mean for s in stabs if s.brier_mean is not None]
    tier_counts = Counter(s.stability_tier for s in stabs)
    high_conf_wrong = [
        {"unit_id": s.unit_id, "gold": s.gold_label, "modal": s.modal_label,
         "confidence_mean": s.confidence_mean}
        for s in stabs
        if (s.modal_correct is False and s.confidence_mean is not None
            and s.confidence_mean >= 0.75)
    ]
    return {
        "model": model_id,
        "analytical_accounting": accounting,
        "model_summary": {
            "n_units": len(stabs),
            "n_expected_units": expected_units,
            "n_units_observed": len(stabs),
            "n_units_scored": acc_all_n,
            "n_units_unscored": max(expected_units - acc_all_n, 0),
            "accuracy_all_units": acc_all,
            "accuracy_denominator_units": acc_all_n,
            "accuracy_bases_only": acc_bases,
            "accuracy_bases_denominator_units": acc_bases_n,
            "accuracy_variants_only": acc_variants,
            "accuracy_variants_denominator_units": acc_variants_n,
            "mean_brier_valid": round(sum(briers) / len(briers), 6) if briers else None,
            "brier_denominator_units": len(briers),
            "brier_denominator_calls": sum(
                1 for r in model_records
                if is_calibration_valid(r) and r.get("brier_contribution") is not None
            ),
            "analysis_status": accounting["analysis_status"],
            "analytical_complete": accounting["analytical_complete"],
            "note": "Per-model; NOT pooled with the other primary model. Denominators are explicit.",
        },
        "boundary_family_results": boundary_assessment(stabs),
        "adversarial_family_results": adversarial_assessment(stabs),
        "perturbation_cluster_results": perturbation_assessment(stabs),
        "replication_stability": {
            "tier_counts": dict(tier_counts),
            "assessment": replication_assessment(stabs),
        },
        "confusion_matrix": _confusion_matrix(stabs),
        "high_confidence_wrong": high_conf_wrong,
        "systematic_failure_triggers": {
            "boundary": boundary_assessment(stabs)["status"],
            "adversarial": adversarial_assessment(stabs)["status"],
            "perturbation": perturbation_assessment(stabs)["status"],
            "replication": replication_assessment(stabs)["status"],
        },
        "limitations": [
            "Isolated analytical errors are INVESTIGATE/LIMITATION, not automatic phase failure.",
            "Level-3 taxonomy contradictions route to separate curator review, not auto-BLOCK.",
        ],
        "taxonomy_review_flags": [],
    }


def build_phase7a_report(records: list[dict], dry_run: bool = True, *,
                         expected_units: int | None = None,
                         expected_calls_per_model: int | None = None) -> dict:
    units = {r["unit_id"] for r in records}
    variants = {r["unit_id"] for r in records if r["unit_type"] == "perturbation_variant"}
    clusters = {r["cluster_root_id"] for r in records if r["unit_type"] == "perturbation_variant"}
    models = sorted({r["model"] for r in records})
    expected_units = len(units) if expected_units is None else expected_units
    per_model = {
        m: build_model_report(
            m, records, expected_units=expected_units,
            expected_calls=(
                sum(1 for r in records if r["model"] == m)
                if expected_calls_per_model is None else expected_calls_per_model
            ),
        )
        for m in models
    }
    analytical_complete = bool(models) and all(
        r["analytical_accounting"]["analytical_complete"] for r in per_model.values()
    )
    return {
        "phase": "7A",
        "dry_run": dry_run,
        "synthetic_non_analytical": dry_run,
        "analysis_status": "COMPLETE" if analytical_complete else "PARTIAL_INCOMPLETE",
        "analytical_complete": analytical_complete,
        "accounting": {
            "n_independent_bases": len(units) - len(variants),
            "n_evaluated_units": len(units),
            "n_expected_units_per_model": expected_units,
            "n_units_scored_by_model": {
                m: per_model[m]["model_summary"]["n_units_scored"] for m in models
            },
            "expected_calls_by_model": {
                m: per_model[m]["analytical_accounting"]["expected_calls"] for m in models
            },
            "classification_valid_calls_by_model": {
                m: per_model[m]["analytical_accounting"]["classification_valid_calls"]
                for m in models
            },
            "calibration_valid_calls_by_model": {
                m: per_model[m]["analytical_accounting"]["calibration_valid_calls"]
                for m in models
            },
            "n_perturbation_variants": len(variants),
            "n_perturbation_clusters": len(clusters),
            "no_pooled_headline_score": True,
            "note": "Reported per model; 50 variants nested in 10 bases, never 50 independent cases.",
        },
        "models": models,
        "per_model": per_model,
    }


def render_report_md(report: dict) -> str:
    L: list[str] = []
    tag = "DRY RUN / SYNTHETIC / NON-ANALYTICAL" if report.get("dry_run") else "REAL PHASE-7A"
    L.append(f"# Phase 7A Execution Report — {tag}\n")
    a = report["accounting"]
    L.append(f"- Analytical status: **{report['analysis_status']}**")
    L.append(f"- Independent bases: **{a['n_independent_bases']}** · Evaluated units: "
             f"**{a['n_evaluated_units']}** · Perturbation variants: **{a['n_perturbation_variants']}** "
             f"nested in **{a['n_perturbation_clusters']}** clusters (NOT independent cases).")
    L.append(f"- Models (reported separately, no pooled headline): {', '.join(report['models'])}\n")
    for m in report["models"]:
        r = report["per_model"][m]
        ms = r["model_summary"]
        L.append(f"## {m}\n")
        L.append(f"- accuracy (all units): {ms['accuracy_all_units']} "
                 f"(n={ms['accuracy_denominator_units']}/{ms['n_expected_units']}) · bases: "
                 f"{ms['accuracy_bases_only']} · variants: {ms['accuracy_variants_only']} · "
                 f"mean Brier (valid): {ms['mean_brier_valid']} "
                 f"(calls n={ms['brier_denominator_calls']})")
        t = r["systematic_failure_triggers"]
        L.append(f"- systematic triggers — boundary: **{t['boundary']}** · adversarial: "
                 f"**{t['adversarial']}** · perturbation: **{t['perturbation']}** · "
                 f"replication: **{t['replication']}**")
        L.append(f"- replication tiers: {r['replication_stability']['tier_counts']}")
        L.append(f"- high-confidence wrong: {len(r['high_confidence_wrong'])}\n")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Artifact writers + CLI (dry-run only in WP-4)
# ---------------------------------------------------------------------------

def write_plan_artifacts(repo_root: str | Path | None = None,
                         out_dir: str | Path | None = None) -> Path:
    target = Path(out_dir) if out_dir else _ARTIFACT_DIR
    target.mkdir(parents=True, exist_ok=True)
    (target / EXECUTION_MANIFEST_FILE).write_text(
        json.dumps(build_execution_manifest(repo_root), indent=2) + "\n")
    (target / CALL_PLAN_FILE).write_text(
        json.dumps(build_call_plan(repo_root), indent=2) + "\n")
    return target


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="agent_arena.phase7a_execution",
        description="Phase-7A readiness: build/verify the execution manifest + call plan, and run a "
                    "fake-provider dry run. WP-4 makes NO real analytical calls.",
    )
    p.add_argument("--write-plan", action="store_true",
                   help="Write the execution manifest + call plan artifacts.")
    p.add_argument("--verify", action="store_true", help="Run the fail-closed fingerprint gate.")
    p.add_argument("--preflight", action="store_true",
                   help="Full real-run readiness gate: fingerprint gate AND executable QA "
                        "(actually runs pytest). GO requires both. Makes 0 analytical model calls.")
    p.add_argument("--write-qa", action="store_true",
                   help="With --preflight, persist the real QA execution record artifact.")
    p.add_argument("--dry-run", action="store_true",
                   help="Execute the full 84x5x2 plan with the deterministic fake provider (no network).")
    p.add_argument("--out-dir", default=None)
    args = p.parse_args(argv)
    process_status = 0

    if args.write_plan:
        target = write_plan_artifacts(out_dir=args.out_dir)
        print(f"wrote execution manifest + call plan to {target}/")
    if args.verify:
        v = verify_pre_run()
        print(f"pre-run gate: {'PASS' if v['passes'] else 'FAIL'} | units={v['n_evaluated_units']} "
              f"bases={v['n_independent_bases']} variants={v['n_perturbation_variants']} "
              f"clusters={v['n_perturbation_clusters']} planned_calls={v['planned_analytical_calls']}")
        for e in v["errors"]:
            print(f"  - {e}")
    if args.preflight:
        pf = real_run_preflight()
        qa = pf["qa"] or {}
        preflight_go = pf.get("go") is True
        print(f"real-run preflight: {'GO' if preflight_go else 'NO-GO'} | gate="
              f"{'PASS' if pf['gate_passes'] else 'FAIL'} | qa={pf['qa_status']}")
        if qa:
            print(f"  QA: {qa.get('summary_line','')} | exit={qa.get('exit_code')} "
                  f"collected={qa.get('tests_collected')} passed={qa.get('tests_passed')} "
                  f"failed={qa.get('tests_failed')} skipped={qa.get('tests_skipped')} "
                  f"fp={(pf.get('qa_record_fingerprint') or '')[:16]}")
        for e in pf["gate_errors"]:
            print(f"  - {e}")
        if args.write_qa and qa:
            target = Path(args.out_dir) if args.out_dir else Path(".agent_arena/qa")
            target.mkdir(parents=True, exist_ok=True)
            (target / QA_RECORD_FILE).write_text(json.dumps(qa, indent=2) + "\n")
            print(f"  wrote QA execution record to {target / QA_RECORD_FILE}")
        if not preflight_go:
            process_status = 2
    if args.dry_run:
        units = resolve_evaluated_units()
        recs = execute(units, lambda mid: FakeLibraryProvider(model=mid), dry_run=True)
        report = build_phase7a_report(recs, dry_run=True)
        print(f"DRY RUN (SYNTHETIC / NON-ANALYTICAL): {len(recs)} records "
              f"({report['accounting']['n_evaluated_units']} units x {N_REPLICATIONS} x "
              f"{len(PRIMARY_MODELS)} models)")
        for m in report["models"]:
            ms = report["per_model"][m]["model_summary"]
            print(f"  {m}: acc(all)={ms['accuracy_all_units']} bases={ms['accuracy_bases_only']} "
                  f"variants={ms['accuracy_variants_only']}")
    if not (args.write_plan or args.verify or args.preflight or args.dry_run):
        p.print_help()
        return 1
    return process_status


if __name__ == "__main__":
    raise SystemExit(main())
