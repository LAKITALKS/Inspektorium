"""Check the links in the repository's Markdown files.

Every relative link must resolve to a tracked file or directory, and every
anchor must match a heading of its target file (GitHub slug rules). With
--external, http(s) links are also requested once each; their status is
reported, and only --strict-external turns a failure into a non-zero exit.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlsplit

FENCE = re.compile(r"^(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
INLINE_LINK = re.compile(
    r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)"
)
REFERENCE_LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\[([^\]]+)\]")
DEFINITION = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*<?(\S+?)>?(?:\s+.*)?$")
AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
HTML_ANCHOR = re.compile(r"<a\s+(?:id|name)=\"([^\"]+)\"")
# Frozen evidence packages keep their original bytes. Their links that no longer
# resolve are listed in evidence/README.md and reported here, not counted as broken.
FROZEN = {("evidence/v0.1.1/CLOSEOUT.md", "../../RELEASE_CHECKLIST.md")}


def tracked_files(root: Path) -> list[Path]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    return [root / name for name in out.decode().split("\0") if name]


def strip_markdown(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("`", "").replace("**", "").replace("__", "")


def slug(heading: str) -> str:
    text = strip_markdown(heading).strip().lower()
    kept = []
    for char in text:
        category = unicodedata.category(char)
        if char in " -" or category[0] in "LMN" or category == "Pc":
            kept.append(char)
    return "".join(kept).replace(" ", "-")


def scan(path: Path) -> tuple[list[tuple[int, str]], set[str]]:
    """Return (line, target) pairs and the anchors defined in a Markdown file."""
    links, anchors, definitions, references = [], set(), {}, []
    counts: dict[str, int] = {}
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = HEADING.match(line)
        if heading:
            base = slug(heading.group(2))
            index = counts.get(base, 0)
            counts[base] = index + 1
            anchors.add(base if index == 0 else f"{base}-{index}")
        anchors.update(HTML_ANCHOR.findall(line))
        definition = DEFINITION.match(line)
        if definition:
            definitions[definition.group(1).lower()] = (number, definition.group(2))
            continue
        visible = INLINE_CODE.sub("", line)
        links += [(number, target) for target in INLINE_LINK.findall(visible)]
        links += [(number, target) for target in AUTOLINK.findall(visible)]
        references += [
            (number, name.lower()) for name in REFERENCE_LINK.findall(visible)
        ]
    for number, name in references:
        if name in definitions:
            links.append(definitions[name])
        elif not name.startswith("^"):
            links.append((number, f"undefined-reference:{name}"))
    return links, anchors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--external", action="store_true", help="also request http(s) links"
    )
    parser.add_argument(
        "--strict-external", action="store_true", help="fail on external errors"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    files = tracked_files(root)
    existing = {p.resolve() for p in files} | {p.resolve().parent for p in files}
    for path in list(existing):
        existing.update(path.parents)
    markdown = sorted(p for p in files if p.suffix == ".md")
    parsed = {p.resolve(): scan(p) for p in markdown}
    errors, frozen, external = [], [], {}
    for path in markdown:
        links, anchors = parsed[path.resolve()]
        for number, target in links:
            where = f"{path.relative_to(root)}:{number}"
            if target.startswith("undefined-reference:"):
                errors.append(
                    f"{where}: undefined reference [{target.split(':', 1)[1]}]"
                )
                continue
            parts = urlsplit(target)
            if parts.scheme in ("http", "https"):
                external.setdefault(target, where)
                continue
            if parts.scheme or target.startswith("//"):
                continue
            fragment = unquote(parts.fragment)
            destination = (
                path
                if not parts.path
                else (path.parent / unquote(parts.path)).resolve()
            )
            if destination not in existing:
                if (path.relative_to(root).as_posix(), target) in FROZEN:
                    frozen.append(
                        f"{where}: frozen link {target} (see evidence/README.md)"
                    )
                else:
                    errors.append(f"{where}: missing {target}")
                continue
            if fragment and destination.suffix == ".md":
                target_anchors = parsed.get(destination, (None, set()))[1]
                if fragment not in target_anchors:
                    errors.append(f"{where}: missing anchor #{fragment} in {target}")
    failures = []
    if args.external:
        for url, where in sorted(external.items()):
            request = urllib.request.Request(
                url, headers={"User-Agent": "inspektorium-link-check"}
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status = response.status
            except urllib.error.HTTPError as exc:
                status = exc.code
            except (urllib.error.URLError, TimeoutError) as exc:
                status = f"error: {exc}"
            print(f"{status} {url} ({where})")
            if status != 200:
                failures.append(url)
    for line in frozen + errors:
        print(line)
    print(
        f"checked {len(markdown)} Markdown files: {len(errors)} broken relative links, "
        f"{len(frozen)} documented frozen links"
        + (
            f", {len(failures)} of {len(external)} external links not 200"
            if args.external
            else ""
        )
    )
    if errors or (args.strict_external and failures):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
