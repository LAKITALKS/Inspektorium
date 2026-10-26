"""Independent E1/E2 measurements of actual CLI Markdown/JSON.

No product encoder is imported. Visual controls remove only raw Mn/Me from
payload text nodes in a second rendering of the SAME report. Host text and
host box dimensions must match; missing/changed rows or images are INVALID.
This avoids the old n=0 twin's changed offsets and silently skipped rows.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import subprocess
import sys
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import cmarkgfm
import markdown
import numpy as np
from markdown_it import MarkdownIt
from PIL import Image
from playwright.sync_api import sync_playwright

DARK = 160
THRESHOLD = 10
VIEWPORT = {"width": 1000, "height": 900}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def longest_marks(text):
    # Independent regular-expression-free scan of actual emitted characters.
    runs, current = [], 0
    for character in text:
        if unicodedata.category(character) in ("Mn", "Me"):
            current += 1
        else:
            runs.append(current)
            current = 0
    return max([current, *runs])


class Parsed(HTMLParser):
    def __init__(self, value):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.links = []
        self.feed(value)

    def handle_data(self, data):
        self.text.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


def renderings(text):
    return {
        "cmark-gfm-safe": cmarkgfm.github_flavored_markdown_to_html(text),
        "cmark-gfm-unsafe": cmarkgfm.github_flavored_markdown_to_html(
            text, options=cmarkgfm.cmark.Options.CMARK_OPT_UNSAFE
        ),
        "markdown-it-py-html": MarkdownIt("commonmark", {"html": True})
        .enable(["table", "strikethrough"])
        .render(text),
        "python-markdown": markdown.markdown(
            text, extensions=["tables", "fenced_code"]
        ),
    }


DOM = r"""({field, finding}) => {
 let section='header', number=0;
 let rows=Array.from(document.querySelectorAll('h1,h2,h3,p,li')).map((el,i)=>{
   const text=el.innerText;
   if(el.tagName==='H2') section=text;
   if(el.tagName==='H3' && text.startsWith('Finding '))
     number=Number(text.split(' ')[1].replace(':',''));
   let payload=section==='Findings' && number===finding+1 && (
     field==='rationale' && el.tagName==='LI' &&
       text.startsWith('Rationale (evaluator-generated):') ||
     field==='claim_text' && el.tagName==='LI' && text.startsWith('Atomic claim:') ||
     field==='evidence_quote' && el.tagName==='P' &&
       el.parentElement.tagName==='BLOCKQUOTE');
   if(payload) el.setAttribute('data-payload','yes');
   const range=document.createRange();range.selectNodeContents(el);
   const r=range.getBoundingClientRect();
   return {i,tag:el.tagName,text,section,number,payload,visible:el.checkVisibility(),
     x:r.x+scrollX,y:r.y+scrollY,w:r.width,h:r.height};
 });
 return {rows, headings:Array.from(document.querySelectorAll('h2')).map(e=>e.innerText),
   links:Array.from(document.querySelectorAll('a')).map(e=>({href:e.getAttribute('href'),text:e.innerText})),
   text:document.body.innerText};
}"""
REMOVE = r"""() => {
 const els=Array.from(document.querySelectorAll('[data-payload]'));
 let removed=0;
 for(const el of els) {
   const walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let node;
   while(node=walk.nextNode())
     node.textContent=node.textContent.replace(
       /[\p{Mn}\p{Me}]/gu,()=>{removed++;return ''});
 }
 return removed;
}"""


def crop(array, row):
    x0, y0 = round(row["x"]) - 2, round(row["y"]) - 2
    x1, y1 = round(row["x"] + row["w"]) + 2, round(row["y"] + row["h"]) + 2
    if x0 < 0 or y0 < 0 or x1 > array.shape[1] or y1 > array.shape[0]:
        raise ValueError("host crop outside screenshot")
    if x1 <= x0 or y1 <= y0:
        raise ValueError("empty host crop")
    return array[y0:y1, x0:x1]


def compare(original, twin, png, clean_png):
    if not png or not clean_png:
        raise ValueError("missing screenshot")
    a = np.asarray(Image.open(io.BytesIO(png)).convert("L"))
    b = np.asarray(Image.open(io.BytesIO(clean_png)).convert("L"))
    rows, twins = original["rows"], twin["rows"]
    if len(rows) != len(twins) or not rows or sum(r["payload"] for r in rows) != 1:
        raise ValueError("missing or ambiguous payload/host rows")
    expected_h2 = [
        "Summary",
        "Findings",
        "Validation Warnings",
        "Scope and Limitations",
    ]
    if original["headings"] != expected_h2 or twin["headings"] != expected_h2:
        raise ValueError("missing critical headings")
    result = []
    for row, other in zip(rows, twins, strict=True):
        if (row["i"], row["tag"], row["payload"]) != (
            other["i"],
            other["tag"],
            other["payload"],
        ):
            raise ValueError("structure changed")
        if row["payload"]:
            continue
        if row["text"] != other["text"] or not row["visible"] or not other["visible"]:
            raise ValueError("host text changed or invisible")
        if abs(row["w"] - other["w"]) > 0.01 or abs(row["h"] - other["h"]) > 0.01:
            raise ValueError("host box dimensions changed")
        ca, cb = crop(a, row), crop(b, other)
        if ca.shape != cb.shape:
            raise ValueError("pixel box dimensions changed")
        count = int(((ca < DARK) & ~(cb < DARK)).sum())
        result.append(
            {
                **row,
                "twin_box": {k: other[k] for k in ("x", "y", "w", "h")},
                "added_ink_px": count,
                "overlap": count >= THRESHOLD,
            }
        )
    guards = [r for r in result if r["text"] == "Deterministic guard: failed"]
    failed = [
        r
        for r in result
        if r["text"]
        == "Reportable proposed relationship: None — deterministic guard failed"
    ]
    warnings = [
        r
        for r in result
        if r["section"] == "Validation Warnings"
        and r["tag"] == "LI"
        and "evidence_span_mismatch" in r["text"]
    ]
    if len(guards) != 1 or len(failed) != 1 or len(warnings) != 1:
        raise ValueError("missing actual failed guard/reportability/warning line")
    return {
        "status": "MEASURED",
        "overlap": any(r["overlap"] for r in result),
        "critical_overlaps": sum(r["overlap"] for r in guards + failed + warnings),
        "critical_rows": len(guards + failed + warnings),
        "rows": result,
    }


def css(fonts, style):
    family = "NotoSerif" if style == "noto-serif" else "NotoSans"
    faces = []
    for weight, number in (("Regular", 400), ("Bold", 700)):
        data = base64.b64encode(
            (fonts / f"{family}-{weight}.ttf").read_bytes()
        ).decode()
        faces.append(
            f"@font-face{{font-family:ProbeNoto;src:url(data:font/ttf;base64,{data});font-weight:{number};}}"
        )
    layout = (
        "body{font-family:ProbeNoto;font-size:16px;"
        + ("line-height:1.5;" if style == "github-like" else "")
        + "}"
    )
    return "<style>" + "".join(faces) + layout + "</style>"


def cli_cases(args, cases):
    rows = []
    executable = args.venv / "bin/inspektorium"
    python = args.venv / "bin/python"
    check = subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            "import inspektorium,json,sys,unicodedata;"
            "print(json.dumps({'file':inspektorium.__file__,"
            "'version':inspektorium.__version__,'python':sys.version,"
            "'unicode':unicodedata.unidata_version}))",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    imported = json.loads(check.stdout)
    if "site-packages" not in imported["file"] or not imported["file"].startswith(
        str(args.venv)
    ):
        raise ValueError("product imported from unexpected path")
    provenance = json.loads(args.provenance.read_text())
    install = json.loads((args.venv / "evidence_venv.json").read_text())
    wheel = args.provenance.parent / "wheels" / provenance["wheel"]
    if provenance["commit"] != args.commit:
        raise ValueError("commit differs from built provenance")
    if sha(wheel.read_bytes()) != provenance["wheel_sha256"]:
        raise ValueError("wheel hash differs from build provenance")
    if install["wheel_sha256"] != provenance["wheel_sha256"]:
        raise ValueError("installed wheel differs from build")
    installed_files = {}
    site = Path(imported["file"]).parent.parent
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith("inspektorium/") and not name.endswith("/"):
                expected = archive.read(name)
                if (site / name).read_bytes() != expected:
                    raise ValueError("installed source differs from built wheel")
                installed_files[name] = sha(expected)
    imported["installed_files_sha256"] = installed_files
    imported["build_provenance"] = provenance
    imported["file"] = (
        "<PRODUCT_VENV>/" + imported["file"].split(str(args.venv) + "/", 1)[1]
    )
    save(args.out / "product.json", imported)
    for case in cases:
        d = args.work / case["id"]
        d.mkdir(parents=True, exist_ok=False)
        for f in ("input", "proposals"):
            (d / f"{f}.json").write_text(
                json.dumps(case[f], ensure_ascii=False, indent=2) + "\n"
            )
        calls = []
        for fmt, ext in (("json", "json"), ("markdown", "md")):
            command = [
                str(executable),
                "inspect",
                "--input",
                str(d / "input.json"),
                "--proposals",
                str(d / "proposals.json"),
                "--format",
                fmt,
                "--output",
                str(d / f"report.{ext}"),
            ]
            p = subprocess.run(command, capture_output=True, text=True, check=False)
            calls.append(
                {
                    "command": [
                        c.replace(str(args.venv), "<PRODUCT_VENV>").replace(
                            str(args.work), "<RUN_WORK>"
                        )
                        for c in command
                    ],
                    "exit_code": p.returncode,
                    "stdout": p.stdout,
                    "stderr": p.stderr,
                }
            )
            if p.returncode != 0:
                raise ValueError(f"CLI failure {case['id']}: {p.stderr}")
        report = (d / "report.json").read_bytes()
        md = (d / "report.md").read_text()
        obj = json.loads(report)
        raw = case["proposals"]["findings"][case["finding"]][case["field"]]
        if obj["findings"][case["finding"]][case["field"]] != raw:
            raise ValueError("raw text changed")
        if [f["deterministic_validation_status"] for f in obj["findings"]] != [
            "passed",
            "failed",
            "passed",
        ]:
            raise ValueError("unexpected semantic guard statuses")
        rows.append(
            {
                "id": case["id"],
                "input_sha256": sha((d / "input.json").read_bytes()),
                "proposals_sha256": sha((d / "proposals.json").read_bytes()),
                "json_sha256": sha(report),
                "markdown_sha256": sha(md.encode()),
                "raw_preserved": True,
                "calls": calls,
                "json": obj,
                "markdown": md,
            }
        )
    save(args.out / "outputs.json", rows)
    return rows


def main():
    p = argparse.ArgumentParser()
    for name in ("catalog", "venv", "fonts", "work", "out", "provenance"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--limit", type=int)
    args = p.parse_args()
    for name in ("catalog", "venv", "fonts", "work", "out", "provenance"):
        setattr(args, name, getattr(args, name).resolve())
    args.work.mkdir(parents=True, exist_ok=False)
    args.out.mkdir(parents=True, exist_ok=False)
    cases = json.loads(args.catalog.read_text())["cases"]
    if args.limit:
        cases = cases[: args.limit]
    envguard = os.environ.get("EVIDENCE_NETGUARD_LOG")
    if not envguard or not Path(envguard).exists():
        raise ValueError("harness guard log missing")
    records = cli_cases(args, cases)
    manifest = {
        "commit": args.commit,
        "catalog_sha256": sha(args.catalog.read_bytes()),
        "harness_sha256": sha(Path(__file__).read_bytes()),
        "python": sys.version,
        "unicode": unicodedata.unidata_version,
        "platform": platform.platform(),
        "versions": {
            n: importlib.metadata.version(n)
            for n in (
                "cmarkgfm",
                "Markdown",
                "markdown-it-py",
                "playwright",
                "numpy",
                "Pillow",
            )
        },
        "font_manifest": json.loads((args.fonts / "manifest.json").read_text()),
        "viewport": VIEWPORT,
        "device_scale_factor": 1,
        "dark_rule": "grayscale < 160",
        "overlap_rule": "added dark pixels >= 10",
        "twin": "remove raw Mn/Me from payload DOM text only; same report host data",
        "styles": {
            "noto-serif": "Noto Serif 2.015;16px;normal line-height",
            "github-like": "Noto Sans 2.015;16px;line-height:1.5",
        },
    }
    texts = []
    visuals = []
    network = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, args=["--host-resolver-rules=MAP * ~NOTFOUND"]
        )
        manifest["browser"] = browser.version
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=1,
            java_script_enabled=False,
            service_workers="block",
        )

        def route(request):
            network.append({"url": request.request.url, "action": "blocked"})
            request.abort()

        context.route("**/*", route)
        page = context.new_page()
        for case, record in zip(cases, records, strict=True):
            renderers = renderings(record["markdown"])
            for renderer, html in renderers.items():
                page.set_content(
                    '<!doctype html><meta charset="utf-8"><body>' + html + "</body>"
                )
                dom = page.evaluate(DOM, case)
                texts.append(
                    {
                        "id": case["id"],
                        "kind": case["kind"],
                        "renderer": renderer,
                        "raw_markdown_max_run": longest_marks(record["markdown"]),
                        "rendered_max_run": longest_marks(dom["text"]),
                        "links": dom["links"],
                        "visible_text": dom["text"],
                        "E1_text_pass": longest_marks(record["markdown"]) <= 4
                        and longest_marks(dom["text"]) <= 4,
                        "K7_no_links": len(dom["links"]) == 0,
                    }
                )
            if case["kind"] != "combining":
                continue
            for style in ("noto-serif", "github-like"):
                page.set_content(
                    '<!doctype html><meta charset="utf-8">'
                    + css(args.fonts, style)
                    + "<body>"
                    + renderers["cmark-gfm-safe"]
                    + "</body>"
                )
                fontload = page.evaluate(
                    "async()=>{getComputedStyle(document.body).fontFamily;"
                    "await document.fonts.load('400 16px ProbeNoto');"
                    "await document.fonts.load('700 16px ProbeNoto');"
                    "await document.fonts.ready;"
                    "return Array.from(document.fonts).map(f=>({family:f.family,"
                    "weight:f.weight,status:f.status}))}"
                )
                # Screenshot forces settled paint with page JavaScript disabled.
                page.screenshot()
                original = page.evaluate(DOM, case)
                cdp = context.new_cdp_session(page)
                cdp.send("DOM.enable")
                cdp.send("CSS.enable")
                doc = cdp.send("DOM.getDocument")
                node = cdp.send(
                    "DOM.querySelector",
                    {"nodeId": doc["root"]["nodeId"], "selector": "[data-payload]"},
                )
                used = cdp.send(
                    "CSS.getPlatformFontsForNode", {"nodeId": node["nodeId"]}
                )["fonts"]
                cdp.detach()
                png = page.screenshot(full_page=True)
                original = page.evaluate(DOM, case)
                removed = page.evaluate(REMOVE)
                twin = page.evaluate(DOM, case)
                clean_png = page.screenshot(full_page=True)
                twin = page.evaluate(DOM, case)
                name = case["id"] + "-" + style
                shots = args.out / "screenshots"
                shots.mkdir(exist_ok=True)
                (shots / (name + "-actual.png")).write_bytes(png)
                (shots / (name + "-twin.png")).write_bytes(clean_png)
                try:
                    if not all(f["status"] == "loaded" for f in fontload):
                        raise ValueError("font not loaded")
                    if not any(
                        f["isCustomFont"] and f["familyName"].startswith("Noto")
                        for f in used
                    ):
                        raise ValueError("Noto not used in payload")
                    result = compare(original, twin, png, clean_png)
                except (ValueError, OSError) as e:
                    result = {"status": "INVALID", "reason": str(e), "overlap": None}
                visuals.append(
                    {
                        "id": case["id"],
                        "style": style,
                        "font_load": fontload,
                        "fonts_used": used,
                        "removed_marks": removed,
                        "original_dom": original,
                        "twin_dom": twin,
                        "png_sha256": sha(png),
                        "twin_png_sha256": sha(clean_png),
                        **result,
                    }
                )
        browser.close()
    guard = [json.loads(line) for line in Path(envguard).read_text().splitlines()]
    save(args.out / "text_measurements.json", texts)
    save(args.out / "visual_measurements.json", visuals)
    save(args.out / "browser_network.json", network)
    save(args.out / "manifest.json", manifest)
    summary = {
        "cases": len(cases),
        "text_renderings": len(texts),
        "E1_text_failures": sum(not x["E1_text_pass"] for x in texts),
        "K7_link_violations": sum(not x["K7_no_links"] for x in texts),
        "raw_preserved": sum(r["raw_preserved"] for r in records),
        "visuals": {
            s: {
                "measured": sum(
                    v["style"] == s and v["status"] == "MEASURED" for v in visuals
                ),
                "invalid": sum(
                    v["style"] == s and v["status"] == "INVALID" for v in visuals
                ),
                "overlaps": sum(
                    v["style"] == s and v["overlap"] is True for v in visuals
                ),
                "critical_overlaps": sum(
                    v["critical_overlaps"]
                    for v in visuals
                    if v["style"] == s and v["status"] == "MEASURED"
                ),
            }
            for s in ("noto-serif", "github-like")
        },
        "guard_armed_processes": len(
            {r["pid"] for r in guard if r["event"] == "armed"}
        ),
        "guard_refusals": sum(r["event"] == "refused" for r in guard),
        "browser_blocked_requests": len(network),
    }
    save(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    if any(v["status"] == "INVALID" for v in visuals):
        sys.exit(2)


if __name__ == "__main__":
    main()
