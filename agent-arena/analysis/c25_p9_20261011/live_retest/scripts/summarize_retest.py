"""Summarize the live retest per attempt and per slot from ledger, captures, bundles and P9 state.

Offline only (no provider call). Checks every executed slot against the frozen expectations (model, host
and effective composite separately; technically incomplete sides are 'not_evaluable'), reports the P9
statuses per review kind, and performs the labelled test releases once (recorded in
evidence/test_releases.json). Re-runnable; tolerates a run that never started. Usage from the
repository root:  .venv/bin/python analysis/c25_p9_20261011/live_retest/scripts/summarize_retest.py
"""
import json
import os
from pathlib import Path

from agent_arena.phase10_bundle import inspect_bundle, release_candidate

RETEST = Path("analysis/c25_p9_20261011/live_retest")
EVIDENCE = RETEST / "evidence"
STRING_ARTIFACT = ("semantic mismatch:", "unsupported product/dose/formulation/route transfer",
                   "semantic transfer unresolved", "product transfer unresolved")
CONSTRAINING_TAIL = ("unresolved material claim attributes", "conflicting relevant support and contradiction")
TECHNICAL_STATUSES = ("RUN_FAILED", "ANALYSIS_INCOMPLETE", "PREFLIGHT_BLOCKED", "RELEASE_BLOCKED")
REVIEW_KINDS = ("counterreview", "stability")
OUTCOMES = {"completed": "completed", "failed": "failed", "denied": "denied", "rejected": "rejected_noop",
            "begun": "interrupted"}
TEST_REVIEWER = "TEST ONLY - not a scientific release"


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else None


def rel(path):
    return os.path.relpath(Path(path).resolve(), RETEST.resolve())


def classify(value, sets):
    if value is None:
        return "not_evaluable"
    if value in sets["acceptable"]:
        return "within"
    if value in sets.get("conservative", []):
        return "conservative"
    return "not_acceptable"


def capture(attempt_id):
    return read_json(RETEST / "captures" / f"{attempt_id}.json") or {}


def attempt_row(a):
    cap = capture(a["attempt_id"])
    call, info = cap.get("call") or {}, cap.get("interpretation") or {}
    return {
        "attempt_id": a["attempt_id"], "slot": a["slot_key"], "kind": a["slot_key"].split("|")[2],
        "state": a["state"], "billing": a.get("billing"), "retry_of": a.get("retry_of"),
        "transport": {"request_sent": call.get("request_sent"), "http_status": call.get("http_status"),
                      "request_id": call.get("request_id"), "error_type": call.get("error_type"),
                      "error": call.get("error")},
        "format": {"stop_reason": info.get("stop_reason"), "completion_state": info.get("completion_state"),
                   "returned_model": info.get("returned_model")},
        "tokens": a.get("usage"), "reserved_microusd": a["reserved_microusd"],
        "confirmed_cost_microusd": a.get("confirmed_token_cost_microusd"),
        "overrun_microusd": a.get("overrun_microusd"), "latency_ms": call.get("latency_ms"),
        "capture_sha256": a.get("capture_sha256")}


def proposition_route(prop):
    """Classify what determines a non-supported host state: attribute strings only, capability, or both."""
    finals, tail = {}, []
    for reason in prop.get("host_reasons", []):
        head, _, text = reason.partition(": ")
        if head.startswith("binding ") and head[len("binding "):].isdigit():
            finals[head] = text  # the last host reason of a binding trail determines its state
        else:
            tail.append(reason)
    artifact = [text for text in finals.values() if text.startswith(STRING_ARTIFACT)]
    constrained = any(t.startswith(CONSTRAINING_TAIL) or (t.startswith("required bridge ")
                                                         and "capable evidence unresolved" in t) for t in tail)
    if finals and len(artifact) == len(finals) and not constrained:
        return "string_mismatch_only"
    return "capability" if not artifact else "mixed"


def host_route(phase8):
    props = phase8.get("propositions", [])
    required = [p for p in props if p.get("required")] or props
    deviating = [p for p in required if p.get("host_state") != "supported"]
    routes = {p["proposition_id"]: proposition_route(p) for p in deviating}
    values = set(routes.values())
    route = ("none" if not routes else values.pop() if len(values) == 1 else "mixed")
    return route, routes


def review_status(kind, prefix, phase9, ledger_attempts, claims):
    key = prefix + kind
    attempts = [a for a in ledger_attempts if a["slot_key"] == key]
    captures = [capture(a["attempt_id"]) for a in attempts]
    sent = any((c.get("call") or {}).get("request_sent") for c in captures)
    possibly = any(a["state"] == "RESERVED_POSSIBLY_BILLABLE" and not c for a, c in zip(attempts, captures))
    received = any((c.get("call") or {}).get("http_status") == 200 for c in captures)
    final_capture_ok = bool(captures) and (captures[-1].get("call") or {}).get("http_status") == 200
    p9 = [x for x in (phase9 or {}).get("attempts", []) if x.get("kind") == kind]
    final = p9[-1] if p9 else None
    if final is not None:
        outcome = OUTCOMES.get(final.get("status"), final.get("status"))
    else:
        outcome = "claimed, no P9 record" if key in claims else "not reached"
    processed = bool(final is not None and final.get("status") in {"completed", "failed"}
                     and final.get("position_id") and final_capture_ok)
    return {"outcome": outcome, "allowance_claimed": key in claims, "ledger_attempts": [a["attempt_id"] for a in attempts],
            "request_sent": "yes" if sent else "possibly" if possibly else "no",
            "response_received": received, "response_processed": processed,
            "reason": ((final or {}).get("reason") or "")[:300], "independence": ((final or {}).get("independence") or "")[:300]}


def conflict_status(phase8, phase9, technical):
    if (phase9 or {}).get("review_state") == "adjudicated":
        return "resolved by human adjudication"
    originals = {p["position_id"] for p in (phase9 or {}).get("positions", []) if p.get("origin") == "original"}
    codes = {t["code"] for t in (phase9 or {}).get("triggers", []) if set(t.get("position_ids", [])) & originals}
    suffix = " (analysis technically incomplete)" if technical else ""
    if "model_host_conflict" in codes:
        return "open_material" + suffix
    if "bounded_model_host_conflict" in codes:
        return "open_bounded" + suffix
    if phase8.get("model_host_conflicts"):
        return "open (no P9 trigger recorded)" + suffix
    return ("none recorded" if technical else "none") + suffix


def bundles_on_disk():
    found = {}
    for record in sorted(RETEST.glob("bundles/*/*/record.json")):
        if record.parent.name.startswith(".audit-staging-"):
            continue
        data = json.loads(record.read_text())
        task = (data.get("run_record") or {}).get("task", {}).get("id")
        found.setdefault((record.parent.parent.name, task), []).append(rel(record.parent))
    return found


def test_release(profile, case, bundle, status, releases):
    key = f"{profile} {case}"
    expected = {"READY_FOR_RELEASE": "RELEASED", "REVIEW_REQUIRED": "RELEASE_BLOCKED"}.get(status)
    if key not in releases:
        root = RETEST / "released" / profile / case
        if root.exists() and any(root.iterdir()):
            releases[key] = {"status": "attempted before, result unrecorded", "paths": sorted(rel(p) for p in root.iterdir())}
        else:
            result = release_candidate(bundle, output_root=root, reviewer=TEST_REVIEWER,
                                       reason=f"AA-P10 live retest {case}: technical release-path check on a "
                                              "synthetic sketch case (not a real study, no gold label)")
            releases[key] = {"status": result.status, "path": rel(result.path) if result.path else None,
                             "errors": result.errors[:2]}
    entry = dict(releases[key])
    paths = [entry["path"]] if entry.get("path") else entry.get("paths", [])
    entry["released_revisions"] = [{"path": p, "valid": inspect_bundle(RETEST / p).valid,
                                    "status": (read_json(RETEST / p / "manifest.json") or {}).get("status")}
                                   for p in paths]
    entry["expected"] = expected
    entry["as_expected"] = expected is not None and entry["status"] == expected
    return entry


def executed_row(profile, case, record, expectations, ledger, disk, releases):
    task_id = f"aa-p10-live-retest-{case}"
    prefix = f"{task_id}|{profile}|"
    attempts = (ledger or {}).get("attempts", [])
    own = [a for a in attempts if a["slot_key"].startswith(prefix)]
    claims = [k for k in (ledger or {}).get("review_cap_claims", []) if k.startswith(prefix)]
    row = {"ledger_attempts": [a["attempt_id"] for a in own],
           "requests_sent": sum(1 for a in own if (capture(a["attempt_id"]).get("call") or {}).get("request_sent")),
           "review_allowance_claims": claims, "bundles_on_disk": disk.get((profile, task_id), [])}
    bundle_rel = (record or {}).get("bundle")
    if bundle_rel is None and record is None and len(row["bundles_on_disk"]) == 1:
        bundle_rel = row["bundles_on_disk"][0]
    bundle = RETEST / bundle_rel if bundle_rel else None
    exp = expectations["cases"][case]
    status = (record or {}).get("status")
    if bundle is None or not (bundle / "record.json").exists():
        phase9 = None
        row.update({"bundle": bundle_rel, "note": "no bundle; statuses derived from the ledger, claims and captures",
                    "expectation_checks": {"model": "not_evaluable", "host": "not_evaluable",
                                           "effective": "not_evaluable", "status": "not_acceptable"},
                    "within_expectations": False,
                    "not_evaluable_cause": {"reason": "technical: no bundle", "status": status}})
        reviews = {kind: review_status(kind, prefix, phase9, attempts, claims) for kind in REVIEW_KINDS}
        row["p9_reviews"] = reviews
        row["p9_status"] = p9_summary(reviews, None, claims, "not determinable (no bundle)")
        return row
    data = json.loads((bundle / "record.json").read_text())
    status = status or data.get("status")
    agent = data["run_record"]["results"][0]["agent_result"]
    phase8 = agent.get("phase8") or {}
    phase9 = data["run_record"]["metadata"].get("phase9") or {}
    positions = {p["position_id"]: p for p in phase9.get("positions", [])}
    sides = {"model": phase8.get("model_composite_state"), "host": phase8.get("host_composite_state"),
             "effective": phase8.get("composite_state")}
    technical = (status in TECHNICAL_STATUSES or phase8.get("technical_status") != "completed"
                 or sides["model"] is None or sides["host"] is None)
    checks = {"model": classify(sides["model"], exp["model_judgment"]),
              "host": classify(sides["host"], exp["host_derivation"]),
              "effective": classify(sides["effective"], exp["effective_composite"]),
              "status": "within" if status in exp["acceptable_status"] else "not_acceptable"}
    if technical:  # never a model or host deviation; a forced effective unknown is never classified
        checks.update(model="not_evaluable", host="not_evaluable", effective="not_evaluable")
    route, routes = host_route(phase8) if not technical else ("not_evaluable", {})
    reviews = {kind: review_status(kind, prefix, phase9, attempts, claims) for kind in REVIEW_KINDS}
    conflict = conflict_status(phase8, phase9, technical)
    review_positions = {p["position_id"] for p in phase9.get("positions", []) if p.get("origin") != "original"}
    row.update({
        "status": status, "bundle": rel(bundle), "bundle_valid": inspect_bundle(bundle).valid,
        "evidence_completeness": phase8.get("technical_status"),
        "transformation_findings": phase8.get("transformation_findings", [])[:5],
        "model_judgment": sides["model"], "host_state": sides["host"], "effective_state": sides["effective"],
        "model_label": phase8.get("original_model_label"), "derived_label": phase8.get("derived_label"),
        "propositions": [{k: p.get(k) for k in ("proposition_id", "required", "reported_verdict", "host_state",
                                                "derived_state", "model_host_conflict")}
                         for p in phase8.get("propositions", [])],
        "host_reasons": {p["proposition_id"]: p.get("host_reasons", []) for p in phase8.get("propositions", [])},
        "host_route": route, "host_route_per_proposition": routes,
        "model_host_conflicts": [(c["scope"], c.get("proposition_id"), c["model_state"], c["host_state"])
                                 for c in phase8.get("model_host_conflicts", [])],
        "p9_route": phase9.get("route"), "p9_mandatory": phase9.get("mandatory"),
        "p9_triggers": sorted({(t["code"], bool(t.get("mandatory")), "review" if set(t.get("position_ids", []))
                                & review_positions else "original") for t in phase9.get("triggers", [])}),
        "p9_reviews": reviews,
        "p9_review_positions": {x["kind"]: {k: (positions.get(x.get("position_id")) or {}).get("phase8", {}).get(k)
                                            for k in ("technical_status", "model_composite_state",
                                                      "host_composite_state", "composite_state")}
                                for x in phase9.get("attempts", []) if x.get("position_id")},
        "p9_position_conflicts": [{"dimension": c.get("dimension"), "material": c.get("material"),
                                   "resolution": c.get("resolution")} for c in phase9.get("conflicts", [])],
        "p9_status": p9_summary(reviews, phase9, claims, conflict),
        "review_resolution": phase9.get("review_state"),
        "expectation_checks": checks,
        "within_expectations": all(v == "within" for v in checks.values()),
        "host_deviation_likely_string_artifact": checks["host"] in ("conservative", "not_acceptable")
        and route == "string_mismatch_only",
        "host_within_representation_artifact": checks["host"] == "within" and route == "string_mismatch_only",
        "not_evaluable_cause": ({"reason": "technical", "status": status,
                                 "technical_status": phase8.get("technical_status"),
                                 "completion_states": [(capture(a["attempt_id"]).get("interpretation") or {})
                                                       .get("completion_state") for a in own
                                                       if a["slot_key"] == prefix + "primary"],
                                 "reasons": (phase8.get("reasons") or [])[:3]} if technical else None)})
    if status in ("READY_FOR_RELEASE", "REVIEW_REQUIRED"):
        row["test_release"] = test_release(profile, case, bundle, status, releases)
        row["released_with_open_material_conflict_or_review"] = (
            row["test_release"]["status"] == "RELEASED" and (conflict == "open_material" or bool(phase9.get("mandatory"))))
    return row


def p9_summary(reviews, phase9, claims, conflict):
    attempts = (phase9 or {}).get("attempts", [])
    calls = [r["request_sent"] for r in reviews.values()]
    return {"routing_reached": bool(attempts) or bool(claims) or bool(
                (phase9 or {}).get("mandatory") and (phase9 or {}).get("route") == "REVIEW_RECOMMENDED"),
            "model_call_made": "yes" if "yes" in calls else "possibly" if "possibly" in calls else "no",
            "response_processed": any(r["response_processed"] for r in reviews.values()),
            "conflict": conflict}


def main():
    manifest = json.loads((RETEST / "manifest.json").read_text())
    expectations = json.loads((RETEST / "expectations.json").read_text())
    labels = {c["case_id"]: c for c in manifest["cases"]}
    ledger = read_json(RETEST / "ledger.json")
    lines = [json.loads(line) for line in (EVIDENCE / "run_log.jsonl").read_text().splitlines()] \
        if (EVIDENCE / "run_log.jsonl").exists() else []
    starts = [i for i, e in enumerate(lines) if e.get("event") == "start"]
    accepted = [i for i in starts if lines[i].get("accepted")]
    current = lines[accepted[-1] + 1:] if accepted else []
    records = {}
    for entry in current:
        if "profile" in entry:
            records.setdefault((entry["profile"], entry["case"]), []).append(entry)
    disk = bundles_on_disk()
    releases = read_json(EVIDENCE / "test_releases.json") or {}
    slots = []
    for item in manifest["call_plan"]["order"]:
        profile, case = item.split()
        own = records.get((profile, case), [])
        record = own[-1] if own else None
        task_id = f"aa-p10-live-retest-{case}"
        executed_elsewhere = record is None and (
            any(a["slot_key"].startswith(f"{task_id}|{profile}|") for a in (ledger or {}).get("attempts", []))
            or (profile, task_id) in disk)
        row = {"profile": profile, "case": case, "case_label": labels[case]["label"], "role": labels[case]["role"],
               "invoked": bool(record and record.get("invoked")) or executed_elsewhere,
               "status": (record or {}).get("status"), "log_records": len(own),
               "executed_outside_the_runner_log": executed_elsewhere}
        if record is not None and not record.get("invoked"):
            row.update(reason=record.get("reason"), reserve_check=record.get("reserve_check"))
        elif record is None and not executed_elsewhere:
            row["reason"] = "no record after the last accepted start" if accepted else "the runner never started"
        else:
            if record is not None:
                row.update(reserve_check=record.get("reserve_check"), stop_reasons=record.get("stop_reasons"),
                           wall_seconds=record.get("wall_seconds"))
            row.update(executed_row(profile, case, record, expectations, ledger, disk, releases))
            row["status"] = row["status"] or (record or {}).get("status")
        slots.append(row)
    if releases:
        (EVIDENCE / "test_releases.json").write_text(json.dumps(releases, indent=2, ensure_ascii=False) + "\n")
    attempts = (ledger or {}).get("attempts", [])
    summary = {
        "schema": "aa-p10-live-retest-summary/1.1", "authorization_id": manifest["authorization_id"],
        "run": ("never started" if not starts else "pre-checks failed; nothing run" if not accepted else
                "ended" if any(e.get("event") == "end" for e in current) else "interrupted (no end event)"),
        "starts": [{k: lines[i].get(k) for k in ("at", "head", "freeze_commit", "restart", "accepted",
                                                  "precheck_errors")} for i in starts],
        "ledger_state": (ledger or {}).get("state"), "attempts_total": len(attempts),
        "technical_retries": sum(1 for a in attempts if a.get("retry_of")),
        "confirmed_or_reserved_microusd": (ledger or {}).get("reserved_microusd"),
        "executable_remaining_microusd": (ledger or {}).get("executable_remaining_microusd"),
        "review_cap_claims": (ledger or {}).get("review_cap_claims", []),
        "work_order_limits": {
            "attempts_max": manifest["budget"]["attempts"]["this_order_max"],
            "retries_max": manifest["budget"]["technical_retries"]["this_order_max"],
            "per_call_ceiling_microusd": manifest["budget"]["per_call_ceiling_microusd"],
            "authorized_microusd": manifest["budget"]["authorized_microusd"],
            "calls_above_per_call_ceiling": [a["attempt_id"] for a in attempts if (a.get("bound_microusd") or 0)
                                             > manifest["budget"]["per_call_ceiling_microusd"]],
            "overruns": {a["attempt_id"]: a["overrun_microusd"] for a in attempts if a.get("overrun_microusd")}},
        "closure": read_json(EVIDENCE / "closure.json"), "replay_check": read_json(EVIDENCE / "replay_check.json"),
        "attempts": [attempt_row(a) for a in attempts], "slots": slots}
    (EVIDENCE).mkdir(exist_ok=True)
    (EVIDENCE / "retest_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("run", "ledger_state", "attempts_total", "technical_retries",
                                               "confirmed_or_reserved_microusd")}, indent=1))
    for row in slots:
        print(json.dumps({k: row.get(k) for k in ("profile", "case", "invoked", "status", "model_judgment", "host_state",
                                                  "effective_state", "host_route", "p9_route", "p9_status",
                                                  "expectation_checks", "test_release", "reason")},
                         ensure_ascii=False)[:1200])


if __name__ == "__main__":
    main()
