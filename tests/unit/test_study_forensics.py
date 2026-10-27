"""Tests for study forensics integration — agent-arena v0.6 pilot."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from inspektorium.audit.schemas import (
    AgentResponse,
    AgentResult,
    Difficulty,
    ExpectedFinding,
    EvaluatedResult,
    GoldEvidenceSpan,
    Task,
    TaskType,
)
from inspektorium.audit.task_loader import load_task
from inspektorium.audit.study_forensics_checker import (
    is_study_forensics_task,
    run_study_forensics_checks,
    _detect_label,
    _detect_findings,
    _detect_false_positives,
    _detect_hedge_overclaim,
    _is_negated,
    _keyword_match_non_negated,
)
from inspektorium.audit.evaluator import evaluate_result
from inspektorium.audit.reporter import generate_report
from inspektorium.audit.runner import (
    _select_system_prompt, STUDY_FORENSICS_PROMPT, STUDY_FORENSICS_PROMPT_PHASE8,
    STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL, SYSTEM_PROMPT,
)

TASK_DIR = Path("tests/fixtures/audit/case_library")
PILOT_RESPONSE_FIXTURE = Path(
    "tests/fixtures/audit/synthetic_study_forensics_pilot_responses.json"
)
PILOT_IDS = (
    "study-forensics-001",
    "study-forensics-004",
    "study-forensics-007",
    "study-forensics-009",
    "study-forensics-013",
    "study-forensics-019",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def task_files():
    """All study forensics task YAML files."""
    return sorted(TASK_DIR.glob("*.yaml"))


@pytest.fixture
def all_tasks(task_files):
    """Load all study forensics tasks."""
    return [load_task(p) for p in task_files]


def _make_task(gold_label: str, expected_findings: list[dict] | None = None) -> Task:
    """Helper to build a minimal study forensics task."""
    findings = [ExpectedFinding(**ef) for ef in (expected_findings or [])]
    return Task(
        id=f"test-sf-{gold_label}",
        title=f"Test {gold_label}",
        domain="study_forensics",
        difficulty=Difficulty.MEDIUM,
        task_type=TaskType.STUDY_FORENSICS,
        prompt="Test prompt.",
        expected_answer=gold_label,
        gold_label=gold_label,
        expected_findings=findings,
    )


def _make_response(**kwargs) -> AgentResponse:
    """Helper to build an AgentResponse."""
    defaults = {
        "final_answer": "",
        "assumptions": [],
        "steps": [],
        "alternative_hypotheses": [],
        "uncertainties": [],
        "key_claims": [],
        "self_check": [],
        "confidence": 0.8,
    }
    defaults.update(kwargs)
    return AgentResponse(**defaults)


def _make_agent_result(parsed: AgentResponse) -> AgentResult:
    return AgentResult(
        provider="test",
        model="test-model",
        raw_output=json.dumps({"final_answer": parsed.final_answer}),
        parsed=parsed,
        parse_ok=True,
        latency_ms=0,
    )


# ---------------------------------------------------------------------------
# 1. Task loading tests
# ---------------------------------------------------------------------------

class TestTaskLoading:
    """Verify all study forensics task files load correctly."""

    def test_task_files_exist(self, task_files):
        assert len(task_files) == 50, f"Expected 50 task files, got {len(task_files)}"

    def test_all_tasks_load(self, all_tasks):
        assert len(all_tasks) == 50
        for task in all_tasks:
            assert task.task_type == TaskType.STUDY_FORENSICS

    def test_task_ids_unique(self, all_tasks):
        ids = [t.id for t in all_tasks]
        assert len(ids) == len(set(ids))

    def test_gold_labels_present(self, all_tasks):
        for task in all_tasks:
            assert task.gold_label is not None
            assert task.gold_label in ("solid", "overclaim", "mechanism_vs_evidence", "correlation_vs_causation")

    def test_expected_findings_present(self, all_tasks):
        for task in all_tasks:
            assert len(task.expected_findings) > 0, f"{task.id} has no expected findings"

    def test_expected_findings_valid(self, all_tasks):
        for task in all_tasks:
            for ef in task.expected_findings:
                assert ef.finding, f"{task.id}: empty finding name"
                assert ef.severity in ("minor", "moderate", "major")
                assert ef.confidence in ("low", "medium", "high")

    def test_gold_evidence_spans_present(self, all_tasks):
        for task in all_tasks:
            assert len(task.gold_evidence_spans) > 0, f"{task.id} has no gold evidence spans"

    def test_gold_evidence_spans_valid(self, all_tasks):
        for task in all_tasks:
            for ges in task.gold_evidence_spans:
                assert ges.span, f"{task.id}: empty evidence span"
                assert ges.supports_finding, f"{task.id}: span missing supports_finding"

    def test_prompts_clean(self, all_tasks):
        """Verify no contentReference artifacts in prompts."""
        for task in all_tasks:
            assert "contentReference" not in task.prompt, f"{task.id}: found contentReference in prompt"

    def test_expected_answer_matches_gold_label(self, all_tasks):
        for task in all_tasks:
            assert task.expected_answer == task.gold_label

    def test_task_families_match_gold_labels(self, all_tasks):
        for task in all_tasks:
            assert task.task_family == task.gold_label, f"{task.id}: task_family != gold_label"

    def test_yaml_roundtrip(self, task_files):
        """Verify YAML files parse correctly as raw dicts too."""
        for tf in task_files:
            with open(tf) as f:
                data = yaml.safe_load(f)
            assert "id" in data
            assert "gold_label" in data
            assert "expected_findings" in data


# ---------------------------------------------------------------------------
# 2. Schema tests
# ---------------------------------------------------------------------------

class TestSchemas:
    def test_task_type_study_forensics(self):
        assert TaskType.STUDY_FORENSICS.value == "study_forensics"

    def test_expected_finding_model(self):
        ef = ExpectedFinding(finding="test", severity="minor", confidence="high")
        assert ef.finding == "test"

    def test_gold_evidence_span_model(self):
        ges = GoldEvidenceSpan(span="text", why_it_matters="reason", supports_finding="test")
        assert ges.span == "text"

    def test_task_with_study_forensics_fields(self):
        task = _make_task("solid", [{"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"}])
        assert task.gold_label == "solid"
        assert len(task.expected_findings) == 1


# ---------------------------------------------------------------------------
# 3. Checker unit tests
# ---------------------------------------------------------------------------

class TestStudyForensicsChecker:
    def test_is_study_forensics_task(self):
        task = _make_task("solid")
        assert is_study_forensics_task(task)

    def test_is_not_study_forensics_task(self):
        task = Task(
            id="test", title="Test", domain="math",
            difficulty=Difficulty.MEDIUM,
            task_type=TaskType.CLOSED_WITH_REASONING,
            prompt="test",
        )
        assert not is_study_forensics_task(task)

    def test_detect_label_solid(self):
        p = _make_response(final_answer="This is a solid study with no major issues.")
        assert _detect_label(p) == "solid"

    def test_detect_label_overclaim(self):
        p = _make_response(final_answer="This is an overclaim. The conclusion is overstated.")
        assert _detect_label(p) == "overclaim"

    def test_detect_label_mechanism_vs_evidence(self):
        p = _make_response(
            final_answer="This is mechanism_vs_evidence. The mechanism is only shown in animal models.",
            key_claims=["mechanism not demonstrated in humans", "preclinical only"],
        )
        assert _detect_label(p) == "mechanism_vs_evidence"

    def test_detect_label_correlation(self):
        p = _make_response(final_answer="Correlation is treated as causation. Cross-sectional data cannot prove cause.")
        assert _detect_label(p) == "correlation_vs_causation"

    def test_detect_findings_evidence_matches(self):
        p = _make_response(steps=["The evidence supports the claim made."])
        findings = _detect_findings(p)
        assert "evidence_matches_claim" in findings

    def test_detect_findings_overclaim(self):
        p = _make_response(steps=["The conclusion exceeds the results. This is overstated."])
        findings = _detect_findings(p)
        assert "conclusion_exceeds_results" in findings

    def test_detect_findings_correlation(self):
        p = _make_response(steps=["This is correlation treated as causation. Confounders present."])
        findings = _detect_findings(p)
        assert "correlation_as_causation" in findings

    def test_detect_findings_mechanism(self):
        p = _make_response(steps=["The mechanism is not demonstrated in humans. Only mice studied."])
        findings = _detect_findings(p)
        assert "mechanism_not_demonstrated" in findings

    def test_detect_findings_decorative(self):
        p = _make_response(steps=["The uncertainty language is decorative. Token caveat only."])
        findings = _detect_findings(p)
        assert "decorative_uncertainty" in findings

    def test_false_positives_in_solid(self):
        p = _make_response(
            final_answer="This is overclaim! Major flaw detected!",
            key_claims=["This study commits fraud"],
        )
        fp = _detect_false_positives(p)
        assert len(fp) > 0

    def test_no_false_positives_in_clean_solid(self):
        p = _make_response(
            final_answer="This is a solid study with no major issues.",
            key_claims=["Evidence matches claim"],
        )
        fp = _detect_false_positives(p)
        assert len(fp) == 0

    def test_full_check_solid_correct(self):
        task = _make_task("solid", [
            {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
            {"finding": "none_or_minor", "severity": "minor", "confidence": "high"},
        ])
        p = _make_response(
            final_answer="This is a solid, well-designed study. No major issues.",
            steps=["The evidence supports the claim."],
        )
        result = run_study_forensics_checks(task, p)
        assert result["is_study_forensics"]
        assert result["label_correct"]
        assert result["finding_recall"] > 0

    def test_full_check_solid_incorrect(self):
        task = _make_task("solid", [
            {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
        ])
        p = _make_response(
            final_answer="This is a clear overclaim case.",
        )
        result = run_study_forensics_checks(task, p)
        assert result["is_study_forensics"]
        assert not result["label_correct"]
        assert len(result["false_positives"]) > 0

    def test_full_check_overclaim(self):
        task = _make_task("overclaim", [
            {"finding": "conclusion_exceeds_results", "severity": "moderate", "confidence": "medium"},
        ])
        p = _make_response(
            final_answer="This is overclaim. The conclusion is overstated and goes beyond the data.",
            steps=["The conclusion exceeds what the results show."],
        )
        result = run_study_forensics_checks(task, p)
        assert result["label_correct"]
        assert "conclusion_exceeds_results" in result["matched_findings"]

    def test_non_study_forensics_returns_early(self):
        task = Task(
            id="test", title="Test", domain="math",
            difficulty=Difficulty.MEDIUM,
            task_type=TaskType.CLOSED_WITH_REASONING,
            prompt="test",
        )
        p = _make_response(final_answer="42")
        result = run_study_forensics_checks(task, p)
        assert not result["is_study_forensics"]


# ---------------------------------------------------------------------------
# 4. Evaluator integration tests
# ---------------------------------------------------------------------------

class TestEvaluatorIntegration:
    def test_evaluate_study_forensics_task(self):
        task = _make_task("overclaim", [
            {"finding": "conclusion_exceeds_results", "severity": "moderate", "confidence": "medium"},
        ])
        p = _make_response(
            final_answer="This is overclaim. The conclusion exceeds the results.",
            steps=["The study overstates its findings."],
            key_claims=["overclaim detected"],
        )
        result = _make_agent_result(p)
        evaluated = evaluate_result(task, result)

        assert isinstance(evaluated, EvaluatedResult)
        assert evaluated.study_forensics.get("is_study_forensics")
        assert evaluated.study_forensics.get("label_correct")

    def test_evaluate_solid_no_false_alarm(self):
        task = _make_task("solid", [
            {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
        ])
        p = _make_response(
            final_answer="This is a solid, well-designed study with no major problems.",
            steps=["The evidence supports the claim. Appropriate caveats present."],
            key_claims=["solid study"],
        )
        result = _make_agent_result(p)
        evaluated = evaluate_result(task, result)
        sf = evaluated.study_forensics

        assert sf.get("label_correct")
        assert sf.get("false_positives") == []

    def test_study_forensics_field_in_evaluated_result(self):
        task = _make_task("solid")
        p = _make_response(final_answer="solid study")
        result = _make_agent_result(p)
        evaluated = evaluate_result(task, result)
        assert "study_forensics" in evaluated.model_dump()


# ---------------------------------------------------------------------------
# 5. Reporter integration tests
# ---------------------------------------------------------------------------

class TestReporterIntegration:
    def test_report_generation_no_crash(self, all_tasks):
        """Ensure report generation doesn't crash for any study forensics task."""
        for task in all_tasks:
            p = _make_response(
                final_answer=f"This is {task.gold_label}.",
                steps=["Analysis step."],
            )
            result = _make_agent_result(p)
            from inspektorium.audit.evaluator import evaluate_run
            record = evaluate_run(task, "test-run", [result])
            report = generate_report(record)
            assert len(report) > 0
            assert "Forensic Dossier" in report

    def test_report_contains_study_forensics_section(self):
        task = _make_task("overclaim", [
            {"finding": "conclusion_exceeds_results", "severity": "moderate", "confidence": "medium"},
        ])
        p = _make_response(
            final_answer="This is overclaim. The conclusion exceeds the results.",
            steps=["Overstated conclusion."],
        )
        result = _make_agent_result(p)
        from inspektorium.audit.evaluator import evaluate_run
        record = evaluate_run(task, "test-run", [result])
        report = generate_report(record)
        assert "Study Forensics Audit" in report


# ---------------------------------------------------------------------------
# 6. Runner tests
# ---------------------------------------------------------------------------

class TestRunner:
    def test_select_system_prompt_study_forensics(self):
        task = _make_task("solid")
        prompt = _select_system_prompt(task)
        assert prompt == STUDY_FORENSICS_PROMPT_PHASE8
        assert _select_system_prompt(task, STUDY_FORENSICS_PROMPT_VERSION_HISTORICAL) == STUDY_FORENSICS_PROMPT

    def test_select_system_prompt_normal(self):
        task = Task(
            id="test", title="Test", domain="math",
            difficulty=Difficulty.MEDIUM,
            task_type=TaskType.CLOSED_WITH_REASONING,
            prompt="test",
        )
        prompt = _select_system_prompt(task)
        assert prompt == SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# 7. Pilot run smoke test
# ---------------------------------------------------------------------------

class TestPilotRun:
    def test_pilot_synthetic_responses_cover_pilot_tasks(self):
        """The tracked QA-only response fixture covers the six historical pilot tasks."""
        fixture = json.loads(PILOT_RESPONSE_FIXTURE.read_text())
        assert fixture["synthetic"] is True
        assert fixture["fixture_role"] == "pipeline_qa_regression_only"
        assert set(fixture["responses"]) == set(PILOT_IDS)

    def test_pilot_end_to_end(self, tmp_path):
        """Run six tracked synthetic responses through evaluation and report generation."""
        from inspektorium.audit.evaluator import evaluate_run

        fixture = json.loads(PILOT_RESPONSE_FIXTURE.read_text())["responses"]
        runs_dir = tmp_path / "runs"
        reports_dir = tmp_path / "reports"
        runs_dir.mkdir()
        reports_dir.mkdir()
        task_paths = {load_task(path).id: path for path in sorted(TASK_DIR.glob("*.yaml"))}
        for task_id in PILOT_IDS:
            task = load_task(task_paths[task_id])
            parsed = AgentResponse(**fixture[task_id])
            result = AgentResult(
                provider="synthetic-qa",
                model="synthetic-qa-v1",
                raw_output=json.dumps(fixture[task_id]),
                parsed=parsed,
                parse_ok=True,
            )
            record = evaluate_run(task, f"qa-{task_id}", [result])
            (runs_dir / f"{task_id}.json").write_text(record.model_dump_json(indent=2))
            (reports_dir / f"{task_id}.md").write_text(generate_report(record))

        runs = list(runs_dir.glob("*.json"))
        reports = list(reports_dir.glob("*.md"))

        assert len(runs) == len(PILOT_IDS)
        assert len(reports) == len(PILOT_IDS)

        # Verify all runs parse back
        for rp in runs:
            data = json.loads(rp.read_text())
            assert "run_id" in data
            assert "results" in data


# ---------------------------------------------------------------------------
# 8. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_response(self):
        task = _make_task("solid")
        p = _make_response()
        result = run_study_forensics_checks(task, p)
        assert result["is_study_forensics"]

    def test_unparsed_result(self):
        task = _make_task("solid")
        result = AgentResult(provider="test", model="test")
        evaluated = evaluate_result(task, result)
        assert isinstance(evaluated, EvaluatedResult)

    def test_task_with_no_expected_findings(self):
        task = _make_task("solid", [])
        p = _make_response(final_answer="solid study")
        result = run_study_forensics_checks(task, p)
        assert result["finding_recall"] == 1.0  # vacuously true


# ---------------------------------------------------------------------------
# 9. v0.6.1 Hardening A — Negation-Blindness Tests
# ---------------------------------------------------------------------------

class TestNegationBlindness:
    """Ensure negated keywords do NOT trigger false positives."""

    def test_no_evidence_of_overclaiming(self):
        p = _make_response(
            final_answer="There is no evidence of overclaiming in this study.",
            key_claims=["The claims are well-supported"],
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_not_an_unsupported_generalization(self):
        p = _make_response(
            final_answer="This is not an unsupported generalization — the authors stay within scope.",
        )
        fp = _detect_false_positives(p)
        assert "unsupported generalization" not in fp

    def test_this_is_not_correlation_as_causation(self):
        p = _make_response(
            final_answer="This is not a correlation as causation problem. The RCT design supports causal claims.",
        )
        fp = _detect_false_positives(p)
        assert "correlation as causation" not in fp

    def test_no_mechanism_gap(self):
        p = _make_response(
            steps=["I do not see mechanism not demonstrated here — the human trials are solid."],
        )
        fp = _detect_false_positives(p)
        assert "mechanism not demonstrated" not in fp

    def test_found_no_major_flaw(self):
        p = _make_response(
            final_answer="I found no major flaw in this study.",
            key_claims=["No major flaw detected"],
        )
        fp = _detect_false_positives(p)
        assert "major flaw" not in fp

    def test_absence_of_fraud(self):
        p = _make_response(
            final_answer="There is an absence of fraud or fabrication in the data.",
        )
        fp = _detect_false_positives(p)
        assert "fraud" not in fp
        assert "fabricat" not in fp

    def test_affirmative_overclaim_still_detected(self):
        """Non-negated overclaim keyword SHOULD still trigger."""
        p = _make_response(
            final_answer="This is overclaim! Major flaw detected!",
            key_claims=["This study commits fraud"],
        )
        fp = _detect_false_positives(p)
        assert len(fp) > 0
        assert "overclaim" in fp

    def test_mixed_negated_and_affirmative(self):
        """If both negated and affirmative uses exist, should still flag."""
        p = _make_response(
            final_answer="There is no major flaw in methods, but there is a major flaw in the conclusions.",
        )
        fp = _detect_false_positives(p)
        assert "major flaw" in fp

    def test_is_negated_utility(self):
        assert _is_negated("there is no evidence of overclaim here", "overclaim")
        assert not _is_negated("this is a clear overclaim case", "overclaim")

    def test_keyword_match_non_negated_utility(self):
        assert not _keyword_match_non_negated(
            "There is no evidence of overclaiming", "overclaim"
        )
        assert _keyword_match_non_negated(
            "This is a clear overclaim", "overclaim"
        )

    def test_full_solid_check_no_fp_with_negation(self):
        """Full pipeline: solid case with negated keywords should have zero FP."""
        task = _make_task("solid", [
            {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
        ])
        p = _make_response(
            final_answer="This is a solid study. There is no evidence of overclaiming. Not an unsupported generalization.",
            steps=["The evidence supports the claim. No major flaw detected."],
            key_claims=["solid study", "no overclaim"],
        )
        result = run_study_forensics_checks(task, p)
        assert result["false_positives"] == []
        assert result["label_correct"]


# ---------------------------------------------------------------------------
# 10. v0.6.1 Hardening B — Flexible Finding Detection Tests
# ---------------------------------------------------------------------------

class TestFlexibleFindingDetection:
    """Ensure regex pattern families catch paraphrased findings."""

    def test_causal_mechanism_not_established(self):
        p = _make_response(steps=["The causal mechanism is not established in humans."])
        findings = _detect_findings(p)
        assert "mechanism_not_demonstrated" in findings

    def test_conclusion_goes_beyond_results(self):
        p = _make_response(steps=["The conclusion goes beyond the reported results."])
        findings = _detect_findings(p)
        assert "conclusion_exceeds_results" in findings

    def test_generalizes_beyond_study_population(self):
        p = _make_response(steps=["This generalizes beyond the study population."])
        findings = _detect_findings(p)
        assert "unsupported_generalization" in findings

    def test_implies_causation_from_association(self):
        p = _make_response(steps=["The text implies causation from association data."])
        findings = _detect_findings(p)
        assert "correlation_as_causation" in findings

    def test_evidence_clearly_supports_claim(self):
        p = _make_response(steps=["The evidence clearly supports the authors' claim."])
        findings = _detect_findings(p)
        assert "evidence_matches_claim" in findings

    def test_only_shown_in_mice(self):
        p = _make_response(steps=["The effect was only shown in mice, not humans."])
        findings = _detect_findings(p)
        assert "mechanism_not_demonstrated" in findings

    def test_overstatement_regex(self):
        p = _make_response(steps=["The authors overstate their conclusions significantly."])
        findings = _detect_findings(p)
        assert "conclusion_exceeds_results" in findings

    def test_claims_justified_regex(self):
        p = _make_response(steps=["The results support the claim made in the abstract."])
        findings = _detect_findings(p)
        assert "evidence_matches_claim" in findings

    def test_decorative_caveat_regex(self):
        p = _make_response(steps=["Further research is needed, but the results are already being used in policy."])
        findings = _detect_findings(p)
        assert "decorative_uncertainty" in findings

    def test_cross_sectional_cannot_prove_causation(self):
        p = _make_response(steps=["Cross-sectional data cannot prove causation."])
        findings = _detect_findings(p)
        assert "correlation_as_causation" in findings

    def test_no_human_clinical_evidence(self):
        p = _make_response(steps=["There is a lack of human clinical evidence for this claim."])
        findings = _detect_findings(p)
        assert "mechanism_not_demonstrated" in findings

    def test_extends_findings_to_general_population(self):
        p = _make_response(steps=["The author extends the findings to all age groups."])
        findings = _detect_findings(p)
        assert "unsupported_generalization" in findings

    def test_confounding_variables_not_controlled(self):
        p = _make_response(steps=["Confounding variables are not controlled for in this survey."])
        findings = _detect_findings(p)
        assert "correlation_as_causation" in findings

    def test_study_is_well_designed_regex(self):
        p = _make_response(steps=["The study is well-designed and rigorous."])
        findings = _detect_findings(p)
        assert "none_or_minor" in findings

    def test_authors_acknowledge_limitations(self):
        p = _make_response(steps=["The authors appropriately acknowledge limitations of scope."])
        findings = _detect_findings(p)
        assert "cautious_scope_control" in findings


# ---------------------------------------------------------------------------
# 11. v0.6.1 Hardening C — Hedge-Language / Decorative Uncertainty Tests
# ---------------------------------------------------------------------------

class TestHedgeLanguageDetection:
    """Ensure hedge + null/weak outcome detection works correctly."""

    def test_null_primary_with_optimistic_hedge(self):
        """Case007 pattern: null primary outcome + 'promising signal'."""
        task = _make_task("overclaim")
        task.prompt = (
            "The primary outcome showed no significant effect on acute severity. "
            "However, lingering symptoms were 21% vs 25% — a promising signal. "
            "The study was conducted remotely with a small sample."
        )
        p = _make_response(
            final_answer="The results are encouraging and suggest further investigation.",
            steps=["The secondary outcome shows a promising trend."],
        )
        result = _detect_hedge_overclaim(task, p)
        assert result["is_suspicious"]
        assert len(result["hedge_phrases"]) > 0
        assert not result["agent_flagged"]

    def test_genuine_caution_not_flagged(self):
        """Study with genuine caution and NO optimistic hedges should NOT be suspicious."""
        task = _make_task("solid")
        task.prompt = (
            "The randomised trial found significant reductions in depression. "
            "The authors noted that the sample was limited to college students "
            "and the effect may not generalize to other populations."
        )
        p = _make_response(
            final_answer="This is a solid study with appropriate caveats.",
            steps=["Evidence supports the claim."],
        )
        result = _detect_hedge_overclaim(task, p)
        assert not result["is_suspicious"]

    def test_agent_that_flags_overclaim_is_acknowledged(self):
        """If the agent correctly flags the hedge-overclaim, agent_flagged should be True."""
        task = _make_task("overclaim")
        task.prompt = (
            "The primary outcome was null. However the authors describe it as a "
            "promising signal for further research. Small sample of 30."
        )
        p = _make_response(
            final_answer="This is overclaim — the null primary outcome is framed with decorative optimism.",
            steps=["The conclusion exceeds the data."],
        )
        result = _detect_hedge_overclaim(task, p)
        assert result["is_suspicious"]
        assert result["agent_flagged"]

    def test_hedge_without_null_outcome_not_suspicious(self):
        """Optimistic language alone without null outcome should NOT trigger."""
        task = _make_task("solid")
        task.prompt = (
            "The trial showed a significant improvement in memory scores. "
            "This is a promising finding for cognitive health."
        )
        p = _make_response(final_answer="Solid study.")
        result = _detect_hedge_overclaim(task, p)
        # has_hedge but no has_null and no strong limitations → not suspicious
        assert not result["is_suspicious"]

    def test_null_outcome_without_hedge_not_suspicious(self):
        """Null outcome alone without optimistic hedging should NOT trigger."""
        task = _make_task("solid")
        task.prompt = (
            "The primary outcome showed no significant effect. "
            "The authors conclude that the intervention was not effective."
        )
        p = _make_response(final_answer="Solid reporting of a null result.")
        result = _detect_hedge_overclaim(task, p)
        assert not result["is_suspicious"]

    def test_small_effect_size_detection(self):
        """Small percentage-point differences should be detected."""
        task = _make_task("overclaim")
        task.prompt = (
            "The study found a 4 percentage point difference in symptoms. "
            "This is described as a promising signal. "
            "The trial had a small sample and was conducted remotely."
        )
        p = _make_response(final_answer="Interesting results worth pursuing.")
        result = _detect_hedge_overclaim(task, p)
        assert result["is_suspicious"]
        assert result["small_effect_detected"]

    def test_hedge_flag_in_full_pipeline(self):
        """Full check: suspicious hedge pattern should produce forensic flag."""
        task = _make_task("overclaim", [
            {"finding": "conclusion_exceeds_results", "severity": "moderate", "confidence": "medium"},
        ])
        task.prompt = (
            "The primary outcome was null but the secondary shows a promising signal. "
            "Study was conducted remotely with self-report measures."
        )
        p = _make_response(
            final_answer="This is overclaim. The null primary makes the optimistic framing unjustified.",
            steps=["The conclusion exceeds the results."],
        )
        result = run_study_forensics_checks(task, p)
        assert result["hedge_overclaim"]["is_suspicious"]
        # Agent flagged it correctly, so no flag should be raised
        assert result["hedge_overclaim"]["agent_flagged"]

    def test_hedge_flag_raised_when_agent_misses(self):
        """When agent doesn't flag suspicious hedge, a forensic flag should be raised."""
        task = _make_task("overclaim", [
            {"finding": "conclusion_exceeds_results", "severity": "moderate", "confidence": "medium"},
        ])
        task.prompt = (
            "The primary outcome was null. The authors call the secondary result "
            "a promising signal. Small sample, conducted remotely."
        )
        p = _make_response(
            final_answer="The study shows interesting preliminary results.",
            steps=["The secondary outcome is worth noting."],
        )
        result = run_study_forensics_checks(task, p)
        assert result["hedge_overclaim"]["is_suspicious"]
        assert not result["hedge_overclaim"]["agent_flagged"]
        # Should have a forensic flag
        flag_types = [f.flag_type for f in result["flags"]]
        assert "hedge_overclaim_undetected" in flag_types


# ---------------------------------------------------------------------------
# 12. v0.6.2 Gold Standard Calibration Fields
# ---------------------------------------------------------------------------

class TestGoldStandardFields:
    """Verify new gold standard calibration fields load and validate."""

    def test_gold_confidence_loaded(self, all_tasks):
        for task in all_tasks:
            assert task.gold_confidence is not None, f"{task.id}: missing gold_confidence"
            assert task.gold_confidence in ("high", "medium", "low")

    def test_gold_case_type_loaded(self, all_tasks):
        for task in all_tasks:
            assert task.gold_case_type is not None, f"{task.id}: missing gold_case_type"
            assert task.gold_case_type in ("clear", "borderline")

    def test_gold_justification_loaded(self, all_tasks):
        for task in all_tasks:
            assert task.gold_justification is not None, f"{task.id}: missing gold_justification"
            assert len(task.gold_justification.strip()) > 20, f"{task.id}: gold_justification too short"

    def test_gold_alternative_reading_loaded(self, all_tasks):
        """Alternative reading is required for borderline cases, optional for clear."""
        for task in all_tasks:
            if task.gold_case_type == "borderline":
                assert task.gold_alternative_reading is not None, f"{task.id}: borderline case missing gold_alternative_reading"
                assert len(task.gold_alternative_reading.strip()) > 10

    def test_curator_notes_loaded(self, all_tasks):
        for task in all_tasks:
            assert task.curator_notes is not None, f"{task.id}: missing curator_notes"

    def test_case007_is_borderline(self, all_tasks):
        c007 = [t for t in all_tasks if t.id == "study-forensics-007"][0]
        assert c007.gold_case_type == "borderline"
        assert c007.gold_confidence == "medium"

    def test_clear_cases_have_high_confidence(self, all_tasks):
        clear_cases = [t for t in all_tasks if t.gold_case_type == "clear"]
        for task in clear_cases:
            assert task.gold_confidence == "high", f"{task.id}: clear case should have high confidence"

    def test_backward_compat_fields_optional(self):
        """New fields are optional — tasks without them still load."""
        task = Task(
            id="compat-test",
            title="Backward Compat",
            domain="test",
            difficulty=Difficulty.MEDIUM,
            task_type=TaskType.STUDY_FORENSICS,
            prompt="test",
            gold_label="solid",
        )
        assert task.gold_confidence is None
        assert task.gold_case_type is None
        assert task.gold_justification is None
        assert task.gold_alternative_reading is None
        assert task.curator_notes is None

    def test_gold_justification_references_label(self, all_tasks):
        """Each justification should be substantive (not just restating the label)."""
        for task in all_tasks:
            justification = task.gold_justification.lower()
            # Should contain reasoning, not just the label word
            assert len(justification.split()) > 10, f"{task.id}: justification is too terse"


# ---------------------------------------------------------------------------
# 13. v0.6.2 Anti-Claim FP Fix Tests
# ---------------------------------------------------------------------------

class TestAntiClaimFPFix:
    """Ensure 'avoids overclaiming' etc. do not trigger false positives."""

    def test_avoids_overclaiming(self):
        p = _make_response(
            final_answer="The text avoids overclaiming and maintains appropriate epistemic humility.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_refrains_from_unsupported_generalization(self):
        p = _make_response(
            final_answer="The author refrains from unsupported generalization throughout.",
        )
        fp = _detect_false_positives(p)
        assert "unsupported generalization" not in fp

    def test_stops_short_of_causal_claims(self):
        p = _make_response(
            final_answer="The study stops short of overclaim by carefully qualifying findings.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_free_of_major_flaw(self):
        p = _make_response(
            final_answer="The methodology is free of major flaw or serious error.",
        )
        fp = _detect_false_positives(p)
        assert "major flaw" not in fp
        assert "serious error" not in fp

    def test_steers_clear_of_overclaim(self):
        p = _make_response(
            final_answer="The conclusion steers clear of overclaim.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_avoiding_does_not_mask_real_fp(self):
        """An affirmative overclaim after an 'avoids' mention should still be caught."""
        p = _make_response(
            final_answer="While section 1 avoids overclaiming, section 2 is blatant overclaim and fraud.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" in fp
        assert "fraud" in fp

    def test_full_solid_pipeline_with_anti_claim_language(self):
        """Full pipeline: solid case with anti-claim phrasing should have zero FP."""
        task = _make_task("solid", [
            {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
        ])
        p = _make_response(
            final_answer="This is a solid study. The text avoids overclaiming throughout.",
            steps=["The evidence supports the claim."],
            key_claims=["solid study", "avoids overclaim"],
        )
        result = run_study_forensics_checks(task, p)
        assert result["false_positives"] == []
        assert result["label_correct"]


# ---------------------------------------------------------------------------
# 14. v0.6.3 Calibration Fix A — Analytical Reference Constructions
# ---------------------------------------------------------------------------

class TestAnalyticalReferenceFP:
    """Ensure analytical reference constructions don't trigger false positives."""

    def test_checked_for_overclaiming(self):
        p = _make_response(
            final_answer="I checked for overclaiming but found none. This is a solid study.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_looked_for_signs_of_overclaim(self):
        p = _make_response(
            final_answer="I looked for signs of overclaim but the claims are well-supported.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_searched_for_unsupported_generalization(self):
        p = _make_response(
            final_answer="I searched for unsupported generalization but found the scope appropriate.",
        )
        fp = _detect_false_positives(p)
        assert "unsupported generalization" not in fp

    def test_tested_whether_overclaims(self):
        p = _make_response(
            final_answer="I tested whether this overclaims and concluded it does not.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_assessed_whether_correlation_as_causation(self):
        p = _make_response(
            final_answer="I assessed whether there is correlation as causation and found none.",
        )
        fp = _detect_false_positives(p)
        assert "correlation as causation" not in fp

    def test_evaluated_whether_mechanism_not_demonstrated(self):
        p = _make_response(
            final_answer="I evaluated whether mechanism not demonstrated applies here. It does not.",
        )
        fp = _detect_false_positives(p)
        assert "mechanism not demonstrated" not in fp

    def test_examined_for_major_flaw(self):
        p = _make_response(
            final_answer="I examined for major flaw in the design and found none.",
        )
        fp = _detect_false_positives(p)
        assert "major flaw" not in fp

    def test_ruled_out_overclaim(self):
        p = _make_response(
            final_answer="I ruled out overclaim after careful analysis. Solid study.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_no_evidence_of_still_works(self):
        """Analytical 'evidence of' cue: 'no evidence of overclaim'."""
        p = _make_response(
            final_answer="There is no evidence of overclaim in this text.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_real_overclaim_still_detected_despite_analytical_nearby(self):
        """Affirmative overclaim after an analytical mention should still be caught."""
        p = _make_response(
            final_answer="I checked for overclaiming and indeed this IS overclaim. The conclusion goes beyond the data.",
        )
        # "overclaim" after "checked for" is analytical,
        # but "overclaim" standalone after "IS" is affirmative — tricky.
        # The second occurrence ("IS overclaim") should be caught.
        fp = _detect_false_positives(p)
        assert "overclaim" in fp

    def test_full_solid_pipeline_analytical_references(self):
        """Full pipeline: solid case with analytical language should have zero FP."""
        task = _make_task("solid", [
            {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
        ])
        p = _make_response(
            final_answer="This is a solid study. I checked for overclaiming and found none.",
            steps=["Evidence supports the claim. Searched for major flaw — none found."],
            key_claims=["solid study", "no overclaim detected"],
        )
        result = run_study_forensics_checks(task, p)
        assert result["false_positives"] == []
        assert result["label_correct"]


# ---------------------------------------------------------------------------
# 15. v0.6.3 Calibration Fix B — Label Detection Priority
# ---------------------------------------------------------------------------

class TestLabelDetectionPriority:
    """Ensure final_answer is prioritized over analysis-body vocabulary."""

    def test_solid_final_answer_with_correlation_in_claims(self):
        """Agent says 'solid' in final_answer but discusses correlation in analysis."""
        p = _make_response(
            final_answer="This is a solid, well-designed study with no major issues.",
            key_claims=["The study discusses correlation but establishes causation via RCT"],
        )
        assert _detect_label(p) == "solid"

    def test_solid_final_answer_with_mechanism_in_claims(self):
        """Agent says 'solid' but discusses mechanism in claims."""
        p = _make_response(
            final_answer="This is a solid study with sound methodology.",
            key_claims=["mechanism is well-demonstrated", "preclinical evidence strong"],
        )
        assert _detect_label(p) == "solid"

    def test_mechanism_final_answer_overrides_correlation_claims(self):
        """Agent says 'mechanism_vs_evidence' despite correlation terms in claims."""
        p = _make_response(
            final_answer="This is mechanism_vs_evidence. Animal model only.",
            key_claims=["cross-sectional observational correlation data"],
        )
        assert _detect_label(p) == "mechanism_vs_evidence"

    def test_overclaim_in_final_answer_wins(self):
        """Explicit overclaim in final_answer should always win."""
        p = _make_response(
            final_answer="This is an overclaim case. The conclusion is exaggerated.",
            key_claims=["solid methodology", "well-designed study"],
        )
        assert _detect_label(p) == "overclaim"

    def test_solid_keyword_only_in_final_answer(self):
        """Keyword 'solid' only appears in final_answer, not in claims."""
        p = _make_response(
            final_answer="solid",
            key_claims=[],
        )
        assert _detect_label(p) == "solid"

    def test_analysis_vocabulary_does_not_hijack(self):
        """Real-world scenario: agent says solid but discusses correlation as part of analysis."""
        p = _make_response(
            final_answer="The study is solid. No major issues with the methodology.",
            key_claims=[
                "The authors acknowledge correlation vs causation distinction",
                "Cross-sectional design noted but controlled for confounders",
                "Not an observational study — this is a proper RCT",
            ],
        )
        assert _detect_label(p) == "solid"

    def test_empty_final_answer_falls_back_to_claims(self):
        """When final_answer is empty, key_claims should be used."""
        p = _make_response(
            final_answer="",
            key_claims=["This is clearly overclaim", "conclusion exceeds results", "overstated"],
        )
        assert _detect_label(p) == "overclaim"


# ---------------------------------------------------------------------------
# 16. v0.6.3 Calibration Fix C — Criticism-Direction Heuristic
# ---------------------------------------------------------------------------

class TestCriticismDirectionHeuristic:
    """Ensure claim-weakening language doesn't trigger false positives."""

    def test_limited_sample_near_overclaim_not_fp(self):
        p = _make_response(
            final_answer="The study has a limited sample but does not overclaim. Solid overall.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_further_research_needed_near_overclaim_not_fp(self):
        p = _make_response(
            final_answer="Further research is needed, and the text honestly says so. No overclaim here.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_preliminary_evidence_near_overclaim_not_fp(self):
        p = _make_response(
            final_answer="This reports preliminary evidence and does not overclaim beyond it.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_does_not_establish_causation_near_correlation_not_fp(self):
        p = _make_response(
            final_answer="The text acknowledges it does not establish causation. This is solid reporting, not correlation as causation error.",
        )
        fp = _detect_false_positives(p)
        assert "correlation as causation" not in fp

    def test_cautious_interpretation_near_overclaim_not_fp(self):
        p = _make_response(
            final_answer="The authors offer cautious interpretation and do not overclaim.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" not in fp

    def test_real_overclaim_without_weakening_still_detected(self):
        """Pure overclaim without weakening cues must still be flagged."""
        p = _make_response(
            final_answer="This is blatant overclaim and fraud.",
        )
        fp = _detect_false_positives(p)
        assert "overclaim" in fp
        assert "fraud" in fp

    def test_weakening_in_different_sentence_does_not_protect(self):
        """Weakening cue in a DIFFERENT sentence should not protect overclaim."""
        p = _make_response(
            final_answer="The sample is small. The conclusion is pure overclaim and unsupported generalization.",
        )
        fp = _detect_false_positives(p)
        # "limited sample" / "small sample" is in sentence 1, overclaim in sentence 2
        # The weakening check looks at the same sentence, so overclaim should still be caught
        # Note: "small" alone doesn't match "limited sample" — we need exact phrase "small sample"
        # but "The sample is small" doesn't match "small sample" — so no protection
        assert "overclaim" in fp

    def test_full_solid_pipeline_with_weakening_cues(self):
        """Full pipeline: solid case with weakening language should have zero FP."""
        task = _make_task("solid", [
            {"finding": "evidence_matches_claim", "severity": "minor", "confidence": "high"},
            {"finding": "cautious_scope_control", "severity": "minor", "confidence": "medium"},
        ])
        p = _make_response(
            final_answer="This is a solid study. Limited sample acknowledged but no overclaim. Further research is needed as authors note.",
            steps=["Evidence supports claim. Cautious interpretation throughout."],
            key_claims=["solid study", "appropriate scope control"],
        )
        result = run_study_forensics_checks(task, p)
        assert result["false_positives"] == []
        assert result["label_correct"]


# ---------------------------------------------------------------------------
# 17. v0.6.6 Label Detector Bug — solid FA vs analytical key_claims
# ---------------------------------------------------------------------------

class TestLabelDetectorSolidPriority:
    """v0.6.6: Bare 'solid' in final_answer must not be overridden by
    analytical vocabulary in key_claims (e.g. 'not causal effects')."""

    def test_bare_solid_fa_not_overridden_by_not_causal_in_claims(self):
        """The exact bug: Sonnet says 'solid', claims mention 'not causal effects'."""
        p = _make_response(
            final_answer="solid",
            key_claims=[
                "Study appropriately presents observational associations without claiming causation",
                "Media coverage uses appropriate hedging language",
                "Authors clearly acknowledge study limitations including observational design",
                "Effect sizes are presented as associations, not causal effects",
            ],
        )
        assert _detect_label(p) == "solid"

    def test_bare_solid_fa_not_overridden_by_cross_sectional_in_claims(self):
        """'cross-sectional' in claims should not flip 'solid' FA."""
        p = _make_response(
            final_answer="solid",
            key_claims=["Appropriate use of cross-sectional data with caveats"],
        )
        assert _detect_label(p) == "solid"

    def test_bare_solid_fa_not_overridden_by_cannot_prove_causation(self):
        """'cannot prove causation' in claims = analytical, not a label signal."""
        p = _make_response(
            final_answer="solid",
            key_claims=["The paper honestly states it cannot prove causation"],
        )
        assert _detect_label(p) == "solid"

    def test_solid_fa_with_rejected_correlation_in_alternatives(self):
        """Agent rejects correlation_vs_causation in alternative_hypotheses."""
        p = _make_response(
            final_answer="solid",
            alternative_hypotheses=[
                "Could be correlation vs causation issue, but no direct causal claims are made",
            ],
            key_claims=["No overclaiming detected"],
        )
        assert _detect_label(p) == "solid"

    def test_negated_solid_does_not_match(self):
        """'not solid' should not return solid."""
        p = _make_response(
            final_answer="This study is not solid. It has major flaws.",
            key_claims=["overclaim", "goes beyond the evidence"],
        )
        assert _detect_label(p) != "solid"

    def test_not_causal_keyword_removed(self):
        """'not causal' alone in claims should NOT trigger correlation_vs_causation."""
        p = _make_response(
            final_answer="",
            key_claims=["The results are presented as not causal effects"],
        )
        # With 'not causal' removed, this should not detect correlation_vs_causation
        label = _detect_label(p)
        assert label != "correlation_vs_causation"

    def test_full_pipeline_sonnet_public001_scenario(self):
        """Full pipeline: Sonnet's actual Public001 output should detect 'solid'."""
        task = _make_task("correlation_vs_causation", [
            {"finding": "correlation_as_causation", "severity": "major", "confidence": "high"},
            {"finding": "unsupported_generalization", "severity": "moderate", "confidence": "medium"},
        ])
        p = _make_response(
            final_answer="solid",
            key_claims=[
                "Study appropriately presents observational associations without claiming causation",
                "Media coverage uses appropriate hedging language ('may', 'could', 'associated with')",
                "Authors clearly acknowledge study limitations including observational design",
                "Effect sizes are presented as associations, not causal effects",
            ],
            alternative_hypotheses=[
                "Could be overclaim due to observational nature, but limitations are clearly stated",
                "Could be correlation vs causation issue, but no direct causal claims are made",
            ],
        )
        result = run_study_forensics_checks(task, p)
        assert result["detected_label"] == "solid"
        assert not result["label_correct"]  # solid != correlation_vs_causation
