"""Human-readable projection of already evaluated data; no new scientific inference."""
from __future__ import annotations

import unicodedata
from copy import deepcopy
from dataclasses import dataclass

from agent_arena.phase10_pipeline import automatic_outcome, digest, review_attempt_states
from agent_arena.phase9_models import CONTRACT_VERSION as P9_CONTRACT

NOTICE = ("RECORDED OFFLINE / SYNTHETIC. Local artifact decision only; no live model execution, "
          "scientific truth, empirical validation, external evidence search or customer approval.")
LIVE_NOTICE = ("LIVE MODEL GENERATION (AA-P10-LIVE/1.0). Actual provider calls produced the analysed responses; "
               "model, request IDs, attempts and cost are bound below and in record.json. Local artifact decision only; "
               "no scientific truth, empirical validation, external evidence search or customer approval.")
REPLAY_NOTICE = ("OFFLINE REPLAY OF EARLIER LIVE MODEL OUTPUT (AA-P10-LIVE/1.0). This execution made no new model call; "
                 "the original live origin is bound below and in record.json. Local artifact decision only; "
                 "no scientific truth, empirical validation, external evidence search or customer approval.")


def notice_for(mode: str) -> str:
    return {"recorded_offline": NOTICE, "live_generation": LIVE_NOTICE,
            "offline_replay_of_live": REPLAY_NOTICE}[mode]


LIMITS = ("Checks validate represented semantics and supplied source spans. Extraction correctness, "
          "exhaustiveness and scientific truth remain outside this assurance. Canonical PDF is unsupported.")
DISPLAY_NOTE = ("Control, bidirectional and invisible format characters in displayed text are shown as ⟦U+XXXX⟧, "
                "and the brackets themselves as ⟦U+27E6⟧ and ⟦U+27E7⟧; record.json keeps the exact characters.")
REASONS_NOTE = ("In 'reasons', model-supplied text (the proposition reason, uncertainty and binding reasons) is "
                "combined with host sentences; only 'host reasons' is host-written.")
TITLES = ("Execution and release", "Original claim", "Scientific judgments", "Original label and taxonomy",
          "Propositions and inference limits", "Evidence and source quotations", "Search scope",
          "Finding and client traces", "UNKNOWN, conflicts and review history", "Mandatory controls",
          "Limitations", "Provenance")


@dataclass(frozen=True)
class RecordReference:
    """Host-generated pointer, distinct from reference-like foreign prose."""
    path: str
    target_fingerprint: str

    @classmethod
    def bind(cls, path, target):
        return cls(path, digest(target))


_HIDDEN = {"Cc", "Cf", "Zl", "Zp"}


def display_text(value: str) -> str:
    """Display-only token for control, bidi and invisible characters; stored data keeps them exactly."""
    return "".join(f"⟦U+{ord(char):04X}⟧" if char in "⟦⟧" or (
        char not in "\n\t" and unicodedata.category(char) in _HIDDEN) else char for char in value)


def text(value, style="normal"):
    # Host-written sentences only; foreign text is shown through quote() or table values.
    return {"kind": "text", "text": str(value), "style": style}


def quote(value):
    return {"kind": "quote", "text": display_text(str(value))}


def _plain(item):
    if isinstance(item, RecordReference):
        return item.path
    if item is None:
        return "Not supplied"
    if isinstance(item, bool):
        return "true" if item else "false"
    return str(item)


def value(item):
    # Applied once per displayed cell; host record paths are shown and resolved verbatim.
    return item.path if isinstance(item, RecordReference) else display_text(_plain(item))


def fields(item, prefix=""):
    """Lossless leaf view of semantic objects, with explicit empty/unspecified values."""
    if isinstance(item, RecordReference):
        return [[prefix or "Reference", item]]
    if isinstance(item, dict):
        if not item:
            return [[prefix or "Value", "No entries recorded"]]
        return [row for key, child in sorted(item.items()) for row in fields(
            child, f"{prefix} / {key.replace('_', ' ')}" if prefix else key.replace("_", " "))]
    if isinstance(item, list):
        if not item:
            return [[prefix or "Value", "No entries recorded"]]
        if all(not isinstance(child, (dict, list, RecordReference)) for child in item):
            return [[prefix or "Value", "\n".join(_plain(child) for child in item)]]
        return [row for index, child in enumerate(item, 1)
                for row in fields(child, f"{prefix} / {index}")]
    return [[prefix or "Value", _plain(item)]]


def table(caption, rows, headers=("Field", "Recorded value")):
    references = [{"row": r, "column": c, "path": cell.path,
                   "target_fingerprint": cell.target_fingerprint}
                  for r, row in enumerate(rows) for c, cell in enumerate(row)
                  if isinstance(cell, RecordReference)]
    return {"kind": "table", "caption": display_text(str(caption)), "headers": [display_text(h) for h in headers],
            "rows": [[value(cell) for cell in row] for row in rows], "record_references": references}


def details(caption, item):
    return table(caption, fields(item))


def group(title, blocks, **metadata):
    return (title, {**metadata, "blocks": blocks})


def _model_keys(item, host_keys):
    """Model keys that would display like a host-labelled key keep their value under a marked name."""
    renamed = {}
    for key, child in item.items():
        name = key
        while str(name).replace("_", " ") in host_keys or (name != key and (name in item or name in renamed)):
            name = "model-supplied " + str(name)
        renamed[name] = child
    return renamed


def _propositions(ledger, assessment):
    blocks = [details("Claim composition", {key: ledger.get(key) for key in
              ("claim_id", "provenance_id", "required_proposition_ids", "logic", "extraction_provenance")})]
    states = {p["proposition_id"]: p for p in assessment.get("propositions", [])}
    for number, prop in enumerate(ledger.get("propositions", []), 1):
        pid = prop.get("proposition_id", "unidentified")
        # The host-derived judgment is written last so a model key cannot replace it.
        blocks += [details(f"Proposition {number}", {**_model_keys({
            key: item for key, item in prop.items() if key not in
            {"proposition_text", "original_span", "attributes", "evidence_bindings"}}, {"derived judgment"}),
            "derived judgment": states.get(pid)}),
            text("Quoted proposition; this is represented input, not a release assertion."),
            quote(prop.get("proposition_text", "")), details("Original span", prop.get("original_span")),
            details("Population, endpoint, product and inference attributes", prop.get("attributes", {})),
            details("Evidence bindings and directness", prop.get("evidence_bindings", []))]
    for key in ("bridges", "product_transfers"):
        blocks.append(details(key.replace("_", " ").title(), ledger.get(key, [])))
    compressed = {"from and to text (identical)", "from and to attributes (identical)"}
    for number, transformation in enumerate(ledger.get("transformations", []), 1):
        item = _model_keys(deepcopy(transformation), compressed)
        # Equality compression is purely structural; every distinct value remains visible.
        for suffix in ("text", "attributes"):
            before, after = "from_" + suffix, "to_" + suffix
            if before in item and after in item and item[before] == item[after]:
                item[f"from and to {suffix} (identical)"] = item.pop(before)
                item.pop(after)
        blocks.append(details(f"Transformation {number}", item))
    return blocks


def _evidence(payload, ledger):
    blocks = [text("Quotations are supplied source text. Evidence type, direction and semantic attributes "
                   "are represented extraction; the checks do not authenticate study findings.")]
    profiles = {d.get("evidence_id"): d for d in ledger.get("evidence_descriptions", [])}
    for number, item in enumerate(payload.get("evidence", []), 1):
        eid = item.get("evidence_id", "unidentified")
        blocks += [details(f"Evidence item {number}", {key: val for key, val in item.items()
                                              if key not in {"text", "exact_reference"}})]
        if item.get("text") == item.get("exact_reference"):
            blocks += [text("Evidence text and exact source reference (identical):"), quote(item.get("text", ""))]
        else:
            blocks += [text("Evidence text:"), quote(item.get("text", "")),
                       text("Exact source reference:"), quote(item.get("exact_reference", ""))]
        blocks += [details("Source type, capability and dependence", profiles.get(eid))]
    if not payload.get("evidence"):
        blocks.append(text("No source-bound evidence is available in the selected analysis."))
    return blocks


def _position(position, pointer, selected_id):
    if not isinstance(position, dict):
        return [details("Unvalidated position", {"reference": pointer, "value": position})]
    assessment = position.get("phase8", {})
    identity = {key: position.get(key) for key in
                ("position_id", "case_id", "claim_id", "run_id", "origin", "provider", "model", "raw_sha256")}
    identity.update(selected=position.get("position_id") == selected_id,
                    raw_response_reference=RecordReference.bind(pointer.path + "/agent_result/raw_output",
                                                               position.get("agent_result", {}).get("raw_output")),
                    complete_analysis_reference=pointer,
                    scientific_state=assessment.get("composite_state", "unknown"),
                    technical_status=assessment.get("technical_status", "not_executed"),
                    original_model_label=assessment.get("original_model_label"),
                    derived_taxonomy=assessment.get("derived_label"),
                    taxonomy_status=assessment.get("taxonomy", {}).get("technical_status", "not_executed"))
    blocks = [details("Position " + str(position.get("position_id", "unidentified")), identity)]
    if position.get("position_id") != selected_id:
        blocks.append(details("Position judgments and uncertainty", {key: assessment.get(key) for key in
                              ("propositions", "reasons", "transformation_findings", "limitations")}))
    raw = position.get("agent_result", {})
    blocks.append(details("Captured execution", {key: raw.get(key) for key in
                                               ("parse_ok", "error", "error_type", "finish_reason", "usage")}))
    return blocks


def _history(audit, review, assessment):
    blocks = [details("Current review state", {key: item for key, item in review.items() if key not in
              {"positions", "conflicts", "triggers", "adjudications", "attempts", "final_decision"}})]
    carriers = [("Current revalidated assessment", "record.json#/run_record", review)]
    stored = audit.run_record.get("metadata", {}).get("phase9")
    if stored:
        carriers.append(("Stored metadata carrier", "record.json#/run_record/metadata/phase9", stored))
    for index, result in enumerate(audit.run_record.get("results", [])):
        carrier = result.get("agent_result", {}).get("phase9")
        if carrier:
            carriers.append((f"Stored result carrier {index + 1}",
                             f"record.json#/run_record/results/{index}/agent_result/phase9", carrier))
    def stored_reference(key, item):
        for _, carrier_pointer, stored_carrier in carriers[1:]:
            for index, stored_item in enumerate(stored_carrier.get(key, [])):
                if digest(stored_item) == digest(item):
                    return RecordReference.bind(f"{carrier_pointer}/{key}/{index}", item)
        return None

    def position_reference(position):
        reference = stored_reference("positions", position)
        if reference is not None:
            return reference
        # Initial revalidation can assign run-bound IDs absent from an old cache.
        # Bind the actual result carrier and independently check its raw response.
        if isinstance(position, dict):
            for index, result in enumerate(audit.run_record.get("results", [])):
                if result.get("agent_result", {}).get("raw_output") == position.get("agent_result", {}).get("raw_output"):
                    return RecordReference.bind(f"record.json#/run_record/results/{index}", result)
        raise ValueError("Position has no actual record carrier for its report reference")

    seen_carriers, seen_items = set(), set()
    for label, pointer, carrier in carriers:
        if digest(carrier) in seen_carriers:
            continue
        seen_carriers.add(digest(carrier))
        source_target = audit.run_record if label.startswith("Current") else carrier
        blocks += [details(label, {"source reference": RecordReference.bind(pointer, source_target),
                    "assessment fingerprint": digest(carrier),
                    "interpretation": "Current revalidated state" if label.startswith("Current") else
                    "Preserved carrier; current validation determines status. Stored claims are not approval.",
                    **{key: carrier.get(key) for key in ("route", "technical_status", "history_validation")}})]
        for key in ("positions", "conflicts", "triggers", "adjudications", "attempts"):
            items = carrier.get(key, [])
            for index, item in enumerate(items):
                identity = (key, digest(item))
                if identity in seen_items:
                    continue
                seen_items.add(identity)
                reference = (stored_reference(key, item) if label.startswith("Current") else
                             RecordReference.bind(f"{pointer}/{key}/{index}", item))
                if key == "positions":
                    blocks += _position(item, position_reference(item), audit.selected_position_id)
                else:
                    displayed = deepcopy(item)
                    if isinstance(displayed, dict):
                        # Per-position machine fingerprints remain bound in the full record.
                        fingerprints = displayed.get("position_fingerprints")
                        if fingerprints is not None and reference is not None:
                            displayed.pop("position_fingerprints")
                            displayed["position binding reference"] = RecordReference.bind(
                                reference.path + "/position_fingerprints", fingerprints)
                        displayed["source reference"] = reference or RecordReference.bind(
                            "record.json#/run_record", audit.run_record)
                        if reference is None:
                            displayed["source relationship"] = "Recomputed from source run; no identical stored object"
                        displayed["projected object fingerprint"] = digest(item)
                    blocks.append(details(key.removesuffix("s").title(), displayed))
    if not review.get("conflicts"):
        model_host = assessment.get("model_host_conflicts") or any(
            (p.get("phase8") or {}).get("model_host_conflicts") for p in review.get("positions", []))
        blocks.append(text(
            "Conflicts were not evaluated: the selected analysis is technically incomplete."
            if _not_evaluated(assessment) else
            "No disagreement between positions is recorded. Model/host conflicts are listed under Execution and "
            "release. This is not evidence of scientific truth." if model_host else
            "Current assessment contains no recorded conflicts. This is not evidence of scientific truth."))
    if not review.get("adjudications"):
        blocks.append(text("No adjudication is recorded; absence is not human approval."))
    return blocks


def _not_evaluated(assessment):
    return assessment.get("technical_status") != "completed" and not assessment.get("propositions")


def _conflict_status(assessment, review, selected_id):
    """Plain conflict summary over the selected judgment and the whole review history.

    The effective scientific judgment stays unknown while a conflict in the selected judgment is
    open. Conflicts of other positions are reported separately: closed only by a documented human
    adjudication, never by a model review.
    """
    current = assessment.get("model_host_conflicts") or []
    earlier = sum(len((p.get("phase8") or {}).get("model_host_conflicts") or [])
                  for p in review.get("positions", []) if p.get("position_id") != selected_id)
    if _not_evaluated(assessment) and not earlier:
        return "not evaluated (analysis technically incomplete)"
    if not current and not earlier:
        return "none recorded"
    adjudicated = review.get("review_state") == "adjudicated"
    parts = []
    if _not_evaluated(assessment):
        parts.append("not evaluated (analysis technically incomplete)")
    elif current:
        codes = [t.get("code") for t in review.get("triggers", []) if selected_id in t.get("position_ids", [])]
        # Materiality is read from the recorded triggers; an unmatched conflict counts as material.
        bounded = min(codes.count("bounded_model_host_conflict"), len(current))
        material = len(current) - bounded
        counter = review_attempt_states(review).get("counterreview") or ""
        summary = f"selected judgment: {len(current)} open" + (
            f" ({material} material, {bounded} not material)" if material and bounded else "")
        if material:
            summary += "; " + ("material; case adjudicated by a recorded human decision" if adjudicated else
                               "mandatory review executed, conflict still open, release blocked"
                               if counter == "completed" else
                               "mandatory review executed but failed, release blocked"
                               if counter.startswith("executed but failed") else
                               "mandatory review not executed, release blocked")
        else:
            summary += ("; not material for the composite, a decisive output or the derived label; no review is "
                        f"required under {P9_CONTRACT} (the Phase-8 conflict reason states the rule for material "
                        "conflicts); " + ("case adjudicated, conflict not closed by the adjudication" if adjudicated
                                          else "not reviewed"))
        parts.append(summary)
    else:
        parts.append("selected judgment: none")
    if earlier:
        parts.append(f"other positions: {earlier} " + (
            "(closed by documented human adjudication)" if adjudicated else "(open; see review route)"))
    return "; ".join(parts)


def projection(audit, controls, review, selected, assessment, forensic):
    payload = forensic.model_dump(mode="json") if forensic else {}
    ledger = payload.get("phase8") or {}
    intent = audit.release_intent.model_dump() if audit.release_intent else None
    sentence, cause = automatic_outcome(audit.status, review, assessment, controls, audit.run_record)
    execution = [text(audit.status + " — local artifact status", "status"), text(sentence, "notice"),
                 text(notice_for(audit.execution_mode), "notice"),
                 details("Independent states", {"scientific judgment": assessment.get("composite_state", "unknown"),
                     "model judgment (composite)": assessment.get("model_composite_state"),
                     "host evidence derivation (composite)": assessment.get("host_composite_state"),
                     "model/host conflicts": _conflict_status(assessment, review, audit.selected_position_id),
                     "analysis execution": assessment.get("technical_status", "not_executed"),
                     "review route": review.get("route", "UNRESOLVED"),
                     "review execution": review.get("execution_status", "not_executed"),
                     "mandatory review": review.get("mandatory", True), "local release": audit.status,
                     "automatic processing": "ended", "open cause": cause}),
                 details("Explicit release intent", intent) if intent else text("No host release intent: this is a candidate, not a released artifact."),
                 details("Revision identity", {"revision": audit.revision_id, "created_at": audit.created_at,
                     "parent": audit.parent.model_dump() if audit.parent else None,
                     "record_fingerprint": digest(audit.model_dump()), "selected_position_id": audit.selected_position_id})]
    if audit.execution_mode != "recorded_offline":
        # Current execution and original response origin are reported separately per carrier.
        execution.append(details("Execution provenance per carrier", audit.provenance.get("execution_evidence", [])))
    scientific = [details("Selected scientific assessment", {key: item for key, item in assessment.items()
                  if key not in {"phase7_controls", "taxonomy", "canonical_proposition_ids", "propositions"}}),
                  text(REASONS_NOTE), details("Proposition judgments", assessment.get("propositions", []))]
    scope = [text("External search executed: false. Scope is limited to the captured supplied material; "
                  "no evidence found does not mean no evidence exists."),
             details("Declared search scopes", payload.get("search_scopes", [])),
             details("Bound negative assertions", payload.get("negative_assertions", [])),
             text("Captured context (source_id: context):"), quote(audit.run_record["task"].get("context", ""))]
    control_blocks = [table("Executed controls", [[c.control_id + " / " + c.version,
                      f"Execution: {c.execution}\nOutcome: {c.outcome}\nEligible: {c.eligible}\n"
                      f"Evaluated: {c.evaluated}\nReason: {c.reason}"] for c in controls],
                      ("Control and version", "Execution, population and result"))]
    for item in controls:
        if item.findings:
            control_blocks.append(details("Findings: " + item.control_id, item.findings))
    control_blocks += [text("Final Markdown and HTML file checks read these actual files before promotion. "
                           "Their results and exact hashes are bound in decision.json; this report does not self-certify its bytes."),
                       table("Post-render control references", [[name, "decision.json#/controls", "Actual rendered bytes"]
                             for name in ("markdown_qa", "html_qa")], ("Control", "Result reference", "Population"))]
    provenance = deepcopy(audit.provenance)
    code = provenance.get("code", {})
    hashes = code.pop("module_hashes", {})
    code["module_count"] = len(hashes)
    code["complete_module_hash_index"] = "manifest.json#/provenance/code/module_hashes"
    return [
        group(TITLES[0], execution, status=audit.status),
        group(TITLES[1], [text("Verbatim quoted input; foreign text is not a trusted status message."),
                          quote(audit.run_record["task"]["prompt"])]),
        group(TITLES[2], scientific),
        group(TITLES[3], [details("Original versus derived classification", {
              "original_model_label": assessment.get("original_model_label"), "derived_taxonomy": assessment.get("derived_label"),
              "taxonomy_check": assessment.get("taxonomy"), "represented_trigger_analysis": payload.get("phase8_taxonomy")})]),
        group(TITLES[4], _propositions(ledger, assessment)),
        group(TITLES[5], _evidence(payload, ledger)),
        group(TITLES[6], scope),
        group(TITLES[7], [details(key.replace("_", " ").title(), payload.get(key, []))
                          for key in ("provenance", "findings", "client_findings")]),
        group(TITLES[8], _history(audit, review, assessment)),
        group(TITLES[9], control_blocks),
        group(TITLES[10], [text(LIMITS), text(DISPLAY_NOTE), text("Not supplied and No entries recorded describe missing fields, "
              "not proof of absence or not-applicability. Confidence cannot override missing mandatory evidence."),
              details("Assessment limitations", assessment.get("limitations", []))]),
        group(TITLES[11], [details("Material provenance", provenance), text(
              "Complete original responses, all review carriers and machine bindings: record.json. "
              "Final control decision: decision.json. File hashes and full source index: manifest.json. "
              "Hashes verify integrity, not actor identity or authentication.")]),
    ]
