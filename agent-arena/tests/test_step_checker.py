"""v0.4.3: Tests for intermediate step verification engine."""

from agent_arena.step_checker import verify_step, verify_all_steps


class TestArithmeticVerification:
    """Verify basic arithmetic assertions in steps."""

    def test_correct_addition(self):
        results = verify_step("30 + 300 = 330", 0)
        assert len(results) == 1
        assert results[0].is_correct
        assert results[0].confidence == "VERIFIED"

    def test_wrong_addition(self):
        results = verify_step("30 + 300 = 340", 0)
        assert len(results) == 1
        assert not results[0].is_correct
        assert "WRONG" in results[0].explanation

    def test_correct_subtraction(self):
        results = verify_step("400 - 300 = 100", 0)
        assert len(results) == 1
        assert results[0].is_correct

    def test_wrong_subtraction(self):
        results = verify_step("400 - 300 = 50", 0)
        assert len(results) == 1
        assert not results[0].is_correct

    def test_correct_multiplication(self):
        results = verify_step("3 * 5 = 15", 0)
        assert len(results) == 1
        assert results[0].is_correct

    def test_wrong_multiplication(self):
        results = verify_step("3 * 5 = 20", 0)
        assert len(results) == 1
        assert not results[0].is_correct


class TestDivisionVerification:
    """Verify division assertions."""

    def test_correct_division(self):
        results = verify_step("330 / 500 = 0.66", 0)
        assert len(results) == 1
        assert results[0].is_correct

    def test_wrong_division(self):
        results = verify_step("330 / 500 = 0.80", 0)
        assert len(results) == 1
        assert not results[0].is_correct

    def test_division_close_enough(self):
        # 1/3 = 0.33 (within tolerance of 0.3333...)
        results = verify_step("1 / 3 = 0.33", 0)
        assert len(results) == 1
        assert results[0].is_correct


class TestFractionPercentageVerification:
    """Verify fraction-to-percentage assertions."""

    def test_correct_fraction_percentage(self):
        results = verify_step("330/500 = 66%", 0)
        assert len(results) == 1
        assert results[0].is_correct

    def test_wrong_fraction_percentage(self):
        results = verify_step("330/500 = 75%", 0)
        assert len(results) == 1
        assert not results[0].is_correct

    def test_correct_small_fraction(self):
        results = verify_step("30/100 = 30%", 0)
        assert len(results) == 1
        assert results[0].is_correct

    def test_correct_decimal_percentage(self):
        results = verify_step("20/50 = 40%", 0)
        assert len(results) == 1
        assert results[0].is_correct

    def test_fraction_pct_not_double_counted_as_division(self):
        """330/500 = 66% should match as fraction-pct, not also as division."""
        results = verify_step("330/500 = 66%", 0)
        assert len(results) == 1  # not 2


class TestMultipleAssertions:
    """Verify multiple assertions in one step or across steps."""

    def test_two_assertions_in_one_step(self):
        results = verify_step("30 + 300 = 330 and 20 + 350 = 370", 0)
        assert len(results) == 2
        assert all(r.is_correct for r in results)

    def test_mixed_correct_and_wrong(self):
        results = verify_step("30 + 300 = 330 and 20 + 350 = 400", 0)
        assert len(results) == 2
        assert results[0].is_correct
        assert not results[1].is_correct

    def test_verify_all_steps(self):
        steps = [
            "30 + 300 = 330",
            "Nothing numeric here",
            "330/500 = 66%",
        ]
        results = verify_all_steps(steps)
        assert len(results) == 2
        assert results[0].step_index == 0
        assert results[1].step_index == 2
        assert all(r.is_correct for r in results)


class TestEdgeCases:
    """Edge cases and robustness."""

    def test_no_assertions(self):
        results = verify_step("The data shows interesting patterns.", 0)
        assert len(results) == 0

    def test_empty_step(self):
        results = verify_step("", 0)
        assert len(results) == 0

    def test_division_by_zero_skipped(self):
        results = verify_step("10 / 0 = 5", 0)
        assert len(results) == 0

    def test_step_index_tracked(self):
        results = verify_step("3 + 4 = 7", 5)
        assert len(results) == 1
        assert results[0].step_index == 5
        assert results[0].source_field == "steps[5]"

    def test_evidence_attached(self):
        results = verify_step("3 + 4 = 7", 0)
        assert len(results) == 1
        assert len(results[0].evidence) == 1
        assert results[0].evidence[0].source_field == "steps[0]"
