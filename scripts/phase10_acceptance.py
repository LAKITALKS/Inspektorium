"""Frozen offline acceptance, separate from development tests and efficacy holdout.

Run with the installed package: python scripts/phase10_acceptance.py --output DIR.
No developer source path is added. Expectations and example bytes must match the
versioned input manifest. Each result includes its actual observations.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import traceback
from unittest.mock import patch

from inspektorium.audit import artifact_binding
from inspektorium.audit.evaluator import evaluate_run
from inspektorium.audit.phase10_bundle import (
    create_candidate, inspect_bundle, release_candidate, review_candidate, run_audit,
)
from inspektorium.audit.phase10_pipeline import canonical, digest
from inspektorium.audit.phase9_review import case_key
from inspektorium.audit.phase9_runtime import (
    OfflineReviewProvider, execute_review, replay_review, submit_human_review,
)
from inspektorium.audit.runner import run_agent
from inspektorium.audit.schemas import RunRecord, Task

HARNESS_VERSION = "AA-P10-HARNESS/1.1"


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    expectation_path = args.repo / "tests/fixtures/audit/phase10/acceptance_v1.json"
    frozen = json.loads(expectation_path.read_text())
    for path, expected in frozen["input_sha256"].items():
        assert hashlib.sha256((args.repo / path).read_bytes()).hexdigest() == expected, path
    expectations = {c["id"]: {k: v for k, v in c.items() if k != "id"}
                    for c in frozen["cases"]}
    results = []

    def sample(name="positive", task_name=None):
        root = args.repo / "examples/audit"
        task = Task.model_validate_json((root / f"{task_name or name}-task.json").read_text())
        return task, (root / f"{name}-recording.json").read_text()

    def fresh(name="positive", task_name=None):
        task, raw = sample(name, task_name)
        return evaluate_run(task, "acceptance-" + name,
                            [run_agent(OfflineReviewProvider(raw), task)])

    def root(case):
        path = output / case
        path.mkdir()
        return path

    def released(result):
        return result.status == "RELEASED" and bool(result.path) and inspect_bundle(
            Path(result.path)).valid

    def release(path, target):
        return release_candidate(Path(path), output_root=target,
                                 reviewer="Offline acceptance fixture operator",
                                 reason="Explicit synthetic local test artifact release")

    def record_at(path):
        return RunRecord.model_validate(json.loads((Path(path) / "record.json").read_text())["run_record"])

    def scientific(path):
        from inspektorium.audit.phase10_pipeline import reconstruct
        return reconstruct(record_at(path))[2]["composite_state"]

    def run_case(case, function):
        try:
            actual = function(root(case))
            ok = all(actual.get(k) == value for k, value in expectations[case].items())
            results.append({"id": case, "passed": ok, "expected": expectations[case], "actual": actual})
        except Exception:
            results.append({"id": case, "passed": False, "error": traceback.format_exc()})
        print(case, "PASS" if results[-1]["passed"] else "FAIL", flush=True)

    def complete(target, name):
        task, raw = sample(name)
        provider = OfflineReviewProvider(raw)
        candidate = run_audit(task, provider, output_root=target)
        assert candidate.path, candidate
        final = release(candidate.path, target)
        return {"released": released(final), "scientific": scientific(final.path),
                "provider_calls": len(provider.requests), "candidate": candidate.path,
                "bundle": final.path}

    for name in ("positive", "negative"):
        run_case(name + "_full_path", lambda target, name=name: complete(target, name))

    def unknown(target):
        task, raw = sample("unknown")
        candidate = run_audit(task, OfflineReviewProvider(raw), output_root=target)
        data = record_at(candidate.path)
        return {"released": released(release(candidate.path, target)),
                "scientific": scientific(candidate.path),
                "mandatory_review": data.metadata["phase9"]["mandatory"],
                "bundle": candidate.path}

    run_case("material_unknown", unknown)

    def optional_unknown(target):
        task, raw = sample("optional-unknown", "positive")
        candidate = run_audit(task, OfflineReviewProvider(raw), output_root=target)
        final = release(candidate.path, target)
        review = record_at(final.path).metadata["phase9"]
        report = (Path(final.path) / "report.md").read_text()
        return {"released": released(final), "unknown_visible":
                "Optional contextual interpretation remains unresolved." in report,
                "mandatory_review": review["mandatory"], "bundle": final.path}

    run_case("optional_unknown", optional_unknown)

    def corrupt_input(target, kind):
        task, raw = sample()
        payload = json.loads(raw)
        if kind == "empty":
            payload["forensic_record"]["client_findings"] = []
        else:
            payload["forensic_record"]["evidence"][0]["exact_reference"] = "Invented source quotation"
        candidate = run_audit(task, OfflineReviewProvider(json.dumps(payload)), output_root=target)
        final = release(candidate.path, target) if candidate.path else candidate
        return {"released": released(final), "status": candidate.status}

    run_case("empty_trace_population", lambda target: corrupt_input(target, "empty"))
    run_case("phase8_source_failure", lambda target: corrupt_input(target, "source"))

    def reseal(path):
        manifest = json.loads((path / "manifest.json").read_text())
        manifest["files"] = {name: digest((path / name).read_bytes()) for name in manifest["files"]}
        manifest.pop("fingerprint")
        manifest["fingerprint"] = digest(manifest)
        (path / "manifest.json").write_bytes(canonical(manifest))

    def decision_corrupt(target, stale):
        candidate = create_candidate(fresh(), output_root=target)
        path = Path(candidate.path)
        decision = json.loads((path / "decision.json").read_text())
        if stale:
            decision["controls"][0]["version"] = "obsolete-version"
        else:
            decision["controls"] = decision["controls"][1:]
        (path / "decision.json").write_bytes(canonical(decision))
        reseal(path)  # Checks must fail even if an attacker recomputes ordinary hashes.
        check = inspect_bundle(path)
        return {"released": released(release(path, target)), "valid": check.valid,
                "errors": check.errors}

    run_case("missing_control", lambda target: decision_corrupt(target, False))
    run_case("stale_control", lambda target: decision_corrupt(target, True))

    def bypass(target):
        with patch.object(artifact_binding, "MANDATORY_PHASE7B_GATE_SPECS",
                          artifact_binding.MANDATORY_PHASE7B_GATE_SPECS[:-1]):
            candidate = create_candidate(fresh(), output_root=target)
            final = release(candidate.path, target) if candidate.path else candidate
        return {"released": released(final), "status": final.status}

    run_case("gate_registry_bypass", bypass)

    def tamper(target, kind):
        candidate = create_candidate(fresh(), output_root=target)
        path = Path(candidate.path)
        if kind == "foreign":
            record = json.loads((path / "record.json").read_text())
            record["run_record"]["task"]["id"] = "foreign-case"
            (path / "record.json").write_bytes(canonical(record))
            reseal(path)
        elif kind == "report":
            (path / "report.html").write_text("<h1>RELEASED</h1><p>All claims true</p>")
            reseal(path)
        elif kind == "manifest":
            manifest = json.loads((path / "manifest.json").read_text())
            manifest["provenance"]["case_id"] = "foreign-case"
            (path / "manifest.json").write_bytes(canonical(manifest))
            reseal(path)
        else:
            (path / "report.md").unlink()
        checked = inspect_bundle(path)
        return {"valid": checked.valid, "errors": checked.errors}

    for case, kind in (("foreign_case", "foreign"), ("modified_report", "report"),
                       ("modified_manifest", "manifest"), ("missing_format", "missing")):
        run_case(case, lambda target, kind=kind: tamper(target, kind))

    def human_import(target):
        task, raw = sample()
        _, contrary = sample("conflict", "positive")
        record = evaluate_run(task, "acceptance-conflict", [
            run_agent(OfflineReviewProvider(raw), task),
            run_agent(OfflineReviewProvider(contrary), task)])
        _, unresolved = sample("unknown")
        reviewed = execute_review(record, OfflineReviewProvider(unresolved),
                                  base_dir=target / "source", authorized=True, budget_calls=1)
        incoming = reviewed.model_copy(update={"metadata": deepcopy(record.metadata)})
        before = incoming.model_dump(mode="json")
        selected = record.metadata["phase9"]["positions"][0]["position_id"]
        destination = target / "rejected-import"
        try:
            result = submit_human_review(incoming, base_dir=destination,
                                         selected_position_id=selected,
                                         reviewer_provenance="Offline human import control",
                                         reason="Preserve every review carrier")
            data = result.metadata["phase9"]
            loss = len(data["positions"]) < len(reviewed.metadata["phase9"]["positions"])
            loss |= not all(x in data["adjudications"] for x in reviewed.metadata["phase9"]["adjudications"])
        except ValueError:
            loss = incoming.model_dump(mode="json") != before
            loss |= destination.exists() and any(destination.rglob("*.json"))
        valid = submit_human_review(reviewed, base_dir=target / "source",
                                    selected_position_id=selected,
                                    reviewer_provenance="Offline human import control",
                                    reason="Select a bound position retaining all history")
        candidate = create_candidate(valid, output_root=target)
        return {"silent_loss": bool(loss), "accepted_consistent_control":
                candidate.status == "READY_FOR_RELEASE", "bundle": candidate.path}

    run_case("human_import_history", human_import)

    def durable(target):
        record = fresh("unknown")
        _, raw = sample("unknown")
        provider = OfflineReviewProvider(raw)
        first = execute_review(record, provider, base_dir=target, authorized=True, budget_calls=2)
        rejected = execute_review(first, provider, base_dir=target, authorized=True, budget_calls=2,
                                  kind="stability", variant={"original_claim": "changed"})
        receipt = deepcopy(rejected.metadata["phase9"]["attempts"][-1])
        sidecar = target / "phase9" / (case_key(record.task) + ".json")
        sidecar.unlink()
        before = len(provider.requests)
        recovered = execute_review(first, provider, base_dir=target, authorized=True,
                                   budget_calls=2, kind="stability")
        assert recovered.metadata["phase9"]["attempts"][-1] == receipt
        replay = replay_review(record.task, base_dir=target)
        assert replay.metadata["phase9"]["attempts"] == recovered.metadata["phase9"]["attempts"]
        rejected_extra = len(provider.requests) - before
        # Paired usable control: execute both admissible variants, then reopen
        # each consumed choice. This prevents a blanket-rejection interpretation.
        payload = json.loads(raw)
        forensic = payload["forensic_record"]
        evidence = deepcopy(forensic["evidence"][0])
        evidence["evidence_id"] = "e2"
        forensic["evidence"].append(evidence)
        description = deepcopy(forensic["phase8"]["evidence_descriptions"][0])
        description["evidence_id"] = "e2"
        forensic["phase8"]["evidence_descriptions"].append(description)
        binding = deepcopy(forensic["phase8"]["propositions"][0]["evidence_bindings"][0])
        binding.update(binding_id="b2", evidence_id="e2")
        forensic["phase8"]["propositions"][0]["evidence_bindings"].append(binding)
        forensic["findings"][0]["supporting_evidence_ids"].append("e2")
        forensic["client_findings"][0]["referenced_evidence_ids"].append("e2")
        paired_raw = json.dumps(payload)
        paired_record = evaluate_run(record.task, "acceptance-two-variants", [
            run_agent(OfflineReviewProvider(paired_raw), record.task)])
        paired_provider = OfflineReviewProvider(paired_raw)
        state = target / "two-valid-variants"
        first_valid = execute_review(paired_record, paired_provider, base_dir=state,
                                     authorized=True, budget_calls=2)
        execute_review(first_valid, paired_provider, base_dir=state,
                       authorized=True, budget_calls=2, kind="stability")
        assert len(paired_provider.requests) == 2
        for kind in ("counterreview", "stability"):
            execute_review(paired_record, paired_provider, base_dir=state,
                           authorized=True, budget_calls=2, kind=kind)
        return {"additional_calls_after_reopen": rejected_extra + len(paired_provider.requests) - 2,
                "recorded_calls_before_reopen": before, "valid_variants_executed": 2,
                "durable_rejection": receipt}

    run_case("durable_variant_limit", durable)

    def long_render(target):
        task, raw = sample("long-hostile")
        candidate = run_audit(task, OfflineReviewProvider(raw), output_root=target)
        checked = inspect_bundle(Path(candidate.path))
        md = (Path(candidate.path) / "report.md").read_text()
        html = (Path(candidate.path) / "report.html").read_text()
        from html import unescape
        decoded = unescape(html)
        complete = all(value in unescape(md) and value in decoded for value in (
            "END_LONG_REASON.", "END_IDENTIFIER.", "e7", "Recorded source 7", "Café"))
        return {"complete": complete, "active_content": "<img src=x" in html,
                "parity": checked.valid, "bundle": candidate.path}

    run_case("long_hostile_render", long_render)

    # Renderer fault injection is applied to the actual boundary serializer,
    # not a fabricated QA return value. Bound bytes must be inspected afresh.
    def malformed(target):
        from inspektorium.audit import phase10_render
        with patch.object(phase10_render, "html_report", return_value=b"<html>truncated</html>"):
            candidate = create_candidate(fresh(), output_root=target)
            final = release(candidate.path, target) if candidate.path else candidate
        return {"released": released(final), "status": final.status}

    run_case("malformed_render", malformed)

    def inspect_replay(target):
        task, raw = sample()
        provider = OfflineReviewProvider(raw)
        candidate = run_audit(task, provider, output_root=target)
        path = Path(candidate.path)
        before = {p.name: p.read_bytes() for p in path.iterdir()}
        count = len(provider.requests)
        for _ in range(2):
            assert inspect_bundle(path).valid
        rerender = create_candidate(record_at(path), output_root=target)
        assert inspect_bundle(Path(rerender.path)).valid
        return {"additional_calls": len(provider.requests) - count,
                "history_unchanged": all((path / name).read_bytes() == value for name, value in before.items())}

    run_case("inspect_replay", inspect_replay)

    def isolated(target):
        class PretendOffline(OfflineReviewProvider):
            def send_prompt(self, *args, **kwargs):
                self.requests.append("FORBIDDEN")
                raise AssertionError("A live-like provider crossed the offline boundary")
        task, raw = sample()
        provider = PretendOffline(raw)
        result = run_audit(task, provider, output_root=target)
        return {"provider_calls": len(provider.requests), "released": released(result),
                "status": result.status}

    run_case("offline_provider_isolation", isolated)

    def human_revision(target):
        task, raw = sample("unknown")
        candidate = run_audit(task, OfflineReviewProvider(raw), output_root=target)
        path = Path(candidate.path)
        before = {p.name: p.read_bytes() for p in path.iterdir()}
        record = record_at(path)
        selected = record.metadata["phase9"]["positions"][0]["position_id"]
        _, correction = sample()
        revision = review_candidate(path, output_root=target, state_dir=target / "human-state",
                                    selected_position_id=selected,
                                    reviewer="Explicit offline acceptance adjudicator",
                                    reason="Bound correction resolves study design from supplied source",
                                    corrected_raw_output=correction)
        final = release(revision.path, target)
        return {"released": released(final),
                "history_unchanged": all((path / name).read_bytes() == data for name, data in before.items()),
                "new_revision": final.path != candidate.path, "bundle": final.path}

    run_case("explicit_human_revision", human_revision)

    def invalid(target):
        task, raw = sample()
        task = task.model_copy(update={"prompt": ""})
        provider = OfflineReviewProvider(raw)
        result = run_audit(task, provider, output_root=target)
        return {"provider_calls": len(provider.requests), "released": released(result),
                "status": result.status}

    run_case("invalid_input", invalid)
    assert {r["id"] for r in results} == set(expectations)
    report = {"version": frozen["version"], "harness_version": HARNESS_VERSION,
              "contract": frozen["contract"],
              "expectations_sha256": hashlib.sha256(expectation_path.read_bytes()).hexdigest(),
              "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "passed": sum(r["passed"] for r in results), "total": len(results), "results": results}
    (output / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"{report['passed']}/{report['total']} passed")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
