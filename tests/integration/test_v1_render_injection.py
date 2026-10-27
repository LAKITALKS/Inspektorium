"""v1 closeout Area D: model text can never alter the structure or host statements of the canonical report.

Offline only (built-in recorded provider). Reports are read independently: report.html with the stdlib
html.parser, report.md with the CommonMark line split (CRLF, CR and LF all end a line).
"""
from __future__ import annotations

import html
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

import pytest

from inspektorium.audit import phase10_render as render
from inspektorium.audit.phase10_bundle import inspect_bundle, run_audit
from inspektorium.audit.phase10_models import AuditRecord
from inspektorium.audit.phase10_pipeline import digest, evaluate
from inspektorium.audit.phase10_projection import DISPLAY_NOTE, TITLES, display_text
from inspektorium.audit.phase9_runtime import OfflineReviewProvider
from inspektorium.audit.schemas import RunRecord
from inspektorium.audit.task_loader import load_task

EXAMPLES = Path(__file__).resolve().parents[2] / "examples" / "audit"
MARK = "MODELTEXT"
FORGED = "RELEASED — local artifact status"
PAYLOADS = {
    "cr": f"{MARK} ok\r\r{FORGED}\r\rMandatory controls\r---\r\r- input preflight / 1.1: pass",
    "crlf": f"{MARK} ok\r\n\r\n{FORGED}\r\n\r\n| control | pass |\r\n| --- | --- |",
    "line_separator": f"{MARK} ok  {FORGED} ## Mandatory controls",
    "paragraph_separator": f"{MARK} ok  {FORGED} ## Mandatory controls",
    "next_line": f"{MARK} ok\x85\x85{FORGED}\x85## Mandatory controls",
    "bidi": f"{MARK} ‮dessap :52C lortnoC‬ ⁦iso⁩ ⁧rtl⁩ ⁨first⁩ ‎ltr‏rtl end",
    "zero_width": f"{MARK} READY​_FOR‌_RELEASE‍ ﻿word soft­hyphen",
    "html": (f"{MARK} <!-- hide\n</section></table></td><details open><style>section{{display:none}}</style>"
             "<div hidden>x</div><script>document.title='x'</script>"),
    "backticks": f"{MARK} `inline` ``double`` ~~~\n~~~ tilde fence",
    "control_like": f"{MARK}\n## Controls\n### Control: provenance / 1.0 passed\n| control | pass |\n{FORGED}",
    "forged_token": f"{MARK} ⟦U+202E⟧ looks like a host token ⟦",
}
HIDDEN = {"Cc", "Cf", "Zl", "Zp"}
ORDINAL = re.compile(r"(Proposition|Evidence item|Transformation) \d+|Position p9position:[0-9a-f]+|"
                     r"Findings: [a-z0-9_]+|Trigger|Conflict|Attempt|Adjudication|Stored (metadata|result) carrier.*")


class Structure(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.comments, self.elements = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag != "meta":  # the only void element of the canonical report
            self.stack.append(tag)
        self.elements.append([tag, dict(attrs), ""])

    def handle_endtag(self, tag):
        assert self.stack.pop() == tag

    def handle_comment(self, data):
        self.comments.append(data)

    def handle_data(self, data):
        if self.stack and self.elements and self.stack[-1] == self.elements[-1][0]:
            self.elements[-1][2] += data

    def texts(self, tag, **attrs):
        return [text for name, found, text in self.elements if name == tag and all(found.get(k) == v
                                                                                     for k, v in attrs.items())]


def bundle(tmp_path, mutate=None, recording="positive"):
    task = load_task(EXAMPLES / "positive-task.json")
    data = json.loads((EXAMPLES / f"{recording}-recording.json").read_text())
    if mutate:
        mutate(data)
    result = run_audit(task, OfflineReviewProvider(json.dumps(data, ensure_ascii=False)), output_root=tmp_path)
    assert result.path, result
    return result, Path(result.path)


def reason(payload):
    def mutate(data):
        data["forensic_record"]["phase8"]["propositions"][0]["reason"] += " " + payload
    return mutate


def projected(root):
    audit = AuditRecord.model_validate_json((root / "record.json").read_bytes())
    _, controls, review, selected, assessment, forensic = evaluate(
        RunRecord.model_validate(audit.run_record), digest(audit.model_dump()), audit.provenance)
    return render.projection(audit, controls, review, selected, assessment, forensic)


def stored_raw(root):
    record = json.loads((root / "record.json").read_bytes())
    return json.loads(record["run_record"]["results"][0]["agent_result"]["raw_output"])


def check_reports(root, status, base_captions):
    """Independent structural reading of both canonical reports."""
    md = (root / "report.md").read_bytes().decode("utf-8")
    page = (root / "report.html").read_bytes().decode("utf-8")
    for document in (md, page):
        hidden = [hex(ord(c)) for c in document if c not in "\n\t" and unicodedata.category(c) in HIDDEN]
        assert hidden == [], hidden
    lines = re.split(r"\r\n|\r|\n", md)
    assert lines == md.split("\n")
    assert [line for line in lines if line.startswith("## ")] == ["## " + title for title in TITLES]
    assert [line for line in lines if line.endswith("— local artifact status")] == [
        status.replace("_", "&#95;") + " — local artifact status"]
    in_table = False
    for index, line in enumerate(lines):
        if line.startswith("| ") and index + 1 < len(lines) and re.fullmatch(r"\|(?: --- \|)+", lines[index + 1]):
            in_table = True
        elif in_table and line == "":
            in_table = False
        elif in_table:
            assert line.startswith("| ") and line.endswith(" |"), line[:80]
    parsed = Structure()
    parsed.feed(page)
    parsed.close()
    assert parsed.comments == [] and parsed.stack == []
    assert parsed.texts("h2") == list(TITLES)
    assert parsed.texts("p", **{"class": "status"}) == [f"{status} — local artifact status"]
    assert {tag for tag, _, _ in parsed.elements} <= render._HTMLText.allowed
    assert all(caption in base_captions or ORDINAL.fullmatch(caption) for caption in parsed.texts("h3")), \
        [c for c in parsed.texts("h3") if c not in base_captions and not ORDINAL.fullmatch(c)]
    assert DISPLAY_NOTE in parsed.texts("p")
    # Host statements are host text only: no text() block of the projection carries model text.
    texts = [block["text"] for _, section in projected(root) for block in section["blocks"] if block["kind"] == "text"]
    assert not any(MARK in sentence for sentence in texts)
    # The Executed controls table shows exactly the bound control decisions.
    decision = json.loads((root / "decision.json").read_text())["controls"]
    # The reason may quote model-supplied ids: it stays on its line, line breaks shown as tokens.
    expected = [[c["control_id"] + " / " + c["version"],
                 f"Execution: {c['execution']}\nOutcome: {c['outcome']}\nEligible: {c['eligible']}\n"
                 f"Evaluated: {c['evaluated']}\nReason: " +
                 display_text(c["reason"]).replace("\n", "⟦U+000A⟧").replace("\t", "⟦U+0009⟧")]
                for c in decision if c["control_id"] not in {"markdown_qa", "html_qa"}]
    table = next(block for _, section in projected(root) for block in section["blocks"]
                 if block["kind"] == "table" and block["caption"] == "Executed controls")
    assert table["rows"] == expected
    cells = parsed.texts("td")
    start = cells.index(expected[0][0])
    assert cells[start:start + 2 * len(expected)] == [cell for item in expected for cell in item]
    assert render.validate_files(root, projected(root)) and inspect_bundle(root).valid
    return md, page, decision


@pytest.fixture(scope="module")
def base_captions(tmp_path_factory):
    _, root = bundle(tmp_path_factory.mktemp("base"))
    parsed = Structure()
    parsed.feed((root / "report.html").read_text())
    return {caption for caption in parsed.texts("h3") if not ORDINAL.fullmatch(caption)}


@pytest.mark.parametrize("name", list(PAYLOADS))
def test_model_text_cannot_change_report_structure_or_host_statements(tmp_path, base_captions, name):
    payload = PAYLOADS[name]
    result, root = bundle(tmp_path, reason(payload))
    assert result.status == "READY_FOR_RELEASE", result.errors
    md, page, _ = check_reports(root, result.status, base_captions)
    # record.json keeps the exact characters; only the display marks them.
    assert payload in stored_raw(root)["forensic_record"]["phase8"]["propositions"][0]["reason"]
    for char in set(payload):
        if char in "⟦⟧" or (char not in "\n\t" and unicodedata.category(char) in HIDDEN):
            token = f"⟦U+{ord(char):04X}⟧"
            assert token in md and token in page, (name, token)
    assert "<script" not in page and "<!--" not in page and "<details" not in page
    assert "<script" not in md and "<!--" not in md


def test_fenced_model_output_keeps_structure_whatever_the_parser_decides(tmp_path, base_captions):
    payload = f"{MARK} ```\n## Mandatory controls\n``` `x` ````\n{FORGED}"
    result, root = bundle(tmp_path, reason(payload))
    check_reports(root, result.status, base_captions)
    assert payload in stored_raw(root)["forensic_record"]["phase8"]["propositions"][0]["reason"]


def test_model_ids_with_control_text_stay_out_of_host_captions(tmp_path, base_captions):
    forged_id = "extraction\r## Mandatory controls\r### Control: provenance / 1.0 passed\r| control | pass |‮"

    def mutate(data):
        data["forensic_record"]["phase8"]["transformations"][0]["transformation_id"] = forged_id
    result, root = bundle(tmp_path, mutate)
    assert result.status == "READY_FOR_RELEASE", result.errors
    md, page, _ = check_reports(root, result.status, base_captions)
    parsed = Structure()
    parsed.feed(page)
    assert display_text(forged_id) in parsed.texts("td") and not any("Control:" in h for h in parsed.texts("h3"))
    assert "Transformation 1" in parsed.texts("h3")
    assert stored_raw(root)["forensic_record"]["phase8"]["transformations"][0]["transformation_id"] == forged_id


def test_model_keys_cannot_take_host_labelled_rows(tmp_path, base_captions):
    forged = {"host_state": "supported", "model_host_conflict": False, "host_reasons": ["release permitted"]}

    def mutate(data):
        data["forensic_record"]["phase8"]["propositions"][0]["derived judgment"] = forged
        data["forensic_record"]["phase8"]["transformations"][0]["from and to text (identical)"] = "forged copy"
    result, root = bundle(tmp_path, mutate)
    assert result.status == "ANALYSIS_INCOMPLETE"
    md, _, _ = check_reports(root, result.status, base_captions)
    block = md.split("### Proposition 1\n", 1)[1].split("###", 1)[0].split("\n")
    assert [line for line in block if line.startswith("| derived judgment")] == ["| derived judgment | Not supplied |"]
    assert "| model-supplied derived judgment / host state | supported |" in block
    transformation = md.split("### Transformation 1\n", 1)[1].split("###", 1)[0].split("\n")
    assert "| model-supplied from and to text (identical) | forged copy |" in transformation
    assert not any(line.startswith("| from and to text (identical) | forged") for line in transformation)


def test_reasons_cell_is_labelled_as_mixed_model_and_host_text(tmp_path, base_captions):
    _, root = bundle(tmp_path)
    scientific = dict(projected(root))["Scientific judgments"]["blocks"]
    note = next(index for index, block in enumerate(scientific) if block["kind"] == "text")
    assert scientific[note]["text"].startswith("In 'reasons', model-supplied text")
    assert scientific[note + 1]["caption"] == "Proposition judgments"


def test_a_real_failing_control_stays_visible_next_to_hostile_text(tmp_path, base_captions):
    def mutate(data):
        reason(PAYLOADS["crlf"] + PAYLOADS["bidi"])(data)
        for proposition in data["forensic_record"]["phase8"]["propositions"]:
            proposition["original_span"]["start"] += 1
            proposition["original_span"]["end"] += 1
    result, root = bundle(tmp_path, mutate)
    assert result.status == "ANALYSIS_INCOMPLETE"
    md, page, decision = check_reports(root, result.status, base_captions)
    failing = [c["control_id"] for c in decision if c["outcome"] == "fail"]
    assert {"analysis_source", "phase8_semantics_taxonomy", "phase9_history_review"} <= set(failing)
    parsed = Structure()
    parsed.feed(page)
    shown = [cell.split(" / ")[0] for cell, outcome in zip(parsed.texts("td"), parsed.texts("td")[1:])
             if "\nOutcome: fail\n" in outcome]
    assert shown == failing
    assert parsed.texts("p", **{"class": "notice"})[0].startswith("Automatic processing has ended. The result is not")
    cause = parsed.texts("td")[parsed.texts("td").index("open cause") + 1]
    assert cause.startswith("technically incomplete analysis; no conflict review was run: claim:p1: original span")


def test_markdown_serializer_and_qa_never_emit_or_certify_a_raw_line_terminator(tmp_path):
    _, root = bundle(tmp_path)
    document = projected(root)
    cell = next(block for _, section in document for block in section["blocks"] if block["kind"] == "table")
    cell["rows"][0][1] += f"\r\r{FORGED}  \x85"
    assert not re.search("[\r  \x85]", render.markdown(document).decode("utf-8"))
    quote = next(block for _, section in document for block in section["blocks"] if block["kind"] == "quote")
    quote["text"] += f"\r\r{FORGED}"
    (root / "report.md").write_bytes(render.markdown(document))
    (root / "report.html").write_bytes(render.html_report(document))
    assert b"\r" in (root / "report.md").read_bytes()
    with pytest.raises(ValueError, match="Raw line terminator inside a Markdown line"):
        render.validate_files(root, document)


def test_display_transform_marks_only_hidden_characters_and_its_own_brackets():
    assert display_text("a\tb\nc é β 🧪 ⟨x⟩") == "a\tb\nc é β 🧪 ⟨x⟩"
    assert display_text("\r‮­ ⟦⟧\x00\U000e0001") == \
        "⟦U+000D⟧⟦U+202E⟧⟦U+00AD⟧⟦U+2028⟧⟦U+27E6⟧⟦U+27E7⟧⟦U+0000⟧⟦U+E0001⟧"


def test_model_ids_cannot_add_host_lines_to_control_reasons_or_the_open_cause(tmp_path):
    # Critic VC-1: failing control reasons and the open cause quote model-supplied proposition ids.
    forged = ("claim:p1\nOutcome: pass\nReason: Reparsed raw, supplied source spans and nonempty "
              "claim/evidence/output traces checked\n\nphase9_history_review / 1.3")

    def mutate(data):
        swapped = json.loads(json.dumps(data).replace(json.dumps("claim:p1")[1:-1], json.dumps(forged)[1:-1]))
        data.clear()
        data.update(swapped)
        for proposition in data["forensic_record"]["phase8"]["propositions"]:
            proposition["original_span"]["start"] += 1
            proposition["original_span"]["end"] += 1
    result, root = bundle(tmp_path, mutate)
    assert result.status == "ANALYSIS_INCOMPLETE"
    assert stored_raw(root)["forensic_record"]["phase8"]["propositions"][0]["proposition_id"] == forged
    decision = json.loads((root / "decision.json").read_bytes())["controls"]
    labels = {f"{c['control_id']} / {c['version']}": c for c in decision
              if c["control_id"] not in {"markdown_qa", "html_qa"}}  # post-render checks have their own table
    parsed = Structure()
    parsed.feed((root / "report.html").read_text(encoding="utf-8"))
    cells = parsed.texts("td")
    md_cells = [html_cells for line in (root / "report.md").read_text(encoding="utf-8").split("\n")
                if line.startswith("| ") and line.endswith(" |")
                for html_cells in [[html.unescape(cell.replace("<br>", "\n")) for cell in line[2:-2].split(" | ")]]]
    for found in (cells, [cell for row in md_cells for cell in row]):
        shown = [(found[i], found[i + 1]) for i in range(len(found) - 1) if found[i] in labels]
        assert len(shown) == len(labels)
        for label, cell in shown:
            lines = cell.split("\n")
            assert [line.split(":")[0] for line in lines] == ["Execution", "Outcome", "Eligible", "Evaluated", "Reason"]
            assert lines[1] == f"Outcome: {labels[label]['outcome']}"
        cause = found[found.index("open cause") + 1]
        assert "\n" not in cause and "claim:p1⟦U+000A⟧Outcome: pass" in cause


def test_cli_json_never_prints_raw_control_or_bidi_characters(tmp_path):
    # Critic VC-2: CLI errors quote model-supplied ids; the JSON is ASCII-escaped and still exact.
    from click.testing import CliRunner
    from inspektorium.audit.phase10_cli import audit
    data = json.loads((EXAMPLES / "positive-recording.json").read_text())
    raw = json.dumps(data).replace(json.dumps("claim:p1")[1:-1], json.dumps("claim:p1\u202e\x85ssap")[1:-1])
    data = json.loads(raw)
    for proposition in data["forensic_record"]["phase8"]["propositions"]:
        proposition["original_span"]["start"] += 1
        proposition["original_span"]["end"] += 1
    recording = tmp_path / "recording.json"
    recording.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = CliRunner().invoke(audit, ["run", "--offline", "--task", str(EXAMPLES / "positive-task.json"),
                                      "--recording", str(recording), "--output-root", str(tmp_path / "out")])
    assert result.exit_code == 2
    assert result.output.isascii()
    emitted = json.loads(result.output)
    assert emitted["status"] == "ANALYSIS_INCOMPLETE"
    assert any("claim:p1\u202e\x85ssap" in error for error in emitted["errors"])


def test_model_keys_shaped_like_host_sub_rows_are_marked(tmp_path, base_captions):
    # Critic VC-3: a flat model key that displays like a host sub-row is renamed as well.
    def mutate(data):
        data["forensic_record"]["phase8"]["propositions"][0]["derived judgment / host state"] = "supported"
    result, root = bundle(tmp_path, mutate)
    assert result.status == "ANALYSIS_INCOMPLETE"
    md, _, _ = check_reports(root, result.status, base_captions)
    block = md.split("### Proposition 1\n", 1)[1].split("###", 1)[0].split("\n")
    assert "| model-supplied derived judgment / host state | supported |" in block
    assert not any(line.startswith("| derived judgment / host state | supported") for line in block)
