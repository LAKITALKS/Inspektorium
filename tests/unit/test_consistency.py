"""Tests of the Inspektorium audit runtime Forensic Consistency 2.0."""

from inspektorium.audit.checks.consistency import run_consistency_checks
from inspektorium.audit.schemas import AgentResponse, Difficulty, Task, TaskType


def _make_task(difficulty: str = "medium", **kwargs) -> Task:
    defaults = dict(
        id="test-001", title="Test Task", domain="test",
        difficulty=Difficulty(difficulty), task_type=TaskType.CLOSED_WITH_REASONING,
        prompt="Test prompt",
    )
    defaults.update(kwargs)
    return Task(**defaults)


def _make_response(**kwargs) -> AgentResponse:
    defaults = dict(
        final_answer="The answer is 42",
        steps=["Step 1: analyze the data", "Step 2: compute the result", "Step 3: conclude with 42"],
        assumptions=["Data is accurate and complete"],
        key_claims=["The computed value is 42"],
        confidence=0.85,
        confidence_state="VALID",
        uncertainties=["rounding errors may affect precision"],
        alternative_hypotheses=["Could be 43 — rejected because calculation shows 42"],
        self_check=["Verified: 2+2 = 4, arithmetic is consistent throughout"],
    )
    defaults.update(kwargs)
    return AgentResponse(**defaults)


# --- v0.3 checks still work ---

class TestSelfCorrections:
    def test_no_corrections(self):
        findings = run_consistency_checks(_make_response(), _make_task())
        corrections = [f for f in findings if f.check_type == "self_correction"]
        assert len(corrections) == 0

    def test_detects_wait_marker(self):
        p = _make_response(steps=["First X = 5", "Wait, that's incorrect. X = 10", "Answer is 10"])
        findings = run_consistency_checks(p, _make_task())
        assert any(f.check_type == "self_correction" for f in findings)

    def test_no_false_positive_on_actually(self):
        p = _make_response(steps=["The trend is actually explained by composition effects"])
        findings = run_consistency_checks(p, _make_task())
        assert not any(f.check_type == "self_correction" for f in findings)


class TestConfidenceUncertainty:
    def test_high_confidence_many_uncertainties(self):
        p = _make_response(confidence=0.95, uncertainties=["u1", "u2", "u3"])
        findings = run_consistency_checks(p, _make_task())
        assert any(f.check_type == "confidence_uncertainty" and "performative" in f.description.lower() for f in findings)

    def test_moderate_confidence_ok(self):
        p = _make_response(confidence=0.80, uncertainties=["some concern"])
        findings = run_consistency_checks(p, _make_task())
        conf = [f for f in findings if f.check_type == "confidence_uncertainty"]
        assert len(conf) == 0


class TestContradictions:
    def test_detects_step_affirms_answer_denies(self):
        p = _make_response(
            final_answer="The claim is not valid.",
            steps=["Therefore the claim is correct and well-supported."],
        )
        findings = run_consistency_checks(p, _make_task())
        assert any(f.check_type == "contradiction" and f.status == "fail" for f in findings)


# --- v0.4 new checks ---

class TestAssumptionUsage:
    def test_detects_unused_assumption(self):
        p = _make_response(
            assumptions=[
                "The data is accurate and complete",
                "Quantum entanglement effects are negligible",  # completely unused
            ],
            steps=["We analyze the accurate data carefully", "The result is 42"],
        )
        findings = run_consistency_checks(p, _make_task())
        unused = [f for f in findings if f.check_type == "unused_assumption"]
        assert len(unused) >= 1

    def test_used_assumptions_no_flag(self):
        p = _make_response(
            assumptions=["The admission data is accurate"],
            steps=["Using the accurate admission data, we compute rates"],
        )
        findings = run_consistency_checks(p, _make_task())
        unused = [f for f in findings if f.check_type == "unused_assumption"]
        assert len(unused) == 0


class TestUncertaintyResolution:
    def test_detects_decorative_uncertainty(self):
        p = _make_response(
            uncertainties=["The gravitational constant of the moon might affect results"],
            steps=["We analyze admissions data", "The paradox is clear"],
            self_check=["Checked arithmetic"],
        )
        findings = run_consistency_checks(p, _make_task())
        decorative = [f for f in findings if f.check_type == "decorative_uncertainty"]
        assert len(decorative) >= 1

    def test_addressed_uncertainty_ok(self):
        p = _make_response(
            uncertainties=["Whether applicant qualifications differ between departments"],
            steps=["We consider whether qualifications differ — the data doesn't suggest this"],
            self_check=["Verified qualifications assumption is reasonable"],
        )
        findings = run_consistency_checks(p, _make_task())
        decorative = [f for f in findings if f.check_type == "decorative_uncertainty"]
        assert len(decorative) == 0


class TestSelfCheckDepth:
    def test_detects_fluff_self_check(self):
        p = _make_response(self_check=["I checked my work."])
        findings = run_consistency_checks(p, _make_task())
        depth = [f for f in findings if f.check_type == "self_check_depth"]
        assert len(depth) >= 1

    def test_substantive_check_ok(self):
        p = _make_response(
            self_check=["Verified arithmetic: 30/100=30%, 20/50=40%, confirming department-level rates are correct"]
        )
        findings = run_consistency_checks(p, _make_task())
        depth = [f for f in findings if f.check_type == "self_check_depth" and f.status == "warning"]
        assert len(depth) == 0


class TestAlternativeHypothesisQuality:
    def test_detects_brief_alternative(self):
        p = _make_response(alternative_hypotheses=["Maybe not."])
        findings = run_consistency_checks(p, _make_task())
        weak = [f for f in findings if f.check_type == "weak_alternative"]
        assert len(weak) >= 1

    def test_good_alternative_ok(self):
        p = _make_response(
            alternative_hypotheses=[
                "The university discriminates against men — rejected because department-level rates show women actually have higher rates in both departments"
            ]
        )
        findings = run_consistency_checks(p, _make_task())
        weak = [f for f in findings if f.check_type == "weak_alternative"]
        assert len(weak) == 0


class TestClaimDrift:
    def test_no_drift_when_consistent(self):
        p = _make_response(
            final_answer="Simpson's Paradox explains the reversal in admissions data.",
            steps=[
                "First I verify admissions data and check Simpson's Paradox",
                "The department-level rates show reversal pattern",
                "This is consistent with Simpson's Paradox aggregation reversal",
            ],
        )
        findings = run_consistency_checks(p, _make_task())
        drift = [f for f in findings if f.check_type == "claim_drift"]
        assert len(drift) == 0


class TestMechanismGap:
    def test_detects_naming_without_mechanism(self):
        p = _make_response(
            final_answer="This is Simpson's Paradox.",
            steps=["I recognize this as Simpson's Paradox", "The answer is clear"],
        )
        findings = run_consistency_checks(p, _make_task())
        mech = [f for f in findings if f.check_type == "mechanism_gap"]
        assert any("named but" in f.description.lower() or "not explained" in f.description.lower() for f in mech)

    def test_expected_mechanism_terms(self):
        p = _make_response(
            final_answer="The data reverses when disaggregated.",
            steps=["The overall rate differs from department rates"],
        )
        task = _make_task(expected_mechanism_terms=["simpson", "confounding"])
        findings = run_consistency_checks(p, task)
        mech = [f for f in findings if f.check_type == "mechanism_gap" and "missing" in f.description.lower()]
        assert len(mech) >= 1
