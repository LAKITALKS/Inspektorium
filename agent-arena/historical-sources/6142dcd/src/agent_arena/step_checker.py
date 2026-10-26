"""v0.4.3: Intermediate step verification engine.

Verifies simple numeric assertions within individual reasoning steps.

Scope (deliberately narrow):
  - Sums:        "30 + 300 = 330"
  - Differences: "400 - 300 = 100"
  - Products:    "3 * 5 = 15"
  - Divisions:   "330 / 500 = 0.66"
  - Percentages: "330/500 = 66%"  or  "30/100 = 30%"
  - Approximate: "≈ 0.09 ≈ 9%"

NOT in scope:
  - Symbolic algebra, multi-step derivations, CAS, NLP-driven extraction.
  - We only verify what can be parsed with simple regexes.

Each check returns a StepCheckResult with confidence label.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from agent_arena.schemas import EvidenceSpan


@dataclass
class StepCheckResult:
    """Result of checking a single numeric assertion in a step."""
    step_index: int
    claim_text: str           # the matched assertion text
    expected_value: float     # what the arithmetic says
    claimed_value: float      # what the agent wrote
    is_correct: bool
    explanation: str
    confidence: str           # "VERIFIED" or "HEURISTIC"
    source_field: str = ""
    evidence: list[EvidenceSpan] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Regex patterns for extractable arithmetic assertions
# ---------------------------------------------------------------------------

# "A + B = C" or "A - B = C" or "A * B = C" or "A × B = C"
_ARITH_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*([+\-*×])\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)"
)

# "A / B = C" (division producing decimal)
_DIV_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)"
)

# "A/B = C%" (fraction to percentage)
_FRAC_PCT_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)\s*%"
)

# Tolerance for floating-point comparison
_ABS_TOL = 0.015
_REL_TOL = 0.02


def _close(a: float, b: float) -> bool:
    """Check if two values are close enough."""
    if abs(b) < 1e-9:
        return abs(a) < _ABS_TOL
    return abs(a - b) <= max(_ABS_TOL, abs(b) * _REL_TOL)


def verify_step(step: str, step_index: int) -> list[StepCheckResult]:
    """Verify all extractable numeric assertions in a single step.

    Returns a list of StepCheckResult for each assertion found.
    """
    results: list[StepCheckResult] = []
    source_field = f"steps[{step_index}]"

    # 1. Fraction → percentage: "330/500 = 66%"
    # Must be checked BEFORE division to avoid double-matching.
    frac_pct_positions: set[int] = set()
    for m in _FRAC_PCT_RE.finditer(step):
        frac_pct_positions.add(m.start())
        num, den, claimed_pct = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if den == 0:
            continue
        expected_pct = round(num / den * 100, 4)
        correct = _close(claimed_pct, expected_pct)
        results.append(StepCheckResult(
            step_index=step_index,
            claim_text=m.group(0),
            expected_value=round(expected_pct, 2),
            claimed_value=claimed_pct,
            is_correct=correct,
            explanation=(
                f"{num}/{den} = {expected_pct:.2f}%, agent claims {claimed_pct}%"
                + ("" if correct else " — WRONG")
            ),
            confidence="VERIFIED",
            source_field=source_field,
            evidence=[EvidenceSpan(
                text=m.group(0), source_field=source_field,
                relevance="Fraction-to-percentage assertion",
            )],
        ))

    # 2. Division: "A / B = C"
    for m in _DIV_RE.finditer(step):
        if m.start() in frac_pct_positions:
            continue  # already handled as fraction→percentage
        num, den, claimed = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if den == 0:
            continue
        expected = round(num / den, 6)
        correct = _close(claimed, expected)
        results.append(StepCheckResult(
            step_index=step_index,
            claim_text=m.group(0),
            expected_value=round(expected, 4),
            claimed_value=claimed,
            is_correct=correct,
            explanation=(
                f"{num} / {den} = {expected:.4f}, agent claims {claimed}"
                + ("" if correct else " — WRONG")
            ),
            confidence="VERIFIED",
            source_field=source_field,
            evidence=[EvidenceSpan(
                text=m.group(0), source_field=source_field,
                relevance="Division assertion",
            )],
        ))

    # 3. Basic arithmetic: "A + B = C", "A - B = C", "A * B = C"
    for m in _ARITH_RE.finditer(step):
        a, op, b, claimed = float(m.group(1)), m.group(2), float(m.group(3)), float(m.group(4))
        if op == "+":
            expected = a + b
        elif op == "-":
            expected = a - b
        elif op in ("*", "×"):
            expected = a * b
        else:
            continue

        correct = _close(claimed, expected)
        results.append(StepCheckResult(
            step_index=step_index,
            claim_text=m.group(0),
            expected_value=round(expected, 4),
            claimed_value=claimed,
            is_correct=correct,
            explanation=(
                f"{a} {op} {b} = {expected}, agent claims {claimed}"
                + ("" if correct else " — WRONG")
            ),
            confidence="VERIFIED",
            source_field=source_field,
            evidence=[EvidenceSpan(
                text=m.group(0), source_field=source_field,
                relevance="Arithmetic assertion",
            )],
        ))

    return results


def verify_all_steps(steps: list[str]) -> list[StepCheckResult]:
    """Verify all steps and return combined results."""
    results: list[StepCheckResult] = []
    for i, step in enumerate(steps):
        results.extend(verify_step(step, i))
    return results
