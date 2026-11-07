"""The prompt generator, tested on invented texts and an example trap file."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Any

import analyze as an
import genius_loader as loader
import import_runs as imp
import make_prompts as mp
import make_run_plan as plan_module
import pytest
from check_quotes import check_quote
from reserve import current_pilot

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SENTENCES = {
    "beispiel_a": [
        "Das Auto fährt 300 km weit.",
        "Der Akku lädt in 30 Minuten.",
        "Wasserstoff bleibt sehr teuer.",
    ],
    "beispiel_b": [
        "Die Bahn ist teurer als der Bus.",
        "Beide fahren durch die Stadt.",
        "Am Ende bleibt der Bus billiger.",
    ],
    "beispiel_c": [
        "Die Sonne geht im Osten auf.",
        "Am Abend wird es kühl.",
    ],
}
MODIFIED_LINES = {
    "beispiel_a": (
        "[S2] Der Akku lädt in 30 Minuten.",
        "[S2] Der Akku lädt in 3 Minuten.",
    ),
    "beispiel_b": (
        "[S3] Am Ende bleibt der Bus billiger.",
        "[S3] Am Ende bleibt die Bahn billiger.",
    ),
    "beispiel_c": (
        "[S1] Die Sonne geht im Osten auf.",
        "[S1] Die Sonne geht im Westen auf.",
    ),
}
TEMPLATE = (
    "Kopf für Menschen.\n\n---\n\nRolle.\n\n{{ERWARTUNGSHORIZONT}}\n\n"
    "## Aufsatz\n\n{{SATZBANK}}\n\n## Ende\n\n{{AUSGABESCHEMA}}\n"
)
SCRIPT_COMMIT = "c" * 40
real_script_commit = mp.script_commit
Traps = dict[str, dict[str, Any]]


class Bench:
    """An invented study folder with the example inputs."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.banks = root / "banks"
        self.banks.mkdir()
        for text_id, sentences in SENTENCES.items():
            bank = loader.build_bank(text_id, sentences)
            path = self.banks / f"{text_id}.json"
            path.write_bytes(loader.dump_json(bank.as_dict()))
        self.plan = root / "laufplan.csv"
        plan = plan_module.build_plan(sorted(SENTENCES), 20261113)
        self.plan.write_bytes(plan_module.plan_bytes(plan))
        self.traps = root / "fallen.json"
        shutil.copy(FIXTURES / "example_traps.json", self.traps)
        self.guide = root / "horizont.md"
        shutil.copy(FIXTURES / "example_guide.md", self.guide)
        self.template = root / "vorlage.md"
        self.template.write_text(TEMPLATE, "utf-8")
        self.schema = imp.DEFAULT_SCHEMA
        self.output = root / "study"

    def arguments(self) -> list[str]:
        return [
            f"--guide={self.guide}",
            f"--traps={self.traps}",
            f"--plan={self.plan}",
            f"--template={self.template}",
            f"--schema={self.schema}",
            f"--banks={self.banks}",
            f"--root={self.output}",
        ]

    def run(self) -> int:
        return mp.main(self.arguments())

    def read_traps(self) -> Traps:
        loaded: Traps = json.loads(self.traps.read_text("utf-8"))
        return loaded

    def write_traps(self, traps: Traps) -> None:
        self.traps.write_text(json.dumps(traps, ensure_ascii=False), "utf-8")

    def edit_first_trap(self, **changes: object) -> None:
        traps = self.read_traps()
        edit = traps["beispiel_a"]["edits"][0]
        edit.update(changes)
        self.write_traps(traps)

    def prompt(self, text_id: str, version: str) -> str:
        path = self.output / "runs/prompts" / f"{text_id}.{version}.md"
        return path.read_text("utf-8")

    def written(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.output).as_posix(): path.read_bytes()
            for path in sorted(self.output.rglob("*"))
            if path.is_file()
        }


@pytest.fixture(autouse=True)
def fixed_script_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    """The commit of the working copy is not what these tests are about."""

    monkeypatch.setattr(mp, "script_commit", lambda: SCRIPT_COMMIT)


@pytest.fixture
def bench(tmp_path: Path) -> Bench:
    return Bench(tmp_path)


@pytest.fixture
def banks() -> dict[str, loader.SentenceBank]:
    return {key: loader.build_bank(key, value) for key, value in SENTENCES.items()}


def _refused(bench: Bench, capsys: pytest.CaptureFixture[str], reason: str) -> None:
    assert bench.run() == 1
    captured = capsys.readouterr().err
    assert "REFUSED, nothing written" in captured
    assert reason in captured
    assert not bench.output.exists()


def test_the_example_inputs_give_six_prompts_six_banks_and_a_manifest(
    bench: Bench,
) -> None:
    assert bench.run() == 0
    expected = [
        f"runs/{folder}/{text_id}{suffix}"
        for text_id in SENTENCES
        for folder, suffix in (
            ("prompts", ".original.md"),
            ("prompts", ".veraendert.md"),
            ("banks", ".json"),
            ("banks", ".veraendert.json"),
        )
    ]
    assert sorted(bench.written()) == sorted([*expected, "runs/manifest.json"])


def test_the_prompts_are_exactly_the_files_of_the_plan(bench: Bench) -> None:
    assert bench.run() == 0
    named = mp.prompt_files(bench.plan.read_text("utf-8"))
    assert sorted(named.values()) == sorted(
        name for name in bench.written() if name.startswith("runs/prompts/")
    )


def test_the_result_is_the_same_in_every_run(tmp_path: Path) -> None:
    (tmp_path / "eins").mkdir()
    (tmp_path / "zwei").mkdir()
    first, second = Bench(tmp_path / "eins"), Bench(tmp_path / "zwei")
    assert first.run() == 0
    assert second.run() == 0
    assert first.written() == second.written()


def test_a_second_run_with_the_same_inputs_changes_nothing(bench: Bench) -> None:
    assert bench.run() == 0
    before = bench.written()
    assert bench.run() == 0
    assert bench.written() == before


@pytest.mark.parametrize("text_id", sorted(SENTENCES))
def test_the_versions_differ_in_exactly_the_defined_line(
    bench: Bench, text_id: str
) -> None:
    assert bench.run() == 0
    original = bench.prompt(text_id, "original").split("\n")
    modified = bench.prompt(text_id, "veraendert").split("\n")
    assert len(original) == len(modified)
    differing = [
        pair for pair in zip(original, modified, strict=True) if pair[0] != pair[1]
    ]
    assert differing == [MODIFIED_LINES[text_id]]


def test_the_sentences_carry_their_numbers_in_the_agreed_form(bench: Bench) -> None:
    assert bench.run() == 0
    for text_id, sentences in SENTENCES.items():
        block = bench.prompt(text_id, "original").split("## Aufsatz\n\n")[1]
        lines = block.split("\n\n## Ende")[0].split("\n")
        assert lines == [
            f"[S{number}] {sentence}" for number, sentence in enumerate(sentences, 1)
        ]


def test_the_prompt_holds_the_guide_and_the_schema(bench: Bench) -> None:
    assert bench.run() == 0
    prompt = bench.prompt("beispiel_a", "original")
    assert bench.guide.read_text("utf-8").strip() in prompt
    assert bench.schema.read_text("utf-8").strip() in prompt
    assert "{{" not in prompt


def test_only_the_part_below_the_line_is_sent(bench: Bench) -> None:
    assert bench.run() == 0
    prompt = bench.prompt("beispiel_a", "original")
    assert prompt.startswith("Rolle.\n")
    assert "Kopf für Menschen" not in prompt
    assert prompt.endswith("}\n")


def test_inserted_text_is_not_filled_again(bench: Bench) -> None:
    bench.guide.write_text("Bitte {{SATZBANK}} wörtlich lassen.", "utf-8")
    assert bench.run() == 0
    assert "Bitte {{SATZBANK}} wörtlich lassen." in bench.prompt(
        "beispiel_a", "original"
    )


def test_the_prompt_reveals_neither_the_trap_nor_the_version(bench: Bench) -> None:
    assert bench.run() == 0
    traps = bench.read_traps()
    for text_id, trap in traps.items():
        for version in ("original", "veraendert"):
            prompt = bench.prompt(text_id, version)
            assert trap["description"] not in prompt
            assert text_id not in prompt
            assert version not in prompt


def test_the_original_prompt_does_not_depend_on_the_edit(bench: Bench) -> None:
    assert bench.run() == 0
    before = bench.prompt("beispiel_a", "original")
    bench.edit_first_trap(to="4 Minuten")
    shutil.rmtree(bench.output)
    assert bench.run() == 0
    assert bench.prompt("beispiel_a", "original") == before


def test_the_original_bank_is_a_byte_copy(bench: Bench) -> None:
    assert bench.run() == 0
    for text_id in SENTENCES:
        copied = bench.output / "runs/banks" / f"{text_id}.json"
        assert copied.read_bytes() == (bench.banks / f"{text_id}.json").read_bytes()


def test_the_modified_bank_is_sound_and_checks_the_changed_text(bench: Bench) -> None:
    assert bench.run() == 0
    bank = loader.read_bank(bench.output / "runs/banks/beispiel_a.veraendert.json")
    for sentence in bank.sentences:
        assert bank.full_text[sentence.start : sentence.end] == sentence.text
    assert check_quote(bank, "S2", "in 3 Minuten", "strict").location_valid
    assert not check_quote(bank, "S2", "in 30 Minuten", "strict").text_valid


def test_the_import_reads_the_written_banks_and_ignores_the_new_folders(
    bench: Bench,
) -> None:
    assert bench.run() == 0
    runs = bench.output / "runs"
    folder = runs / "chatgpt/beispiel_a/veraendert"
    folder.mkdir(parents=True)
    quote = {"sid": "[S2]", "quote": "in 3 Minuten"}
    answer = {
        "grade": 3,
        "comments": [
            {"text": "x", "scope": "local", "quotes": [quote], "criteria": ["K1"]}
        ],
        "errors": [],
    }
    assert (runs / "manifest.json").is_file()
    (folder / "1.json").write_text(json.dumps(answer), "utf-8")
    (folder / "1.meta.json").write_text(
        json.dumps(
            {
                "date": "2026-11-20",
                "time": "14:30",
                "model_name": "Spielmodell",
                "chat_mode": "Temporär",
                "account_type": "Kostenlos",
            }
        ),
        "utf-8",
    )
    schema = json.loads(imp.DEFAULT_SCHEMA.read_text("utf-8"))
    records = imp.import_all(runs, runs / "banks", schema)
    assert [asdict(record)["status"] for record in records] == [imp.USABLE]
    assert records[0].references[0].origin_strict == imp.DELIVERED_VALID


def test_the_analysis_accepts_the_same_trap_file(bench: Bench) -> None:
    an.validate_traps(bench.read_traps())


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _manifest(bench: Bench) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(
        (bench.output / "runs/manifest.json").read_text("utf-8")
    )
    return loaded


def test_the_manifest_names_every_input_and_result_by_hash(bench: Bench) -> None:
    assert bench.run() == 0
    written = bench.written()
    manifest = _manifest(bench)
    assert set(manifest) == {
        "script_commit",
        "guide_sha256",
        "traps_sha256",
        "banks",
        "prompts",
    }
    assert manifest["script_commit"] == SCRIPT_COMMIT
    assert manifest["guide_sha256"] == _sha256(bench.guide.read_bytes())
    assert manifest["traps_sha256"] == _sha256(bench.traps.read_bytes())
    for key, folder in (("banks", "runs/banks/"), ("prompts", "runs/prompts/")):
        expected = {
            name: _sha256(content)
            for name, content in written.items()
            if name.startswith(folder)
        }
        assert len(expected) == 6
        assert manifest[key] == expected


def test_the_manifest_hashes_the_guide_as_a_file_not_as_inserted(bench: Bench) -> None:
    bench.guide.write_bytes(b"\n\n  Text mit Rand.  \n\n")
    assert bench.run() == 0
    assert _manifest(bench)["guide_sha256"] == _sha256(bench.guide.read_bytes())


def test_a_changed_guide_changes_the_manifest(tmp_path: Path) -> None:
    (tmp_path / "eins").mkdir()
    (tmp_path / "zwei").mkdir()
    first, second = Bench(tmp_path / "eins"), Bench(tmp_path / "zwei")
    second.guide.write_text("Ein anderer Text.", "utf-8")
    assert first.run() == 0
    assert second.run() == 0
    assert _manifest(first)["guide_sha256"] != _manifest(second)["guide_sha256"]
    assert _manifest(first)["prompts"] != _manifest(second)["prompts"]


def test_the_manifest_holds_no_local_path(bench: Bench) -> None:
    assert bench.run() == 0
    written = (bench.output / "runs/manifest.json").read_text("utf-8")
    assert str(bench.root) not in written


def test_a_new_script_commit_does_not_replace_the_manifest(
    bench: Bench,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert bench.run() == 0
    before = bench.written()
    monkeypatch.setattr(mp, "script_commit", lambda: "d" * 40)
    assert bench.run() == 1
    assert "different files already exist" in capsys.readouterr().err
    assert bench.written() == before


def test_a_script_without_a_commit_writes_nothing(
    bench: Bench,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refused() -> str:
        raise mp.PromptError("make_prompts.py differs from its commit")

    monkeypatch.setattr(mp, "script_commit", refused)
    _refused(bench, capsys, "differs from its commit")


def _git(folder: Path, *arguments: str) -> str:
    identity = ("-c", "user.name=Test", "-c", "user.email=test@example.invalid")
    return subprocess.run(
        ["git", *identity, *arguments],
        cwd=folder,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    """A small repository with the script in one commit; returns the script."""

    _git(tmp_path, "init", "-q")
    script = tmp_path / "werkzeug.py"
    script.write_text("# Fassung eins\n", "utf-8")
    _git(tmp_path, "add", "werkzeug.py")
    _git(tmp_path, "commit", "-q", "-m", "eins")
    return script


def test_the_script_commit_is_the_commit_of_a_clean_script(repository: Path) -> None:
    assert real_script_commit(repository) == _git(
        repository.parent, "rev-parse", "HEAD"
    )


def test_a_later_commit_of_another_file_keeps_the_script_commit(
    repository: Path,
) -> None:
    folder = repository.parent
    expected = _git(folder, "rev-parse", "HEAD")
    (folder / "anderes.txt").write_text("x", "utf-8")
    _git(folder, "add", "anderes.txt")
    _git(folder, "commit", "-q", "-m", "zwei")
    assert real_script_commit(repository) == expected


def test_a_later_commit_of_the_script_is_the_new_commit(repository: Path) -> None:
    folder = repository.parent
    repository.write_text("# Fassung zwei\n", "utf-8")
    _git(folder, "add", "werkzeug.py")
    _git(folder, "commit", "-q", "-m", "zwei")
    assert real_script_commit(repository) == _git(folder, "rev-parse", "HEAD")


def test_a_changed_script_has_no_commit(repository: Path) -> None:
    repository.write_text("# Geändert\n", "utf-8")
    with pytest.raises(mp.PromptError, match="differs from its commit"):
        real_script_commit(repository)


def test_a_staged_change_has_no_commit(repository: Path) -> None:
    repository.write_text("# Geändert\n", "utf-8")
    _git(repository.parent, "add", "werkzeug.py")
    with pytest.raises(mp.PromptError, match="differs from its commit"):
        real_script_commit(repository)


def test_an_untracked_script_has_no_commit(repository: Path) -> None:
    other = repository.parent / "neu.py"
    other.write_text("# Neu\n", "utf-8")
    with pytest.raises(mp.PromptError, match="differs from its commit"):
        real_script_commit(other)


def test_an_ignored_script_has_no_commit(repository: Path) -> None:
    folder = repository.parent
    (folder / ".gitignore").write_text("verborgen.py\n", "utf-8")
    hidden = folder / "verborgen.py"
    hidden.write_text("# Verborgen\n", "utf-8")
    with pytest.raises(mp.PromptError, match="has no commit"):
        real_script_commit(hidden)


def test_a_script_outside_git_has_no_commit(tmp_path: Path) -> None:
    script = tmp_path / "werkzeug.py"
    script.write_text("# Ohne Git\n", "utf-8")
    with pytest.raises(mp.PromptError, match="not in a Git checkout"):
        real_script_commit(script)


def test_a_missing_git_is_refused(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_git(*_: object, **__: object) -> None:
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", no_git)
    with pytest.raises(mp.PromptError, match="Git cannot run"):
        real_script_commit(repository)


@pytest.mark.parametrize(
    "ignored",
    [
        "runs/",
        "prereg/injection_proposals.md",
        "prereg/injection_proposals_v2.md",
        "prereg/traps_draft.json",
    ],
)
def test_private_files_stay_out_of_git(study_root: Path, ignored: str) -> None:
    assert ignored in (study_root / ".gitignore").read_text("utf-8").split()


def test_the_guide_and_the_traps_have_no_default_path(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as stopped:
        mp.main([])
    assert stopped.value.code == 2
    message = capsys.readouterr().err
    assert "--guide" in message
    assert "--traps" in message


def test_the_script_names_no_held_out_path(study_root: Path) -> None:
    source = (study_root / "scripts/make_prompts.py").read_text("utf-8")
    assert "sealed" not in source


def test_the_committed_plan_and_banks_give_six_prompts(
    study_root: Path, tmp_path: Path
) -> None:
    """A placeholder replaces each first sentence; no real site is involved."""

    plan = (study_root / "prereg/laufplan.csv").read_text("utf-8")
    files = mp.prompt_files(plan)
    selection = json.loads((study_root / "prereg/selection.json").read_text("utf-8"))
    pilot = current_pilot(selection)
    assert sorted(files) == sorted(
        (text_id, version) for text_id in pilot for version in plan_module.VERSIONS
    )
    selected = study_root / "data/selected"
    traps: Traps = {}
    for text_id in pilot:
        first = loader.read_bank(selected / f"{text_id}.json").sentences[0]
        traps[text_id] = {
            "version": "veraendert",
            "type": "Unsinn",
            "accepted_categories": ["Unsinn"],
            "sids": ["S1"],
            "description": "Platzhalter.",
            "edits": [{"sid": "S1", "from": first.text, "to": "Platzhalter."}],
        }
    built = mp.build_files(
        files,
        selected,
        traps,
        "Platzhalter.",
        (study_root / "prompts/grading_prompt_de.md").read_text("utf-8"),
        imp.DEFAULT_SCHEMA.read_text("utf-8"),
    )
    assert len(built) == 12
    mp.write_files(built, tmp_path)
    for text_id in pilot:
        sent = (tmp_path / f"runs/prompts/{text_id}.original.md").read_text("utf-8")
        assert sent.startswith("Du bist eine Korrekturhilfe")
        assert sent.count("[S1] ") == 1
        assert "{{" not in sent


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        pytest.param({"from": "99 Minuten"}, "exactly once", id="from-not-in-sentence"),
        pytest.param({"from": "e"}, "exactly once", id="from-twice"),
        pytest.param({"from": ""}, "exactly once", id="from-empty"),
        pytest.param({"to": "30 Minuten"}, "changes nothing", id="no-change"),
        pytest.param({"to": ""}, "one line", id="to-empty"),
        pytest.param({"to": "   "}, "one line", id="to-blank"),
        pytest.param({"to": "3\nMinuten"}, "one line", id="to-line-break"),
        pytest.param({"to": "3 Minuten"}, "one line", id="to-line-separator"),
        pytest.param({"sid": "S1"}, "not a target", id="outside-the-target"),
        pytest.param({"sid": "S99"}, "not a target", id="unknown-sentence"),
        pytest.param({"to": 3}, "must be texts", id="to-not-a-text"),
        pytest.param({"extra": "x"}, "exactly sid, from and to", id="extra-key"),
    ],
)
def test_an_unusable_edit_is_refused(
    bench: Bench,
    capsys: pytest.CaptureFixture[str],
    changes: dict[str, object],
    reason: str,
) -> None:
    bench.edit_first_trap(**changes)
    _refused(bench, capsys, reason)


def test_a_passage_that_overlaps_itself_counts_twice(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    bench.banks.joinpath("beispiel_a.json").write_bytes(
        loader.dump_json(
            loader.build_bank("beispiel_a", ["Eins.", "Es ist aaa."]).as_dict()
        )
    )
    bench.edit_first_trap(**{"from": "aa", "to": "b"})
    _refused(bench, capsys, "exactly once")


def test_a_clean_edit_with_the_same_shape_passes(bench: Bench) -> None:
    bench.edit_first_trap(**{"from": "lädt", "to": "tankt"})
    assert bench.run() == 0


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        pytest.param(lambda trap: trap.pop("edits"), "no edits", id="no-edits-key"),
        pytest.param(lambda trap: trap.update(edits=[]), "no edits", id="empty-edits"),
        pytest.param(
            lambda trap: trap.update(edits="S2"), "no edits", id="edits-not-a-list"
        ),
        pytest.param(
            lambda trap: trap["edits"].append(
                {"sid": "S2", "from": "Akku", "to": "Tank"}
            ),
            "one edit only",
            id="two-edits-in-a-sentence",
        ),
        pytest.param(
            lambda trap: trap.update(type="Sprache"), "type must be", id="wrong-type"
        ),
        pytest.param(
            lambda trap: trap.update(sids=["S1", "S2"]), "allows 1", id="two-sites"
        ),
        pytest.param(
            lambda trap: trap.update(sids=["S9"]),
            "no sentence",
            id="target-not-in-the-text",
        ),
        pytest.param(
            lambda trap: trap.update(version="anders"),
            "version is veraendert",
            id="other-version",
        ),
    ],
)
def test_an_unusable_trap_is_refused(
    bench: Bench,
    capsys: pytest.CaptureFixture[str],
    change: Callable[[dict[str, Any]], object],
    reason: str,
) -> None:
    traps = bench.read_traps()
    change(traps["beispiel_a"])
    bench.write_traps(traps)
    _refused(bench, capsys, reason)


def test_a_contradiction_may_edit_both_of_its_sentences(bench: Bench) -> None:
    traps = bench.read_traps()
    traps["beispiel_b"]["edits"].append(
        {"sid": "S1", "from": "teurer", "to": "billiger"}
    )
    bench.write_traps(traps)
    assert bench.run() == 0
    original = bench.prompt("beispiel_b", "original").split("\n")
    modified = bench.prompt("beispiel_b", "veraendert").split("\n")
    assert sum(old != new for old, new in zip(original, modified, strict=True)) == 2


def test_a_change_in_the_text_conversion_stops_the_script(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    """The bank conversion would alter these, so the text would not be as defined."""

    decomposed = unicodedata.normalize("NFD", "3 Münzen")
    assert decomposed != "3 Münzen"
    bench.edit_first_trap(to=decomposed)
    _refused(bench, capsys, "differs from its definition")


def test_an_html_entity_in_an_edit_stops_the_script(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    bench.edit_first_trap(to="3 &amp; 4 Minuten")
    _refused(bench, capsys, "differs from its definition")


def test_an_entity_elsewhere_in_the_text_stops_the_script(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    bank = loader.build_bank("beispiel_a", SENTENCES["beispiel_a"])
    data = bank.as_dict()
    text = "Es kostet &lt;viel&gt;."
    sentences = data["sentences"]
    assert isinstance(sentences, list)
    last = sentences[-1]
    data["full_text"] = str(data["full_text"]).replace(last["text"], text)
    last["text"] = text
    last["end"] = last["start"] + len(text)
    (bench.banks / "beispiel_a.json").write_bytes(loader.dump_json(data))
    _refused(bench, capsys, "S3 differs from its definition")


@pytest.mark.parametrize(
    ("traps", "reason"),
    [
        pytest.param("{", "not strict JSON", id="broken"),
        pytest.param('{"a": 1, "a": 2}', "not strict JSON", id="repeated-key"),
        pytest.param("[]", "must map", id="list"),
        pytest.param('{"beispiel_a": 1}', "must map", id="trap-not-an-object"),
    ],
)
def test_an_unreadable_trap_file_is_refused(
    bench: Bench, capsys: pytest.CaptureFixture[str], traps: str, reason: str
) -> None:
    bench.traps.write_text(traps, "utf-8")
    _refused(bench, capsys, reason)


def test_a_missing_trap_is_refused(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    traps = bench.read_traps()
    del traps["beispiel_c"]
    bench.write_traps(traps)
    _refused(bench, capsys, "exactly the texts of the plan")


def test_a_trap_for_a_foreign_text_is_refused(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    traps = bench.read_traps()
    traps["fremd"] = traps["beispiel_c"]
    bench.write_traps(traps)
    _refused(bench, capsys, "exactly the texts of the plan")


def test_a_missing_trap_file_is_refused(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    bench.traps.unlink()
    _refused(bench, capsys, "cannot be read")


def test_a_missing_bank_is_refused(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    (bench.banks / "beispiel_b.json").unlink()
    _refused(bench, capsys, "no sentence bank")


@pytest.mark.parametrize("guide", ["", " \n\n"], ids=["empty", "blank"])
def test_an_empty_guide_is_refused(
    bench: Bench, capsys: pytest.CaptureFixture[str], guide: str
) -> None:
    bench.guide.write_text(guide, "utf-8")
    _refused(bench, capsys, "guide is empty")


@pytest.mark.parametrize(
    ("template", "reason"),
    [
        pytest.param("Ohne Linie {{SATZBANK}}\n", "no part below", id="no-line"),
        pytest.param("Kopf\n---\n", "no part below", id="nothing-below"),
        pytest.param(
            TEMPLATE.replace("{{ERWARTUNGSHORIZONT}}", ""),
            "agreed placeholders",
            id="placeholder-missing",
        ),
        pytest.param(
            TEMPLATE + "{{NEU}}\n", "agreed placeholders", id="placeholder-unknown"
        ),
    ],
)
def test_an_unusable_template_is_refused(
    bench: Bench, capsys: pytest.CaptureFixture[str], template: str, reason: str
) -> None:
    bench.template.write_text(template, "utf-8")
    _refused(bench, capsys, reason)


def _plan_rows(bench: Bench) -> list[str]:
    return bench.plan.read_text("utf-8").splitlines()


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        pytest.param(
            lambda lines: [
                line.replace(",runs/prompts/", ",andere/") for line in lines
            ],
            "unusable prompt file",
            id="other-folder",
        ),
        pytest.param(
            lambda lines: [
                line.replace("runs/prompts/", "runs/prompts/../") for line in lines
            ],
            "unusable prompt file",
            id="path-escape",
        ),
        pytest.param(
            lambda lines: [line.replace("prompt_datei", "datei") for line in lines],
            "unusable prompt file",
            id="column-missing",
        ),
        pytest.param(
            lambda lines: [
                line for line in lines if "beispiel_a.veraendert" not in line
            ],
            "both versions",
            id="version-missing",
        ),
        pytest.param(
            lambda lines: [line for line in lines if "beispiel_c" not in line],
            "4 prompts",
            id="text-missing",
        ),
        pytest.param(lambda lines: lines[:1], "0 prompts", id="no-rows"),
    ],
)
def test_an_unusable_plan_is_refused(
    bench: Bench,
    capsys: pytest.CaptureFixture[str],
    change: Callable[[list[str]], list[str]],
    reason: str,
) -> None:
    bench.plan.write_text("\n".join(change(_plan_rows(bench))) + "\n", "utf-8")
    _refused(bench, capsys, reason)


def _example_edit() -> list[mp.Edit]:
    return [mp.Edit("S2", "30 Minuten", "3 Minuten")]


def _with_sentences(*sentences: str) -> loader.SentenceBank:
    return loader.build_bank("beispiel_a", list(sentences))


def test_the_bank_comparison_passes_the_defined_change(
    banks: dict[str, loader.SentenceBank],
) -> None:
    original = banks["beispiel_a"]
    modified = mp.apply_edits(original, _example_edit())
    mp.verify_banks(original, modified, _example_edit())


@pytest.mark.parametrize(
    "sentences",
    [
        pytest.param(SENTENCES["beispiel_a"], id="change-missing"),
        pytest.param(
            [
                "Das Auto fährt 301 km weit.",
                "Der Akku lädt in 3 Minuten.",
                SENTENCES["beispiel_a"][2],
            ],
            id="another-sentence-changed",
        ),
        pytest.param(
            [
                SENTENCES["beispiel_a"][0],
                "Der Akku lädt in 4 Minuten.",
                SENTENCES["beispiel_a"][2],
            ],
            id="other-replacement",
        ),
        pytest.param(
            [
                SENTENCES["beispiel_a"][0],
                "Der Akku tankt in 3 Minuten.",
                SENTENCES["beispiel_a"][2],
            ],
            id="second-change-in-the-sentence",
        ),
        pytest.param(
            [*SENTENCES["beispiel_a"][:1], "Der Akku lädt in 3 Minuten."],
            id="sentence-removed",
        ),
        pytest.param(
            [
                SENTENCES["beispiel_a"][0],
                "Der Akku lädt in 3 Minuten.",
                SENTENCES["beispiel_a"][2],
                "Neu.",
            ],
            id="sentence-added",
        ),
        pytest.param(
            [
                "Der Akku lädt in 3 Minuten.",
                SENTENCES["beispiel_a"][0],
                SENTENCES["beispiel_a"][2],
            ],
            id="sentences-swapped",
        ),
    ],
)
def test_the_bank_comparison_stops_at_any_other_difference(
    banks: dict[str, loader.SentenceBank], sentences: list[str]
) -> None:
    with pytest.raises(mp.PromptError):
        mp.verify_banks(
            banks["beispiel_a"], _with_sentences(*sentences), _example_edit()
        )


def test_the_bank_comparison_rejects_when_no_change_is_defined(
    banks: dict[str, loader.SentenceBank],
) -> None:
    with pytest.raises(mp.PromptError, match="no defined change"):
        mp.verify_banks(banks["beispiel_a"], banks["beispiel_a"], [])


def test_the_bank_comparison_rejects_an_edit_outside_the_text(
    banks: dict[str, loader.SentenceBank],
) -> None:
    edit = [mp.Edit("S9", "x", "y")]
    with pytest.raises(mp.PromptError, match="no sentence"):
        mp.verify_banks(banks["beispiel_a"], banks["beispiel_a"], edit)


def _prompt_pair(
    banks: dict[str, loader.SentenceBank],
) -> tuple[str, str, loader.SentenceBank, loader.SentenceBank]:
    original = banks["beispiel_a"]
    modified = mp.apply_edits(original, _example_edit())
    body = "Kopf.\n\n{{SATZBANK}}\n\nFuß.\n"

    def filled(bank: loader.SentenceBank) -> str:
        return mp.render(body, {"SATZBANK": mp.sentence_block(bank)})

    return filled(original), filled(modified), original, modified


def test_the_prompt_comparison_passes_the_defined_change(
    banks: dict[str, loader.SentenceBank],
) -> None:
    before, after, original, modified = _prompt_pair(banks)
    mp.verify_prompts(before, after, original, modified, _example_edit())


@pytest.mark.parametrize(
    "tamper",
    [
        pytest.param(lambda text: text.replace("Kopf.", "Kopf!"), id="other-line"),
        pytest.param(lambda text: text.replace("Fuß.\n", "Fuß."), id="last-line"),
        pytest.param(lambda text: text + "Mehr.\n", id="added-line"),
        pytest.param(lambda text: text.replace("\n\nFuß", "\nFuß"), id="removed-line"),
        pytest.param(
            lambda text: text.replace("3 Minuten", "30 Minuten"), id="change-undone"
        ),
        pytest.param(
            lambda text: text.replace("3 Minuten", "4 Minuten"), id="other-change"
        ),
        pytest.param(lambda text: text.replace("[S1]", "[S9]"), id="other-number"),
        pytest.param(
            lambda text: text.replace("300 km", "301 km"), id="other-sentence"
        ),
    ],
)
def test_the_prompt_comparison_stops_at_any_other_difference(
    banks: dict[str, loader.SentenceBank], tamper: Callable[[str], str]
) -> None:
    before, after, original, modified = _prompt_pair(banks)
    assert tamper(after) != after
    with pytest.raises(mp.PromptError):
        mp.verify_prompts(before, tamper(after), original, modified, _example_edit())


def test_the_prompt_comparison_rejects_when_no_change_is_defined(
    banks: dict[str, loader.SentenceBank],
) -> None:
    before, _, original, _ = _prompt_pair(banks)
    with pytest.raises(mp.PromptError, match="no defined change"):
        mp.verify_prompts(before, before, original, original, [])


def test_a_faulty_modification_is_stopped_in_the_run(
    bench: Bench,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correct = mp.apply_edits

    def faulty(bank: loader.SentenceBank, edits: list[mp.Edit]) -> loader.SentenceBank:
        changed = correct(bank, edits)
        texts = [sentence.text for sentence in changed.sentences]
        return loader.build_bank(bank.text_id, [*texts[:-1], "Etwas anderes."])

    monkeypatch.setattr(mp, "apply_edits", faulty)
    _refused(bench, capsys, "differs from its definition")


@pytest.mark.parametrize(
    ("tamper", "reason"),
    [
        pytest.param(
            lambda text: text.replace("Rolle.", "Rolle!"),
            "outside the defined lines",
            id="same-number-of-lines",
        ),
        pytest.param(
            lambda text: text + "Achtung, hier stimmt etwas nicht.\n",
            "number of lines",
            id="added-line",
        ),
    ],
)
def test_a_faulty_prompt_is_stopped_in_the_run(
    bench: Bench,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tamper: Callable[[str], str],
    reason: str,
) -> None:
    correct = mp.render

    def faulty(body: str, values: dict[str, str]) -> str:
        prompt = correct(body, values)
        return tamper(prompt) if "in 3 Minuten" in prompt else prompt

    monkeypatch.setattr(mp, "render", faulty)
    _refused(bench, capsys, reason)


def test_a_prompt_that_was_already_written_is_not_replaced(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    assert bench.run() == 0
    target = bench.output / "runs/prompts/beispiel_a.original.md"
    target.write_text("Schon gesendet.", "utf-8")
    bench.edit_first_trap(to="4 Minuten")
    before = bench.written()
    assert bench.run() == 1
    assert "different files already exist" in capsys.readouterr().err
    assert bench.written() == before


def test_a_refusal_in_the_last_text_writes_nothing_for_the_first(
    bench: Bench, capsys: pytest.CaptureFixture[str]
) -> None:
    traps = bench.read_traps()
    traps["beispiel_c"]["edits"][0]["from"] = "gibt es nicht"
    bench.write_traps(traps)
    _refused(bench, capsys, "exactly once")


def test_the_example_file_is_invented(study_root: Path) -> None:
    traps = json.loads((FIXTURES / "example_traps.json").read_text("utf-8"))
    selection = json.loads((study_root / "prereg/selection.json").read_text("utf-8"))
    used = {text for group in selection["groups"].values() for text in group}
    assert not used & set(traps)
    assert all(
        re.fullmatch(r"Erfundenes Beispiel: .+", trap["description"])
        for trap in traps.values()
    )
