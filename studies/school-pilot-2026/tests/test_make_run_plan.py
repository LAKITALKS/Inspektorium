"""The run plan, tested on invented text ids; no chatbot is involved."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from pathlib import Path

import import_runs as imp
import make_run_plan as plan_module
import pytest
import select_texts

TEXTS = ["t1", "t2", "t3"]
SCHEMA = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas/output.schema.json").read_text(
        "utf-8"
    )
)


@pytest.fixture(scope="module")
def plan() -> list[plan_module.PlannedRun]:
    return plan_module.build_plan(TEXTS, 20261113)


def test_the_plan_has_the_agreed_54_runs(plan: list[plan_module.PlannedRun]) -> None:
    assert len(plan) == 3 * 2 * 3 * 3 == 54
    keys = {(r.chatbot, r.text_id, r.version, r.repetition) for r in plan}
    assert len(keys) == 54


def test_numbers_run_through_both_days(plan: list[plan_module.PlannedRun]) -> None:
    assert [run.number for run in plan] == list(range(1, 55))
    days = [run.day for run in plan]
    assert days == sorted(days)


def test_every_chatbot_has_nine_runs_on_each_day(
    plan: list[plan_module.PlannedRun],
) -> None:
    counts = Counter((run.chatbot, run.day) for run in plan)
    assert counts == {
        (chatbot, day): 9
        for chatbot in plan_module.CHATBOTS
        for day in plan_module.DAYS
    }


def test_the_repetitions_of_a_group_are_on_both_days(
    plan: list[plan_module.PlannedRun],
) -> None:
    days: dict[tuple[str, str, str], set[int]] = {}
    for run in plan:
        days.setdefault((run.chatbot, run.text_id, run.version), set()).add(run.day)
    assert all(found == {1, 2} for found in days.values())


def test_the_order_is_mixed_and_not_grouped_by_chatbot(
    plan: list[plan_module.PlannedRun],
) -> None:
    first_day = [run.chatbot for run in plan if run.day == 1]
    assert first_day != sorted(first_day)
    runs_of_same = sum(a == b for a, b in zip(first_day, first_day[1:], strict=False))
    assert runs_of_same < len(first_day) - 3


def test_the_plan_repeats_and_follows_the_seed(
    plan: list[plan_module.PlannedRun],
) -> None:
    assert plan_module.build_plan(TEXTS, 20261113) == plan
    assert plan_module.build_plan(TEXTS, 7) != plan


def test_the_input_order_of_the_texts_does_not_matter_for_the_days() -> None:
    forward = plan_module.assign_days(TEXTS, 1)
    assert sorted(forward) == sorted(plan_module.assign_days(TEXTS[::-1], 1))


def test_the_plan_names_the_files_the_importer_reads(
    plan: list[plan_module.PlannedRun],
) -> None:
    run = plan[0]
    assert run.target_file == (
        f"runs/{run.chatbot}/{run.text_id}/{run.version}/{run.repetition}.json"
    )
    assert run.metadata_file.endswith(f"/{run.repetition}.meta.json")
    assert run.prompt_file == f"runs/prompts/{run.text_id}.{run.version}.md"


def test_the_csv_has_one_row_per_run(plan: list[plan_module.PlannedRun]) -> None:
    rows = list(csv.DictReader(io.StringIO(plan_module.plan_bytes(plan).decode())))
    assert len(rows) == 54
    assert tuple(rows[0]) == plan_module.COLUMNS
    assert rows[0]["nummer"] == "1"


def test_every_run_gets_an_empty_named_file(
    plan: list[plan_module.PlannedRun], tmp_path: Path
) -> None:
    assert plan_module.prepare_files(plan, tmp_path) == 54
    for run in plan:
        assert (tmp_path / run.target_file).read_bytes() == b""
        form = json.loads((tmp_path / run.metadata_file).read_text("utf-8"))
        assert form == dict.fromkeys(imp.Metadata.__dataclass_fields__, "")


def test_preparing_again_changes_nothing(
    plan: list[plan_module.PlannedRun], tmp_path: Path
) -> None:
    plan_module.prepare_files(plan, tmp_path)
    (tmp_path / plan[0].target_file).write_text("Antwort", "utf-8")
    (tmp_path / plan[0].metadata_file).write_text("{}", "utf-8")
    assert plan_module.prepare_files(plan, tmp_path) == 0
    assert (tmp_path / plan[0].target_file).read_text("utf-8") == "Antwort"
    assert (tmp_path / plan[0].metadata_file).read_text("utf-8") == "{}"


def test_an_untouched_form_cannot_pass_as_a_run(
    plan: list[plan_module.PlannedRun], tmp_path: Path
) -> None:
    plan_module.prepare_files(plan[:1], tmp_path)
    with pytest.raises(imp.MetadataRejected) as caught:
        imp.import_all(tmp_path / "runs", tmp_path, SCHEMA)
    assert len(caught.value.problems) == len(imp.Metadata.__dataclass_fields__)


def test_the_plan_cannot_be_redrawn(
    plan: list[plan_module.PlannedRun], tmp_path: Path
) -> None:
    target = tmp_path / "laufplan.csv"
    select_texts.write_once(plan_module.plan_bytes(plan), target)
    other = plan_module.build_plan(TEXTS, 7)
    with pytest.raises(select_texts.SelectionError, match="different draw"):
        select_texts.write_once(plan_module.plan_bytes(other), target)


def test_the_committed_plan_matches_the_pilot_group(study_root: Path) -> None:
    groups = json.loads((study_root / "prereg/selection.json").read_text("utf-8"))
    seed = select_texts.read_seed(study_root / "prereg/seed.txt")
    expected = plan_module.build_plan(groups["groups"]["pilot"], seed)
    committed = (study_root / "prereg/laufplan.csv").read_bytes()
    assert committed == plan_module.plan_bytes(expected)


def test_the_chatbots_are_the_agreed_ones() -> None:
    assert plan_module.CHATBOTS == ("chatgpt", "gemini", "grok")
