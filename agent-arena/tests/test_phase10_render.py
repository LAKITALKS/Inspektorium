"""Human report contract and independent byte/content QA, separate from acceptance."""
import hashlib
import json
from copy import deepcopy
from html import unescape
from pathlib import Path

import pytest

from agent_arena import phase10_render as render
from agent_arena.evaluator import evaluate_run
from agent_arena.phase10_bundle import (
    create_candidate, inspect_bundle, release_candidate, review_candidate, run_audit,
)
from agent_arena.phase10_models import AuditRecord
from agent_arena.phase10_pipeline import digest, evaluate
from agent_arena.phase10_projection import TITLES
from agent_arena.phase9_runtime import OfflineReviewProvider, execute_review, submit_human_review
from agent_arena.runner import run_agent
from agent_arena.schemas import RunRecord
from tests.test_phase10_bundle import recorded


def document(directory, *, state="supported", task=None, raw=None):
    if task is None:
        task, raw = recorded(state)
    outcome = run_audit(task, OfflineReviewProvider(raw), output_root=directory)
    assert outcome.path, outcome
    root = Path(outcome.path)
    audit = AuditRecord.model_validate_json((root / "record.json").read_text())
    record = RunRecord.model_validate(audit.run_record)
    _, controls, review, selected, assessment, forensic = evaluate(record, digest(audit.model_dump()), audit.provenance)
    projected = render.projection(audit, controls, review, selected, assessment, forensic)
    return root, audit, projected


def visible(root):
    parser = render._HTMLText()
    parser.feed((root / "report.html").read_text())
    return parser.tokens


def test_semantic_report_is_complete_without_machine_dump_duplicates(tmp_path):
    root, audit, projected = document(tmp_path)
    text = "\n".join(value for _, value in visible(root))
    assert [value for kind, value in visible(root) if kind == "h2"] == list(TITLES)
    for expected in (audit.run_record["task"]["prompt"], "claim:p1", "e1", "controlled_intervention",
                     "direct", "support", "adults", "clinical_event", "12 weeks", "source_reported",
                     "External search executed: false.", "UNKNOWN", "READY_FOR_RELEASE", "not_applicable"):
        assert expected in text
    raw = audit.run_record["results"][0]["agent_result"]["raw_output"]
    assert raw not in text
    assert "artifact_binding.py" not in text  # full index remains in manifest
    assert "manifest.json#/provenance/code/module_hashes" in text
    assert "raw response reference" in text
    assert audit.run_record["results"][0]["agent_result"]["raw_output"] == raw
    assert render.validate_files(root, projected)
    assert inspect_bundle(root).valid


@pytest.mark.parametrize("format", ["markdown", "html"])
@pytest.mark.parametrize("mutation", ["cell", "order", "missing"])
def test_independent_qa_rejects_bad_content_even_if_serializer_agrees(tmp_path, monkeypatch, format, mutation):
    root, _, projected = document(tmp_path)
    function, filename = ("markdown", "report.md") if format == "markdown" else ("html_report", "report.html")
    raw = (root / filename).read_bytes()
    if mutation == "cell":
        altered = raw.replace(b"supported", b"unsupported", 1)
    elif mutation == "order":
        altered = raw.replace(b"Original claim", b"__SWAP__", 1).replace(
            b"Scientific judgments", b"Original claim", 1).replace(b"__SWAP__", b"Scientific judgments", 1)
    else:
        altered = raw.replace(render.NOTICE.encode(), b"", 1)
    assert raw != altered
    (root / filename).write_bytes(altered)
    monkeypatch.setattr(render, function, lambda _: altered)
    with pytest.raises(ValueError, match="parity"):
        render.validate_files(root, projected)


@pytest.mark.parametrize("injection", ['<script>alert(1)</script>', '<iframe src="https://example.invalid"></iframe>',
                                      '<p style="display:none">hidden</p>', '<img src=x onerror=alert(1)>',
                                      '<style>body{display:none}</style>'])
def test_active_or_hidden_content_rejected_independently(tmp_path, monkeypatch, injection):
    root, _, projected = document(tmp_path)
    altered = (root / "report.html").read_bytes().replace(b"</body>", injection.encode() + b"</body>")
    (root / "report.html").write_bytes(altered)
    monkeypatch.setattr(render, "html_report", lambda _: altered)
    with pytest.raises(ValueError):
        render.validate_files(root, projected)


@pytest.mark.parametrize("fenced", [False, True])
def test_long_hostile_unicode_and_literal_fences_roundtrip_as_text(tmp_path, fenced):
    task, raw = recorded()
    hostile = "Café β 🧪 <img src=x onerror=alert(1)> [RELEASED](javascript:alert(1)) & O'Brien\n```\n## false status\n" + "W" * 1400 + " END_LONG_VALUE."
    if not fenced:
        hostile = hostile.replace("```", "quoted boundary")
    task = task.model_copy(update={"prompt": task.prompt.replace("endpoint Delta", hostile),
                                   "context": task.context.replace("endpoint Delta", hostile)})
    payload = json.loads(raw.replace("endpoint Delta", "REPLACE_ENDPOINT"))
    def replace(value):
        if isinstance(value, str):
            return value.replace("REPLACE_ENDPOINT", hostile)
        if isinstance(value, list):
            return [replace(item) for item in value]
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        return value
    payload = replace(payload)
    payload["forensic_record"]["phase8"]["propositions"][0]["original_span"]["end"] = len(task.prompt)
    root, _, projected = document(tmp_path, task=task, raw=json.dumps(payload))
    # Existing structured parser treats embedded fences as repaired/incomplete; preserve that guard.
    assert inspect_bundle(root).status == ("ANALYSIS_INCOMPLETE" if fenced else "READY_FOR_RELEASE")
    assert ("pre", task.prompt) in visible(root)
    assert any(hostile in value for _, value in visible(root))
    html = (root / "report.html").read_text()
    assert "<img" not in html and "<script" not in html
    assert "&lt;img" in html
    assert "END_LONG_VALUE." in (root / "report.md").read_text()
    assert "overflow:hidden" not in html and "overflow:clip" not in html
    assert "table-header-group" in html and "@media print" in html and "pre-wrap" in html
    assert render.validate_files(root, projected)


def test_optional_unknown_remains_visible_without_strengthening(tmp_path):
    task, raw = recorded()
    payload = json.loads(raw)
    prop = deepcopy(payload["forensic_record"]["phase8"]["propositions"][0])
    prop.update(proposition_id="claim:optional", materiality="optional", reported_verdict="unknown",
                evidence_bindings=[], uncertainty=["Optional contextual meaning is unresolved."])
    payload["forensic_record"]["phase8"]["propositions"].append(prop)
    root, _, _ = document(tmp_path, task=task, raw=json.dumps(payload))
    assert inspect_bundle(root).status == "READY_FOR_RELEASE"
    for filename in ("report.md", "report.html"):
        text = unescape((root / filename).read_text())
        assert "claim:optional" in text and "Optional contextual meaning is unresolved." in text
        assert "unknown" in text and "bounded_unknown" in text


def resolve_pointer(record, reference):
    assert reference.startswith("record.json#/")
    value = record
    for part in reference.removeprefix("record.json#/").split("/"):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def test_every_history_position_and_adjudication_is_visible_with_resolving_raw_refs(tmp_path):
    task, original_raw = recorded("unknown")
    original = evaluate_run(task, "review-original", [run_agent(OfflineReviewProvider(original_raw), task)])
    _, review_raw = recorded()
    compared = execute_review(original, OfflineReviewProvider(review_raw), base_dir=tmp_path / "state",
                              authorized=True, budget_calls=2)
    selected = compared.metadata["phase9"]["positions"][-1]["position_id"]
    resolved = submit_human_review(compared, base_dir=tmp_path / "state", selected_position_id=selected,
                                   reviewer_provenance="human example", reason="Resolve the represented interpretation")
    outcome = create_candidate(resolved, output_root=tmp_path / "bundles")
    assert outcome.status == "READY_FOR_RELEASE", outcome
    root = Path(outcome.path)
    record = json.loads((root / "record.json").read_text())
    tokens = visible(root)
    text = "\n".join(value for _, value in tokens)
    for position in resolved.metadata["phase9"]["positions"]:
        assert position["position_id"] in text
        assert position["raw_sha256"] in text
    for decision in resolved.metadata["phase9"]["adjudications"]:
        assert decision["adjudication_id"] in text and decision["reason"] in text
    assert "counterreview" in text and "human example" in text
    references = [value for kind, value in tokens if kind == "td" and value.endswith("/raw_output")]
    raw_values = [resolve_pointer(record, reference) for reference in references]
    assert set(raw_values) == {original_raw, review_raw}
    assert {hashlib.sha256(raw.encode()).hexdigest() for raw in raw_values} == {
        p["raw_sha256"] for p in resolved.metadata["phase9"]["positions"]}
    assert original_raw not in text and review_raw not in text


def test_missing_required_section_is_not_a_supported_projection(tmp_path):
    root, _, projected = document(tmp_path)
    projected.pop(5)
    with pytest.raises(ValueError, match="section"):
        render.validate_files(root, projected)


@pytest.mark.parametrize("part", ["style", "viewport"])
def test_missing_print_or_narrow_contract_is_not_approved_by_matching_serializer(tmp_path, monkeypatch, part):
    root, _, projected = document(tmp_path)
    raw = (root / "report.html").read_text()
    removed = '<style>' + render.STYLE + '</style>' if part == "style" else (
        '<meta name="viewport" content="width=device-width,initial-scale=1">')
    altered = raw.replace(removed, '').encode()
    assert altered != raw.encode()
    (root / "report.html").write_bytes(altered)
    monkeypatch.setattr(render, "html_report", lambda _: altered)
    with pytest.raises(ValueError, match="Mandatory"):
        render.validate_files(root, projected)


def test_invalid_history_displays_positions_from_every_preserved_carrier(tmp_path):
    task, raw = recorded("unknown")
    original = evaluate_run(task, "original", [run_agent(OfflineReviewProvider(raw), task)])
    _, counter = recorded("contradicted")
    compared = execute_review(original, OfflineReviewProvider(counter), base_dir=tmp_path / "state",
                              authorized=True, budget_calls=2)
    stale = compared.model_copy(deep=True)
    stale.metadata["phase9"] = deepcopy(original.metadata["phase9"])
    outcome = create_candidate(stale, output_root=tmp_path / "bundles")
    assert outcome.status == "REVIEW_REQUIRED", outcome
    root = Path(outcome.path)
    tokens = visible(root)
    text = "\n".join(value for _, value in tokens)
    assert "invalid" in text and "Stored result carrier" in text
    for position in compared.metadata["phase9"]["positions"]:
        assert position["position_id"] in text
    record = json.loads((root / "record.json").read_text())
    refs = [value for kind, value in tokens if kind == "td" and value.endswith("/raw_output")]
    assert {resolve_pointer(record, ref) for ref in refs} == {raw, counter}


def test_released_human_revision_has_only_actual_bound_host_record_references(tmp_path):
    root, first, _ = document(tmp_path / "bundles", state="unknown")
    _, correction = recorded()
    position_id = first.run_record["metadata"]["phase9"]["positions"][0]["position_id"]
    reviewed = review_candidate(root, output_root=tmp_path / "bundles", state_dir=tmp_path / "state",
                                selected_position_id=position_id, reviewer="host reviewer",
                                reason="Correct represented interpretation", corrected_raw_output=correction)
    assert reviewed.status == "READY_FOR_RELEASE", reviewed
    released = release_candidate(Path(reviewed.path), output_root=tmp_path / "bundles",
                                 reviewer="local operator", reason="Approve local artifact")
    assert released.status == "RELEASED", released
    directory = Path(released.path)
    audit = AuditRecord.model_validate_json((directory / "record.json").read_text())
    _, controls, review, selected, assessment, forensic = evaluate(
        RunRecord.model_validate(audit.run_record), digest(audit.model_dump()), audit.provenance)
    projected = render.projection(audit, controls, review, selected, assessment, forensic)
    references = [ref for _, section in projected for block in section["blocks"]
                  for ref in block.get("record_references", [])]
    assert references
    for ref in references:
        assert digest(resolve_pointer(audit.model_dump(), ref["path"])) == ref["target_fingerprint"]
    binding_refs = [ref for ref in references if ref["path"].endswith("/position_fingerprints")]
    assert binding_refs
    assert all(ref["path"].startswith("record.json#/run_record/metadata/phase9/adjudications/")
               for ref in binding_refs)
    html_tokens = visible(directory)
    md_tokens = render._markdown_tokens((directory / "report.md").read_text())
    for ref in references:
        assert ("td", ref["path"]) in html_tokens and ("td", ref["path"]) in md_tokens
    assert inspect_bundle(directory).valid


@pytest.mark.parametrize("wrong_path", ["record.json#/run_record/missing/0", "record.json#/run_record/task/prompt"])
def test_reference_qa_rejects_nonresolving_and_wrong_existing_target(tmp_path, wrong_path):
    root, _, projected = document(tmp_path)
    block = next(block for _, section in projected for block in section["blocks"]
                 if block.get("record_references"))
    reference = block["record_references"][0]
    reference["path"] = wrong_path
    block["rows"][reference["row"]][reference["column"]] = wrong_path
    # Both formats and their expected content agree on the bad pointer. Only
    # independent resolution/content binding can reject it.
    (root / "report.md").write_bytes(render.markdown(projected))
    (root / "report.html").write_bytes(render.html_report(projected))
    with pytest.raises(ValueError, match="Host record reference"):
        render.validate_files(root, projected)


def test_reference_like_foreign_prose_is_not_interpreted_as_host_pointer(tmp_path):
    task, raw = recorded()
    response = json.loads(raw)
    foreign = "Quoted model reason: record.json#/does/not/exist is foreign text, not a host reference."
    response["forensic_record"]["phase8"]["propositions"][0]["reason"] = foreign
    root, _, projected = document(tmp_path, task=task, raw=json.dumps(response))
    assert ("td", foreign) in visible(root)
    assert inspect_bundle(root).valid
    assert render.validate_files(root, projected)
