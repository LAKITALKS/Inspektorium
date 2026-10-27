"""Common semantic report serializers and independent actual-file content checks."""
from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from inspektorium.audit.workflow.pipeline import digest
from inspektorium.audit.workflow.projection import LIMITS, NOTICE, TITLES, notice_for, projection

__all__ = ["LIMITS", "NOTICE", "projection", "markdown", "html_report", "validate_files"]
TITLE = "Canonical local audit"
STYLE = """
:root{color-scheme:light}*{box-sizing:border-box}body{font-family:system-ui,sans-serif;color:#18232d;
background:#fff;max-width:74rem;margin:0 auto;padding:1.4rem;line-height:1.45}
h1{font-size:1.8rem}h2{font-size:1.35rem;margin-top:2rem;border-bottom:2px solid #354858;padding-bottom:.35rem}
h3{font-size:1rem;margin:1.3rem 0 .4rem}h1,h2,h3{overflow-wrap:anywhere;break-after:avoid}
p{white-space:pre-wrap;overflow-wrap:anywhere}.status{font-size:1.25rem;font-weight:750;border-left:5px solid #354858;padding:.7rem;background:#edf2f5}
.notice{border:2px solid #7a571a;background:#fff8e8;padding:.8rem;font-weight:600}
blockquote{margin:.6rem 0;padding:.7rem 1rem;border-left:3px solid #687d8c;background:#f5f7f8}
pre{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}
table{width:100%;table-layout:fixed;border-collapse:collapse;font-size:.9rem;margin:.4rem 0 1rem}
th,td{text-align:left;vertical-align:top;border:1px solid #bac5cd;padding:.4rem;white-space:pre-wrap;overflow-wrap:anywhere}
th{background:#edf2f5;font-weight:650}thead{display:table-header-group}tr{break-inside:auto}
@media(max-width:600px){body{padding:.7rem}h1{font-size:1.5rem}table{font-size:.85rem}th,td{padding:.3rem}}
@media print{@page{size:A4;margin:14mm}body{max-width:none;padding:0;font-size:9pt;color:#000}
h1{font-size:17pt}h2{font-size:13pt;margin-top:14pt}h3{font-size:10pt}
table{font-size:8pt}th,td{padding:3pt}section,table,tbody,tr,td,blockquote,pre{break-inside:auto}
thead{display:table-header-group}p{orphans:2;widows:2}.notice,.status{background:#fff}}
""".strip()


def _checked_sections(projected):
    if [title for title, _ in projected] != list(TITLES):
        raise ValueError("Required semantic report section set/order is incomplete")
    for _, section in projected:
        if not isinstance(section, dict) or not section.get("blocks"):
            raise ValueError("Empty semantic report section")
        for block in section["blocks"]:
            kind = block.get("kind")
            if kind in {"text", "quote"}:
                if not isinstance(block.get("text"), str):
                    raise ValueError("Invalid semantic text")
            elif kind == "table":
                if (not isinstance(block.get("caption"), str) or not block.get("headers") or
                        not block.get("rows") or any(len(row) != len(block["headers"]) for row in block["rows"])):
                    raise ValueError("Invalid semantic table")
                if not all(isinstance(cell, str) for row in [block["headers"], *block["rows"]] for cell in row):
                    raise ValueError("Invalid semantic table value")
            else:
                raise ValueError("Unknown semantic block")
    return projected


# CommonMark/JavaScript line terminators besides LF; the projection already shows them as tokens.
LINE_TERMINATORS = "\r\u2028\u2029\x85"


def _md_inline(text):
    # Entities are decoded as text by Markdown, never reparsed as links/markup.
    escaped = "".join(f"&#{ord(char)};" if char in "\\`*_{}[]|#!~@:" + LINE_TERMINATORS else
                      html.escape(char, quote=True) for char in text)
    escaped = re.sub(r"(?i)www\.", "www&#46;", escaped)
    return escaped.replace("\n", "<br>")


def markdown(projected) -> bytes:
    parts = [f"# {TITLE}\n"]
    for title, section in _checked_sections(projected):
        parts.append(f"## {title}\n")
        for block in section["blocks"]:
            if block["kind"] == "text":
                parts.append(_md_inline(block["text"]) + "\n")
            elif block["kind"] == "quote":
                body = block["text"]
                fence = "`" * max(3, max((len(s) for s in re.findall(r"`+", body)), default=0) + 1)
                parts.append(f"{fence}\n{body}\n{fence}\n")
            else:
                parts.append("### " + _md_inline(block["caption"]) + "\n")
                parts.append("| " + " | ".join(_md_inline(v) for v in block["headers"]) + " |")
                parts.append("| " + " | ".join("---" for _ in block["headers"]) + " |")
                parts.extend("| " + " | ".join(_md_inline(v) for v in row) + " |" for row in block["rows"])
                parts.append("")
    return ("\n".join(parts) + "\n").encode("utf-8")


def html_report(projected) -> bytes:
    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             f'<title>{TITLE}</title><style>{STYLE}</style></head><body><h1>{TITLE}</h1>']
    for title, section in _checked_sections(projected):
        parts.append(f'<section><h2>{html.escape(title)}</h2>')
        for block in section["blocks"]:
            kind = block["kind"]
            if kind == "text":
                style = block.get("style", "normal")
                if style not in {"normal", "notice", "status"}:
                    raise ValueError("Unknown paragraph style")
                parts.append(f'<p class="{style}">{html.escape(block["text"])}</p>')
            elif kind == "quote":
                parts.append(f'<blockquote><pre>{html.escape(block["text"])}</pre></blockquote>')
            else:
                parts.append(f'<h3>{html.escape(block["caption"])}</h3><table><thead><tr>')
                parts.extend(f'<th scope="col">{html.escape(v)}</th>' for v in block["headers"])
                parts.append('</tr></thead><tbody>')
                for row in block["rows"]:
                    parts.append('<tr>' + ''.join(f'<td>{html.escape(v)}</td>' for v in row) + '</tr>')
                parts.append('</tbody></table>')
        parts.append('</section>')
    parts.append('</body></html>\n')
    return ''.join(parts).encode('utf-8')


def _expected_tokens(projected):
    tokens = [("h1", TITLE)]
    for title, section in _checked_sections(projected):
        tokens.append(("h2", title))
        for block in section["blocks"]:
            if block["kind"] == "text":
                tokens.append(("p", block["text"]))
            elif block["kind"] == "quote":
                tokens.append(("pre", block["text"]))
            else:
                tokens.append(("h3", block["caption"]))
                tokens.extend(("th", v) for v in block["headers"])
                tokens.extend(("td", v) for row in block["rows"] for v in row)
    return tokens


class _HTMLText(HTMLParser):
    """Independent extraction: foreign content must remain inert text in visible cells."""
    allowed = {"html", "head", "meta", "title", "style", "body", "section", "h1", "h2", "h3", "p",
               "blockquote", "pre", "table", "thead", "tbody", "tr", "th", "td"}
    captures = {"h1", "h2", "h3", "p", "pre", "th", "td"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tokens, self.stack, self.parts = [], [], []
        self.capture = None
        self.style_parts, self.title_parts, self.meta_values = [], [], []
        self.style_count = 0

    def handle_starttag(self, tag, attrs):
        if tag not in self.allowed or self.capture:
            raise ValueError("Active, nested or unexpected HTML markup")
        parents = {"html": {None}, "head": {"html"}, "body": {"html"},
                   "meta": {"head"}, "title": {"head"}, "style": {"head"},
                   "section": {"body"}, "h1": {"body"}, "h2": {"section"}, "h3": {"section"},
                   "p": {"section"}, "blockquote": {"section"}, "pre": {"blockquote"},
                   "table": {"section"}, "thead": {"table"}, "tbody": {"table"},
                   "tr": {"thead", "tbody"}, "th": {"tr"}, "td": {"tr"}}
        if (self.stack[-1] if self.stack else None) not in parents[tag]:
            raise ValueError("Unexpected HTML element placement")
        permitted = {"html": {("lang", "en")}, "meta": {("charset", "utf-8"), ("name", "viewport"),
                     ("content", "width=device-width,initial-scale=1")},
                     "p": {("class", v) for v in ("normal", "notice", "status")}, "th": {("scope", "col")}}
        if any(attr not in permitted.get(tag, set()) for attr in attrs):
            raise ValueError("Unexpected or active HTML attribute")
        if tag == "meta":
            self.meta_values.append(dict(attrs))
        else:
            self.stack.append(tag)
        if tag in self.captures:
            self.capture, self.parts = tag, []

    def handle_data(self, data):
        if self.capture:
            self.parts.append(data)
        elif self.stack and self.stack[-1] == "style":
            self.style_parts.append(data)
        elif self.stack and self.stack[-1] == "title":
            self.title_parts.append(data)
        elif data.strip() and (not self.stack or self.stack[-1] not in {"style", "title"}):
            raise ValueError("Unaccounted visible HTML text")

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise ValueError("Malformed HTML structure")
        if tag == "style":
            self.style_count += 1
            if "".join(self.style_parts) != STYLE:
                raise ValueError("Unverified stylesheet or hidden report content")
        if tag == "title" and "".join(self.title_parts) != TITLE:
            raise ValueError("Unexpected document title")
        if tag == self.capture:
            self.tokens.append((tag, ''.join(self.parts)))
            self.capture = None


def _markdown_tokens(document):
    """Read the supported Markdown grammar without consulting serializer output."""
    if any(char in document for char in LINE_TERMINATORS):
        raise ValueError("Raw line terminator inside a Markdown line")
    lines, tokens, index = document.split("\n"), [], 0
    def decode(value):
        return html.unescape(value.replace("<br>", "\n"))
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line:
            continue
        if re.fullmatch(r"`{3,}", line):
            body = []
            while index < len(lines) and lines[index] != line:
                body.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError("Unterminated literal Markdown quote")
            tokens.append(("pre", "\n".join(body)))
            index += 1
        elif line.startswith("| ") and line.endswith(" |"):
            header = index < len(lines) and re.fullmatch(r"\|(?: --- \|)+", lines[index])
            tag = "th" if header else "td"
            tokens.extend((tag, decode(cell)) for cell in line[2:-2].split(" | "))
            if header:
                index += 1
        elif line.startswith("### "):
            tokens.append(("h3", decode(line[4:])))
        elif line.startswith("## "):
            tokens.append(("h2", decode(line[3:])))
        elif line.startswith("# "):
            tokens.append(("h1", decode(line[2:])))
        else:
            tokens.append(("p", decode(line)))
    return tokens


def _validate_record_references(directory, projected):
    """Resolve only explicitly typed host references against the actual bound record file."""
    record = json.loads((directory / "record.json").read_bytes())
    for _, section in projected:
        for block in section["blocks"]:
            if block["kind"] != "table":
                continue
            for reference in block["record_references"]:
                path = reference["path"]
                if not isinstance(path, str) or not path.startswith("record.json#/"):
                    raise ValueError("Invalid host record reference")
                if block["rows"][reference["row"]][reference["column"]] != path:
                    raise ValueError("Displayed host reference differs from its binding")
                target = record
                try:
                    for component in path.removeprefix("record.json#/").split("/"):
                        key = component.replace("~1", "/").replace("~0", "~")
                        if isinstance(target, list):
                            if not re.fullmatch(r"0|[1-9][0-9]*", key):
                                raise ValueError("Invalid array index")
                            target = target[int(key)]
                        else:
                            target = target[key]
                except (KeyError, IndexError, TypeError, ValueError) as exc:
                    raise ValueError(f"Host record reference does not resolve: {path}") from exc
                if digest(target) != reference["target_fingerprint"]:
                    raise ValueError(f"Host record reference points to different content: {path}")


def validate_files(directory: Path, projected, mode: str = "recorded_offline") -> dict[str, str]:
    """Actual UTF-8 bytes, all semantic cells/quotes in order, inert HTML and format parity."""
    md, page = (directory / "report.md").read_bytes(), (directory / "report.html").read_bytes()
    expected = _expected_tokens(projected)
    _validate_record_references(directory, projected)
    parser = _HTMLText()
    parser.feed(page.decode("utf-8"))
    parser.close()
    if parser.style_count != 1 or parser.meta_values != [
        {"charset": "utf-8"}, {"name": "viewport", "content": "width=device-width,initial-scale=1"}
    ]:
        raise ValueError("Mandatory encoding, viewport or print stylesheet is absent")
    if parser.stack or parser.tokens != expected:
        raise ValueError("HTML section/order/content parity failed")
    if _markdown_tokens(md.decode("utf-8")) != expected:
        raise ValueError("Markdown section/order/content parity failed")
    if ("p", notice_for(mode)) not in expected or ("p", LIMITS) not in expected:
        raise ValueError("Mandatory execution-mode/assurance warning absent")
    if md != markdown(projected) or page != html_report(projected):
        raise ValueError("Rendered bytes differ from the canonical semantic projection")
    return {"report.md": digest(md), "report.html": digest(page)}
