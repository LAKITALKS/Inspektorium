"""Tests for the Phase 6.4A prompt-only baseline preparation (offline; no model calls).

Covers the frozen prompt bytes/digest, the four-label vocabulary and the biological
mechanism_vs_evidence scope, the deterministic answer-blind input projection, the strict
parser and Phase 6.1 confidence semantics, the frozen runtime parameters, and
determinism/leakage guarantees. All fixtures are SYNTHETIC.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from agent_arena import prompt_only_baseline as b
from agent_arena.prompt_only_baseline import (
    CONTRACT_ID,
    EXACT_MODEL_ID,
    FROZEN_LABELS,
    baseline_prompt_digest,
    build_baseline_input_projection,
    build_baseline_messages,
    build_runtime_contract,
    canonical_baseline_prompt_bytes,
    classify_baseline_confidence,
    parse_baseline_response,
    validate_baseline_result,
    validate_no_forbidden_fields,
    validate_runtime_contract,
)
from agent_arena.schemas import Task

REPO = Path(__file__).resolve().parents[1]
PILOT = REPO / "analysis" / "phase6_4_prompt_only_pilot"
FIXTURES = PILOT / "synthetic_fixtures"
OUTPUTS = PILOT / "deterministic_fixture_outputs"


def _task(**over) -> Task:
    base = {"id": "synthetic-x", "title": "syn", "domain": "study_forensics",
            "difficulty": "medium", "task_type": "study_forensics",
            "prompt": "A mouse study is described.", "gold_label": "solid"}
    base.update(over)
    return Task(**base)


# ---------------------------------------------------------------------------
# Frozen prompt bytes and digest
# ---------------------------------------------------------------------------

def test_prompt_bytes_and_digest_frozen():
    txt = (PILOT / "prompt_only_system_prompt.txt").read_bytes()
    assert txt == canonical_baseline_prompt_bytes()
    sha_file = (PILOT / "prompt_only_system_prompt.sha256").read_text().strip()
    assert sha_file == baseline_prompt_digest()
    assert sha_file == hashlib.sha256(txt).hexdigest()


def test_one_char_prompt_change_changes_digest():
    original = b.BASELINE_SYSTEM_PROMPT
    mutated = original + " "
    assert hashlib.sha256(mutated.encode()).hexdigest() != baseline_prompt_digest()


def test_four_label_vocabulary_exact():
    assert FROZEN_LABELS == ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence")
    # every label is defined in the prompt
    for lbl in FROZEN_LABELS:
        assert lbl in b.BASELINE_SYSTEM_PROMPT


def test_mechanism_vs_evidence_biologically_scoped_in_prompt():
    p = b.BASELINE_SYSTEM_PROMPT.lower()
    assert "human clinical benefit" in p
    assert "preclinical" in p or "animal" in p or "biomarker" in p
    # anti-trigger clause: the word "mechanism" alone must not force the label
    assert "do not assign this label merely because the word" in p


# ---------------------------------------------------------------------------
# Deterministic, answer-blind input projection
# ---------------------------------------------------------------------------

def test_projection_is_task_prompt_only_and_deterministic():
    t = _task(prompt="Claim text only.", gold_label="overclaim")
    assert build_baseline_input_projection(t) == "Claim text only."
    assert build_baseline_input_projection(t) == build_baseline_input_projection(t)
    msgs = build_baseline_messages(t)
    assert msgs["system"] == b.BASELINE_SYSTEM_PROMPT
    assert msgs["user"] == "Claim text only."


def test_gold_and_expected_labels_cannot_enter_prompt():
    # gold_label differs from any token in the clean prompt → not present in the message
    t = _task(prompt="A neutral claim with no label words.", gold_label="mechanism_vs_evidence",
              expected_answer="mechanism_vs_evidence", gold_summary="secret rationale text")
    msgs = build_baseline_messages(t)
    assert "mechanism_vs_evidence" not in msgs["user"]
    assert "secret rationale text" not in msgs["user"]
    assert not validate_no_forbidden_fields(t)


def test_canonical_and_dev_ids_cannot_enter_prompt():
    # forbidden-shaped tokens assembled at runtime so this tracked file holds no literal
    # canonical/DEV id (they are synthetic inputs that exercise the guard).
    canonical = "study-" + "forensics-42"
    dev = "DEV" + "-0007"
    t = _task(id=canonical, prompt="A neutral claim.", gold_label="solid")
    # the canonical id is on the task, but the projection is task.prompt only
    assert canonical not in build_baseline_input_projection(t)
    # and a prompt that embedded a DEV id would be flagged
    leak = _task(prompt=f"Refer to {dev} for the answer.", gold_label="solid")
    errs = validate_no_forbidden_fields(leak)
    assert any("dev_id" in e for e in errs)


@pytest.mark.parametrize("fx", json.loads((FIXTURES / "projection_tasks.json").read_text())["fixtures"])
def test_projection_fixtures_forbidden_field_behavior(fx):
    t = Task(**fx["task"])
    errs = validate_no_forbidden_fields(t)
    assert (not errs) == fx["expect_clean"], f"{fx['id']}: errors={errs}"
    assert build_baseline_input_projection(t) == (t.prompt or "")


def test_leaked_gold_token_is_flagged():
    fx = next(f for f in json.loads((FIXTURES / "projection_tasks.json").read_text())["fixtures"]
              if f["id"] == "t07_leaked_gold_token_in_prompt")
    t = Task(**fx["task"])
    assert validate_no_forbidden_fields(t)  # non-empty → flagged


# ---------------------------------------------------------------------------
# Strict parser + confidence semantics
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fx", json.loads((FIXTURES / "responses.json").read_text())["fixtures"])
def test_response_fixture_parse_matches_expectation(fx):
    p = parse_baseline_response(fx["raw"])
    e = fx["expect"]
    assert p.parse_ok == e["parse_ok"], fx["id"]
    assert p.ok == e["ok"], fx["id"]
    assert p.predicted_label == e["predicted_label"], fx["id"]
    assert p.confidence_validity == e["confidence_validity"], fx["id"]
    assert p.confidence_value == e["confidence_value"], fx["id"]


def test_missing_confidence_not_coerced_to_zero():
    p = parse_baseline_response('{"predicted_label":"solid","brief_reason":"x"}')
    assert p.confidence_validity == "MISSING"
    assert p.confidence_value is None


def test_bool_confidence_rejected():
    p = parse_baseline_response('{"predicted_label":"solid","confidence":true,"brief_reason":"x"}')
    assert p.confidence_validity == "INVALID"
    assert p.confidence_value is None
    assert classify_baseline_confidence(True) == "INVALID"


def test_out_of_range_confidence_rejected():
    for bad in (1.5, -0.2):
        p = parse_baseline_response(f'{{"predicted_label":"solid","confidence":{bad},"brief_reason":"x"}}')
        assert p.confidence_validity == "INVALID"
        assert p.confidence_value is None


def test_zero_confidence_is_valid():
    p = parse_baseline_response('{"predicted_label":"solid","confidence":0.0,"brief_reason":"x"}')
    assert p.confidence_validity == "VALID"
    assert p.confidence_value == 0.0


def test_malformed_json_is_parser_failure():
    p = parse_baseline_response("this is not json { , }")
    assert p.parse_ok is False
    assert p.predicted_label is None
    assert any("parser_failure" in e for e in p.errors)


def test_repaired_truncated_json_is_parser_failure_not_verdict():
    # a truncated body the shared extractor could repair must NOT be accepted as a verdict
    p = parse_baseline_response('{"predicted_label":"solid","confidence":0.7,"brief_reason":"trunc')
    assert p.parse_ok is False
    assert p.predicted_label is None


def test_extra_fields_rejected():
    p = parse_baseline_response(
        '{"predicted_label":"solid","confidence":0.7,"brief_reason":"x","chain_of_thought":"..."}')
    assert p.ok is False
    assert any("extra_fields" in e for e in p.errors)


def test_unknown_label_rejected():
    p = parse_baseline_response('{"predicted_label":"bogus","confidence":0.5,"brief_reason":"x"}')
    assert p.ok is False
    assert any("unknown_label" in e for e in p.errors)


# ---------------------------------------------------------------------------
# Baseline result record validation (envelope-ready, opaque only)
# ---------------------------------------------------------------------------

def test_baseline_result_requires_opaque_dev_id_and_frozen_labels():
    ok_record = {"dev_id": "DEV-0007", "model": EXACT_MODEL_ID,
                 "predicted_label": "solid", "gold_label": "solid", "stratum": "clear",
                 "confidence": 0.8}
    assert validate_baseline_result(ok_record) == []
    bad = dict(ok_record, dev_id="study-" + "forensics-7")  # canonical-shaped → rejected
    assert any("DEV-" in e or "opaque" in e for e in validate_baseline_result(bad))
    bad2 = dict(ok_record, predicted_label="nope")
    assert any("frozen label" in e for e in validate_baseline_result(bad2))
    bad3 = dict(ok_record, confidence=True)
    assert any("INVALID" in e for e in validate_baseline_result(bad3))


# ---------------------------------------------------------------------------
# Frozen runtime contract
# ---------------------------------------------------------------------------

def test_runtime_contract_validates_and_matches_committed():
    contract = build_runtime_contract()
    assert validate_runtime_contract(contract) == []
    committed = json.loads((PILOT / "prompt_only_runtime_contract_haiku.json").read_text())
    assert committed == contract


def test_runtime_parameters_exact():
    c = build_runtime_contract()
    assert c["exact_model_id"] == "claude-haiku-4-5-20251001"
    assert c["contract_id"] == CONTRACT_ID
    assert c["temperature"] == 0.0
    assert c["max_output_tokens"] == 4096
    assert c["replication_count"] == 1
    assert c["concurrency"] == 1
    assert c["request_timeout_seconds"] == 120
    assert c["max_transport_retries_after_initial_request"] == 2
    assert c["semantic_or_quality_retries"] == "PROHIBITED"


def test_top_p_omitted_and_seed_absent():
    c = build_runtime_contract()
    assert c["top_p"] == "OMITTED_FROM_REQUEST"
    assert c["seed"] == "UNSUPPORTED"


def test_model_id_is_dated_snapshot():
    import re
    assert re.match(r"^claude-[a-z]+-\d+-\d+-\d{8}$", EXACT_MODEL_ID)


def test_contract_binds_prompt_projection_parser_hashes():
    c = build_runtime_contract()
    assert c["system_prompt_sha256"] == baseline_prompt_digest()
    assert c["input_projection_sha256"] == b.input_projection_sha256()
    assert c["parser_contract_sha256"] == b.parser_contract_sha256()
    # tampering the prompt would break the contract
    tampered = dict(c, system_prompt_sha256="0" * 64)
    assert any("system_prompt_sha256" in e for e in validate_runtime_contract(tampered))


def test_no_semantic_retry_in_contract():
    c = build_runtime_contract()
    assert c["semantic_or_quality_retries"] == "PROHIBITED"
    assert c["prohibit_selective_reruns"] is True
    assert "parse_ok=false" in c["parser_failure_handling"]
    # retryable classes are transport-only
    for cls in c["retryable_error_classes"]:
        assert cls in ("connection_error", "request_timeout", "rate_limit_429",
                       "transient_server_error_5xx", "overloaded_529")


# ---------------------------------------------------------------------------
# Protocol / interpretation freeze (paired, not pooled; fixed metrics)
# ---------------------------------------------------------------------------

def test_protocol_is_paired_not_54_independent():
    proto = (PILOT / "paired_comparison_protocol.md").read_text()
    assert "not 54 independent cases" in proto
    assert "never" in proto.lower() and "pooled" in proto.lower()
    interp = (PILOT / "interpretation_rules.md").read_text()
    assert "increases n to 54" in interp  # listed as forbidden language
    assert "ceiling" in interp.lower()


def test_protocol_reuses_frozen_metric_definitions():
    proto = (PILOT / "paired_comparison_protocol.md").read_text()
    assert "five-bin" in proto
    assert "0.0, 0.1" in proto  # frozen tau grid
    assert "small_n" in proto and "descriptive_only" in proto


# ---------------------------------------------------------------------------
# No hidden threshold / model-selection logic; no holdout/private paths
# ---------------------------------------------------------------------------

def test_no_threshold_or_model_selection_logic():
    src = Path(b.__file__).read_text()
    for forbidden in ("select_operating_threshold", "argmax", "optimize_threshold", "def select_"):
        assert forbidden not in src
    public = [n for n in dir(b) if not n.startswith("_")]
    assert not any(n.startswith(("select", "choose", "optimize", "rank_best")) for n in public)


def test_arms_differ_in_response_contract_not_only_prompt():
    # the completed Agent Arena arm elicits/parses many more fields than the baseline;
    # the arms therefore differ in MORE than the system prompt (package-level contrast).
    from agent_arena.output_contract import _CORE_FIELDS as AA_PARSER_FIELDS
    baseline_fields = set(b.RESPONSE_REQUIRED_KEYS)
    aa_fields = set(AA_PARSER_FIELDS)
    assert baseline_fields != aa_fields
    assert len(aa_fields) > len(baseline_fields)  # ~8 core (11 elicited) vs 3
    # the response contracts share only the confidence field
    assert baseline_fields & aa_fields == {"confidence"}
    assert "predicted_label" in baseline_fields and "predicted_label" not in aa_fields


def test_contract_carries_accurate_treatment_contrast():
    c = build_runtime_contract()
    assert c["treatment_contrast"] == b.TREATMENT_CONTRAST
    assert "package-level" in c["treatment_contrast"].lower()
    assert "not the causal effect of one" in c["treatment_contrast"].lower()
    # source checkpoint present as a 40-hex commit, and NOT the execution HEAD
    import re
    assert re.match(r"^[0-9a-f]{40}$", c["repository_source_checkpoint"])
    assert "repository_commit" not in c
    # a contract that claims a system-prompt-only contrast must be rejected
    tampered = dict(c, treatment_contrast="only the system prompt differs between arms")
    errs = validate_runtime_contract(tampered)
    assert any("system-prompt only" in e or "treatment_contrast" in e for e in errs)


def test_no_artifact_falsely_claims_system_prompt_only():
    # Documentation must never state the contrast as a single-prompt-string difference.
    # (The module SOURCE legitimately contains these phrases as validator guard/detector
    # vocabulary, so it is checked via the contract metadata below, not by source scan.)
    forbidden = ("only the system prompt", "only a different system prompt",
                 "differ in exactly one thing", "system-prompt only", "system prompt only")
    for path in PILOT.glob("*.md"):
        text = path.read_text().lower()
        for phrase in forbidden:
            assert phrase not in text, f"{path.name} contains false framing: {phrase!r}"
    # contract metadata (machine-checkable) must be accurate and reject the false claim
    c = build_runtime_contract()
    for phrase in forbidden:
        assert phrase not in json.dumps(c).lower()
    assert any("system-prompt only" in e or "treatment_contrast" in e
               for e in validate_runtime_contract(dict(c, treatment_contrast="only the system prompt differs")))
    # and the accurate framing IS present in the key artifacts
    assert "package-level" in (PILOT / "pilot_rationale.md").read_text().lower()
    assert "package-level" in (PILOT / "paired_comparison_protocol.md").read_text().lower()


def test_no_holdout_or_private_path_in_module():
    src = Path(b.__file__).read_text().lower()
    # search targets assembled from fragments so this tracked test file holds no literal
    # private-path / holdout token
    for bad in ("hold" + "out", "/us" + "ers/", "agentarena" + "_iaa_private",
                "candidate" + "_eligibility"):
        assert bad not in src


# ---------------------------------------------------------------------------
# Deterministic regeneration of fixture outputs
# ---------------------------------------------------------------------------

def test_committed_fixture_outputs_reproduce():
    responses = json.loads((FIXTURES / "responses.json").read_text())["fixtures"]
    committed = json.loads((OUTPUTS / "responses_parsed.json").read_text())["results"]
    by_id = {r["id"]: r for r in committed}
    for f in responses:
        p = parse_baseline_response(f["raw"])
        assert by_id[f["id"]]["parsed"] == p.as_dict(), f["id"]


def test_committed_projection_outputs_reproduce():
    tasks = json.loads((FIXTURES / "projection_tasks.json").read_text())["fixtures"]
    committed = json.loads((OUTPUTS / "projection_outputs.json").read_text())["results"]
    by_id = {r["id"]: r for r in committed}
    for f in tasks:
        t = Task(**f["task"])
        assert by_id[f["id"]]["forbidden_field_errors"] == validate_no_forbidden_fields(t), f["id"]
