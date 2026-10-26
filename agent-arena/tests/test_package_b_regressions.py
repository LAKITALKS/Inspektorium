"""Package B (C25/P9 order, diagnosis P1-P10): regression tests for the bounded material fixes.

Each test reproduces the counter-case of the diagnosis finding named in its docstring. Kept in
its own module so the pinned canonical QA inventories (preflight_integrity) stay unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_arena.artifact_binding import (
    QA_ASYMMETRIC_EVIDENCE_SELECTION, MANDATORY_PHASE7B_GATE_SPECS, check_evidence_symmetry, final_binding_check,
    load_forensic_record,
)
from agent_arena.evaluator import evaluate_run
from agent_arena.output_contract import extract_json_object
from agent_arena.phase7a_execution import is_classification_valid
from agent_arena.phase8_pipeline import assess_agent_result
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.phase10_bundle import run_audit
from agent_arena.phase10_pipeline import GATE_VERSIONS, REGISTRY, preflight, reconstruct
from agent_arena.providers.anthropic_live import build_user_message
from agent_arena.run_library import LIBRARY_PROMPT_VERSIONS, run_library
from agent_arena.runner import (
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL, STUDY_FORENSICS_PROMPT_VERSION_PHASE8, run_agent,
)
from agent_arena.schemas import Task
from agent_arena.task_loader import load_task
from tests.phase8_case_factory import raw_record

ROOT = Path(__file__).resolve().parents[1]


def _payload_text(label="solid"):
    claim, context, payload = raw_record()
    task = Task(id="pkg-b-case", title="Package B", domain="study_forensics", difficulty="medium",
                task_type="study_forensics", prompt=claim, context=context)
    return task, json.dumps({"final_answer": label, "confidence": 0.8, "steps": ["recorded"],
                             "forensic_record": payload})


# ---------------------------------------------------------------- P1-F1 / P1-A2: ambiguous outputs

@pytest.mark.parametrize("shape,flagged", [
    ("single", False),
    ("single_with_prose_braces", False),
    ("two_fences", True),
    ("two_raw_objects", True),
    ("truncated_trailing_object", True),
    ("bare_fence_then_json_fence", True),
    ("trailing_bare_brace", True),
    ("fenced_then_bare_brace_with_whitespace", True),
])
def test_P1_a_second_analysis_is_flagged_and_never_a_complete_phase8_analysis(shape, flagged):
    task, one = _payload_text("overclaim")
    _, two = _payload_text("solid")
    raw = {
        "single": f"```json\n{one}\n```",
        "single_with_prose_braces": f"```json\n{one}\n```\nNote: the set {{x}} is empty.",
        "two_fences": f"```json\n{one}\n```\n**CORRECTED RESPONSE:**\n```json\n{two}\n```",
        "two_raw_objects": f"{one}\nCorrection: {two}",
        "truncated_trailing_object": f"```json\n{one}\n```\nCorrected:\n{two[:200]}",
        "bare_fence_then_json_fence": f"```\n{one}\n```\n```json\n{two}\n```",
        "trailing_bare_brace": f"{one}\nCorrected:\n{{",  # BE10: cut right after the opening brace
        "fenced_then_bare_brace_with_whitespace": f"```json\n{one}\n```\nCorrected:\n{{\n  ",
    }[shape]
    data, diagnostics = extract_json_object(raw, "stop")
    assert data is not None and diagnostics.ok
    assert diagnostics.multiple_objects is flagged
    result = run_agent(OfflineReviewProvider(raw), task)
    phase8 = assess_agent_result(task, result)
    assert (phase8["technical_status"] == "completed") is (not flagged)
    record = evaluate_run(task, "run-b", [result])
    _, _, _, forensic = reconstruct(record)
    assert (forensic is None) is flagged
    row = {"error": None, "parse_ok": True, "truncation_suspected": False, "label": "solid",
           "parse_multiple_objects": flagged, "error_type": None}
    assert is_classification_valid(row) is (not flagged)


@pytest.mark.parametrize("finish_reason", ["length", None, "stop"])
def test_P1_F2_a_cached_parse_without_raw_text_is_never_complete(finish_reason):
    task, text = _payload_text()
    result = run_agent(OfflineReviewProvider(text), task)
    assert assess_agent_result(task, result)["technical_status"] == "completed"
    stripped = result.model_copy(update={"raw_output": "", "finish_reason": finish_reason})
    assert assess_agent_result(task, stripped)["technical_status"] == "incomplete"  # BE11


def test_P1_frozen_records_without_the_new_flag_are_evaluated_as_before():
    old = {"error": None, "parse_ok": True, "truncation_suspected": False, "label": "solid", "error_type": None}
    assert is_classification_valid(old) is True


# ---------------------------------------------------------------- P2-F1 / P3-F1 / P6-F1: curated cases

def test_P2_P3_curated_library_cases_are_refused_before_any_model_message(tmp_path):
    library = load_task(ROOT / "tasks/study_forensics/case001_social_media.yaml")
    assert "solid" in library.context  # curator commentary naming the expected label
    errors = preflight(library)
    assert errors and "Curated benchmark case fields present" in errors[-1]
    with pytest.raises(ValueError, match="never sent to a model"):
        build_user_message(library)
    result = run_audit(library, OfflineReviewProvider("{}"), output_root=tmp_path / "out")
    assert result.status == "PREFLIGHT_BLOCKED"
    assert REGISTRY["input_preflight"] == "1.1"
    for path in sorted((ROOT / "analysis/live_smoke_20261011/live_run/tasks").glob("LS-*.json")) + \
            sorted((ROOT / "examples/phase10").glob("*-task.json")):
        task = load_task(path)
        assert preflight(task) == [] and build_user_message(task)


def test_P2_P3_every_tracked_library_and_robustness_case_is_refused():
    paths = sorted((ROOT / "tasks/study_forensics").glob("*.yaml")) + \
        sorted((ROOT / "tasks/study_forensics_robustness").rglob("*.yaml"))
    loaded = []
    for path in paths:
        try:
            loaded.append(load_task(path))
        except Exception:  # noqa: BLE001 - non-task YAML (manifests) is not an audit input either
            continue
    assert len(loaded) >= 50
    assert all(preflight(task) for task in loaded)


# ---------------------------------------------------------------- P4-F1: harness prompt condition

class _Recorder(OfflineReviewProvider):
    def __init__(self, raw):
        super().__init__(raw)


def test_P4_library_harness_uses_a_context_free_prompt_and_records_its_identity(tmp_path):
    case_file = ROOT / "tasks/study_forensics/case001_social_media.yaml"
    task = load_task(case_file)
    provider = _Recorder(json.dumps({"final_answer": "solid", "confidence": 0.7}))
    summary = run_library(provider, [(case_file, task)], out_dir=tmp_path / "lib")
    record = summary.records[0]
    assert record["prompt_version"] == STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL
    assert record["prompt_condition_id"] == "study_forensics.historical.v1"
    assert record["system_prompt_sha256"] == "f7704fa50a7689ae56f8fc6d7a383205a5aca34d0c400be36335d6ad8abfcfd5"
    assert "task.context" not in provider.requests[0]["system_prompt"]
    manifest = json.loads((tmp_path / "lib" / "manifest.json").read_text())
    assert manifest["prompt_version"] == STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL
    assert STUDY_FORENSICS_PROMPT_VERSION_PHASE8 not in LIBRARY_PROMPT_VERSIONS
    with pytest.raises(ValueError, match="sends no task context"):
        run_library(provider, [(case_file, task)], write_artifacts=False,
                    prompt_version=STUDY_FORENSICS_PROMPT_VERSION_PHASE8)


# ---------------------------------------------------------------- P7-F1 / P7-V1: symmetry opt-out

FIXTURE = ROOT / "tests/fixtures/pipeline_qa/qa_evidence_symmetry_mixed_outcomes.json"


@pytest.mark.parametrize("which", ["dropped_item", "all_items"])
def test_P7_material_false_no_longer_switches_off_evidence_symmetry(which):
    record = load_forensic_record(FIXTURE)
    record.client_findings[0].referenced_evidence_ids = ["E1"]  # drop the E2 direction
    for item in record.evidence:
        if which == "all_items" or item.evidence_id == "E2":
            item.material = False
    findings = check_evidence_symmetry(record)
    assert [f.code for f in findings] == [QA_ASYMMETRIC_EVIDENCE_SELECTION] and "E2" in findings[0].refs
    assert final_binding_check(record).releasable is False
    spec = next(s for s in MANDATORY_PHASE7B_GATE_SPECS if s.gate_id == "evidence_symmetry")
    assert spec.gate_version == GATE_VERSIONS["evidence_symmetry"] == "1.1.0"
    from agent_arena.artifact_binding import _symmetry_population
    assert _symmetry_population(record) == 1  # the context stays eligible; no host-derived N/A


# ---------------------------------------------------------------- P5-F1: one-shot namespace

def test_P5_lost_lease_or_aborted_namespace_never_opens_a_second_one_shot_batch(tmp_path):
    import tests.test_full_replication_contract as frc_tests
    from agent_arena import full_replication_contract as frc
    from agent_arena.phase7a_real_run import ConditionAuthorizationError
    document = frc_tests._synthetic_document()
    complete = tmp_path / "complete"
    frc_tests._run_synthetic(complete, document, frc_tests._ProviderBuilder())
    (complete / frc.LEASE_FILENAME).unlink()  # A3: lease lost after a complete run
    builder = frc_tests._ProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="prior-run artifacts without its lease"):
        frc_tests._run_synthetic(complete, document, builder)
    assert builder.constructions == 0
    aborted = tmp_path / "aborted"
    frc_tests._run_synthetic(aborted, document, frc_tests._AuthErrorBuilder())
    (aborted / frc.LEASE_FILENAME).unlink()  # B2: aborted run, lease lost
    builder = frc_tests._ProviderBuilder()
    with pytest.raises(ConditionAuthorizationError, match="prior-run artifacts without its lease"):
        frc_tests._run_synthetic(aborted, document, builder)
    assert sum(p.requests for p in builder.providers) == 0


# ---------------------------------------------------------------- P8-F1 / P8-AF1 and P8-F2

CLAIM = "intervention X reduces event Q in adults."
S1 = "A randomized comparison in adults (human) found that intervention X reduced event Q versus placebo at 12 weeks."
S2 = "In an observational cohort of adults, intervention X use was associated with lower event Q."
S3 = "Event Q rose in adults given intervention X."
ATTRS = {"species": "human", "population": "adults", "intervention": "intervention X", "comparator": "placebo",
         "endpoint": "event Q", "endpoint_type": "clinical_event", "relation": "causal", "follow_up": "12 weeks",
         "certainty": "asserted", "comparison": "between"}
DESC = dict(ATTRS, relation="description")


def _taxonomy_case(p1_model="unsupported", optional_support_on_contrary=False):
    """AND(p1, p2): p1 causal (RCT + cohort), p2 contradicted; CvC trigger on p1 via the cohort (diagnosis probe A)."""
    from copy import deepcopy

    def binding(bid, pid, eid, observation):
        return {"binding_id": bid, "proposition_id": pid, "evidence_id": eid, "directness": "direct",
                "observation": observation, "reason": bid}

    def proposition(pid, text, attrs, bindings, verdict, materiality="required"):
        return {"proposition_id": pid, "parent_claim_id": "claim", "proposition_text": text,
                "original_span": {"start": 0, "end": len(CLAIM), "text": CLAIM}, "materiality": materiality,
                "attributes": deepcopy(attrs), "material_dimensions": list(attrs), "evidence_bindings": bindings,
                "reported_verdict": verdict, "reason": "model judgment", "provenance_id": "origin",
                "search_question": f"q-{pid}", "search_scope_ids": ["review"]}
    p2_text = "event Q falls in adults given intervention X"
    props = [proposition("claim:p1", CLAIM, ATTRS, [binding("b1", "claim:p1", "e1", "support"),
                                                     binding("b2", "claim:p1", "e2", "support")], p1_model),
             proposition("claim:p2", p2_text, DESC, [binding("b3", "claim:p2", "e3", "contradiction")], "contradicted")]
    if optional_support_on_contrary:
        props.append(proposition("claim:p3", p2_text, DESC, [binding("b4", "claim:p3", "e3", "support")],
                                 "supported", materiality="optional"))
    transformations = []
    for p in props[:2]:
        pid, a = p["proposition_id"], p["attributes"]
        for stage, ft, tt in (("extraction", CLAIM, p["proposition_text"]),
                              ("search_question", p["proposition_text"], p["search_question"]),
                              ("internal", p["proposition_text"], p["proposition_text"])):
            transformations.append({"transformation_id": f"{stage}-{pid}", "stage": stage, "target_id": pid,
                                    "from_proposition_ids": [pid], "from_text": ft, "to_text": tt,
                                    "from_attributes": deepcopy(a), "to_attributes": deepcopy(a),
                                    "asserted_state": None, "asserts_whole_claim": False, "reason": "same"})
    transformations.append({"transformation_id": "summary", "stage": "summary", "target_id": "client1",
                            "from_proposition_ids": ["claim:p1"], "from_text": CLAIM, "to_text": CLAIM,
                            "from_attributes": deepcopy(ATTRS), "to_attributes": deepcopy(ATTRS),
                            "asserted_state": "contradicted", "asserts_whole_claim": True, "reason": "whole claim"})

    def evidence(eid, role, text):
        return {"evidence_id": eid, "source_id": "context", "role": role, "endpoint": "event Q", "text": text,
                "exact_reference": text, "value_origin": "source_reported"}
    record = {
        "record_id": "pkg-b-taxonomy", "synthetic_fixture": True,
        "provenance": [{"provenance_id": "origin", "exact_claim_text": CLAIM, "source_id": "input"}],
        "evidence": [evidence("e1", "supporting", S1), evidence("e2", "supporting", S2),
                     evidence("e3", "contradictory", S3)],
        "findings": [{"finding_id": "claim:p1", "provenance_id": "origin", "proposition": CLAIM,
                      "supporting_evidence_ids": ["e1", "e2"], "allowed_summary_strength": "not_assessed"},
                     {"finding_id": "claim:p2", "provenance_id": "origin", "proposition": p2_text,
                      "contrary_evidence_ids": ["e3"], "allowed_summary_strength": "not_assessed"}],
        "client_findings": [{"client_finding_id": "client1", "parent_finding_id": "claim:p1", "display_claim": CLAIM,
                             "provenance_id": "origin", "referenced_evidence_ids": ["e1"],
                             "client_strength": "not_assessed"}],
        "search_scopes": [{"search_scope_id": "review", "scope_type": "reviewed_set",
                           "reviewed_source_ids": ["input", "context"]}],
        "phase8": {"claim_id": "claim", "provenance_id": "origin", "original_claim": CLAIM,
                   "required_proposition_ids": ["claim:p1", "claim:p2"], "propositions": props,
                   "logic": {"operator": "and", "children": [{"operator": "leaf", "proposition_id": "claim:p1"},
                                                             {"operator": "leaf", "proposition_id": "claim:p2"}]},
                   "extraction_provenance": "fixture",
                   "evidence_descriptions": [
                       {"evidence_id": "e1", "evidence_type": "controlled_intervention", "source_role": "primary_study",
                        "attributes": deepcopy(ATTRS), "randomized": True, "study_id": "s1"},
                       {"evidence_id": "e2", "evidence_type": "observational", "source_role": "primary_study",
                        "attributes": dict(ATTRS, relation="association"), "study_id": "s2"},
                       {"evidence_id": "e3", "evidence_type": "descriptive", "source_role": "primary_study",
                        "attributes": deepcopy(DESC), "study_id": "s3"}],
                   "transformations": transformations},
        "phase8_taxonomy": {"core_error": "causal_inference", "causal_claim": True, "noncausal_result_used": True,
                            "described_biological_mechanism": False, "implies_human_benefit": False,
                            "proposition_ids": ["claim:p1"], "evidence_ids": ["e2"],
                            "trigger_proposition_id": "claim:p1", "trigger_evidence_id": "e2",
                            "trigger_quote": "associated with lower event Q", "reason": "cvc"},
    }
    task = Task(id="pkg-b-taxonomy", title="Package B taxonomy", domain="study_forensics", difficulty="medium",
                task_type="study_forensics", prompt=CLAIM, context=" ".join([S1, S2, S3]))
    return task, json.dumps({"final_answer": "correlation_vs_causation", "confidence": 0.7, "steps": ["x"],
                             "forensic_record": record})


def test_P8_F1_a_conflict_that_alone_decides_the_derived_label_is_material(tmp_path):
    from agent_arena.phase9_review import assess_case, position_from_result
    task, raw = _taxonomy_case("unsupported")
    position = position_from_result(task, run_agent(OfflineReviewProvider(raw), task), "run1")
    assert position.phase8["derived_label"] == "correlation_vs_causation"
    routed = assess_case(task, [position])
    assert routed.route == "REVIEW_RECOMMENDED" and routed.mandatory
    assert any(t.code == "model_host_conflict" and t.mandatory for t in routed.triggers)
    assert run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "a").status == "REVIEW_REQUIRED"
    control_task, control_raw = _taxonomy_case("supported")  # no conflict, no label: stays regular
    assert run_audit(control_task, OfflineReviewProvider(control_raw), output_root=tmp_path / "b").status == \
        "READY_FOR_RELEASE"


def test_P8_F2_an_optional_proposition_cannot_bind_contradictory_evidence_as_support():
    task, raw = _taxonomy_case("supported", optional_support_on_contrary=True)
    phase8 = assess_agent_result(task, run_agent(OfflineReviewProvider(raw), task))
    assert phase8["technical_status"] == "incomplete"
    assert "claim:p3: binding support contradicts evidence role" in phase8["reasons"]


# ---------------------------------------------------------------- P8-F3 and P9-F5 (Package A follow-ups)

def test_P8_F3_bridge_host_reasons_use_ordinals_even_for_prefix_sharing_ids():
    from agent_arena.phase8_semantics import evaluate_phase8
    from tests.test_phase8_semantics import add_auxiliary_evidence, ledger_record
    record = ledger_record(("supported",))
    record.phase8["propositions"][0]["evidence_bindings"][0]["directness"] = "indirect"
    add_auxiliary_evidence(record)
    ids = ["b", "b: HOST VERIFIED adopt supported"]
    record.phase8["bridges"] = [{"bridge_id": bid, "kind": "semantic_transfer", "conclusion_proposition_id": "claim-1:p1",
                                 "state": state, "evidence_ids": ["bridge-evidence"] if state == "supported" else [],
                                 "reason": "model text"} for bid, state in zip(ids, ("supported", "unknown"))]
    record.phase8["propositions"][0]["required_bridge_ids"] = ids
    result = evaluate_phase8(record)
    assert result.technical_status == "completed", result.reasons
    host = result.propositions[0].host_reasons
    labels = [r.split(": ", 1)[0] for r in host if r.startswith("required bridge")]
    assert labels == ["required bridge 1", "required bridge 2"]
    assert not any("HOST VERIFIED" in r or r.startswith("b:") for r in host)


def test_P9_F5_a_whole_claim_conflict_entry_carries_both_positions_with_reasons():
    from tests.test_phase8_9_conflict import case, position
    from agent_arena.phase9_runtime import build_challenge
    task, payload = case("supported", "unsupported")
    entry = next(c for c in build_challenge(task, position(task, payload))["model_host_conflicts"]
                 if c["scope"] == "composite")
    assert entry["model_position"]["reason"] and entry["host_position"]["reasons"]
    assert "proposition 1 supported" in entry["host_position"]["reasons"][0]


# ---------------------------------------------------------------- Package B round 1 (BF2, BF4, BF5)

def test_BF4_the_harness_records_a_second_analysis_and_marks_the_classification_invalid(tmp_path):
    from agent_arena.run_library import run_single
    task, one = _payload_text("overclaim")
    _, two = _payload_text("solid")
    raw = f"```json\n{one}\n```\n**CORRECTED RESPONSE:**\n```json\n{two}\n```"
    record = run_single(OfflineReviewProvider(raw), Path("pkg-b.yaml"), task, 0, "pkg-b-run")
    assert record["parse_multiple_objects"] is True and record["parse_ok"] is True
    assert is_classification_valid(record) is False
    single = run_single(OfflineReviewProvider(f"```json\n{one}\n```"), Path("pkg-b.yaml"), task, 0, "pkg-b-run")
    assert single["parse_multiple_objects"] is False


def test_BF5_an_agreed_unknown_on_the_taxonomy_trigger_is_a_mandatory_review(tmp_path):
    """P8-AF1: no conflict, but the shared UNKNOWN alone decides the released CvC label."""
    from agent_arena.phase9_review import assess_case, position_from_result
    task, raw = _taxonomy_case("unknown")
    data = json.loads(raw)
    for description in data["forensic_record"]["phase8"]["evidence_descriptions"]:
        if description["evidence_id"] == "e1":
            description["attributes"]["comparison"] = None
    raw = json.dumps(data)
    position = position_from_result(task, run_agent(OfflineReviewProvider(raw), task), "run1")
    p1 = position.phase8["propositions"][0]
    assert (p1["reported_verdict"], p1["host_state"], p1["model_host_conflict"]) == ("unknown", "unknown", False)
    assert position.phase8["derived_label"] == "correlation_vs_causation"
    routed = assess_case(task, [position])
    assert any(t.code == "necessary_unknown" and t.mandatory for t in routed.triggers)
    assert run_audit(task, OfflineReviewProvider(raw), output_root=tmp_path / "out").status == "REVIEW_REQUIRED"


@pytest.mark.parametrize("stored", ["AA-P9/1.1", "AA-P9/1.2"])
def test_BF2_a_stored_older_case_state_fails_closed_under_aa_p9_1_3(tmp_path, stored):
    from tests.test_phase8_9_conflict import case, raw_output
    from agent_arena.phase9_models import CONTRACT_VERSION
    from agent_arena.phase9_runtime import execute_review, replay_review
    task, payload = case("supported", "unsupported")
    record = evaluate_run(task, "run1", [run_agent(OfflineReviewProvider(raw_output(payload)), task)])
    execute_review(record, OfflineReviewProvider(raw_output(payload)), base_dir=tmp_path, authorized=True,
                   budget_calls=2, kind="counterreview")
    assert CONTRACT_VERSION == "AA-P9/1.3"
    current = replay_review(task, base_dir=tmp_path).metadata["phase9"]
    assert current.get("history_validation") != "invalid"
    from agent_arena.phase9_review import case_key
    path = tmp_path / "phase9" / f"{case_key(task)}.json"
    text = path.read_text()
    assert '"AA-P9/1.3"' in text
    path.write_text(text.replace('"AA-P9/1.3"', f'"{stored}"'))
    stale = replay_review(task, base_dir=tmp_path).metadata["phase9"]
    assert stale["route"] == "UNRESOLVED" and stale["history_validation"] == "invalid"



# ---------------------------------------------------------------- Package B round 2 (RE4/RF3)

def test_BF8_record_fingerprint_binds_the_new_flag_only_where_present():
    from agent_arena.phase7a_real_run import _RECORD_FP_FIELDS, record_fingerprint
    from agent_arena import phase7a_execution as p7
    legacy = {field: f"v-{field}" for field in _RECORD_FP_FIELDS}
    # A frozen record without the field keeps exactly its historical fingerprint.
    assert record_fingerprint(legacy) == p7._fp({k: legacy.get(k) for k in _RECORD_FP_FIELDS})
    flagged, clear = dict(legacy, parse_multiple_objects=True), dict(legacy, parse_multiple_objects=False)
    assert record_fingerprint(flagged) != record_fingerprint(clear) != record_fingerprint(legacy)


def test_BF6_a_namespace_with_only_finder_metadata_is_not_a_prior_run(tmp_path):
    import tests.test_full_replication_contract as frc_tests
    document = frc_tests._synthetic_document()
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    (fresh / ".DS_Store").write_bytes(b"\x00\x00\x00\x01Bud1")
    builder = frc_tests._ProviderBuilder()
    frc_tests._run_synthetic(fresh, document, builder)
    assert builder.constructions >= 1


def test_registry_versions_of_package_b():
    assert (REGISTRY["input_preflight"], REGISTRY["evidence_symmetry"], REGISTRY["phase8_semantics_taxonomy"],
            REGISTRY["phase9_history_review"]) == ("1.1", "1.1.0", "1.3", "1.3")
    from agent_arena.phase10_pipeline import LIVE_REGISTRY
    assert {k: v for k, v in LIVE_REGISTRY.items() if k != "provenance"} == \
        {k: v for k, v in REGISTRY.items() if k != "provenance"}


def test_P9_F2_offline_adjudication_texts_for_blind_and_disclosed_reviews(tmp_path):
    from tests.test_phase8_9_conflict import case, raw_output
    from agent_arena.phase9_runtime import execute_review

    def model_decision(host, model, base):
        task, payload = case(host, model)
        record = evaluate_run(task, "run1", [run_agent(OfflineReviewProvider(raw_output(payload)), task)])
        reviewed = execute_review(record, OfflineReviewProvider(raw_output(payload)), base_dir=base, authorized=True,
                                  budget_calls=2, kind="counterreview")
        return next(d for d in reviewed.metadata["phase9"]["adjudications"] if d["reviewer_type"] == "model")
    disclosed = model_decision("supported", "unsupported", tmp_path / "disclosed")
    assert disclosed["reviewer_provenance"] == "Built-in offline recording via existing runner/parser"
    assert disclosed["independence"].startswith(
        "Host comparison of a recorded offline model review: model and host positions of the open conflicts supplied")
    blind = model_decision("unknown", "unknown", tmp_path / "blind")
    assert blind["independence"].startswith("Recorded offline comparison: first verdict withheld")
