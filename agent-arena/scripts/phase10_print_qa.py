"""Check QA-only print PDFs and rasterize selected pages for actual visual review.

Usage: python scripts/phase10_print_qa.py RENDER_DIRECTORY
Optional engineering dependencies: pypdf and Poppler pdftoppm. No PDF is authored.
"""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pypdf


class Cells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag, self.parts, self.values = None, [], []
        self.header_rows, self.current_headers = [], None

    def handle_starttag(self, tag, attrs):
        if tag == "thead":
            self.current_headers = []
        if tag in {"p", "pre", "td", "th", "h1", "h2", "h3"}:
            self.tag, self.parts = tag, []

    def handle_data(self, value):
        if self.tag:
            self.parts.append(value)

    def handle_endtag(self, tag):
        if tag == self.tag:
            self.values.append("".join(self.parts))
            if tag == "th" and self.current_headers is not None:
                self.current_headers.append("".join(self.parts))
            self.tag = None
        if tag == "thead":
            self.header_rows.append("".join(self.current_headers))
            self.current_headers = None


def main():
    root = Path(sys.argv[1])
    manifest = json.loads((root / "render-manifest.json").read_text())
    def normalize(text):
        return re.sub(r"\s+", "", text)
    results = []
    for case in manifest["cases"]:
        pdf = root / case["pdf"]
        reader = pypdf.PdfReader(pdf)
        parser = Cells()
        parser.feed(Path(case["html"]).read_text())
        page_texts, removed_headers = [], 0
        for page in reader.pages:
            text = normalize(page.extract_text() or "")
            for header in set(parser.header_rows):
                prefix = normalize(header)
                if text.startswith(prefix):
                    text = text[len(prefix):]
                    removed_headers += 1
                    break
            page_texts.append(text)
        text = "".join(page_texts)
        missing = [value for value in parser.values if normalize(value) not in text]
        pages = sorted({1, len(reader.pages) // 2 or 1, len(reader.pages)})
        for number in pages:
            subprocess.run([shutil.which("pdftoppm"), "-f", str(number), "-l", str(number),
                            "-scale-to", "1200", "-singlefile", "-png", str(pdf),
                            str(root / f"{case['id']}-page-{number}")],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        result = {"id": case["id"], "pages": len(reader.pages),
                  "visible_values_checked": len(parser.values), "missing_values": missing,
                  "selected_visual_pages": pages, "repeated_page_header_prefixes_removed": removed_headers}
        results.append(result)
        print(case["id"], len(reader.pages), "pages; missing values:", len(missing), flush=True)
    (root / "print-checks.json").write_text(json.dumps({
        "method": "Full visible-cell inclusion after whitespace normalization and removal of exact repeated table-header prefixes at page starts; Poppler PNG pages for separate visual inspection",
        "pypdf_version": pypdf.__version__, "python": sys.version,
        "results": results,
    }, ensure_ascii=False, indent=2) + "\n")
    return int(any(result["missing_values"] for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
