"""Markdown-to-HTML renderers used for the display matrix.

* ``cmark-gfm-unsafe``: GitHub's C implementation cmark-gfm (via the cmarkgfm
  package) with the GitHub extensions table, autolink, tagfilter,
  strikethrough and tasklist and ``CMARK_OPT_UNSAFE`` (raw HTML passed through;
  an HTML-processing configuration).
* ``cmark-gfm-safe``: the same with default options (raw HTML replaced by
  ``<!-- raw HTML omitted -->``).
* ``markdown-it-py-html``: markdown-it-py, CommonMark preset, ``html=True``,
  plus the table and strikethrough rules.
* ``python-markdown``: Python-Markdown with the ``tables`` and ``fenced_code``
  extensions (an independent, non-CommonMark implementation).

This is a local, GFM-compatible library rendering. It is not the GitHub web
service and does not reproduce GitHub's HTML sanitizer.
"""

from __future__ import annotations

import html
import importlib.metadata
from collections.abc import Callable

import cmarkgfm
import markdown  # type: ignore[import-untyped]
from cmarkgfm import _cmark
from cmarkgfm.cmark import Options
from markdown_it import MarkdownIt

PAGE = (
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
    "<title>{title}</title></head>\n<body>\n{body}\n</body></html>\n"
)


def _cmark_unsafe(text: str) -> str:
    return str(
        cmarkgfm.github_flavored_markdown_to_html(
            text, options=Options.CMARK_OPT_UNSAFE
        )
    )


def _cmark_safe(text: str) -> str:
    return str(cmarkgfm.github_flavored_markdown_to_html(text))


_MARKDOWN_IT = MarkdownIt("commonmark", {"html": True}).enable(
    ["table", "strikethrough"]
)


def _markdown_it(text: str) -> str:
    return str(_MARKDOWN_IT.render(text))


def _python_markdown(text: str) -> str:
    return str(markdown.markdown(text, extensions=["tables", "fenced_code"]))


RENDER_FUNCTIONS: dict[str, Callable[[str], str]] = {
    "cmark-gfm-unsafe": _cmark_unsafe,
    "cmark-gfm-safe": _cmark_safe,
    "markdown-it-py-html": _markdown_it,
    "python-markdown": _python_markdown,
}


def render_page(renderer: str, markdown_text: str, title: str) -> str:
    body = RENDER_FUNCTIONS[renderer](markdown_text)
    return PAGE.format(title=html.escape(title), body=body)


def renderer_versions() -> dict[str, dict[str, str]]:
    cmark_version = _cmark.ffi.string(_cmark.lib.cmark_version_string()).decode()
    cmarkgfm_version = importlib.metadata.version("cmarkgfm")
    return {
        "cmark-gfm-unsafe": {
            "implementation": "cmark-gfm (C) via cmarkgfm",
            "package": f"cmarkgfm=={cmarkgfm_version}",
            "library": f"cmark-gfm {cmark_version}",
            "settings": "github_flavored_markdown_to_html, extensions table, "
            "autolink, tagfilter, strikethrough, tasklist; options "
            "CMARK_OPT_UNSAFE | CMARK_OPT_GITHUB_PRE_LANG",
        },
        "cmark-gfm-safe": {
            "implementation": "cmark-gfm (C) via cmarkgfm",
            "package": f"cmarkgfm=={cmarkgfm_version}",
            "library": f"cmark-gfm {cmark_version}",
            "settings": "github_flavored_markdown_to_html, same extensions; "
            "options CMARK_OPT_GITHUB_PRE_LANG (default safe mode)",
        },
        "markdown-it-py-html": {
            "implementation": "markdown-it-py (Python)",
            "package": "markdown-it-py=="
            + importlib.metadata.version("markdown-it-py"),
            "library": f"mdurl=={importlib.metadata.version('mdurl')}",
            "settings": "MarkdownIt('commonmark', {'html': True})"
            ".enable(['table', 'strikethrough'])",
        },
        "python-markdown": {
            "implementation": "Python-Markdown (Python)",
            "package": f"Markdown=={importlib.metadata.version('Markdown')}",
            "library": "",
            "settings": "markdown.markdown(text, extensions=['tables', 'fenced_code'])",
        },
    }
