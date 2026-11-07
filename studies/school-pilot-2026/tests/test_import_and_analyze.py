"""Import and analysis, tested on invented outputs only."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any

import analyze as an
import export_for_coding as export
import genius_loader as loader
import import_runs as imp
import pytest
from export_for_coding import Code, CodingError

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/output.schema.json"
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text("utf-8"))
SENTENCES = [
    "Das Auto fährt 300 km weit.",
    "Der Akku lädt in 30 Minuten.",
    "Wasserstoff bleibt sehr teuer.",
]
ANNOTATED = {"toy": {"S1": ["K1"], "S2": ["K1", "K4"], "S3": ["K4"]}}
TRAPS = {
    "toy": {
        "version": "v1",
        "type": "Zahl",
        "accepted_categories": ["Zahl"],
        "sids": ["S2"],
        "description": "Die Ladezeit im Satz ist falsch.",
    }
}
ORIGINAL_VERSION = "original"
NO_REWRITES = {"count": 0, "by_form": {"text": 0, "number": 0, "brackets": 0}}
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
    quotes: list[tuple[str | None, str]] | None = None,
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
        pytest.param(
            b'{"grade": 3, "errors": [], "comments": [{"text": "x", "scope": "local", '
            b'"quotes": [], "criteria": [7]}]}',
            id="criterion-not-text",
        ),
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


def test_an_unknown_criterion_is_marked_and_the_run_stays_usable(lab: Lab) -> None:
    lab.add(_output([_comment(criteria=["K1", "K9"])]))
    run = lab.imported()[0]
    assert run.status == imp.USABLE
    assert run.comments[0]["criteria"] == [
        {"value": "K1", "id": "K1"},
        {"value": "K9", "id": None},
    ]


def test_a_criterion_named_in_full_counts_as_its_id(lab: Lab) -> None:
    lab.add(_output([_comment(criteria=["  wirkungsgrad "])]))
    assert lab.imported()[0].comments[0]["criteria"][0]["id"] == "K6"


@pytest.mark.parametrize(
    ("spelling", "criterion"),
    [
        pytest.param("Energiedichte", "K1", id="prompt-name-k1"),
        pytest.param(" verfügbarkeit ", "K2", id="prompt-name-k2"),
        pytest.param("BETRIEB", "K4", id="prompt-name-k4"),
        pytest.param("Jahresertrag/Energiedichte", "K1", id="old-name-k1"),
        pytest.param("Lebensdauer/Verfügbarkeit", "K2", id="old-name-k2"),
        pytest.param("Preis/Betrieb", "K4", id="old-name-k4"),
        pytest.param("Lokale Emissionen/Geräuschemissionen", "K3", id="unchanged"),
    ],
)
def test_old_and_new_names_count_as_the_criterion(
    lab: Lab, spelling: str, criterion: str
) -> None:
    lab.add(_output([_comment(criteria=[spelling])]))
    assert lab.imported()[0].comments[0]["criteria"][0]["id"] == criterion


@pytest.mark.parametrize("spelling", ["Jahresertrag", "Lebensdauer", "Preis"])
def test_the_dropped_part_of_a_name_stays_outside_the_grid(
    lab: Lab, spelling: str
) -> None:
    lab.add(_output([_comment(criteria=[spelling])]))
    assert lab.imported()[0].comments[0]["criteria"][0]["id"] is None


def test_an_unknown_criterion_saves_no_other_violation(lab: Lab) -> None:
    payload = json.loads(_output([_comment(criteria=["K9"])]))
    payload["comments"][0]["extra"] = 1
    lab.add(json.dumps(payload).encode())
    assert lab.imported()[0].status == imp.FAILED


OTHER_SID_FORMS = [
    pytest.param(None, id="null"),
    pytest.param("", id="empty"),
    pytest.param("  ", id="blank"),
    pytest.param("s1", id="lower-case"),
    pytest.param("S01", id="leading-zero-with-letter"),
    pytest.param("01", id="leading-zero"),
    pytest.param("S0", id="sentence-zero"),
    pytest.param("0", id="zero"),
    pytest.param("S 1", id="inner-space"),
    pytest.param(" S1", id="leading-space"),
    pytest.param("1 ", id="trailing-space"),
    pytest.param("S1\n", id="newline-with-letter"),
    pytest.param("1\n", id="newline"),
    pytest.param("[1]", id="brackets-without-letter"),
    pytest.param("[S01]", id="brackets-with-leading-zero"),
    pytest.param("[S0]", id="brackets-with-sentence-zero"),
    pytest.param("[s1]", id="brackets-lower-case"),
    pytest.param("[S 1]", id="brackets-inner-space"),
    pytest.param(" [S1]", id="brackets-leading-space"),
    pytest.param("[[S1]]", id="brackets-doubled"),
    pytest.param("[S1", id="bracket-not-closed"),
    pytest.param("Satz 1", id="word"),
    pytest.param("S1, S2", id="two-numbers"),
    pytest.param("١", id="arabic-digit"),
    pytest.param("１", id="fullwidth-digit"),
    pytest.param(0, id="number-zero"),
    pytest.param(-1, id="number-negative"),
    pytest.param(1.0, id="whole-decimal"),
    pytest.param(1.5, id="decimal"),
    pytest.param(True, id="true"),
    pytest.param(False, id="false"),
    pytest.param(["S1"], id="list"),
    pytest.param({"sid": "S1"}, id="object"),
]


def _with_sids(comment_sid: object = "S1", error_sid: object = "S1") -> bytes:
    payload = json.loads(
        _output(
            [_comment(quotes=[("S1", "300 km")])],
            [_error("S1", "300 km", "Zahl")],
        )
    )
    payload["comments"][0]["quotes"][0]["sid"] = comment_sid
    payload["errors"][0]["sid"] = error_sid
    return json.dumps(payload).encode()


def test_a_number_in_the_agreed_form_is_not_rewritten(lab: Lab) -> None:
    lab.add(_with_sids())
    run = lab.imported()[0]
    assert run.sid_rewrites == []
    assert [item.sid for item in run.references] == ["S1", "S1"]


@pytest.mark.parametrize(
    ("original", "form"),
    [
        pytest.param("1", imp.SID_FORM_TEXT, id="digits-as-text"),
        pytest.param(1, imp.SID_FORM_NUMBER, id="json-number"),
        pytest.param("[S1]", imp.SID_FORM_BRACKETS, id="prompt-spelling"),
    ],
)
def test_an_agreed_spelling_becomes_the_agreed_form_and_keeps_its_original(
    lab: Lab, original: object, form: str
) -> None:
    lab.add(_with_sids(original, original))
    run = lab.imported()[0]
    assert run.status == imp.USABLE
    assert run.sid_rewrites == [{"original": original, "sid": "S1", "form": form}] * 2
    assert type(run.sid_rewrites[0]["original"]) is type(original)
    assert [item.sid for item in run.references] == ["S1", "S1"]
    assert [item.origin_strict for item in run.references] == [imp.DELIVERED_VALID] * 2
    assert run.errors[0]["sid"] == "S1"


def test_a_rewritten_number_is_still_checked_against_its_sentence(lab: Lab) -> None:
    lab.add(_with_sids("[S2]", 99))
    run = lab.imported()[0]
    assert len(run.sid_rewrites) == 2
    assert [item.origin_strict for item in run.references] == [
        imp.DELIVERED_INVALID,
        imp.DELIVERED_INVALID,
    ]


@pytest.mark.parametrize("sid", OTHER_SID_FORMS)
def test_any_other_form_counts_as_a_missing_number(lab: Lab, sid: object) -> None:
    lab.add(_with_sids(sid, sid))
    run = lab.imported()[0]
    assert (run.status, run.sid_rewrites) == (imp.USABLE, [])
    for reference in run.references:
        assert reference.sid is None
        assert reference.origin_strict == imp.DELIVERED_WITHOUT_SID
        assert reference.text_valid_strict is True
    assert run.errors[0]["sid"] is None


def test_another_form_counts_only_in_measure_2(lab: Lab) -> None:
    lab.add(_with_sids("Satz 1", 1))
    counts = _report(lab, {}, {})["counts"]
    assert counts["quotes"]["strict"]["text"]["label"] == "2 von 2"
    assert counts["quotes"]["strict"]["text_and_location"]["label"] == "1 von 1"
    assert counts["quotes_without_sid"] == 1


def test_a_rewrite_saves_no_other_violation(lab: Lab) -> None:
    payload = json.loads(_with_sids(1, "[S1]"))
    payload["errors"][0]["extra"] = 1
    lab.add(json.dumps(payload).encode())
    run = lab.imported()[0]
    assert (run.status, run.sid_rewrites) == (imp.FAILED, [])


def test_rewrites_are_counted_per_chatbot(lab: Lab) -> None:
    lab.add(_with_sids("1", 1), "1", model="eins")
    lab.add(_with_sids("[S2]", "S2"), "2", model="eins")
    lab.add(_with_sids(), "1", model="zwei")
    lab.add(_with_sids("Satz 1", None), "2", model="zwei")
    report = an.analyze(lab.records(), {}, {})
    assert report["eins"]["import_notes"]["sids_rewritten"] == {
        "count": 3,
        "by_form": {"text": 1, "number": 1, "brackets": 1},
    }
    assert report["zwei"]["import_notes"]["sids_rewritten"] == NO_REWRITES


def test_a_failed_run_adds_no_rewrite_to_the_report(lab: Lab) -> None:
    raw = _with_sids("1", "1").replace(b'"grade": 3', b'"grade": 9')
    lab.add(raw)
    assert _report(lab, {}, {})["import_notes"]["sids_rewritten"] == NO_REWRITES


def test_a_quote_without_a_number_keeps_the_run_usable(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[(None, "300 km")])]))
    run = lab.imported()[0]
    reference = run.references[0]
    assert run.status == imp.USABLE
    assert reference.sid is None
    assert reference.origin_strict == imp.DELIVERED_WITHOUT_SID
    assert reference.text_valid_strict is True


def test_a_quote_without_the_key_keeps_the_run_usable(lab: Lab) -> None:
    payload = json.loads(_output([_comment(quotes=[("S1", "300 km")])]))
    del payload["comments"][0]["quotes"][0]["sid"]
    lab.add(json.dumps(payload).encode())
    assert lab.imported()[0].references[0].origin_strict == imp.DELIVERED_WITHOUT_SID


def test_an_error_report_without_a_number_keeps_the_run_usable(lab: Lab) -> None:
    payload = json.loads(_output(errors=[_error("S1", "300 km", "Zahl")]))
    del payload["errors"][0]["sid"]
    lab.add(json.dumps(payload).encode())
    run = lab.imported()[0]
    assert run.status == imp.USABLE
    assert run.errors[0]["sid"] is None


def test_a_missing_quote_text_stays_a_failure(lab: Lab) -> None:
    payload = json.loads(_output([_comment(quotes=[("S1", "x")])]))
    del payload["comments"][0]["quotes"][0]["quote"]
    lab.add(json.dumps(payload).encode())
    assert lab.imported()[0].status == imp.FAILED


def test_a_text_that_occurs_twice_is_marked_as_ambiguous(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "t "), ("S1", "300 km")])]))
    references = lab.imported()[0].references
    assert [item.ambiguous for item in references] == [True, False]


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
    before = an.analyze(lab.records(), {}, {})["spiel"]
    note = json.dumps({"protocol_error": "Modus fehlt"}).encode()
    lab.add(_output([_comment(quotes=[("S1", "999 km")])], grade=6), "3", meta=note)
    lab.add(b"kein JSON", "4", meta=note)
    after = an.analyze(lab.records(), {}, {})["spiel"]
    assert after.pop("protocol_errors") == 2
    assert before.pop("protocol_errors") == 0
    assert after == before


def test_a_protocol_error_is_no_failure(lab: Lab) -> None:
    lab.add(_output(), "1")
    note = json.dumps({"protocol_error": "Datum fehlt"}).encode()
    lab.add(_output(), "2", meta=note)
    report = an.analyze(lab.records(), {}, {})["spiel"]
    assert report["counts"]["failures"]["label"] == "0 von 1"
    assert report["attempted_runs"] == 1


def test_a_missing_bank_is_a_setup_error_not_a_model_failure(lab: Lab) -> None:
    lab.add(_output(), version="v2")
    with pytest.raises(imp.RunSetupError, match="no sentence bank"):
        lab.imported()


def test_a_comment_with_two_quotes_gives_two_references(lab: Lab) -> None:
    quotes: list[tuple[str | None, str]] = [
        ("S1", "fährt 300 km"),
        ("S2", "lädt in 31 Minuten"),
    ]
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


def _report(
    lab: Lab,
    traps: Mapping[str, Any] | None = None,
    codes: Mapping[Any, Code] | None = None,
) -> dict[str, Any]:
    return an.analyze(lab.records(), traps or {}, codes or {})["spiel"]


def _code(
    repetition: str = "1",
    version: str = "original",
    answer: str = "nein",
    report: int | None = None,
) -> dict[Any, Code]:
    return {("spiel", "toy", version, repetition): Code(answer, report)}


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
        _output(errors=[_error("S2", "30 Minuten", "Zahl")], grade=4),
        "1",
        version="v1",
    )
    lab.add(
        _output(errors=[_error("S2", "30 Minuten", "Sprache")], grade=5),
        "2",
        version="v1",
    )
    lab.add(b"kein JSON", "3", version="v1")
    codes = {
        **_code("1"),
        **_code("2"),
        **_code("1", "v1", "ja", 1),
        **_code("2", "v1", "ja", 1),
    }
    return an.analyze(lab.records(), TRAPS, codes)


def test_measure_1_counts_every_attempt(lab: Lab) -> None:
    report = _full_lab(lab)["spiel"]
    assert report["attempted_runs"] == 6
    assert report["usable_runs"] == 4
    assert report["counts"]["failures"]["label"] == "2 von 6"


def test_a_run_without_a_quote_is_undefined_not_zero(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global")]))
    report = _report(lab)
    assert report["counts"]["quotes"]["strict"]["text"]["label"] == "nicht definiert"
    assert report["rates"]["quote_fidelity"]["strict"]["text"] is None


def test_failures_never_enter_the_quote_denominator(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km")])]), "1")
    lab.add(b"kein JSON", "2")
    counts = _report(lab)["counts"]
    assert counts["quotes"]["strict"]["text_and_location"]["label"] == "1 von 1"
    assert counts["failures"]["label"] == "1 von 2"


def test_quote_fidelity_counts_comment_and_error_quotes(lab: Lab) -> None:
    counts = _full_lab(lab)["spiel"]["counts"]
    assert counts["quotes"]["strict"]["text_and_location"]["label"] == "4 von 5"


def test_text_only_fidelity_ignores_the_location(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S2", "300 km"), ("S1", "999 km")])]))
    strict = _report(lab)["counts"]["quotes"]["strict"]
    assert strict["text"]["label"] == "1 von 2"
    assert strict["text_and_location"]["label"] == "0 von 2"


def test_normalized_fidelity_differs_from_strict_on_a_final_mark(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "fährt 300 km.")])]))
    quotes = _report(lab)["counts"]["quotes"]
    assert quotes["strict"]["text_and_location"]["label"] == "0 von 1"
    assert quotes["normalized"]["text_and_location"]["label"] == "1 von 1"


def test_a_quote_without_a_number_counts_only_in_measure_2(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[(None, "300 km"), ("S1", "300 km")])]))
    counts = _report(lab)["counts"]
    assert counts["quotes"]["strict"]["text"]["label"] == "2 von 2"
    assert counts["quotes"]["strict"]["text_and_location"]["label"] == "1 von 1"
    assert counts["quotes_without_sid"] == 1


def test_only_quotes_without_a_number_leave_measure_3_undefined(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[(None, "300 km")])]))
    quotes = _report(lab)["counts"]["quotes"]["strict"]
    assert quotes["text_and_location"]["label"] == "nicht definiert"


def test_ambiguous_quotes_are_counted(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "t "), ("S1", "300 km")])]))
    assert _report(lab)["counts"]["ambiguous_quotes"] == 1


def test_invalid_quotes_are_listed_one_by_one(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km"), ("S1", "Fährt 300 km")])]))
    listed = _report(lab)["invalid_quotes"]
    assert len(listed) == 1
    assert listed[0]["quote"] == "Fährt 300 km"
    assert (listed[0]["valid_strict"], listed[0]["valid_normalized"]) == (False, False)


def test_a_quote_valid_only_in_normalized_mode_is_listed_too(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "fährt 300 km.")])]))
    listed = _report(lab)["invalid_quotes"]
    assert (listed[0]["valid_strict"], listed[0]["valid_normalized"]) == (False, True)


def test_a_valid_quote_is_not_listed(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km"), (None, "300 km")])]))
    assert _report(lab)["invalid_quotes"] == []


def test_measure_4_counts_a_delivered_quote_even_if_invalid(lab: Lab) -> None:
    lab.add(
        _output(
            [
                _comment(quotes=[("S1", "999 km")]),
                _comment(quotes=[(None, "300 km")]),
                _comment(scope="global"),
                _comment(),
            ]
        )
    )
    assert _report(lab)["counts"]["evidence"]["label"] == "2 von 4"


def test_measure_4_is_undefined_without_comments(lab: Lab) -> None:
    lab.add(_output())
    assert _report(lab)["counts"]["evidence"]["label"] == "nicht definiert"


def test_a_quote_in_an_error_report_is_no_evidence_for_a_comment(lab: Lab) -> None:
    lab.add(_output([_comment()], [_error("S1", "300 km", "Zahl")]))
    assert _report(lab)["counts"]["evidence"]["label"] == "0 von 1"


def test_comments_marked_global_by_the_chatbot_are_counted(lab: Lab) -> None:
    lab.add(_output([_comment(scope="global"), _comment(), _comment()]))
    assert _report(lab)["counts"]["self_marked_global"]["label"] == "1 von 3"


def test_measure_6_counts_references_inside_the_grid(lab: Lab) -> None:
    lab.add(_output([_comment(criteria=["K1", "K9"]), _comment(criteria=["K3"])]))
    assert _report(lab)["counts"]["criterion_fidelity"]["label"] == "2 von 3"


def test_measure_6_accepts_the_name_of_a_criterion(lab: Lab) -> None:
    lab.add(_output([_comment(criteria=["Wirkungsgrad", "Kosten"])]))
    assert _report(lab)["counts"]["criterion_fidelity"]["label"] == "1 von 2"


def test_measure_6_is_undefined_without_a_reference(lab: Lab) -> None:
    lab.add(_output([_comment()]))
    assert _report(lab)["counts"]["criterion_fidelity"]["label"] == "nicht definiert"


def test_measure_7_counts_comments_with_a_reference(lab: Lab) -> None:
    lab.add(_output([_comment(criteria=["K1", "K2"]), _comment(), _comment()]))
    assert _report(lab)["counts"]["criterion_coverage"]["label"] == "1 von 3"


def test_measure_7_counts_a_reference_outside_the_grid(lab: Lab) -> None:
    lab.add(_output([_comment(criteria=["K9"])]))
    assert _report(lab)["counts"]["criterion_coverage"]["label"] == "1 von 1"


def test_the_annotation_comparison_is_exploratory_and_not_reported(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km")], criteria=["K1", "K4"])]))
    report = an.analyze(lab.records(), {}, {}, ANNOTATED)
    label = report["spiel"]["exploratory"]["annotation_agreement"]["label"]
    assert label == "1 von 2"
    assert "exploratory" not in an.pilot_report(report)["spiel"]


def test_measure_8_uses_the_original_and_the_modified_grades_stay_apart(
    lab: Lab,
) -> None:
    report = _full_lab(lab)["spiel"]
    assert report["grade_variation"]["toy"]["distribution"] == {"2": 2}
    assert report["grades_modified"]["toy"]["v1"]["distribution"] == {"4": 1, "5": 1}


def test_a_grade_cell_gives_distribution_range_and_most_common_grade(lab: Lab) -> None:
    for number, grade in enumerate((2, 2, 5), start=1):
        lab.add(_output(grade=grade), str(number))
    assert _report(lab)["grade_variation"]["toy"] == {
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
    cell = _report(lab)["grade_variation"]["toy"]
    assert (cell["usable_runs"], cell["marked"]) == (2, True)
    assert cell["most_common"] == [2, 3]


def test_a_modified_cell_with_too_few_usable_runs_is_marked_too(lab: Lab) -> None:
    lab.add(_output(grade=2), version="v1")
    report = _report(lab)
    assert report["grades_modified"]["toy"]["v1"]["marked"] is True
    assert report["grade_variation"] == {}


def test_a_grade_cell_without_a_usable_run_stays_visible(lab: Lab) -> None:
    lab.add(b"kein JSON")
    report = an.analyze(lab.records(), {}, {})
    cell = report["spiel"]["grade_variation"]["toy"]
    assert (cell["usable_runs"], cell["marked"], cell["range"]) == (0, True, None)
    rendered = an.render(an.pilot_report(report))
    assert isinstance(rendered, dict)
    assert rendered["spiel"]["grade_variation"]["toy"]["range"] == "nicht definiert"


def test_detection_per_usable_and_per_attempted_run(lab: Lab) -> None:
    counts = _full_lab(lab)["spiel"]["counts"]
    assert counts["detection_per_usable_run"]["label"] == "1 von 2"
    assert counts["detection_per_attempted_run"]["label"] == "1 von 3"


def _one_report(lab: Lab, error: dict[str, str], version: str = "v1") -> None:
    lab.add(_output(errors=[error]), version=version)


def test_a_hit_needs_stage_1_and_ja_for_the_same_report(lab: Lab) -> None:
    lab.add(
        _output(
            errors=[
                _error("S1", "300 km", "Faktum"),
                _error("S2", "30 Minuten", "Zahl"),
            ]
        ),
        version="v1",
    )
    counts = _report(lab, TRAPS, _code("1", "v1", "ja", 2))["counts"]
    assert counts["detection_per_usable_run"]["label"] == "1 von 1"


def test_a_rewritten_number_can_pass_stage_1(lab: Lab) -> None:
    payload = json.loads(_output(errors=[_error("S2", "30 Minuten", "Zahl")]))
    payload["errors"][0]["sid"] = 2
    lab.add(json.dumps(payload).encode(), version="v1")
    counts = _report(lab, TRAPS, _code("1", "v1", "ja", 1))["counts"]
    assert counts["detection_per_usable_run"]["label"] == "1 von 1"


def test_a_number_in_another_form_cannot_pass_stage_1(lab: Lab) -> None:
    _one_report(lab, _error("Satz 2", "30 Minuten", "Zahl"))
    report = _report(lab, TRAPS, _code("1", "v1", "ja", 1))
    assert report["counts"]["detection_per_usable_run"]["label"] == "0 von 1"
    assert report["misplaced_hits"]["in_modified"] == 1


TWO_CATEGORIES = {
    "toy": {**TRAPS["toy"], "accepted_categories": ["Zahl", "Widerspruch"]}
}


def test_a_trap_with_two_accepted_categories_is_valid() -> None:
    an.validate_traps(TWO_CATEGORIES)


@pytest.mark.parametrize("category", ["Zahl", "Widerspruch"])
def test_either_accepted_category_passes_stage_1(lab: Lab, category: str) -> None:
    _one_report(lab, _error("S2", "30 Minuten", category))
    report = _report(lab, TWO_CATEGORIES, _code("1", "v1", "ja", 1))
    assert report["counts"]["detection_per_usable_run"]["label"] == "1 von 1"
    assert report["misplaced_hits"]["in_modified"] == 0


@pytest.mark.parametrize("category", ["Zahl", "Widerspruch"])
def test_either_accepted_category_can_be_a_false_alarm(lab: Lab, category: str) -> None:
    _one_report(lab, _error("S2", "30 Minuten", category), ORIGINAL_VERSION)
    report = _report(lab, TWO_CATEGORIES, _code("1", ORIGINAL_VERSION, "ja", 1))
    assert report["counts"]["false_alarm"]["label"] == "1 von 1"


def test_a_category_outside_the_list_does_not_pass_stage_1(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Faktum"))
    report = _report(lab, TWO_CATEGORIES, _code("1", "v1", "ja", 1))
    assert report["counts"]["detection_per_usable_run"]["label"] == "0 von 1"
    assert report["misplaced_hits"]["in_modified"] == 1


def test_an_accepted_category_elsewhere_does_not_pass_stage_1(lab: Lab) -> None:
    _one_report(lab, _error("S1", "300 km", "Widerspruch"))
    report = _report(lab, TWO_CATEGORIES, _code("1", "v1", "ja", 1))
    assert report["counts"]["detection_per_usable_run"]["label"] == "0 von 1"
    assert report["misplaced_hits"]["in_modified"] == 1


def test_the_list_decides_stage_1_not_the_type(lab: Lab) -> None:
    traps = {"toy": {**TRAPS["toy"], "type": "Zahl", "accepted_categories": ["Zahl"]}}
    _one_report(lab, _error("S2", "30 Minuten", "Widerspruch"))
    report = _report(lab, traps, _code("1", "v1", "ja", 1))
    assert report["counts"]["detection_per_usable_run"]["label"] == "0 von 1"


def test_ja_for_another_report_is_no_hit(lab: Lab) -> None:
    lab.add(
        _output(
            errors=[
                _error("S1", "300 km", "Faktum"),
                _error("S2", "30 Minuten", "Zahl"),
            ]
        ),
        version="v1",
    )
    report = _report(lab, TRAPS, _code("1", "v1", "ja", 1))
    assert report["counts"]["detection_per_usable_run"]["label"] == "0 von 1"
    assert report["misplaced_hits"]["in_modified"] == 1


def test_a_hit_does_not_need_a_valid_quote(lab: Lab) -> None:
    _one_report(lab, _error("S2", "99 Minuten", "Zahl"))
    counts = _report(lab, TRAPS, _code("1", "v1", "ja", 1))["counts"]
    assert counts["detection_per_usable_run"]["label"] == "1 von 1"


def test_nein_is_no_hit_even_at_stage_1(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Zahl"))
    counts = _report(lab, TRAPS, _code("1", "v1"))["counts"]
    assert counts["detection_per_usable_run"]["label"] == "0 von 1"


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(_error("S2", "30 Minuten", "Faktum"), id="other-type"),
        pytest.param(_error("S1", "300 km", "Zahl"), id="other-sentence"),
    ],
)
def test_ja_without_stage_1_is_reported_apart(lab: Lab, error: dict[str, str]) -> None:
    _one_report(lab, error)
    report = _report(lab, TRAPS, _code("1", "v1", "ja", 1))
    assert report["counts"]["detection_per_usable_run"]["label"] == "0 von 1"
    assert report["misplaced_hits"] == {"in_modified": 1, "in_original": 0}


def test_stage_1_takes_a_report_at_either_sentence_of_a_contradiction(lab: Lab) -> None:
    traps = {
        **TRAPS,
        "toy": {
            **TRAPS["toy"],
            "type": "Widerspruch",
            "accepted_categories": ["Widerspruch"],
            "sids": ["S1", "S2"],
        },
    }
    _one_report(lab, _error("S1", "300 km", "Widerspruch"))
    counts = _report(lab, traps, _code("1", "v1", "ja", 1))["counts"]
    assert counts["detection_per_usable_run"]["label"] == "1 von 1"


def test_a_false_alarm_needs_stage_1_and_ja_in_the_original(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Zahl"), ORIGINAL_VERSION)
    counts = _report(lab, TRAPS, _code("1", ORIGINAL_VERSION, "ja", 1))["counts"]
    assert counts["false_alarm"]["label"] == "1 von 1"


def test_other_criticism_at_the_site_is_no_false_alarm(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Zahl"), ORIGINAL_VERSION)
    counts = _report(lab, TRAPS, _code("1", ORIGINAL_VERSION))["counts"]
    assert counts["false_alarm"]["label"] == "0 von 1"


def test_ja_without_stage_1_in_the_original_is_no_false_alarm(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Sprache"), ORIGINAL_VERSION)
    report = _report(lab, TRAPS, _code("1", ORIGINAL_VERSION, "ja", 1))
    assert report["counts"]["false_alarm"]["label"] == "0 von 1"
    assert report["misplaced_hits"]["in_original"] == 1


def test_unclear_in_the_modified_version_is_a_hit_only_in_the_counter_view(
    lab: Lab,
) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Zahl"))
    counts = _report(lab, TRAPS, _code("1", "v1", "unklar"))["counts"]
    assert counts["unclear"]["label"] == "1 von 1"
    assert counts["detection_per_usable_run"]["label"] == "0 von 1"
    counter = counts["counter_assumption"]
    assert counter["detection_per_usable_run"]["label"] == "1 von 1"


def test_unclear_in_the_original_is_an_alarm_only_in_the_main_view(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Zahl"), ORIGINAL_VERSION)
    counts = _report(lab, TRAPS, _code("1", ORIGINAL_VERSION, "unklar"))["counts"]
    assert counts["false_alarm"]["label"] == "1 von 1"
    assert counts["counter_assumption"]["false_alarm"]["label"] == "0 von 1"


def test_a_coded_unknown_category_follows_the_same_two_views(lab: Lab) -> None:
    unknown = _error("S2", "30 Minuten", "Grammatik")
    _one_report(lab, unknown)
    _one_report(lab, unknown, ORIGINAL_VERSION)
    codes = {**_code("1", "v1", "ja", 1), **_code("1", ORIGINAL_VERSION, "ja", 1)}
    counts = _report(lab, TRAPS, codes)["counts"]
    assert counts["detection_per_usable_run"]["label"] == "0 von 1"
    assert counts["false_alarm"]["label"] == "1 von 1"
    counter = counts["counter_assumption"]
    assert counter["detection_per_usable_run"]["label"] == "1 von 1"
    assert counter["false_alarm"]["label"] == "0 von 1"


def test_an_unknown_category_away_from_the_target_stays_misplaced_in_both_views(
    lab: Lab,
) -> None:
    unknown = _error("S1", "300 km", "Grammatik")
    _one_report(lab, unknown)
    _one_report(lab, unknown, ORIGINAL_VERSION)
    codes = {**_code("1", "v1", "ja", 1), **_code("1", ORIGINAL_VERSION, "ja", 1)}
    report = _report(lab, TRAPS, codes)
    counts = report["counts"]
    counter = counts["counter_assumption"]
    assert counts["detection_per_usable_run"]["label"] == "0 von 1"
    assert counter["detection_per_usable_run"]["label"] == "0 von 1"
    assert counts["false_alarm"]["label"] == "0 von 1"
    assert counter["false_alarm"]["label"] == "0 von 1"
    assert report["misplaced_hits"] == {"in_modified": 1, "in_original": 1}


def test_an_unknown_category_coded_nein_changes_nothing(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Grammatik"), ORIGINAL_VERSION)
    counts = _report(lab, TRAPS, _code("1", ORIGINAL_VERSION))["counts"]
    assert counts["false_alarm"]["label"] == "0 von 1"
    assert counts["counter_assumption"]["false_alarm"]["label"] == "0 von 1"


def test_unknown_categories_are_counted_by_place(lab: Lab) -> None:
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Grammatik")]))
    lab.add(_output(errors=[_error("S2", "30 Minuten", "Stil")]), version="v1")
    lab.add(_output(errors=[_error("S1", "300 km", "Stil")]), "2", version="v1")
    codes = {**_code(), **_code("1", "v1"), **_code("2", "v1")}
    assert _report(lab, TRAPS, codes)["unknown_category"] == {
        "reports": 3,
        "at_target_in_original": 1,
        "at_target_in_modified": 1,
        "elsewhere": 1,
    }


def test_the_counter_view_changes_nothing_without_unclear_cases(lab: Lab) -> None:
    counts = _full_lab(lab)["spiel"]["counts"]
    counter = counts["counter_assumption"]
    assert counter["detection_per_usable_run"] == counts["detection_per_usable_run"]
    assert counter["false_alarm"] == counts["false_alarm"]


def test_a_usable_run_without_a_code_stops_the_analysis(lab: Lab) -> None:
    _one_report(lab, _error("S2", "30 Minuten", "Zahl"))
    with pytest.raises(CodingError, match="run has no code"):
        _report(lab, TRAPS, {})


def test_a_failed_run_needs_no_code(lab: Lab) -> None:
    lab.add(b"kein JSON", version="v1")
    counts = _report(lab, TRAPS, {})["counts"]
    assert counts["detection_per_attempted_run"]["label"] == "0 von 1"
    assert counts["detection_per_usable_run"]["label"] == "nicht definiert"


def test_no_trap_leaves_the_trap_measures_undefined(lab: Lab) -> None:
    lab.add(_output())
    counts = _report(lab)["counts"]
    assert counts["detection_per_usable_run"]["label"] == "nicht definiert"
    assert counts["detection_per_attempted_run"]["label"] == "nicht definiert"
    assert counts["false_alarm"]["label"] == "nicht definiert"
    assert counts["unclear"]["label"] == "nicht definiert"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        pytest.param({"type": "Sprache"}, "type must be", id="type-outside-the-list"),
        pytest.param({"sids": ["S1", "S2"]}, "allows 1", id="two-sites-for-a-number"),
        pytest.param({"sids": []}, "allows 1", id="no-site"),
        pytest.param({"sids": ["1"]}, "sentence numbers", id="malformed-site"),
        pytest.param(
            {"accepted_categories": None}, "one or two", id="no-accepted-categories"
        ),
        pytest.param(
            {"accepted_categories": "Zahl"}, "one or two", id="categories-not-a-list"
        ),
        pytest.param({"accepted_categories": []}, "one or two", id="empty-categories"),
        pytest.param(
            {"accepted_categories": ["Zahl", "Faktum", "Unsinn"]},
            "one or two",
            id="three-categories",
        ),
        pytest.param(
            {"accepted_categories": ["Zahl", "Sprache"]},
            "one or two",
            id="category-outside-the-list",
        ),
        pytest.param(
            {"accepted_categories": ["Zahl", "Zahl"]},
            "one or two",
            id="category-repeated",
        ),
        pytest.param(
            {"accepted_categories": ["Zahl", ["Faktum"]]},
            "one or two",
            id="category-not-a-text",
        ),
        pytest.param(
            {"accepted_categories": ["Faktum"]}, "hold the type", id="type-not-accepted"
        ),
        pytest.param({"version": "original"}, "modified version", id="original"),
        pytest.param({"description": " "}, "description", id="blank-description"),
    ],
)
def test_a_trap_outside_the_agreed_form_is_refused(
    lab: Lab, change: dict[str, Any], message: str
) -> None:
    lab.add(_output())
    traps = {"toy": {**TRAPS["toy"], **change}}
    with pytest.raises(an.TrapError, match=message):
        an.analyze(lab.records(), traps, {})


def test_a_contradiction_may_not_span_three_sentences(lab: Lab) -> None:
    trap = {
        **TRAPS["toy"],
        "type": "Widerspruch",
        "accepted_categories": ["Widerspruch"],
        "sids": ["S1", "S2", "S3"],
    }
    with pytest.raises(an.TrapError, match="allows 2"):
        an.analyze(lab.records(), {"toy": trap}, {})


def test_code_blocks_are_counted_per_chatbot(lab: Lab) -> None:
    fenced = b"```json\n" + _output() + b"\n```"
    lab.add(fenced, "1", model="eins")
    lab.add(fenced, "2", model="eins")
    lab.add(_output(), "1", model="zwei")
    report = an.analyze(lab.records(), {}, {})
    assert report["eins"]["import_notes"]["code_fences_removed"] == 2
    assert report["zwei"]["import_notes"]["code_fences_removed"] == 0


def test_the_report_counts_what_the_importer_tolerated(lab: Lab) -> None:
    body = _output(errors=[_error("S1", "x", "Grammatik"), _error("S2", "y", "Stil")])
    lab.add(b"```json\n" + body + b"\n```", "1")
    lab.add(_output(errors=[_error("S1", "x", "Zahl")]), "2")
    lab.add(b"```json\nkein JSON\n```", "3")
    report = _report(lab)
    assert report["import_notes"] == {
        "code_fences_removed": 1,
        "sids_rewritten": NO_REWRITES,
        "invalid_category_entries": 2,
    }
    assert report["counts"]["failures"]["label"] == "1 von 3"


def test_the_estimate_is_the_mean_per_text_not_the_pooled_mean() -> None:
    assert an.mean_per_text({"a": [1.0], "b": [0.0, 0.0, 0.0]}) == 0.5


def test_a_text_without_a_defined_value_leaves_the_mean() -> None:
    assert an.mean_per_text({"a": [1.0], "b": [None, None]}) == 1.0
    assert an.mean_per_text({"a": [None]}) is None


def test_counts_and_rates_agree_on_a_single_run(lab: Lab) -> None:
    lab.add(_output([_comment(quotes=[("S1", "300 km"), ("S1", "999 km")])]))
    report = _report(lab)
    assert report["counts"]["quotes"]["strict"]["text"]["label"] == "1 von 2"
    assert report["rates"]["quote_fidelity"]["strict"]["text"] == 0.5


def test_models_are_kept_apart(lab: Lab) -> None:
    lab.add(_output(grade=1), model="spiel")
    lab.add(_output(grade=6), model="anderes")
    report = an.analyze(lab.records(), {}, {})
    assert list(report) == ["anderes", "spiel"]
    assert report["anderes"]["grade_variation"]["toy"]["most_common"] == [6]


def test_the_pilot_report_gives_counts_and_no_rates(lab: Lab) -> None:
    report = an.pilot_report(_full_lab(lab))["spiel"]
    assert "rates" not in report
    assert report["counts"]["failures"] == {"count": 2, "of": 6, "label": "2 von 6"}
    assert report["counts"]["evidence"]["label"] == "1 von 4"
    assert report["counts"]["false_alarm"]["label"] == "0 von 2"


def test_the_report_holds_every_measure_of_the_pilot(lab: Lab) -> None:
    """Measure 5 does not apply to the pilot."""

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
        12: counts["unclear"],
    }
    assert len(measures) == 11
    assert all(value is not None for value in measures.values())
    assert counts["quotes"]["normalized"]["text"]
    assert counts["quotes"]["normalized"]["text_and_location"]


def test_the_scripts_run_from_import_to_report(lab: Lab, tmp_path: Path) -> None:
    _full_lab(lab)
    imported = tmp_path / "imported.json"
    arguments = ["--runs", str(lab.runs), "--banks", str(lab.banks)]
    arguments += ["--schema", str(SCHEMA_PATH), "--out", str(imported)]
    assert imp.main(arguments) == 0

    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps(TRAPS), "utf-8")
    sheet, key = tmp_path / "sheet.csv", tmp_path / "key.json"
    arguments = ["--imported", str(imported), "--targets", str(targets)]
    assert export.main([*arguments, "--sheet", str(sheet), "--key", str(key)]) == 0

    runs = json.loads(key.read_text("utf-8"))["runs"]
    rows = list(csv.DictReader(io.StringIO(sheet.read_text("utf-8-sig"))))
    for row in rows:
        if "\n" in row["meldungen"] or row["meldungen"].startswith("1:"):
            hit = runs[row["lauf"]]["version"] == "v1"
            row["antwort"], row["meldung_nr"] = ("ja", "1") if hit else ("nein", "")
    sheet.write_bytes(export.sheet_bytes(rows))

    report = tmp_path / "report.json"
    arguments = ["--imported", str(imported), "--targets", str(targets)]
    arguments += ["--coding-sheet", str(sheet), "--coding-key", str(key)]
    assert an.main([*arguments, "--out", str(report)]) == 0
    written = json.loads(report.read_text("utf-8"))["spiel"]
    assert written["usable_runs"] == 4
    assert written["counts"]["detection_per_usable_run"]["label"] == "1 von 2"
    assert "rates" not in written
