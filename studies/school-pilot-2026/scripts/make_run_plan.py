"""Write the run plan of the pilot and prepare one empty file per run.

The runs themselves are done by hand in the chat windows. This script only says
in which order, and names the files. All choices derive from the seed through
SHA-256, not from a random generator.

Every chatbot works on both days. Each chatbot has the same number of runs per
day, and the repetitions of one text and version are spread over both days.

The prompt files named in the plan do not exist yet. ``make_prompts.py`` writes
them from the marking guide and the inserted errors, and they stay out of Git like
everything below ``runs/``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from dataclasses import dataclass
from pathlib import Path

from genius_loader import dump_json
from import_runs import ORIGINAL, Metadata
from reserve import current_pilot
from select_texts import read_seed, write_once

STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = STUDY_ROOT / "prereg" / "seed.txt"
DEFAULT_SELECTION = STUDY_ROOT / "prereg" / "selection.json"
DEFAULT_PLAN = STUDY_ROOT / "prereg" / "laufplan.csv"

CHATBOTS = ("chatgpt", "gemini", "grok")
MODIFIED = "veraendert"
VERSIONS = (ORIGINAL, MODIFIED)
REPETITIONS = ("1", "2", "3")
DAYS = (1, 2)
COLUMNS = ("nummer", "tag", "chatbot", "prompt_datei", "zieldatei", "metadatendatei")


@dataclass(frozen=True)
class PlannedRun:
    number: int
    day: int
    chatbot: str
    text_id: str
    version: str
    repetition: str

    @property
    def prompt_file(self) -> str:
        return f"runs/prompts/{self.text_id}.{self.version}.md"

    @property
    def folder(self) -> str:
        return f"runs/{self.chatbot}/{self.text_id}/{self.version}"

    @property
    def target_file(self) -> str:
        return f"{self.folder}/{self.repetition}.json"

    @property
    def metadata_file(self) -> str:
        return f"{self.folder}/{self.repetition}.meta.json"


def _rank(*parts: object) -> str:
    joined = ":".join(str(part) for part in parts)
    return hashlib.sha256(joined.encode()).hexdigest()


def assign_days(text_ids: list[str], seed: int) -> dict[tuple[str, str, str, str], int]:
    """Give every run a day; each chatbot gets the same number on both days.

    Three repetitions do not divide evenly, so half of a chatbot's groups put two
    on the first day and the other half put one there.
    """

    days: dict[tuple[str, str, str, str], int] = {}
    for chatbot in CHATBOTS:
        groups = [(text_id, version) for text_id in text_ids for version in VERSIONS]
        groups.sort(key=lambda group: _rank(seed, "group", chatbot, *group))
        for position, (text_id, version) in enumerate(groups):
            on_first_day = 2 if position < len(groups) // 2 else 1
            ordered = sorted(
                REPETITIONS,
                key=lambda number: _rank(
                    seed, "day", chatbot, text_id, version, number
                ),
            )
            for place, repetition in enumerate(ordered):
                day = DAYS[0] if place < on_first_day else DAYS[1]
                days[(chatbot, text_id, version, repetition)] = day
    return days


def build_plan(text_ids: list[str], seed: int) -> list[PlannedRun]:
    """Mix the runs within each day and number them through both days."""

    days = assign_days(text_ids, seed)
    ordered = sorted(days, key=lambda key: (days[key], _rank(seed, "order", *key)))
    return [
        PlannedRun(number, days[key], *key)
        for number, key in enumerate(ordered, start=1)
    ]


def plan_bytes(plan: list[PlannedRun]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(COLUMNS)
    for run in plan:
        writer.writerow(
            (
                run.number,
                run.day,
                run.chatbot,
                run.prompt_file,
                run.target_file,
                run.metadata_file,
            )
        )
    return buffer.getvalue().encode("utf-8")


def prepare_files(plan: list[PlannedRun], root: Path) -> int:
    """Create the empty output files and metadata forms; touch nothing existing.

    Blank metadata fields are rejected by the import, so a run that was not done
    cannot pass as one.
    """

    form = dump_json(dict.fromkeys(Metadata.__dataclass_fields__, ""))
    created = 0
    for run in plan:
        folder = root / run.folder
        folder.mkdir(parents=True, exist_ok=True)
        target = root / run.target_file
        if not target.exists():
            target.touch()
            created += 1
        metadata = root / run.metadata_file
        if not metadata.exists():
            metadata.write_bytes(form)
    return created


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-file", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--root", type=Path, default=STUDY_ROOT)
    args = parser.parse_args(argv)
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    plan = build_plan(current_pilot(selection), read_seed(args.seed_file))
    write_once(plan_bytes(plan), args.plan)
    created = prepare_files(plan, args.root)
    print(f"planned {len(plan)} runs, created {created} empty files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
