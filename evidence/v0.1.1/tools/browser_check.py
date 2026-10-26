"""Load rendered report pages in a local Chromium and extract DOM facts.

Browser network is blocked: every request other than the page's own file://
document is aborted through Playwright routing and recorded, and the browser's
host resolver maps every name to NOTFOUND (defense in depth). Page JavaScript
is disabled, so active content is detected structurally, never executed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.sync_api import Route, sync_playwright

PROBE_JS = (Path(__file__).resolve().parent / "dom_probe.js").read_text(
    encoding="utf-8"
)
LAUNCH_ARGS = ["--host-resolver-rules=MAP * ~NOTFOUND"]
VIEWPORT = {"width": 1280, "height": 1600}


def probe_pages(
    jobs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    """Return (facts rows, network rows, browser info) for jobs.

    Each job: {"case", "renderer", "path", "tokens", "fields"}.
    """

    facts: list[dict[str, Any]] = []
    network: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=LAUNCH_ARGS)
        info = {
            "browser": "Chromium (Playwright build, headless)",
            "version": browser.version,
            "launch_args": " ".join(LAUNCH_ARGS),
            "javascript_enabled": "false",
            "service_workers": "block",
        }
        context = browser.new_context(
            java_script_enabled=False,
            service_workers="block",
            viewport=VIEWPORT,
        )
        current: dict[str, Any] = {}

        def handle(route: Route) -> None:
            request = route.request
            own_page = request.url == current.get("url")
            row = {
                "case": current.get("case"),
                "renderer": current.get("renderer"),
                "url": request.url if own_page else request.url[:200],
                "resource_type": request.resource_type,
                "own_page": own_page,
                "network": request.url.split(":", 1)[0] not in ("file", "data"),
                "action": "continue" if own_page else "abort",
            }
            network.append(row)
            if own_page:
                route.continue_()
            else:
                route.abort()

        context.route("**/*", handle)
        page = context.new_page()
        info["user_agent"] = page.evaluate("() => navigator.userAgent")
        for job in jobs:
            url = Path(job["path"]).resolve().as_uri()
            current.update(
                {"url": url, "case": job["case"], "renderer": job["renderer"]}
            )
            row: dict[str, Any] = {"case": job["case"], "renderer": job["renderer"]}
            try:
                page.goto(url, wait_until="load", timeout=30000)
                row["facts"] = page.evaluate(
                    PROBE_JS, {"tokens": job["tokens"], "fields": job["fields"]}
                )
                row["error"] = None
            except Exception as exc:  # recorded as NOT_EXECUTED downstream
                row["facts"] = None
                row["error"] = f"{type(exc).__name__}: {exc}"[:500]
            facts.append(row)
        context.close()
        browser.close()
    for row in network:
        if row["own_page"]:
            row["url"] = "<own page>"
    return facts, network, info
