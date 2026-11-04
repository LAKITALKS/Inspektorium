"""Import and analysis, tested on invented outputs only."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import analyze as an
import genius_loader as loader
import import_runs as imp
import pytest

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/output.schema.json"
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text("utf-8"))
SENTENCES = [
    "Das Auto fährt 300 km weit.",
    "Der Akku lädt in 30 Minuten.",
    "Wasserstoff bleibt sehr teuer.",
]
ANNOTATED = {"toy": {"S1": ["K1"], "S2": ["K1", "K4"], "S3": ["K4"]}}
TARGETS = {"toy": {"v1": [{"sid": "S2", "accepted_categories": ["Zahl"]}]}}
META = {
    "date": "2026-11-20",
    "time": "14:30",
    "model_name": "Spielmodell 1",
    "chat_mode": "Temporärer Chat",
    "account_type": "Kostenlos",
}


def _meta(**changes: object) -> bytes:
    fields: dict[str, object] = {**META, **changes}
    return json.dumps({k: v for k, v in fields.items() if v is not None}).encode()


def _comment(
    scope: str = "local",
    quotes: list[tuple[str, str]] | None = None,
    criteria: list[str] | None = None,
    text: str = "Ein Kommentar.",
) -> dict[str, Any]:
    return {
        "text": text,
        "scope": scope,
        "quotes": [{"sid": sid, "quote": quote} for sid, quote in quotes or []],
        "criteria": criteria or [],
    }


def _error(sid: str, quote: str, category: str) -> dict[str, str]:
    return {"sid": sid, "quote": quote, "category": category, "explanation": "Weil."}


def _output(
    comments: list[dict[str, Any]] | None = None,
    errors: list[dict[str, str]] | None = None,
    grade: int = 3,
) -> bytes:
    payload = {"grade": grade, "comments": comments or [], "errors": errors or []}
    return json.dumps(payload).encode()


class Lab:
    """An invented study folder."""

    def __init__(self, root: Path) -> None:
        self.runs = root / "runs"
        self.banks = root / "banks"
        self.banks.mkdir()
        bank = loader.build_bank("toy", SENTENCES)
        (self.banks / "toy.json").write_bytes(loader.dump_json(bank.as_dict()))
        (self.banks / "toy.v1.json").write_bytes(loader.dump_json(bank.as_dict()))

    def add(
        self,
        raw: bytes | None,
        repetition: str = "1",
        model: str = "spiel",
        text_id: str = "toy",
        version: str = "original",
        meta: bytes | None = None,
    ) -> None:
        folder = self.runs / model / text_id / version
        folder.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            (folder / f"{repetition}.json").write_bytes(raw)
        (folder / f"{repetition}.meta.json").write_bytes(
            json.dumps(META).encode() if meta is None else meta
        )

    def imported(self) -> list[imp.RunRecord]:
        return imp.import_all(self.runs, self.banks, SCHEMA)

    def records(self) -> list[dict[str, Any]]:
        return [asdict(record) for record in self.imported()]


@pytest.fixture
def lab(tmp_path: Path) -> Lab:
    return Lab(tmp_path)


def test_a_clean_run_is_usable_with_its_metadata(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "fährt 300 km")])]))
    run = lab.imported()[0]
    assert run.status == imp.USABLE
    assert (run.date, run.time) == ("2026-11-20", "14:30")
    assert (run.model_name, run.chat_mode) == ("Spielmodell 1", "Temporärer Chat")
    assert run.account_type == "Kostenlos"
    assert (run.model, run.text_id, run.version, run.repetition) == (
        "spiel",
        "toy",
        "original",
        "1",
    )
    assert run.references[0].origin_strict == imp.DELIVERED_VALID


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(b"", id="empty"),
        pytest.param(b"Hier ist meine Bewertung.", id="prose"),
        pytest.param(b"not json {", id="broken"),
        pytest.param(b'{"grade": 3, "comments": [], "errors": [], "x": 1}', id="extra"),
        pytest.param(b'{"grade": 3, "comments": []}', id="missing-key"),
        pytest.param(
            b'{"grade": 3, "grade": 4, "comments": [], "errors": []}', id="dup"
        ),
        pytest.param(_output(grade=0), id="grade-low"),
        pytest.param(_output(grade=7), id="grade-high"),
        pytest.param(b'{"grade": true, "comments": [], "errors": []}', id="grade-bool"),
        pytest.param(b'{"grade": "3", "comments": [], "errors": []}', id="grade-text"),
        pytest.param(_output([_comment(scope="partly")]), id="bad-scope"),
        pytest.param(_output([_comment(criteria=["K8"])]), id="bad-criterion"),
        pytest.param(
            b'{"grade": 3, "comments": [], "errors": '
            b'[{"sid": "S1", "quote": "x", "category": 7, "explanation": "y"}]}',
            id="category-not-text",
        ),
        pytest.param(
            b'{"grade": 3, "comments": [], "errors": '
            b'[{"sid": "S1", "quote": "x", "explanation": "y"}]}',
            id="category-missing",
        ),
        pytest.param(_output([_comment(quotes=[("1", "x")])]), id="bad-sid"),
        pytest.param(_output([_comment(quotes=[("S1\n", "x")])]), id="sid-newline"),
    ],
)
def test_an_unreadable_output_is_a_failure(lab: Lab, raw: bytes) -> None:
    lab.add(raw)
    run = lab.imported()[0]
    assert (run.status, run.failure_reason) == (imp.FAILED, "unreadable_output")
    assert run.references == []


@pytest.mark.parametrize(
    "wrap",
    [
        pytest.param("```json\n{}\n```", id="json-fence"),
        pytest.param("```JSON\n{}\n```", id="upper-case-tag"),
        pytest.param("```\n{}\n```", id="plain-fence"),
        pytest.param("```json\r\n{}\r\n```\r\n", id="windows-line-ends"),
        pytest.param("\n  ```json  \n{}\n```\n\n", id="outer-whitespace"),
    ],
)
def test_one_enclosing_code_block_is_removed(lab: Lab, wrap: str) -> None:
    body = _output([_comment(quotes=[("S1", "300 km")])]).decode()
    lab.add(wrap.replace("{}", body).encode())
    run = lab.imported()[0]
    assert (run.status, run.code_fence_removed) == (imp.USABLE, True)
    assert run.references[0].origin_strict == imp.DELIVERED_VALID


def test_an_answer_without_a_code_block_is_not_marked(lab: Lab) -> None:
    lab.add(_output())
    run = lab.imported()[0]
    assert (run.status, run.code_fence_removed) == (imp.USABLE, False)


def test_backticks_inside_a_comment_survive_the_removal(lab: Lab) -> None:
    body = _output([_comment(text="Siehe ``` hier.")]).decode()
    lab.add(f"```json\n{body}\n```".encode())
    assert lab.imported()[0].status == imp.USABLE


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(b'```json\n{"grade": 3,\n```', id="broken-json-in-block"),
        pytest.param(b"```json\n```", id="empty-block"),
        pytest.param(b"```json\nkein JSON\n```", id="prose-in-block"),
        pytest.param(b"Hier ist es:\n```json\n%s\n```", id="text-before"),
        pytest.param(b"```json\n%s\n```\nViel Erfolg!", id="text-after"),
        pytest.param(b"```json\n%s\n```\n```json\n%s\n```", id="two-blocks"),
        pytest.param(b"```json %s ```", id="fence-on-one-line"),
        pytest.param(b"```python\n%s\n```", id="other-language"),
        pytest.param(b"```json\n%s", id="no-closing-fence"),
        pytest.param(b"~~~json\n%s\n~~~", id="other-fence"),
    ],
)
def test_invalid_json_stays_a_failure(lab: Lab, raw: bytes) -> None:
    body = _output()
    lab.add(raw.replace(b"%s", body))
    run = lab.imported()[0]
    assert (run.status, run.failure_reason) == (imp.FAILED, "unreadable_output")
    assert run.code_fence_removed is False


def test_an_unknown_category_marks_the_entry_and_keeps_the_run(lab: Lab) -> None:
    errors = [_error("S1", "300 km", "Grammatik"), _error("S2", "30 Minuten", "Zahl")]
    lab.add(_output(errors=errors))
    run = lab.imported()[0]
    assert run.status == imp.USABLE
    assert [entry["invalid_category"] for entry in run.errors] == [True, False]
    assert run.errors[0]["category"] == "Grammatik"


def test_a_marked_entry_keeps_its_quote_check(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S1", "300 km", "Grammatik")]))
    assert lab.imported()[0].references[0].origin_strict == imp.DELIVERED_VALID


def test_an_unknown_category_saves_no_other_violation(lab: Lab) -> None:
    payload = json.loads(_output(errors=[_error("S1", "x", "Grammatik")]))
    payload["errors"][0]["extra"] = 1
    lab.add(json.dumps(payload).encode())
    assert lab.imported()[0].status == imp.FAILED


def test_an_unknown_criterion_stays_a_failure(lab: Lab) -> None:
    lab.add(_output([_comment(criteria=["K9"])], [_error("S1", "x", "Grammatik")]))
    assert lab.imported()[0].status == imp.FAILED


def test_an_attempt_without_output_is_a_failure(lab: Lab) -> None:
    lab.add(None)
    assert lab.imported()[0].failure_reason == "no_output"


@pytest.mark.parametrize(
    ("meta", "named"),
    [
        pytest.param(b"", "not valid JSON", id="empty"),
        pytest.param(b"[]", "not a JSON object", id="not-an-object"),
        pytest.param(_meta(date="bald"), "field date", id="bad-date"),
        pytest.param(_meta(time="spät"), "field time", id="bad-time"),
        pytest.param(_meta(time=None), "missing field time", id="no-time"),
        pytest.param(_meta(date=None), "missing field date", id="no-date"),
        pytest.param(
            _meta(model_name=" "), "missing field model_name", id="blank-name"
        ),
        pytest.param(_meta(model_name=None), "missing field model_name", id="no-name"),
        pytest.param(_meta(chat_mode=" "), "missing field chat_mode", id="blank-mode"),
        pytest.param(_meta(chat_mode=None), "missing field chat_mode", id="no-mode"),
        pytest.param(_meta(chat_mode=3), "missing field chat_mode", id="mode-not-text"),
        pytest.param(
            _meta(account_type=None), "missing field account_type", id="no-account"
        ),
        pytest.param(
            _meta(account_type=" "), "missing field account_type", id="blank-account"
        ),
    ],
)
def test_unusable_metadata_is_rejected_by_name(
    lab: Lab, meta: bytes, named: str
) -> None:
    lab.add(_output(), meta=meta)
    with pytest.raises(imp.MetadataRejected) as caught:
        lab.imported()
    assert named in str(caught.value)
    assert "spiel/toy/original/1.meta.json" in str(caught.value)


def test_a_run_without_a_metadata_file_is_rejected(lab: Lab) -> None:
    lab.add(_output())
    (lab.runs / "spiel/toy/original/1.meta.json").unlink()
    with pytest.raises(imp.MetadataRejected, match="no metadata file") as caught:
        lab.imported()
    assert "chat_mode" in str(caught.value)


def test_all_metadata_problems_are_named_at_once(lab: Lab) -> None:
    lab.add(_output(), "1", meta=_meta(time=None, chat_mode=None))
    lab.add(_output(), "2", meta=_meta(date=None))
    lab.add(_output(), "3")
    with pytest.raises(imp.MetadataRejected) as caught:
        lab.imported()
    assert len(caught.value.problems) == 3


def test_a_rejected_import_writes_nothing(
    lab: Lab, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    lab.add(_output(), meta=_meta(time=None))
    out = tmp_path / "imported.json"
    arguments = ["--runs", str(lab.runs), "--banks", str(lab.banks)]
    assert imp.main([*arguments, "--schema", str(SCHEMA_PATH), "--out", str(out)]) == 1
    assert "missing field time" in capsys.readouterr().err
    assert not out.exists()


def test_a_protocol_error_is_recorded_with_its_reason(lab: Lab) -> None:
    lab.add(_output(), meta=json.dumps({"protocol_error": "Uhrzeit fehlt"}).encode())
    run = lab.imported()[0]
    assert (run.status, run.protocol_note) == (imp.PROTOCOL_ERROR, "Uhrzeit fehlt")
    assert run.failure_reason is None


@pytest.mark.parametrize("reason", ["", "  ", 3, None])
def test_a_protocol_error_needs_a_reason(lab: Lab, reason: object) -> None:
    lab.add(_output(), meta=json.dumps({"protocol_error": reason}).encode())
    with pytest.raises(imp.MetadataRejected, match="needs a reason"):
        lab.imported()


def test_a_protocol_error_never_reads_the_output(lab: Lab) -> None:
    lab.add(b"kein JSON", meta=json.dumps({"protocol_error": "x"}).encode())
    assert lab.imported()[0].status == imp.PROTOCOL_ERROR


def test_a_protocol_error_enters_no_measure(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km")])], grade=2), "1")
    lab.add(b"kein JSON", "2")
    before = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    note = json.dumps({"protocol_error": "Modus fehlt"}).encode()
    lab.add(_output([_comment(quotes=[("S1", "999 km")])], grade=6), "3", meta=note)
    lab.add(b"kein JSON", "4", meta=note)
    after = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert after.pop("protocol_errors") == 2
    assert before.pop("protocol_errors") == 0
    assert after == before


def test_a_protocol_error_is_no_failure(lab: Lab) -> None:
    lab.add(_output(), "1")
    note = json.dumps({"protocol_error": "Datum fehlt"}).encode()
    lab.add(_output(), "2", meta=note)
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["counts"]["failures"]["label"] == "0 von 1"
    assert report["attempted_runs"] == 1


def test_a_missing_bank_is_a_setup_error_not_a_model_failure(lab: Lab) -> None:
    lab.add(_output(), version="v2")
    with pytest.raises(imp.RunSetupError, match="no sentence bank"):
        lab.imported()


def test_a_comment_with_two_quotes_gives_two_references(lab: Lab) -> None:
    quotes = [("S1", "fährt 300 km"), ("S2", "lädt in 31 Minuten")]
    lab.add(_output([_comment(quotes=quotes)]))
    origins = [item.origin_strict for item in lab.imported()[0].references]
    assert origins == [imp.DELIVERED_VALID, imp.DELIVERED_INVALID]


def test_a_global_comment_is_not_a_missing_reference(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global"), _comment(scope="local")]))
    origins = [item.origin_strict for item in lab.imported()[0].references]
    assert origins == [imp.GLOBAL_COMMENT, imp.MISSING]


def test_a_global_comment_with_a_quote_keeps_the_quote(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global", quotes=[("S1", "300 km")])]))
    assert lab.imported()[0].references[0].origin_strict == imp.DELIVERED_VALID


def test_the_importer_sets_no_pointer_from_comment_text(lab: Lab) -> None:
    text = 'In S1 steht "fährt 300 km".'
    lab.add(_output([_comment(text=text)]))
    reference = lab.imported()[0].references[0]
    assert (reference.origin_strict, reference.sid, reference.quote) == (
        imp.MISSING,
        None,
        None,
    )


def test_modes_are_recorded_separately(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "fährt 300 km.")])]))
    reference = lab.imported()[0].references[0]
    assert reference.origin_strict == imp.DELIVERED_INVALID
    assert reference.origin_normalized == imp.DELIVERED_VALID


def test_a_wrong_location_keeps_the_text_valid(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S2", "fährt 300 km")])]))
    reference = lab.imported()[0].references[0]
    assert reference.text_valid_strict is True
    assert reference.origin_strict == imp.DELIVERED_INVALID


def test_an_unsupported_schema_keyword_stops_the_import() -> None:
    with pytest.raises(imp.RunSetupError, match="unsupported schema keywords"):
        imp.schema_problems({}, {"type": "object", "oneOf": []})


def test_the_schema_accepts_a_clean_output() -> None:
    value = json.loads(_output([_comment()], [_error("S1", "x", "Zahl")]))
    assert imp.schema_problems(value, SCHEMA) == []


def _full_lab(lab: Lab) -> dict[str, dict[str, Any]]:
    """One text with three original and three modified runs."""

    lab.add(
        _output(
            [
                _comment(
                    quotes=[("S1", "fährt 300 km"), ("S2", "lädt in 31 Minuten")],
                    criteria=["K1"],
                ),
                _comment(scope="global", criteria=["K4"]),
                _comment(),
            ],
            [_error("S3", "sehr teuer", "Faktum")],
            grade=2,
        ),
        "1",
    )
    lab.add(_output([_comment(scope="global")], grade=2), "2")
    lab.add(b"kein JSON", "3")
    lab.add(
        _output(errors=[_error("S2", "30 Minuten", "Zahl")], grade=4), "1", version="v1"
    )
    lab.add(
        _output(errors=[_error("S2", "30 Minuten", "Sprache")], grade=5),
        "2",
        version="v1",
    )
    lab.add(b"kein JSON", "3", version="v1")
    return an.analyze(lab.records(), ANNOTATED, TARGETS)


def test_the_failure_rate_counts_every_attempt(lab: Lab) -> None:
    report = _full_lab(lab)["spiel"]
    assert report["attempted_runs"] == 6
    assert report["usable_runs"] == 4
    assert report["rates"]["failure_rate"] == pytest.approx(2 / 6)


def test_a_run_without_a_quote_is_undefined_not_zero(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global")]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    fidelity = report["rates"]["quote_fidelity"]
    assert fidelity["strict"]["text"] is None
    assert fidelity["normalized"]["text_and_location"] is None
    rendered = an.render(report)
    assert isinstance(rendered, dict)
    assert rendered["rates"]["quote_fidelity"]["strict"]["text"] == "nicht definiert"


def test_an_undefined_run_leaves_the_mean_of_the_others_alone(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km")])]), "1")
    lab.add(_output([_comment(scope="global")]), "2")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["quote_fidelity"]["strict"]["text_and_location"] == 1.0


def test_failures_never_enter_the_quote_denominator(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km")])]), "1")
    lab.add(b"kein JSON", "2")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["quote_fidelity"]["strict"]["text_and_location"] == 1.0
    assert report["rates"]["failure_rate"] == 0.5


def test_quote_fidelity_counts_comment_and_error_quotes(lab: Lab) -> None:
    fidelity = _full_lab(lab)["spiel"]["rates"]["quote_fidelity"]
    assert fidelity["strict"]["text_and_location"] == pytest.approx((2 / 3 + 1 + 1) / 3)


def test_text_only_fidelity_ignores_the_location(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S2", "300 km"), ("S1", "999 km")])]))
    fidelity = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["rates"][
        "quote_fidelity"
    ]
    assert fidelity["strict"]["text"] == 0.5
    assert fidelity["strict"]["text_and_location"] == 0.0


def test_normalized_fidelity_differs_from_strict_on_a_final_mark(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "fährt 300 km.")])]))
    fidelity = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["rates"][
        "quote_fidelity"
    ]
    assert fidelity["strict"]["text_and_location"] == 0.0
    assert fidelity["normalized"]["text_and_location"] == 1.0


def test_evidence_coverage_counts_all_comments(lab: Lab) -> None:
    lab.add(
        _output(
            [
                _comment(quotes=[("S1", "300 km"), ("S2", "30 Minuten")]),
                _comment(scope="global"),
                _comment(),
            ]
        )
    )
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["evidence_coverage"]["strict"] == pytest.approx(1 / 3)


def test_evidence_coverage_is_undefined_without_comments(lab: Lab) -> None:
    lab.add(_output())
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["evidence_coverage"]["strict"] is None


def test_criterion_fidelity_uses_the_corpus_annotation_of_the_quoted_sentence(
    lab: Lab,
) -> None:
    lab.add(
        _output(
            [
                _comment(quotes=[("S1", "300 km")], criteria=["K1", "K4"]),
                _comment(scope="global", criteria=["K6"]),
            ]
        )
    )
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["criterion_fidelity"] == 0.5


def test_criterion_fidelity_is_undefined_without_an_evidenced_comment(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global", criteria=["K1"])]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["criterion_fidelity"] is None


def test_criterion_coverage_compares_with_the_annotated_criteria(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global", criteria=["K1", "K6"])]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["criterion_coverage"] == 0.5


def test_measure_8_uses_the_original_and_the_modified_grades_stay_apart(
    lab: Lab,
) -> None:
    report = _full_lab(lab)["spiel"]
    assert report["grade_variation"]["toy"]["distribution"] == {"2": 2}
    assert report["grades_modified"]["toy"]["v1"]["distribution"] == {"4": 1, "5": 1}


def test_a_grade_cell_gives_distribution_range_and_most_common_grade(lab: Lab) -> None:
    for number, grade in enumerate((2, 2, 5), start=1):
        lab.add(_output(grade=grade), str(number))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["grade_variation"]["toy"] == {
        "usable_runs": 3,
        "marked": False,
        "distribution": {"2": 2, "5": 1},
        "range": [2, 5],
        "most_common": [2],
        "most_common_count": 2,
    }


def test_a_grade_cell_with_too_few_usable_runs_is_marked(lab: Lab) -> None:
    lab.add(_output(grade=2), "1")
    lab.add(_output(grade=3), "2")
    lab.add(b"kein JSON", "3")
    cell = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["grade_variation"]
    assert cell["toy"]["usable_runs"] == 2
    assert cell["toy"]["marked"] is True
    assert cell["toy"]["most_common"] == [2, 3]


def test_a_modified_cell_with_too_few_usable_runs_is_marked_too(lab: Lab) -> None:
    lab.add(_output(grade=2), version="v1")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["grades_modified"]["toy"]["v1"]["marked"] is True
    assert report["grade_variation"] == {}


def test_a_grade_cell_without_a_usable_run_stays_visible(lab: Lab) -> None:
    lab.add(b"kein JSON")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)
    cell = report["spiel"]["grade_variation"]["toy"]
    assert (cell["usable_runs"], cell["marked"], cell["range"]) == (0, True, None)
    rendered = an.render(an.pilot_report(report))
    assert isinstance(rendered, dict)
    assert rendered["spiel"]["grade_variation"]["toy"]["range"] == "nicht definiert"


def test_detection_per_usable_and_per_attempted_run(lab: Lab) -> None:
    report = _full_lab(lab)["spiel"]
    assert report["rates"]["detection_per_usable_run"] == 0.5
    assert report["rates"]["detection_per_attempted_run"] == pytest.approx(1 / 3)


def test_a_wrong_category_is_no_detection_and_stays_visible(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Sprache")]), version="v1")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["detection_per_usable_run"] == 0.0
    assert report["wrong_category_hits"] == 1


def test_a_right_category_with_an_invalid_quote_is_no_detection(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "99 Minuten", "Zahl")]), version="v1")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["detection_per_usable_run"] == 0.0


def test_a_false_alarm_is_an_error_report_at_a_site_in_the_original(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Faktum")]), "1")
    lab.add(_output(errors=[_error("S3", "sehr teuer", "Faktum")]), "2")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["false_alarm"] == 0.5


def test_no_target_means_detection_and_false_alarm_are_undefined(lab: Lab) -> None:
    lab.add(_output())
    report = an.analyze(lab.records(), ANNOTATED, {})["spiel"]
    assert report["rates"]["detection_per_usable_run"] is None
    assert report["rates"]["detection_per_attempted_run"] is None
    assert report["rates"]["false_alarm"] is None


def test_the_estimate_is_the_mean_per_text_not_the_pooled_mean() -> None:
    assert an.mean_per_text({"a": [1.0], "b": [0.0, 0.0, 0.0]}) == 0.5


def test_a_text_without_a_defined_value_leaves_the_mean(lab: Lab) -> None:
    assert an.mean_per_text({"a": [1.0], "b": [None, None]}) == 1.0
    assert an.mean_per_text({"a": [None]}) is None


def test_models_are_kept_apart(lab: Lab) -> None:
    lab.add(_output(grade=1), model="spiel")
    lab.add(_output(grade=6), model="anderes")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)
    assert list(report) == ["anderes", "spiel"]
    assert report["anderes"]["grade_variation"]["toy"]["most_common"] == [6]


def test_the_report_counts_what_the_importer_tolerated(lab: Lab) -> None:
    body = _output(errors=[_error("S1", "x", "Grammatik"), _error("S2", "y", "Stil")])
    lab.add(b"```json\n" + body + b"\n```", "1")
    lab.add(_output(errors=[_error("S1", "x", "Zahl")]), "2")
    lab.add(b"```json\nkein JSON\n```", "3")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["import_notes"] == {
        "code_fences_removed": 1,
        "invalid_category_entries": 2,
    }
    assert report["rates"]["failure_rate"] == pytest.approx(1 / 3)


def test_an_unknown_category_is_no_detection(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Grammatik")]), version="v1")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["detection_per_usable_run"] == 0.0
    assert report["wrong_category_hits"] == 0
    assert report["unknown_category"]["at_target_in_modified"] == 1


def test_an_unknown_category_at_a_site_is_still_a_false_alarm(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Grammatik")]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["rates"]["false_alarm"] == 1.0


def test_unknown_categories_count_as_unclear_by_place(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Grammatik")]))
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Stil")]), version="v1")
    lab.add(_output(errors=[_error("S1", "300 km", "Stil")]), "2", version="v1")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["unknown_category"] == {
        "unclear_reports": 3,
        "at_target_in_original": 1,
        "at_target_in_modified": 1,
        "elsewhere": 1,
    }


def test_the_counter_assumption_reverses_both_results(lab: Lab) -> None:
    unknown = [_error("S2", "30 Minuten", "Grammatik")]
    lab.add(_output(errors=unknown))
    lab.add(_output(errors=unknown), version="v1")
    counts = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["counts"]
    assert counts["detection_per_usable_run"]["label"] == "0 von 1"
    assert counts["false_alarm"]["label"] == "1 von 1"
    counter = counts["counter_assumption"]
    assert counter["detection_per_usable_run"]["label"] == "1 von 1"
    assert counter["detection_per_attempted_run"]["label"] == "1 von 1"
    assert counter["false_alarm"]["label"] == "0 von 1"


def test_the_counter_assumption_still_needs_a_valid_quote(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "99 Minuten", "Grammatik")]), version="v1")
    counts = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["counts"]
    assert counts["counter_assumption"]["detection_per_usable_run"]["count"] == 0


def test_the_counter_assumption_leaves_a_known_category_alone(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Sprache")]), version="v1")
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Faktum")]))
    counts = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["counts"]
    counter = counts["counter_assumption"]
    assert counter["detection_per_usable_run"] == counts["detection_per_usable_run"]
    assert counter["false_alarm"] == counts["false_alarm"]


def test_code_blocks_are_counted_per_chatbot(lab: Lab) -> None:
    fenced = b"```json\n" + _output() + b"\n```"
    lab.add(fenced, "1", model="eins")
    lab.add(fenced, "2", model="eins")
    lab.add(_output(), "1", model="zwei")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)
    assert report["eins"]["import_notes"]["code_fences_removed"] == 2
    assert report["zwei"]["import_notes"]["code_fences_removed"] == 0


def test_the_pilot_report_gives_counts_and_no_rates(lab: Lab) -> None:
    report = an.pilot_report(_full_lab(lab))["spiel"]
    assert "rates" not in report
    counts = report["counts"]
    assert counts["failures"] == {"count": 2, "of": 6, "label": "2 von 6"}
    assert counts["quotes"]["strict"]["text_and_location"]["label"] == "4 von 5"
    assert counts["evidence"]["strict"]["label"] == "1 von 4"
    assert counts["detection_per_usable_run"]["label"] == "1 von 2"
    assert counts["detection_per_attempted_run"]["label"] == "1 von 3"
    assert counts["false_alarm"]["label"] == "0 von 2"


def test_nothing_of_nothing_is_undefined_in_the_pilot_report(lab: Lab) -> None:
    lab.add(_output())
    counts = an.analyze(lab.records(), ANNOTATED, {})["spiel"]["counts"]
    assert counts["quotes"]["strict"]["text"]["label"] == "nicht definiert"
    assert counts["detection_per_usable_run"]["label"] == "nicht definiert"
    assert counts["false_alarm"]["label"] == "nicht definiert"


def test_counts_and_rates_agree_on_a_single_run(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km"), ("S1", "999 km")])]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["counts"]["quotes"]["strict"]["text"]["label"] == "1 von 2"
    assert report["rates"]["quote_fidelity"]["strict"]["text"] == 0.5


def test_the_report_holds_the_measures_that_are_built(lab: Lab) -> None:
    """Measure 5 needs human coding and is not built."""

    report = _full_lab(lab)["spiel"]
    counts = report["counts"]
    measures = {
        1: counts["failures"],
        2: counts["quotes"]["strict"]["text"],
        3: counts["quotes"]["strict"]["text_and_location"],
        4: counts["evidence"],
        6: counts["criterion_fidelity"],
        7: counts["criterion_coverage"],
        8: report["grade_variation"],
        9: counts["detection_per_usable_run"],
        10: counts["detection_per_attempted_run"],
        11: counts["false_alarm"],
        12: report["unknown_category"],
    }
    assert all(value is not None for value in measures.values())
    assert counts["quotes"]["normalized"]["text"]
    assert counts["quotes"]["normalized"]["text_and_location"]


def test_the_scripts_run_from_the_command_line(lab: Lab, tmp_path: Path) -> None:
    _full_lab(lab)
    imported = tmp_path / "imported.json"
    assert (
        imp.main(
            [
                "--runs",
                str(lab.runs),
                "--banks",
                str(lab.banks),
                "--schema",
                str(SCHEMA_PATH),
                "--out",
                str(imported),
            ]
        )
        == 0
    )
    annotated = tmp_path / "annotated.json"
    annotated.write_text(json.dumps(ANNOTATED), "utf-8")
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps(TARGETS), "utf-8")
    report = tmp_path / "report.json"
    arguments = ["--imported", str(imported), "--sentence-criteria", str(annotated)]
    arguments += ["--targets", str(targets), "--out", str(report)]
    assert an.main(arguments) == 0
    written = json.loads(report.read_text("utf-8"))["spiel"]
    assert written["usable_runs"] == 4
    assert "rates" not in written
