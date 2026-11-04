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
META = {"date": "2026-11-20", "model_name": "Spielmodell 1"}


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
    assert (run.date, run.model_name) == ("2026-11-20", "Spielmodell 1")
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
        pytest.param(b'```json\n{"grade": 3}\n```', id="code-fence"),
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
            _output(errors=[_error("S1", "x", "Grammatik")]), id="bad-category"
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


def test_an_attempt_without_output_is_a_failure(lab: Lab) -> None:
    lab.add(None)
    assert lab.imported()[0].failure_reason == "no_output"


@pytest.mark.parametrize(
    "meta",
    [
        pytest.param(b"", id="empty"),
        pytest.param(b'{"date": "2026-11-20"}', id="no-name"),
        pytest.param(b'{"date": "bald", "model_name": "x"}', id="bad-date"),
        pytest.param(b'{"date": "2026-11-20", "model_name": " "}', id="blank-name"),
        pytest.param(b"[]", id="not-an-object"),
    ],
)
def test_unusable_metadata_is_a_failure(lab: Lab, meta: bytes) -> None:
    lab.add(_output(), meta=meta)
    assert lab.imported()[0].failure_reason == "metadata_unusable"


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
    assert report["failure_rate"] == pytest.approx(2 / 6)


def test_a_run_without_a_quote_is_undefined_not_zero(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global")]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    fidelity = report["quote_fidelity"]
    assert fidelity["strict"]["text"] is None
    assert fidelity["normalized"]["text_and_location"] is None
    rendered = an.render(report)
    assert isinstance(rendered, dict)
    assert rendered["quote_fidelity"]["strict"]["text"] == "nicht definiert"


def test_an_undefined_run_leaves_the_mean_of_the_others_alone(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km")])]), "1")
    lab.add(_output([_comment(scope="global")]), "2")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["quote_fidelity"]["strict"]["text_and_location"] == 1.0


def test_failures_never_enter_the_quote_denominator(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km")])]), "1")
    lab.add(b"kein JSON", "2")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["quote_fidelity"]["strict"]["text_and_location"] == 1.0
    assert report["failure_rate"] == 0.5


def test_quote_fidelity_counts_comment_and_error_quotes(lab: Lab) -> None:
    fidelity = _full_lab(lab)["spiel"]["quote_fidelity"]
    assert fidelity["strict"]["text_and_location"] == pytest.approx((2 / 3 + 1 + 1) / 3)


def test_text_only_fidelity_ignores_the_location(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S2", "300 km"), ("S1", "999 km")])]))
    fidelity = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["quote_fidelity"]
    assert fidelity["strict"]["text"] == 0.5
    assert fidelity["strict"]["text_and_location"] == 0.0


def test_normalized_fidelity_differs_from_strict_on_a_final_mark(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "fährt 300 km.")])]))
    fidelity = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]["quote_fidelity"]
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
    assert report["evidence_coverage"]["strict"] == pytest.approx(1 / 3)


def test_evidence_coverage_is_undefined_without_comments(lab: Lab) -> None:
    lab.add(_output())
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["evidence_coverage"]["strict"] is None


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
    assert report["criterion_fidelity"] == 0.5


def test_criterion_fidelity_is_undefined_without_an_evidenced_comment(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global", criteria=["K1"])]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["criterion_fidelity"] is None


def test_criterion_coverage_compares_with_the_annotated_criteria(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global", criteria=["K1", "K6"])]))
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["criterion_coverage"] == 0.5


def test_grades_are_counted_per_text_and_model(lab: Lab) -> None:
    report = _full_lab(lab)["spiel"]
    assert report["grade_distribution"] == {"toy": {"2": 2, "4": 1, "5": 1}}


def test_detection_per_usable_and_per_attempted_run(lab: Lab) -> None:
    report = _full_lab(lab)["spiel"]
    assert report["detection_per_usable_run"] == 0.5
    assert report["detection_per_attempted_run"] == pytest.approx(1 / 3)


def test_a_wrong_category_is_no_detection_and_stays_visible(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Sprache")]), version="v1")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["detection_per_usable_run"] == 0.0
    assert report["wrong_category_hits"] == 1


def test_a_right_category_with_an_invalid_quote_is_no_detection(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "99 Minuten", "Zahl")]), version="v1")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["detection_per_usable_run"] == 0.0


def test_a_false_alarm_is_an_error_report_at_a_site_in_the_original(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Faktum")]), "1")
    lab.add(_output(errors=[_error("S3", "sehr teuer", "Faktum")]), "2")
    report = an.analyze(lab.records(), ANNOTATED, TARGETS)["spiel"]
    assert report["false_alarm"] == 0.5


def test_no_target_means_detection_and_false_alarm_are_undefined(lab: Lab) -> None:
    lab.add(_output())
    report = an.analyze(lab.records(), ANNOTATED, {})["spiel"]
    assert report["detection_per_usable_run"] is None
    assert report["detection_per_attempted_run"] is None
    assert report["false_alarm"] is None


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
    assert report["anderes"]["grade_distribution"] == {"toy": {"6": 1}}


def test_the_report_holds_the_twelve_measures(lab: Lab) -> None:
    report = _full_lab(lab)["spiel"]
    measures = [
        report["failure_rate"],
        report["quote_fidelity"]["strict"]["text"],
        report["quote_fidelity"]["strict"]["text_and_location"],
        report["quote_fidelity"]["normalized"]["text"],
        report["quote_fidelity"]["normalized"]["text_and_location"],
        report["evidence_coverage"],
        report["criterion_fidelity"],
        report["criterion_coverage"],
        report["grade_distribution"],
        report["detection_per_usable_run"],
        report["detection_per_attempted_run"],
        report["false_alarm"],
    ]
    assert len(measures) == 12


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
    assert json.loads(report.read_text("utf-8"))["spiel"]["usable_runs"] == 4
