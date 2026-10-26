"""Read-only historical reconstruction. No provider construction or network calls.

Run from the repository root with .venv/bin/python <this file>.
Only writes this mission's evidence/historical_recomputed.json.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from statistics import mean
import subprocess

from agent_arena import condition_contract as cc
from agent_arena import full_replication_analysis as fra
from agent_arena import phase7a_execution as p7
from agent_arena import phase7a_real_run as rr
from agent_arena import resume_integrity as ri
from agent_arena.output_contract import parse_structured_output
from agent_arena.runner import (
    STUDY_FORENSICS_PROMPT,
    STUDY_FORENSICS_PROMPT_PROSPECTIVE,
)
from agent_arena.study_forensics_checker import _detect_label

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "evidence/historical_recomputed.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def historical_fp_fields(commit: str) -> tuple:
    # Read the original field selection as data, never execute historical code.
    tree = ast.parse(git("show", f"{commit}:src/agent_arena/phase7a_real_run.py"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "_RECORD_FP_FIELDS"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError("original fingerprint field selection unavailable")


def main() -> None:
    units = p7.resolve_evaluated_units(ROOT)
    by_id = {unit.unit_id: unit for unit in units}
    bindings = [
        {"unit_id": u.unit_id, "unit_type": u.unit_type,
         "gold_label": u.gold_label, "family_id": u.family_id}
        for u in units
    ]
    result = {
        "schema": "harness-value-historical-audit/1",
        "status": "RECOMPUTED_FROM_RAW",
        "source_head": git("rev-parse", "HEAD"),
        "v1_prompt_sha256": sha(STUDY_FORENSICS_PROMPT.encode()),
        "v2_prompt_sha256": sha(STUDY_FORENSICS_PROMPT_PROSPECTIVE.encode()),
        "units": [{**b, "base_case_id": by_id[b['unit_id']].base_case_id,
                   "cluster_root_id": by_id[b['unit_id']].cluster_root_id,
                   "perturbation_family": by_id[b['unit_id']].perturbation_family}
                  for b in bindings],
        "independence_note": "84 analytical units: 34 bases and 50 variants in ten families; not 84 independent studies.",
        "cells": {},
    }
    for cell, key, relative in (
        ("H0", "haiku", "analysis/phase7a_execution/haiku"),
        ("S0", "sonnet", "analysis/phase7a_execution/sonnet"),
        ("H1", "haiku", "analysis/phase5b_haiku_full_replication/run/haiku"),
        ("S1", "sonnet", "analysis/phase5b_sonnet_full_replication/run/sonnet"),
    ):
        directory = ROOT / relative
        raw_path = directory / "raw" / f"{key}_raw_records.jsonl"
        freeze_path = directory / f"{key}_raw_result_freeze.json"
        rows = rr._load_jsonl(raw_path)
        freeze = json.loads(freeze_path.read_text())
        errors = []
        for row in rows:
            parsed, diag = parse_structured_output(
                row["raw_response"], finish_reason=row.get("finish_reason")
            )
            expected = {
                "raw_response_sha256": sha(row["raw_response"].encode()),
                "gold_label": by_id[row["unit_id"]].gold_label,
                "unit_fingerprint": by_id[row["unit_id"]].unit_fingerprint,
                "model": rr.model_id_for(key),
                "parse_ok": diag.ok,
                "label": _detect_label(parsed) if parsed else None,
                "confidence": parsed.confidence if parsed else None,
            }
            for field, value in expected.items():
                if row.get(field) != value:
                    errors.append([row["unit_id"], row["run_index"], field])
        fields = historical_fp_fields(freeze["repository_commit"])
        aggregate = p7._fp(sorted(
            p7._fp({field: row.get(field) for field in fields}) for row in rows
        ))
        if aggregate != freeze["aggregate_result_set_fingerprint"]:
            errors.append(["aggregate_result_set_fingerprint"])
        summary = fra.summarize_records(
            rows, ordered_unit_bindings=bindings, model_id=rr.model_id_for(key),
            repetitions=5, condition=cell,
        )
        grouped = defaultdict(list)
        for row in rows:
            grouped[row["unit_id"]].append(row)
        modal = {}
        for unit in units:
            group = grouped[unit.unit_id]
            counts = Counter(r["label"] for r in group if p7.is_classification_valid(r))
            top = max(counts.values(), default=0)
            winners = [label for label, n in counts.items() if n == top]
            label = winners[0] if len(winners) == 1 else None
            modal[unit.unit_id] = {
                "gold": unit.gold_label, "label": label,
                "correct": label == unit.gold_label, "support": top,
                "mean_confidence": mean(r['confidence'] for r in group
                                        if p7.is_calibration_valid(r)),
            }
        historical_checkpoint = None
        if cell.endswith("1"):
            manifest_path = directory / "raw" / f"{key}_checkpoint_manifest.json"
            manifest = json.loads(manifest_path.read_text())
            contract = {k: v for k, v in manifest.items() if k not in {
                "checkpoint_record_count", "checkpoint_records_fingerprint",
                "checkpoint_accounting", "checkpoint_fingerprint",
            }}
            checked = ri.validate_resume_checkpoint(raw_path, manifest_path, contract, units)
            historical_checkpoint = {k: v for k, v in checked.items() if k != "records"}
            errors.extend(checked["errors"])
        result["cells"][cell] = {
            "raw_path": str(raw_path.relative_to(ROOT)),
            "raw_file_sha256": sha(raw_path.read_bytes()),
            "freeze_path": str(freeze_path.relative_to(ROOT)),
            "freeze_file_sha256": sha(freeze_path.read_bytes()),
            "freeze_commit": freeze["repository_commit"],
            "aggregate_result_set_fingerprint": aggregate,
            "integrity_errors": errors,
            "correct_units": sum(r["correct"] for r in modal.values()),
            "error_ids": sorted(k for k, r in modal.items() if not r["correct"]),
            "unanimous_units": sum(r["support"] == 5 for r in modal.values()),
            "unit_rows": modal,
            "summary": summary,
            "checkpoint_against_own_historical_contract": historical_checkpoint,
            "model_identity_limit": "Stored requested snapshot verified; historical raw artifacts do not preserve provider response model or message ID.",
            "confidence_denominator_note": "Response-level Brier/ECE use all calibration-valid responses; mean unit confidence is separate, never silently substituted.",
            "http_attempts": sum((r.get("usage") or {}).get("http_attempts", 0) for r in rows)
                if all("http_attempts" in (r.get("usage") or {}) for r in rows) else None,
        }
        print(cell, result["cells"][cell]["correct_units"], "/84", "errors", errors)
    result["historical_authorizations"] = {}
    for key in ("haiku", "sonnet"):
        document = cc.resolve_registered_plan(f"AA-P5B-{key.upper()}-FULL-REPLICATION-001", ROOT)
        result["historical_authorizations"][key] = {
            "validation_errors": cc.validate_plan_document(document, ROOT),
            "authorization": document["authorization"], "progress": document["progress"],
        }
    result["historical_changes"] = {}
    for old, new in (("H0", "H1"), ("S0", "S1")):
        x = result["cells"][old]["correct_units"] / 84
        y = result["cells"][new]["correct_units"] / 84
        result["historical_changes"][f"{old}->{new}"] = {
            "accuracy_delta_pp": 100 * (y-x),
            "relative_accuracy_change_percent": 100 * (y-x) / x,
            "relative_error_reduction_percent": 100 * (y-x) / (1-x),
        }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    if any(cell["integrity_errors"] for cell in result["cells"].values()):
        raise SystemExit("Material historical integrity mismatch; stop before spending")


if __name__ == "__main__":
    main()
