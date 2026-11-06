"""Write the prompt files of the pilot from the template, the guide and the traps.

The run plan names six prompt files: three texts, each as the original and as the
modified version. The modified version is the original plus the ``edits`` of the
trap file. An edit replaces one exact passage of one target sentence:

    {"sid": "S2", "from": "30 Minuten", "to": "3 Minuten"}

A sentence keeps its number, because a sentence number identifies the same place
in both versions. Two checks then compare the results and stop the script if
anything else differs: one compares the two banks sentence by sentence, the other
compares the two finished prompts line by line.

The marking guide and the trap file have no default path. This script reads only
the files it is given. It writes the prompts and the banks of both versions below
``runs/``, which stays out of Git, and it writes everything or nothing. It never
replaces a different file, so a prompt that was already sent cannot change. The
result depends on the inputs alone: nothing here uses the clock or chance.

``runs/manifest.json`` records the SHA-256 of the guide, the trap file, all banks
and all prompts, and the commit of this script. A script that differs from its
commit writes nothing, because the manifest could not name it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from analyze import Trap, TrapError, Traps, validate_traps
from genius_loader import SentenceBank, build_bank, dump_json, read_bank
from import_runs import DEFAULT_SCHEMA, ORIGINAL, bank_path
from make_run_plan import DEFAULT_PLAN, MODIFIED, VERSIONS

from inspektorium.core.strict_json import StrictJSONError, load_strict_json

STUDY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = STUDY_ROOT / "prompts" / "grading_prompt_de.md"
DEFAULT_SOURCE_BANKS = STUDY_ROOT / "data" / "selected"
RUN_BANKS = Path("runs") / "banks"
RUN_PROMPTS = "runs/prompts/"
MANIFEST = "runs/manifest.json"
THIS_SCRIPT = Path(__file__).resolve()
PROMPT_COUNT = 6
SENT_PART_MARK = "\n---\n"
EDIT_KEYS = {"sid", "from", "to"}
GUIDE = "ERWARTUNGSHORIZONT"
BANK = "SATZBANK"
SCHEMA = "AUSGABESCHEMA"
_PROMPT_FILE = re.compile(r"runs/prompts/([^/.]+)\.([^/.]+)\.md")
_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


class PromptError(ValueError):
    """An input or a result breaks the rules, so nothing is written."""


@dataclass(frozen=True)
class Edit:
    """One defined change: ``before`` becomes ``after`` in one sentence."""

    sid: str
    before: str
    after: str


def prompt_files(plan: str) -> dict[tuple[str, str], str]:
    """Map every text and version to the prompt file the run plan names."""

    files: dict[tuple[str, str], str] = {}
    for row in csv.DictReader(io.StringIO(plan)):
        name = row.get("prompt_datei") or ""
        match = _PROMPT_FILE.fullmatch(name)
        if match is None:
            raise PromptError(f"the plan names an unusable prompt file: {name!r}")
        files[(match[1], match[2])] = name
    texts = {text_id for text_id, _ in files}
    if set(files) != {(text_id, version) for text_id in texts for version in VERSIONS}:
        raise PromptError("the plan must name both versions of every text")
    if len(files) != PROMPT_COUNT:
        raise PromptError(f"the plan names {len(files)} prompts, not {PROMPT_COUNT}")
    return files


def read_traps(raw: str) -> Traps:
    """Decode the trap file; a repeated key must not hide an edit."""

    try:
        value = load_strict_json(raw)
    except StrictJSONError as error:
        raise PromptError("the trap file is not strict JSON") from error
    if not isinstance(value, dict) or not all(
        isinstance(trap, dict) for trap in value.values()
    ):
        raise PromptError("the trap file must map text ids to traps")
    return value


def _occurrences(text: str, passage: str) -> int:
    """Count every position of ``passage``, overlapping ones included."""

    return sum(text.startswith(passage, index) for index in range(len(text)))


def _read_edit(
    label: str, item: object, trap: Trap, sentences: Mapping[str, str]
) -> Edit:
    if not isinstance(item, dict) or set(item) != EDIT_KEYS:
        raise PromptError(f"{label}: an edit needs exactly sid, from and to")
    sid, before, after = item["sid"], item["from"], item["to"]
    if not all(isinstance(value, str) for value in (sid, before, after)):
        raise PromptError(f"{label}: sid, from and to must be texts")
    if sid not in trap["sids"]:
        raise PromptError(f"{label}: {sid} is not a target sentence")
    if not before or _occurrences(sentences[sid], before) != 1:
        raise PromptError(f"{label}: 'from' must occur exactly once in {sid}")
    if before == after:
        raise PromptError(f"{label}: the edit of {sid} changes nothing")
    if not after.strip() or "".join(after.splitlines()) != after:
        raise PromptError(f"{label}: 'to' of {sid} must be one line of text")
    return Edit(sid, before, after)


def read_edits(text_id: str, trap: Trap, bank: SentenceBank) -> list[Edit]:
    """Read the edits of one trap; each stands in its own target sentence."""

    raw = trap.get("edits")
    if not isinstance(raw, list) or not raw:
        raise PromptError(f"{text_id}: the trap defines no edits")
    sentences = {sentence.sid: sentence.text for sentence in bank.sentences}
    unknown = [sid for sid in trap["sids"] if sid not in sentences]
    if unknown:
        raise PromptError(f"{text_id}: the text has no sentence {unknown}")
    edits = [_read_edit(text_id, item, trap, sentences) for item in raw]
    if len({edit.sid for edit in edits}) != len(edits):
        raise PromptError(f"{text_id}: a sentence takes one edit only")
    return edits


def apply_edits(bank: SentenceBank, edits: Sequence[Edit]) -> SentenceBank:
    """Build the modified bank; offsets follow from the changed sentences."""

    planned = {edit.sid: edit for edit in edits}
    texts: list[str] = []
    for sentence in bank.sentences:
        edit = planned.get(sentence.sid)
        changed = (
            sentence.text
            if edit is None
            else sentence.text.replace(edit.before, edit.after, 1)
        )
        texts.append(changed)
    return build_bank(bank.text_id, texts)


def verify_banks(
    original: SentenceBank, modified: SentenceBank, edits: Sequence[Edit]
) -> None:
    """Stop unless the banks differ in exactly the defined passages.

    Every sentence is compared, and an edit that left no trace stops the script
    as well. A sentence the study's text conversion would change also ends here.
    """

    text_id = original.text_id
    if not edits:
        raise PromptError(f"{text_id}: no defined change to compare")
    sids = [sentence.sid for sentence in original.sentences]
    if sids != [sentence.sid for sentence in modified.sentences]:
        raise PromptError(f"{text_id}: the versions do not have the same sentences")
    planned = {edit.sid: edit for edit in edits}
    if not set(planned) <= set(sids):
        raise PromptError(f"{text_id}: an edit names no sentence of the text")
    for old, new in zip(original.sentences, modified.sentences, strict=True):
        expected = old.text
        edit = planned.get(old.sid)
        if edit is not None:
            if edit.before == edit.after or _occurrences(old.text, edit.before) != 1:
                raise PromptError(f"{text_id}: the edit of {old.sid} is not usable")
            head, _, tail = old.text.partition(edit.before)
            expected = f"{head}{edit.after}{tail}"
        if new.text != expected:
            raise PromptError(f"{text_id}: {old.sid} differs from its definition")


def verify_prompts(
    before: str,
    after: str,
    original: SentenceBank,
    modified: SentenceBank,
    edits: Sequence[Edit],
) -> None:
    """Stop unless the prompts differ in exactly the lines of the edited sentences."""

    text_id = original.text_id
    if not edits:
        raise PromptError(f"{text_id}: no defined change to compare")
    old_lines, new_lines = before.split("\n"), after.split("\n")
    if len(old_lines) != len(new_lines):
        raise PromptError(f"{text_id}: the prompts differ in their number of lines")
    edited = {edit.sid for edit in edits}
    expected = [
        (sentence_line(old.sid, old.text), sentence_line(new.sid, new.text))
        for old, new in zip(original.sentences, modified.sentences, strict=True)
        if old.sid in edited
    ]
    found = [
        pair for pair in zip(old_lines, new_lines, strict=True) if pair[0] != pair[1]
    ]
    if found != expected:
        raise PromptError(f"{text_id}: the prompts differ outside the defined lines")


def sentence_line(sid: str, text: str) -> str:
    return f"[{sid}] {text}"


def sentence_block(bank: SentenceBank) -> str:
    return "\n".join(sentence_line(s.sid, s.text) for s in bank.sentences)


def sent_part(template: str) -> str:
    """Keep what goes to the chatbot: everything below the line of the template."""

    _, mark, body = template.partition(SENT_PART_MARK)
    if not mark or not body.strip():
        raise PromptError("the template has no part below its line")
    return f"{body.strip()}\n"


def render(body: str, values: Mapping[str, str]) -> str:
    """Fill every placeholder in one pass, so inserted text is not read again."""

    if set(_PLACEHOLDER.findall(body)) != set(values):
        raise PromptError("the template does not have the agreed placeholders")
    return _PLACEHOLDER.sub(lambda match: values[match[1]], body)


def build_files(
    files: Mapping[tuple[str, str], str],
    banks: Path,
    traps: Traps,
    guide: str,
    template: str,
    schema: str,
) -> dict[str, bytes]:
    """Build and verify all prompts and banks in memory."""

    validate_traps(traps)
    texts = sorted({text_id for text_id, _ in files})
    if sorted(traps) != texts:
        raise PromptError("the trap file must define exactly the texts of the plan")
    guide_text, schema_text = guide.strip(), schema.strip()
    if not guide_text:
        raise PromptError("the marking guide is empty")
    body = sent_part(template)
    built: dict[str, bytes] = {}
    for text_id in texts:
        trap = traps[text_id]
        if trap["version"] != MODIFIED:
            raise PromptError(f"{text_id}: the plan's version is {MODIFIED}")
        source = bank_path(banks, text_id, ORIGINAL)
        if not source.is_file():
            raise PromptError(f"{text_id}: no sentence bank")
        original = read_bank(source)
        edits = read_edits(text_id, trap, original)
        modified = apply_edits(original, edits)
        verify_banks(original, modified, edits)
        pair = {ORIGINAL: original, MODIFIED: modified}
        prompts = {
            version: render(
                body,
                {GUIDE: guide_text, BANK: sentence_block(bank), SCHEMA: schema_text},
            )
            for version, bank in pair.items()
        }
        verify_prompts(prompts[ORIGINAL], prompts[MODIFIED], original, modified, edits)
        for version, bank in pair.items():
            built[files[(text_id, version)]] = prompts[version].encode("utf-8")
            name = bank_path(RUN_BANKS, text_id, version).as_posix()
            built[name] = dump_json(bank.as_dict())
    return built


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _git(folder: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=folder,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise PromptError("Git cannot run, so the script has no commit") from error
    if result.returncode != 0:
        raise PromptError("the script is not in a Git checkout")
    return result.stdout.strip()


def script_commit(script: Path = THIS_SCRIPT) -> str:
    """Return the last commit of the script; a differing copy is refused."""

    folder, name = script.parent, script.name
    if _git(folder, "status", "--porcelain", "--", name):
        raise PromptError(f"{name} differs from its commit")
    commit = _git(folder, "log", "-1", "--format=%H", "--", name)
    if not commit:
        raise PromptError(f"{name} has no commit")
    return commit


def build_manifest(
    files: Mapping[str, bytes], guide: str, traps: str, commit: str
) -> bytes:
    """Name every input and result by hash; these values go into the prereg."""

    def digests(folder: str) -> dict[str, str]:
        return {
            name: _sha256(content)
            for name, content in sorted(files.items())
            if name.startswith(folder)
        }

    return dump_json(
        {
            "script_commit": commit,
            "guide_sha256": _sha256(guide.encode("utf-8")),
            "traps_sha256": _sha256(traps.encode("utf-8")),
            "banks": digests(f"{RUN_BANKS.as_posix()}/"),
            "prompts": digests(RUN_PROMPTS),
        }
    )


def write_files(files: Mapping[str, bytes], root: Path) -> None:
    """Write everything or nothing; a different existing file stays."""

    different = [
        name
        for name, content in files.items()
        if (root / name).exists() and (root / name).read_bytes() != content
    ]
    if different:
        raise PromptError(f"different files already exist: {sorted(different)}")
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def _read(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise PromptError(f"{path.name} cannot be read") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--traps", type=Path, required=True)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--banks", type=Path, default=DEFAULT_SOURCE_BANKS)
    parser.add_argument("--root", type=Path, default=STUDY_ROOT)
    args = parser.parse_args(argv)
    try:
        commit = script_commit()
        files = prompt_files(_read(args.plan))
        guide, traps = _read(args.guide), _read(args.traps)
        built = build_files(
            files,
            args.banks,
            read_traps(traps),
            guide,
            _read(args.template),
            _read(args.schema),
        )
        manifest = build_manifest(built, guide, traps, commit)
        write_files({**built, MANIFEST: manifest}, args.root)
    except (PromptError, TrapError) as refused:
        print(f"REFUSED, nothing written: {refused}", file=sys.stderr)
        return 1
    print(
        f"wrote {len(files)} prompts, {len(built) - len(files)} sentence banks "
        f"and {MANIFEST}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
