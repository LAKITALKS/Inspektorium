"""Known mandatory regression left open at the user-defined WP9.2 review limit.

Do not xfail or change the expectation: a new bounded work order must fix the
human-import carrier check before Phase9 can be accepted.
"""
from inspektorium.audit.evaluator import evaluate_run
from inspektorium.audit.phase9_runtime import OfflineReviewProvider, execute_review, submit_human_review
from inspektorium.audit.runner import run_agent
from tests.unit.test_phase9_runtime import fixture


def test_human_import_without_sidecar_must_not_discard_newer_agent_result_history(tmp_path):
    task, supported = fixture("supported")
    _, contradicted = fixture("contradicted")
    _, unknown = fixture("unknown")
    original = evaluate_run(task, "competing-originals", [
        run_agent(OfflineReviewProvider(supported), task),
        run_agent(OfflineReviewProvider(contradicted), task),
    ])
    reviewed = execute_review(original, OfflineReviewProvider(unknown), base_dir=tmp_path / "source",
                              authorized=True, budget_calls=1)
    assert len(reviewed.metadata["phase9"]["positions"]) == 3
    assert len(reviewed.metadata["phase9"]["adjudications"]) == 1
    # Two actually supported persistence carriers, saved at different points in time.
    incoming = reviewed.model_copy(update={"metadata": original.metadata})
    try:
        outcome = submit_human_review(
            incoming, base_dir=tmp_path / "fresh-import",
            selected_position_id=original.metadata["phase9"]["positions"][0]["position_id"],
            reviewer_provenance="Explicit offline host fixture", reason="Consider all competing positions",
        )
    except ValueError:
        return  # Explicit rejection leaves both submitted histories intact and is permitted.
    data = outcome.metadata["phase9"]
    assert len(data["positions"]) == 3, "Human import discarded the newer counterreview position"
    assert sum(d["reviewer_type"] == "model" for d in data["adjudications"]) == 1
