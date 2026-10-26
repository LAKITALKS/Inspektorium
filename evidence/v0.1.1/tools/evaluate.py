"""Criteria, outcome classes and case verdicts (pure functions, no I/O).

Every decision is derived from recorded process output (CLI rows, JSON report
text) and DOM facts extracted by the browser. Missing inputs never pass.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import unicodedata
from dataclasses import dataclass
from typing import Any

from common import canonical_text, get_path, normalize_ws

INTACT = "RENDERED_CONTROLS_INTACT"
MANIPULATED = "RENDERED_MANIPULATED"
REJECTED = "REJECTED_BEFORE_RENDER"
NOT_EXECUTED = "NOT_EXECUTED"
OUTCOMES = (REJECTED, INTACT, MANIPULATED, NOT_EXECUTED)

HOLDS = "HOLDS"
FAILS = "FAILS"
NOT_DEMONSTRATED = "NOT_DEMONSTRATED"
VERDICTS = (HOLDS, FAILS, NOT_DEMONSTRATED, NOT_EXECUTED)

PRODUCT_FAILURES = (
    "CRASHED",
    "REJECTED_OUTPUT_DAMAGED",
    "REJECTED_IRREGULAR",
    "ACCEPTED_IRREGULAR",
    "TIMEOUT",
)


# --------------------------------------------------------------------------
# Expected skeleton from the JSON report and the version label map
# --------------------------------------------------------------------------
@dataclass
class Expected:
    tag: str
    text: str | None = None
    label: str | None = None
    field: str | None = None
    raw: str | None = None
    finding: int | None = None
    claim_id: str | None = None
    role: str | None = None


def _fmt(value: Any) -> str:
    if value is None:
        return "None"
    return str(value)


def _key(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _substitute(template: str, context: dict[str, Any]) -> str:
    out = []
    index = 0
    while index < len(template):
        char = template[index]
        if char == "{":
            close = template.index("}", index)
            name = template[index + 1 : close]
            out.append(_fmt(get_path(context, name)))
            index = close + 1
        else:
            out.append(char)
            index += 1
    return "".join(out)


def _derive(vmap: dict[str, Any], context: dict[str, Any]) -> dict[str, str]:
    derived = {}
    for name, spec in vmap.get("derived", {}).items():
        key = "|".join(_key(context.get(part)) for part in spec["key"])
        if key in spec["map"]:
            derived[name] = spec["map"][key]
        elif "default" in spec:
            derived[name] = _substitute(spec["default"], context)
        else:
            raise KeyError(f"label map: no value for {name} with key {key}")
    return derived


def _expand(
    items: list[dict[str, Any]],
    vmap: dict[str, Any],
    context: dict[str, Any],
    lists: dict[str, list[dict[str, Any]]],
    out: list[Expected],
) -> None:
    for item in items:
        if "each" in item:
            entries = lists[item["each"]]
            if not entries:
                _expand(item.get("empty", []), vmap, context, lists, out)
            for entry in entries:
                _expand(vmap["templates"][item["template"]], vmap, entry, lists, out)
            continue
        when = item.get("when")
        if when is not None and context.get(when) is None:
            continue
        role = None
        if item.get("status_line"):
            role = "status"
        elif item.get("warning_line"):
            role = "warning"
        elif item.get("limitation_line"):
            role = "limitation"
        expected = Expected(
            tag=item["unit"],
            finding=context.get("index"),
            claim_id=context.get("claim_id"),
            role=role,
        )
        if "field" in item:
            expected.field = item["field"]
            expected.label = item.get("label")
            expected.raw = context.get(item["field"])
        else:
            expected.text = _substitute(item["text"], context)
        out.append(expected)


def expected_units(report: dict[str, Any], vmap: dict[str, Any]) -> list[Expected]:
    findings = []
    issues = []
    for index, finding in enumerate(report["findings"], start=1):
        context = dict(finding)
        context["index"] = index
        context.update(_derive(vmap, context))
        findings.append(context)
        for issue in finding["validation_issues"]:
            issues.append(
                {
                    "claim_id": finding["claim_id"],
                    "code": issue["code"],
                    "message": issue["message"],
                }
            )
    limitations = [{"limitation": item} for item in report["scope"]["limitations"]]
    top = dict(report)
    generated = report.get("generated_at")
    if generated is not None:
        top["generated_at_iso"] = dt.datetime.fromisoformat(
            generated.replace("Z", "+00:00")
        ).isoformat()
    out: list[Expected] = []
    _expand(
        vmap["document"],
        vmap,
        top,
        {"findings": findings, "issues": issues, "limitations": limitations},
        out,
    )
    return out


# --------------------------------------------------------------------------
# Display rule (version-specific) for fidelity checks
# --------------------------------------------------------------------------
# All Unicode general category values. "Cn" (unassigned) is a valid entry: a
# map that lists it expects every code point that is unassigned in this
# Python's Unicode database (unicodedata.unidata_version) to be a marker.
# The expected display is therefore only meaningful when the harness and the
# product use the same Unicode database; run_evidence.py records both and
# refuses a tokenize map if they differ.
GENERAL_CATEGORIES = frozenset(
    "Lu Ll Lt Lm Lo Mn Mc Me Nd Nl No Pc Pd Ps Pe Pi Pf Po "
    "Sm Sc Sk So Zs Zl Zp Cc Cf Cs Co Cn".split()
)


def display(raw: str, field_name: str, vmap: dict[str, Any]) -> str:
    rule = vmap.get("display", {"mode": "identity"})
    if rule.get("mode") == "identity":
        return raw
    if rule.get("mode") != "tokenize":
        raise ValueError(f"unknown display mode {rule.get('mode')}")
    keep = set(rule.get("keep", []))
    keep |= set(rule.get("field_keep", {}).get(field_name, []))
    categories = set(rule["categories"])
    unknown = sorted(categories - GENERAL_CATEGORIES)
    if unknown:
        raise ValueError(f"unknown Unicode categories in display rule: {unknown}")
    token = rule["token"]
    literal = rule.get("literal_escapes", {})
    out = []
    for char in raw:
        if char in literal:
            out.append(literal[char])
        elif char not in keep and unicodedata.category(char) in categories:
            out.append(token.replace("{cp}", f"{ord(char):04X}"))
        else:
            out.append(char)
    return "".join(out)


# --------------------------------------------------------------------------
# Matching helpers
# --------------------------------------------------------------------------
def _unit_tag(unit: dict[str, Any]) -> str:
    return str(unit["tag"])


def _norm(unit: dict[str, Any]) -> str:
    return normalize_ws(unit["text"])


def _remainder(expected: Expected, unit: dict[str, Any]) -> str | None:
    text = _norm(unit)
    if expected.label is None:
        return text
    if text == expected.label:
        return ""
    prefix = expected.label + " "
    if text.startswith(prefix):
        return text[len(prefix) :]
    return None


def unit_matches(expected: Expected, unit: dict[str, Any]) -> bool:
    if _unit_tag(unit) != expected.tag:
        return False
    if expected.field is None:
        return _norm(unit) == normalize_ws(expected.text or "")
    return _remainder(expected, unit) is not None


def _visible(unit: dict[str, Any]) -> bool:
    return not unit["visible_reasons"]


def _segments(units: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """Map heading text -> (heading index, next heading index) for h1-h6."""

    heads = [i for i, unit in enumerate(units) if unit["kind"] == "heading"]
    segments: dict[str, tuple[int, int]] = {}
    for position, index in enumerate(heads):
        end = heads[position + 1] if position + 1 < len(heads) else len(units)
        segments.setdefault(_norm(units[index]), (index, end))
    return segments


def field_unit_index(
    units: list[dict[str, Any]],
    expected: list[Expected],
    finding_index: int,
    field_name: str,
) -> int | None:
    """Locate the intended field unit structurally inside the finding segment."""

    heading = next(
        (e for e in expected if e.tag == "h3" and e.finding == finding_index), None
    )
    target = next(
        (e for e in expected if e.finding == finding_index and e.field == field_name),
        None,
    )
    if heading is None or target is None:
        return None
    segment = _segments(units).get(normalize_ws(heading.text or ""))
    if segment is None:
        return None
    for index in range(segment[0] + 1, segment[1]):
        unit = units[index]
        if unit["tag"] == target.tag and (
            target.label is None or _remainder(target, unit) is not None
        ):
            return index
    return None


# --------------------------------------------------------------------------
# Criteria
# --------------------------------------------------------------------------
@dataclass
class Result:
    passed: bool
    detail: str = ""


def k1_sections(units: list[dict[str, Any]], exp: list[Expected]) -> Result:
    actual = [
        (u["tag"], _norm(u), _visible(u)) for u in units if u["tag"] in ("h1", "h2")
    ]
    wanted = [(e.tag, normalize_ws(e.text or "")) for e in exp if e.tag in ("h1", "h2")]
    if [(t, x) for t, x, _ in actual] != wanted:
        return Result(False, f"headings {[(t, x) for t, x, _ in actual]} != {wanted}")
    hidden = [x for _, x, visible in actual if not visible]
    if hidden:
        return Result(False, f"hidden section headings: {hidden}")
    return Result(True)


def k2_findings(units: list[dict[str, Any]], exp: list[Expected]) -> Result:
    lower = ("h3", "h4", "h5", "h6")
    actual = [(u["tag"], _norm(u), _visible(u)) for u in units if u["tag"] in lower]
    wanted = [(e.tag, normalize_ws(e.text or "")) for e in exp if e.tag in lower]
    if [(t, x) for t, x, _ in actual] != wanted:
        return Result(False, f"finding headings {[(t, x) for t, x, _ in actual]}")
    hidden = [x for _, x, visible in actual if not visible]
    if hidden:
        return Result(False, f"hidden finding headings: {hidden}")
    return Result(True)


def k3_status(
    units: list[dict[str, Any]], exp: list[Expected], vmap: dict[str, Any]
) -> Result:
    problems = []
    guard_label = vmap["guard_label"]
    segments = _segments(units)
    for heading in [e for e in exp if e.tag == "h3"]:
        status = next(
            e for e in exp if e.finding == heading.finding and e.role == "status"
        )
        segment = segments.get(normalize_ws(heading.text or ""))
        if segment is None:
            problems.append(f"finding {heading.finding}: heading missing")
            continue
        lines = [
            units[i]
            for i in range(segment[0] + 1, segment[1])
            if _norm(units[i]).startswith(guard_label)
        ]
        if len(lines) != 1:
            problems.append(f"finding {heading.finding}: {len(lines)} guard lines")
            continue
        if _norm(lines[0]) != normalize_ws(status.text or ""):
            problems.append(
                f"finding {heading.finding}: guard text {_norm(lines[0])!r}"
            )
        if not _visible(lines[0]):
            problems.append(f"finding {heading.finding}: guard line hidden")
    for label in vmap["control_labels"]:
        actual = sum(_norm(u).startswith(label) for u in units)
        wanted = sum(
            normalize_ws(e.text or e.label or "").startswith(label) for e in exp
        )
        if actual != wanted:
            problems.append(f"label {label!r}: {actual} lines, expected {wanted}")
    return Result(not problems, "; ".join(problems))


def _section_units(
    units: list[dict[str, Any]], heading_text: str
) -> list[dict[str, Any]] | None:
    segment = _segments(units).get(heading_text)
    if segment is None:
        return None
    return units[segment[0] + 1 : segment[1]]


def k4_warnings_limitations(
    units: list[dict[str, Any]], exp: list[Expected], vmap: dict[str, Any]
) -> Result:
    problems = []
    sections = vmap["sections"]
    for key in ("warnings", "limitations"):
        heading = sections[key]
        actual = _section_units(units, heading)
        start = next(
            (i for i, e in enumerate(exp) if e.tag == "h2" and e.text == heading), None
        )
        if start is None:
            problems.append(f"label map lacks section {heading}")
            continue
        end = next(
            (i for i in range(start + 1, len(exp)) if exp[i].tag in ("h1", "h2")),
            len(exp),
        )
        wanted = exp[start + 1 : end]
        if actual is None:
            problems.append(f"section {heading!r} missing")
            continue
        if len(actual) != len(wanted) or not all(
            unit_matches(e, u) for e, u in zip(wanted, actual, strict=False)
        ):
            problems.append(
                f"section {heading!r}: {[(u['tag'], _norm(u)[:60]) for u in actual]}"
            )
            continue
        hidden = [_norm(u)[:60] for u in actual if not _visible(u)]
        if hidden:
            problems.append(f"section {heading!r} hidden lines: {hidden}")
    return Result(not problems, "; ".join(problems))


def k5_skeleton(units: list[dict[str, Any]], exp: list[Expected]) -> Result:
    for index, expected in enumerate(exp):
        if index >= len(units):
            return Result(False, f"missing units from #{index} ({expected.tag})")
        if not unit_matches(expected, units[index]):
            unit = units[index]
            want = expected.text if expected.field is None else expected.label
            return Result(
                False,
                f"unit #{index}: got {unit['tag']} {_norm(unit)[:80]!r}, "
                f"expected {expected.tag} {want!r}",
            )
    if len(units) != len(exp):
        extra = units[len(exp)]
        return Result(
            False, f"extra unit #{len(exp)}: {extra['tag']} {_norm(extra)[:80]!r}"
        )
    return Result(True)


def _field_ref(ref: str, report: dict[str, Any]) -> tuple[int, str]:
    claim_id, field_name = ref.split(".", 1)
    for index, finding in enumerate(report["findings"], start=1):
        if finding["claim_id"] == claim_id:
            return index, field_name
    raise KeyError(f"no finding {claim_id}")


def k6_containment(
    facts: dict[str, Any],
    exp: list[Expected],
    report: dict[str, Any],
    sentinels: dict[str, list[str]],
) -> Result:
    problems = []
    located = {item["token"]: item for item in facts["sentinels"]}
    for ref, tokens in sentinels.items():
        finding_index, field_name = _field_ref(ref, report)
        target = field_unit_index(facts["units"], exp, finding_index, field_name)
        for token in tokens:
            info = located.get(token)
            if info is None:
                problems.append(f"{token}: not probed")
                continue
            hits = info["hits"]
            if len(hits) != 1:
                problems.append(f"{token}: {len(hits)} visible-text occurrences")
            elif target is None or hits[0]["unit"] != target:
                problems.append(f"{token}: outside its field (unit {hits[0]['unit']})")
            elif not hits[0]["visible"]:
                problems.append(f"{token}: not visible {hits[0]['reasons']}")
            if info["in_comments"] or info["in_attributes"]:
                problems.append(f"{token}: also inside comment/attribute")
    return Result(not problems, "; ".join(problems))


def k7_markup(facts: dict[str, Any], vmap: dict[str, Any]) -> Result:
    problems = []
    allowed = set(vmap["allowed_tags"])
    foreign = sorted(set(facts["tag_counts"]) - allowed)
    if foreign:
        problems.append(f"foreign elements {foreign}")
    if facts["attributes"]:
        names = sorted({f"{a['tag']}[{a['name']}]" for a in facts["attributes"]})
        problems.append(f"attributes {names[:8]}")
    if facts["comments"]:
        problems.append(f"{len(facts['comments'])} comment node(s)")
    for item in facts["ranges"]:
        field_name = item["field"].split(".", 1)[1]
        permitted = set(vmap["payload_allowed_tags"].get(field_name, []))
        if item["tags"] is None:
            continue
        extra = sorted(set(item["tags"]) - permitted)
        if extra:
            problems.append(f"{item['field']}: elements in payload {extra}")
    return Result(not problems, "; ".join(problems))


def k8_visibility(facts: dict[str, Any]) -> Result:
    hidden = [
        f"#{u['index']} {u['tag']} {u['visible_reasons'][:2]}"
        for u in facts["units"]
        if u["visible_reasons"]
    ]
    problems = []
    if hidden:
        problems.append(f"hidden units {hidden[:6]} (total {len(hidden)})")
    if facts["orphan_text"]:
        problems.append(f"text outside units {facts['orphan_text'][:2]}")
    return Result(not problems, "; ".join(problems))


def k9_controls(facts: dict[str, Any]) -> Result:
    if facts["controls"]:
        cps = sorted({item["cp"] for item in facts["controls"]})
        return Result(False, f"raw code points {cps}")
    return Result(True)


def _field_display_actual(
    facts: dict[str, Any], exp: list[Expected], finding_index: int, field_name: str
) -> str | None:
    index = field_unit_index(facts["units"], exp, finding_index, field_name)
    if index is None:
        return None
    target = next(
        e for e in exp if e.finding == finding_index and e.field == field_name
    )
    return _remainder(target, facts["units"][index])


def k10_fidelity(
    facts: dict[str, Any],
    exp: list[Expected],
    vmap: dict[str, Any],
    sentinels: dict[str, list[str]],
    report: dict[str, Any],
    include_payload: bool,
) -> Result:
    payload_refs = {_field_ref(ref, report) for ref in sentinels}
    problems = []
    for expected in exp:
        if expected.field is None or expected.raw is None:
            continue
        key = (expected.finding, expected.field)
        if key in payload_refs and not include_payload:
            continue
        assert expected.finding is not None
        actual = _field_display_actual(facts, exp, expected.finding, expected.field)
        wanted = normalize_ws(display(expected.raw, expected.field, vmap))
        if actual is None:
            problems.append(f"finding {expected.finding} {expected.field}: not found")
        elif actual != wanted:
            problems.append(
                f"finding {expected.finding} {expected.field}: {actual[:80]!r} != "
                f"{wanted[:80]!r}"
            )
    return Result(not problems, "; ".join(problems))


def k11_collision(
    facts: dict[str, Any],
    exp: list[Expected],
    report: dict[str, Any],
    pair: list[str],
    sentinels: dict[str, list[str]],
) -> Result:
    shown = []
    for ref in pair:
        finding_index, field_name = _field_ref(ref, report)
        text = _field_display_actual(facts, exp, finding_index, field_name)
        if text is None:
            return Result(False, f"{ref}: not found")
        for token in sentinels.get(ref, []):
            text = text.replace(token, "")
        shown.append(normalize_ws(text))
    if shown[0] == shown[1]:
        return Result(False, f"identical display {shown[0]!r}")
    return Result(True)


def k12_network(network_rows: list[dict[str, Any]]) -> Result:
    foreign = [row for row in network_rows if not row["own_page"]]
    if foreign:
        kinds = sorted({f"{row['resource_type']}:{row['url'][:60]}" for row in foreign})
        return Result(False, f"{len(foreign)} blocked request(s) {kinds[:4]}")
    return Result(True)


BASE_CRITERIA = ("K1", "K2", "K3", "K4", "K5", "K7", "K8", "K9", "K10", "K12")


def applicable_criteria(case: dict[str, Any]) -> set[str]:
    """Criteria that every rendered row of this case must carry (catalog
    ``criteria_application.rendered``)."""

    keys = set(BASE_CRITERIA)
    if case.get("sentinels"):
        keys.add("K6")
    if case.get("collision_pair"):
        keys.add("K11")
    return keys


def evaluate_rendering(
    case: dict[str, Any],
    report: dict[str, Any],
    facts: dict[str, Any],
    vmap: dict[str, Any],
    network_rows: list[dict[str, Any]],
) -> dict[str, Result]:
    exp = expected_units(report, vmap)
    units = facts["units"]
    sentinels = case.get("sentinels", {})
    kind = case["kind"]
    clean = kind in ("clean_counterpart", "readability", "input_acceptance")
    include_payload = clean or bool(vmap.get("display", {}).get("fidelity_on_attacks"))
    results = {
        "K1": k1_sections(units, exp),
        "K2": k2_findings(units, exp),
        "K3": k3_status(units, exp, vmap),
        "K4": k4_warnings_limitations(units, exp, vmap),
        "K5": k5_skeleton(units, exp),
        "K7": k7_markup(facts, vmap),
        "K8": k8_visibility(facts),
        "K9": k9_controls(facts),
        "K10": k10_fidelity(facts, exp, vmap, sentinels, report, include_payload),
        "K12": k12_network(network_rows),
    }
    if sentinels:
        results["K6"] = k6_containment(facts, exp, report, sentinels)
    if case.get("collision_pair"):
        results["K11"] = k11_collision(
            facts, exp, report, case["collision_pair"], sentinels
        )
    if set(results) != applicable_criteria(case):
        raise ValueError(f"{case['id']}: criteria set differs from the catalog rule")
    return dict(sorted(results.items(), key=lambda item: int(item[0][1:])))


# --------------------------------------------------------------------------
# Preconditions, CLI-level checks and verdicts
# --------------------------------------------------------------------------
def check_preconditions(case: dict[str, Any], report: dict[str, Any]) -> list[str]:
    problems = []
    for path, wanted in case.get("expect_json", []):
        try:
            actual = get_path(report, path)
        except (KeyError, IndexError, ValueError):
            problems.append(f"{path}: missing")
            continue
        if actual != wanted:
            problems.append(f"{path}: {actual!r} != {wanted!r}")
    return problems


def cli_summary(cli_rows: list[dict[str, Any]]) -> str:
    outcomes = {row["format"]: row["cli_outcome"] for row in cli_rows}
    if set(outcomes) != {"json", "markdown"}:
        return "MISSING"
    values = set(outcomes.values())
    if values == {"ACCEPTED"}:
        return "ACCEPTED"
    if values == {"REJECTED_CLEAN"}:
        return "REJECTED_CLEAN"
    for failure in PRODUCT_FAILURES:
        if failure in values:
            return failure
    return "INCONSISTENT"


def probe_ambiguity(case: dict[str, Any], json_text: str | None) -> str | None:
    """For accepted duplicate-key inputs: which candidate value was used."""

    probe = case.get("ambiguity_probe")
    if not probe or json_text is None:
        return None
    report = json.loads(json_text)
    path = probe["path"]
    if path.startswith("answer"):
        digest = report["fingerprints"]["answer_sha256"]
    else:
        digest = report["fingerprints"]["sources"][0]["sha256"]
    for label in ("first", "last"):
        candidate = canonical_text(probe[label]).encode("utf-8")
        if hashlib.sha256(candidate).hexdigest() == digest:
            return label
    return "neither"


def case_verdict(
    case: dict[str, Any], cli: str, rows: list[dict[str, Any]], extra_ok: bool
) -> tuple[str, str]:
    expected = case["expected_outcome"]
    outcomes = [row["outcome"] for row in rows]
    if cli == "MISSING":
        return NOT_EXECUTED, "CLI rows missing"
    if expected == REJECTED:
        if (
            cli == "REJECTED_CLEAN"
            and outcomes
            and all(o == REJECTED for o in outcomes)
        ):
            return HOLDS, "rejected before render; existing output preserved"
        if cli == "ACCEPTED":
            return FAILS, "accepted although rejection was expected"
        if cli in PRODUCT_FAILURES or cli == "INCONSISTENT":
            return FAILS, f"CLI outcome {cli}"
        return NOT_EXECUTED, f"CLI outcome {cli}"
    if cli in PRODUCT_FAILURES or cli == "INCONSISTENT":
        return FAILS, f"CLI outcome {cli}"
    if not outcomes:
        return NOT_EXECUTED, "no measurement rows"
    if MANIPULATED in outcomes:
        return FAILS, "manipulated rendering observed"
    if NOT_EXECUTED in outcomes:
        return NOT_EXECUTED, "at least one renderer not executed"
    if REJECTED in outcomes:
        if case["kind"] in ("input_acceptance", "clean_counterpart", "readability"):
            return FAILS, "valid input rejected"
        return NOT_DEMONSTRATED, "rejected before render; not a rendering pass"
    if not extra_ok:
        return FAILS, "case-level check failed"
    return HOLDS, "all renderers intact"
