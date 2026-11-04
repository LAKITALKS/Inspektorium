"""The prompt template and the output schema agree with each other."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def prompt(study_root: Path) -> str:
    return (study_root / "prompts/grading_prompt_de.md").read_text("utf-8")


@pytest.fixture(scope="module")
def schema(study_root: Path) -> dict[str, dict[str, dict[str, object]]]:
    loaded: dict[str, dict[str, dict[str, object]]] = json.loads(
        (study_root / "schemas/output.schema.json").read_text("utf-8")
    )
    return loaded


def test_the_prompt_has_exactly_the_agreed_placeholders(prompt: str) -> None:
    assert set(re.findall(r"\{\{(\w+)\}\}", prompt)) == {
        "SCHREIBAUFGABE",
        "ERWARTUNGSHORIZONT",
        "SATZBANK",
        "AUSGABESCHEMA",
    }


def test_the_prompt_keeps_the_agreed_role_and_the_json_only_request(
    prompt: str,
) -> None:
    assert "Du bist eine Korrekturhilfe für eine Lehrkraft" in prompt
    assert "Antworte **nur** mit einem JSON-Objekt" in prompt
    assert "1 = sehr gut" in prompt
    assert "6 = ungenügend" in prompt


def test_the_prompt_lists_every_criterion(prompt: str, study_root: Path) -> None:
    criteria = json.loads((study_root / "data/criteria.json").read_text("utf-8"))
    for item in criteria["criteria"]:
        assert f"- {item['id']}: {item['name']}\n" in prompt


def test_the_prompt_does_not_reveal_inserted_errors(prompt: str) -> None:
    sent = prompt.split("\n---\n", maxsplit=1)[1].lower()
    for word in ("eingebaut", "manipuliert", "verändert", "test", "pilot"):
        assert word not in sent


def test_the_prompt_lists_the_schema_vocabularies(
    prompt: str, schema: dict[str, dict[str, dict[str, object]]]
) -> None:
    errors = schema["properties"]["errors"]
    items = errors["items"]
    assert isinstance(items, dict)
    for category in items["properties"]["category"]["enum"]:
        assert f"`{category}`" in prompt


def test_the_schema_has_the_agreed_shape(
    schema: dict[str, dict[str, dict[str, object]]],
) -> None:
    properties = schema["properties"]
    assert set(properties) == {"grade", "comments", "errors"}
    assert (properties["grade"]["minimum"], properties["grade"]["maximum"]) == (1, 6)
    comment = properties["comments"]["items"]
    assert isinstance(comment, dict)
    assert comment["properties"]["scope"]["enum"] == ["local", "global"]
    assert comment["properties"]["criteria"]["items"]["enum"] == [
        f"K{number}" for number in range(1, 8)
    ]
