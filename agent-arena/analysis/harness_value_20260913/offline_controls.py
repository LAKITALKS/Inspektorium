"""Fixed pre-spend control probes; imports production controls, never a real provider.

Artifact acceptance here means authenticated, analytically complete research data.
It does NOT mean official publication. Production replication artifacts have the
diagnostic_validation_raw_freeze role, and no classification-to-official-release
conversion is invented. All scratch checkpoints live in temporary directories.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import socket
import tempfile
from unittest.mock import patch

from agent_arena import condition_contract as cc
from agent_arena import phase7a_execution as p7
from agent_arena import phase7a_real_run as rr
from agent_arena import resume_integrity as ri
from agent_arena.confidence_validity import VALID, classify_confidence
from agent_arena.output_contract import extract_json_object, parse_structured_output
from agent_arena.study_forensics_checker import _detect_label

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "evidence/offline_controls.json"
LABELS = {"solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"}


def standard_parser(text):
    from agent_arena.bounded_harness_mission import interpretation
    return interpretation(text)['common_operational_valid']


def replace_raw(record, text, unit, contract):
    row = copy.deepcopy(record)
    parsed, diag = parse_structured_output(text, finish_reason="stop")
    row.update(raw_response=text, raw_response_sha256=None,
               parse_ok=diag.ok, truncation_suspected=diag.truncation_suspected,
               confidence=parsed.confidence if parsed else None,
               confidence_state=parsed.confidence_state if parsed else "MISSING",
               label=_detect_label(parsed) if parsed else None)
    row["label_correct"] = row["label"] == unit.gold_label
    row["brier_contribution"] = ((row["confidence"] - int(row["label_correct"])) ** 2
                                if classify_confidence(row["confidence"]) == VALID else None)
    return ri.seal_new_record(row, unit, contract)


def artifact_probes():
    document = cc.resolve_registered_plan("AA-P5B-HAIKU-FULL-REPLICATION-001", ROOT)
    arm = document["specification"]["arms"][0]
    units = cc.units_for_plan(document, ROOT)
    by_id = {u.unit_id: u for u in units}
    directory = ROOT / arm["artifact_namespace"] / "haiku" / "raw"
    rows = rr._load_jsonl(directory / "haiku_raw_records.jsonl")
    manifest = json.loads((directory / "haiku_checkpoint_manifest.json").read_text())
    contract = {k: v for k, v in manifest.items() if k not in {
        "checkpoint_record_count", "checkpoint_records_fingerprint",
        "checkpoint_accounting", "checkpoint_fingerprint",
    }}
    # A strictly valid JSON mate, same binding. Exact label avoids treating free-text
    # label interpretation as a baseline format failure in the fixed challenge set.
    for i, row in enumerate(rows):
        payload = {"final_answer": row["label"], "confidence": 0.8,
                   "evidence_tier": "clinical_human", "conclusion_tier": "same as evidence",
                   "bridge_supported": True, "assumptions": [], "steps": ["Synthetic fixture."],
                   "alternative_hypotheses": [], "uncertainties": [],
                   "key_claims": [], "self_check": []}
        rows[i] = replace_raw(row, json.dumps(payload), by_id[row["unit_id"]], contract)
    clean_manifest = ri.build_checkpoint_manifest(contract, rows)

    def evaluate(fid, records, checkpoint, desired_valid, fault):
        with tempfile.TemporaryDirectory(prefix="arena-fixed-fault-") as scratch:
            raw_path, manifest_path = Path(scratch) / "records.jsonl", Path(scratch) / "checkpoint.json"
            rr._write_jsonl_atomic(raw_path, records)
            manifest_path.write_text(json.dumps(checkpoint))
            checked = ri.validate_resume_checkpoint(raw_path, manifest_path, contract, units)
            freeze = rr.build_condition_raw_freeze(
                records, document=document, arm=arm, model_key="haiku", repo_root=ROOT,
                dry_run=False, execution_type=p7.EXEC_TYPE_ADJUDICATION,
            ) if checked["valid"] else None
            c_accept = checked["valid"] and freeze["analytical_complete"]
        return {
            "fixture_id": fid, "scope": "research_run_artifact",
            "desired_technically_valid": desired_valid, "fault": fault,
            "clean_mate": fid[:2] + "-clean", "records": len(records),
            "B_accept": all(standard_parser(r['raw_response']) for r in records),
            "C_accept": c_accept, "C_checkpoint_valid": checked["valid"],
            "C_reason": checked["errors"] or ([] if c_accept else ["analytical_complete=false"]),
            "official_release": False,
            "official_release_reason": "Diagnostic validation role; official release not invoked or inferred",
            "entry_points": ["resume_integrity.validate_resume_checkpoint",
                             "phase7a_real_run.build_condition_raw_freeze"],
            "fixture_content_fingerprint": p7._fp({"records": records, "manifest": checkpoint}),
        }

    output = []
    for family in range(1, 7):
        output.append(evaluate(f"F{family}-clean", rows, clean_manifest, True, None))
        faults = {
            1: ["confidence_missing", "confidence_1.2"],
            2: ["malformed_json", "unknown_label"],
            3: ["other_source_hash", "other_case_id"],
            4: ["stale_checkpoint", "duplicate_terminal_slot"],
            5: ["omitted_terminal_record", "incorrect_reported_denominator"],
            6: ["other_code_commit", "raw_changed_hash_retained"],
        }[family]
        for index, fault in enumerate(faults, 1):
            changed, altered_manifest = copy.deepcopy(rows), copy.deepcopy(clean_manifest)
            if family <= 2:
                payload = json.loads(changed[0]["raw_response"])
                if fault == "confidence_missing": payload.pop("confidence")
                if fault == "confidence_1.2": payload["confidence"] = 1.2
                if fault == "unknown_label": payload["final_answer"] = "unrecognized_taxonomy_label"
                # Remove optional analysis prose in the syntax family from BOTH mates
                # below if necessary; never feed the fixture gold to a control.
                text = "{unparseable" if fault == "malformed_json" else json.dumps(payload)
                changed[0] = replace_raw(changed[0], text, by_id[changed[0]['unit_id']], contract)
                altered_manifest = ri.build_checkpoint_manifest(contract, changed)
            elif fault == "other_source_hash": changed[0]["unit_fingerprint"] = rows[5]["unit_fingerprint"]
            elif fault == "other_case_id": changed[0]["case_id"] = rows[5]["case_id"]
            elif fault == "stale_checkpoint": altered_manifest = ri.build_checkpoint_manifest(contract, rows[:-1])
            elif fault == "duplicate_terminal_slot": changed.append(copy.deepcopy(changed[0]))
            elif fault == "omitted_terminal_record": changed.pop()
            elif fault == "incorrect_reported_denominator": altered_manifest["expected_slots"] += 1
            elif fault == "other_code_commit": altered_manifest["repository_commit"] = "0" * 40
            elif fault == "raw_changed_hash_retained": changed[0]["raw_response"] += " "
            output.append(evaluate(f"F{family}-fault{index}", changed, altered_manifest, False, fault))
    return output


def pre_execution_probes():
    # Reuse existing repository test scaffolding only to construct valid synthetic
    # states. Production gate implementation remains the code under test.
    spec = importlib.util.spec_from_file_location("arena_existing_test_helpers", ROOT / "tests/test_condition_contract.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    outcomes = []
    for family, faults in ((7, (None, "consumed_authorization", "different_specification")),
                           (8, (None, "unauthorized_model", "wrong_environment"))):
        for index, fault in enumerate(faults):
            doc = helpers._synthetic_document()
            builder = helpers.ProviderBuilder()
            source = helpers._source_binding()
            if fault == "consumed_authorization": doc["authorization"]["status"] = cc.AUTH_CONSUMED
            if fault == "different_specification":
                other = helpers._synthetic_document(unit_ids=("P7A-NEU-003",))
                assert cc.validate_plan_document(other, ROOT, _allow_synthetic_test=True) == []
                doc["authorization"] = copy.deepcopy(other["authorization"])
            if fault == "unauthorized_model":
                doc["specification"]["arms"][1]["runtime_contracts"]["haiku"]["exact_model_id"] = "claude-sonnet-4-5-20250929"
            calls = [0]
            def inspect(_root):
                calls[0] += 1
                value = copy.deepcopy(source)
                if fault == "wrong_environment" and calls[0] > 1:
                    value["python_environment_fingerprint"] = "0" * 64
                return value
            error = None
            with tempfile.TemporaryDirectory(prefix="arena-preexecution-fault-") as scratch:
                try:
                    helpers._run_synthetic(Path(scratch), doc, builder=builder, source_inspector=inspect)
                except rr.ConditionAuthorizationError as exc:
                    error = str(exc)
            outcomes.append({
                "fixture_id": f"F{family}-" + ("clean" if index == 0 else f"fault{index}"),
                "scope": "shared_pre_execution_infrastructure", "fault": fault,
                "desired_technically_valid": fault is None,
                "accepted": error is None, "reason": error,
                "fake_provider_constructions": builder.constructions,
                "fake_provider_calls": sum(len(p.requests) for p in builder.providers),
                "paid_provider_calls": 0,
                "entry_point": "phase7a_real_run._run_registered_condition (existing private synthetic-only seam)",
                "isolation_note": "Synthetic QA/credential doubles; real authorization, binding, state-comparison and checkpoint checks",
            })
    return outcomes


def main():
    with patch.object(socket.socket, "connect", side_effect=AssertionError("offline fixture attempted network")):
        artifacts = artifact_probes()
        pre_execution = pre_execution_probes()
    # Full correctly-bound synthetic envelopes; oracle correctness is metadata,
    # never used as a rejection predicate by the technical production controls.
    from agent_arena.bounded_harness_mission import bind_research_records, sha, canon, LIST_FIELDS
    semantic = []
    for fid, claim, evidence, gold, predicted in (
        ("S-negative", "This trial proves treatment has no benefit at any dose in any adult.",
         "A randomized trial compared 10 mg daily with placebo in 100 adults. The primary outcome difference was 0.1 (95% CI -0.3 to 0.5).", "overclaim", "solid"),
        ("S-taxonomy", "An observed association proves the exposure causes the outcome.",
         "A cross-sectional survey found an adjusted association between self-reported exposure and symptoms. Exposure was not assigned.", "correlation_vs_causation", "mechanism_vs_evidence"),
    ):
        inp = {"id":fid,"claim":claim,"packet":{"source":{"title":"Synthetic control source"},"evidence":evidence}}
        oracle = [{"id":fid,"root_id":fid,"role":"primary","gold":gold}]
        raw = canon({"final_answer":predicted,"confidence":0.99,"evidence_tier":"limited_human","conclusion_tier":"general_public","bridge_supported":True,**{k:[] for k in LIST_FIELDS}})
        with tempfile.TemporaryDirectory(prefix="arena-semantic-fixture-") as scratch:
            records, units, contract = bind_research_records(
                [{"id":fid,"raw_text":raw,"raw_sha256":sha(raw.encode()),"finish_reason":"stop"}],
                oracle,[inp],rr.pi.inspect_source_state(ROOT),arm_id="B",root=ROOT,synthetic=True,checkpoint_root=Path(scratch))
            rp,mp=Path(scratch)/"raw.jsonl",Path(scratch)/"manifest.json"
            rr._write_jsonl_atomic(rp,records);mp.write_text(json.dumps(ri.build_checkpoint_manifest(contract,records)))
            checked=ri.validate_resume_checkpoint(rp,mp,contract,units)
            accepted=checked["valid"] and all(p7.is_calibration_valid(x) for x in records)
        semantic.append({"fixture_id":fid,"scope":"synthetic_full_bound_checkpoint","input":inp,
            "fixture_gold":gold,"predicted_label":predicted,"B_accept":standard_parser(raw),"C_accept":accepted,
            "checkpoint_valid":checked["valid"],"C_reason":checked["errors"],"official_release":False,
            "entry_points":["resume_integrity.validate_resume_checkpoint","phase7a_execution.is_calibration_valid"],
            "envelope":records,"contract":contract,"limit":"Technical validity accepts a semantically wrong result; no scientific truth verifier or official release claim"})
    data = {"schema": "harness-value-offline-controls/1", "artifacts": artifacts,
            "shared_pre_execution": pre_execution, "semantic_probes": semantic,
            "actual_paid_calls": 0,
            "limitations": ["Research analytical acceptance and official artifact release are distinct.",
                            "Gold establishes semantic wrongness but is not a rejection rule."]}
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    for row in artifacts:
        print(row["fixture_id"], row["B_accept"], row["C_accept"], row["C_reason"][:1])
    for row in pre_execution:
        print(row["fixture_id"], row["accepted"], row["fake_provider_constructions"])


if __name__ == "__main__":
    main()
