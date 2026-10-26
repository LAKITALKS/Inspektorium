"""Gen 5 Disagreement Lab — forensic divergence layer for agent-arena v0.6.10.

Analyzes cross-model disagreement cases and produces structured forensic
reports that make dissent visible and interpretable. Does NOT resolve
disagreements, change gold labels, or pick winners.

Answers:
- Which cases produce genuine epistemic disagreement?
- What plausible alternative readings exist?
- Is the disagreement a borderline signal or noise?
- Is the root issue gold-label, model, case-design, or category-boundary?
- Which model characters emerge (charitable, aggressive, taxonomically unstable)?
- Should a case be flagged for gold review?

Data sources: RunJournalEntry (journal.jsonl), InsightsReport (optional).
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime, timezone

from agent_arena.confidence_validity import confidence_value_if_valid
from agent_arena.schemas import (
    AlternativeReading,
    DisagreementCaseReport,
    DisagreementLabReport,
    InsightsReport,
    ModelPosition,
    RunJournalEntry,
)


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

_MIN_MODELS = 2                    # need >= 2 distinct models to analyze disagreement
_DISAGREEMENT_THRESHOLD = 0.01     # entropy > 0 = any disagreement
_BORDERLINE_ENTROPY = 0.4          # entropy >= 0.4 = likely borderline
_HIGH_CONFIDENCE = 0.7             # confidence >= 0.7 = high confidence
_HIGH_SCORE = 60.0                 # total_score >= 60 = well-reasoned
_CHARITABLE_LABELS = {"solid", "no major issues", "well-supported", "sound methodology"}
_CRITICAL_LABELS = {"overclaim", "overclaiming", "significant issues", "major issues"}
_CORRELATION_LABELS = {"correlation_vs_causation", "correlation as causation",
                       "correlation treated as causation", "correlational"}
_MECHANISM_LABELS = {"mechanism_vs_evidence", "mechanism gap", "mechanism issue",
                     "weak mechanism"}

# Study forensics gold labels (canonical)
_KNOWN_LABELS = {"solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence"}


# ---------------------------------------------------------------------------
# Entropy
# ---------------------------------------------------------------------------

def _entropy(distribution: dict[str, int]) -> float:
    """Shannon entropy normalized to [0, 1]."""
    total = sum(distribution.values())
    if total == 0:
        return 0.0
    n_labels = len(distribution)
    if n_labels <= 1:
        return 0.0
    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    max_entropy = math.log2(n_labels)
    return round(entropy / max_entropy, 3) if max_entropy > 0 else 0.0


# ---------------------------------------------------------------------------
# Label normalization
# ---------------------------------------------------------------------------

def _normalize_label(raw: str) -> str:
    """Normalize a final_answer to a canonical-ish label for comparison."""
    label = raw.strip().lower()[:100]
    if not label:
        return "(empty)"
    return label


def _label_family(label: str) -> str:
    """Map a normalized label to a broad reading family.

    Returns the reading family name or the label itself if unrecognized.
    """
    if label in _CHARITABLE_LABELS or label == "solid":
        return "charitable"
    if label in _CRITICAL_LABELS or label == "overclaim":
        return "critical"
    if label in _CORRELATION_LABELS or label == "correlation_vs_causation":
        return "correlation_caution"
    if label in _MECHANISM_LABELS or label == "mechanism_vs_evidence":
        return "mechanism_focus"
    return label


# ---------------------------------------------------------------------------
# Core analysis: per-case disagreement report
# ---------------------------------------------------------------------------

def _analyze_case(
    task_id: str,
    entries: list[RunJournalEntry],
) -> DisagreementCaseReport | None:
    """Analyze a single case for disagreement patterns.

    Returns None if fewer than 2 distinct models or no disagreement.
    """
    # Deduplicate by model (take latest run per model)
    by_model: dict[str, RunJournalEntry] = {}
    for e in sorted(entries, key=lambda x: x.timestamp):
        model = e.model or e.agent_id
        by_model[model] = e  # latest wins

    if len(by_model) < _MIN_MODELS:
        return None

    # Build positions
    positions: list[ModelPosition] = []
    label_dist: Counter[str] = Counter()

    for model, e in sorted(by_model.items()):
        label = _normalize_label(e.final_answer)
        label_dist[label] += 1
        confidence = confidence_value_if_valid(e.confidence, e.confidence_state)
        positions.append(ModelPosition(
            model=model,
            label=label,
            confidence=confidence,
            confidence_state=e.confidence_state,
            total_score=e.total_score,
            correctness=e.correctness,
            reasoning_integrity=e.reasoning_integrity_class,
            key_failures=e.failure_categories[:5],
            key_flags=e.forensic_flag_types[:5],
        ))

    # Check for any disagreement
    entropy = _entropy(dict(label_dist))
    if entropy < _DISAGREEMENT_THRESHOLD:
        return None  # unanimous — no disagreement to analyze

    task_family = entries[0].task_family or ""

    # Confidence analysis
    confidence_values = [
        confidence_value_if_valid(p.confidence, p.confidence_state) for p in positions
    ]
    confidences = [v for v in confidence_values if v is not None]
    avg_conf = sum(confidences) / len(confidences) if confidences else None
    conf_spread = (
        max(confidences) - min(confidences) if len(confidences) >= 2
        else (0.0 if confidences else None)
    )
    all_high_conf = bool(
        len(confidences) == len(positions) and confidences
        and all(c >= _HIGH_CONFIDENCE for c in confidences)
    )

    # --- Alternative readings ---
    readings = _derive_alternative_readings(positions, label_dist, task_family)

    # --- Borderline / gold-review signals ---
    likely_borderline = _assess_borderline(entropy, all_high_conf, positions, readings)
    likely_gold_review = _assess_gold_review(
        entropy, all_high_conf, positions, task_family
    )

    # --- Root issue heuristic ---
    root_issue, root_conf, root_evidence = _assess_root_issue(
        positions, label_dist, entropy, task_family, all_high_conf
    )

    # --- Model character notes ---
    character_notes = _derive_model_character_notes(positions, task_family)

    # --- Epistemic value ---
    epistemic = _assess_epistemic_value(
        entropy, readings, likely_borderline, root_issue, positions
    )

    # --- Review recommendation ---
    review_rec = _build_review_recommendation(
        likely_borderline, likely_gold_review, epistemic, root_issue
    )

    return DisagreementCaseReport(
        task_id=task_id,
        task_family=task_family,
        n_models=len(positions),
        model_positions=positions,
        label_distribution=dict(label_dist),
        disagreement_score=entropy,
        avg_confidence=round(avg_conf, 3) if avg_conf is not None else None,
        confidence_spread=round(conf_spread, 3) if conf_spread is not None else None,
        all_high_confidence=all_high_conf,
        n_confidence_observations=len(positions),
        n_confidence_eligible=len(confidences),
        n_confidence_ineligible=len(positions) - len(confidences),
        plausible_readings=readings,
        likely_borderline=likely_borderline,
        likely_gold_review=likely_gold_review,
        likely_root_issue=root_issue,
        root_issue_confidence=root_conf,
        root_issue_evidence=root_evidence,
        model_character_notes=character_notes,
        epistemic_value=epistemic,
        review_recommendation=review_rec,
    )


# ---------------------------------------------------------------------------
# Alternative reading derivation
# ---------------------------------------------------------------------------

def _derive_alternative_readings(
    positions: list[ModelPosition],
    label_dist: dict[str, int],
    task_family: str,
) -> list[AlternativeReading]:
    """Derive plausible alternative readings from model positions."""
    readings: list[AlternativeReading] = []

    # Group models by label family
    family_groups: dict[str, list[ModelPosition]] = defaultdict(list)
    for p in positions:
        fam = _label_family(p.label)
        family_groups[fam].append(p)

    for reading_fam, group_positions in sorted(family_groups.items()):
        models = [p.model for p in group_positions]
        labels = sorted(set(p.label for p in group_positions))
        avg_score = sum(p.total_score for p in group_positions) / len(group_positions)
        confidences = [
            value for p in group_positions
            if (value := confidence_value_if_valid(
                p.confidence, p.confidence_state
            )) is not None
        ]

        # Plausibility assessment
        has_well_supported = any(
            p.reasoning_integrity == "well_supported" for p in group_positions
        )
        has_high_score = any(p.total_score >= _HIGH_SCORE for p in group_positions)

        if has_well_supported and has_high_score:
            plausibility = "high"
        elif has_well_supported or has_high_score:
            plausibility = "medium"
        else:
            plausibility = "low"

        # Build description
        description = _reading_description(reading_fam, labels, task_family)

        evidence = [
            f"{len(models)} model(s): {', '.join(models)}",
            f"Labels: {', '.join(labels)}",
            f"Avg score: {avg_score:.1f}/100",
        ]
        if confidences:
            evidence.append(
                f"Avg confidence: {sum(confidences) / len(confidences):.2f} "
                f"({len(confidences)}/{len(group_positions)} eligible)"
            )
        else:
            evidence.append(
                f"Avg confidence: unavailable (0/{len(group_positions)} eligible)"
            )
        if has_well_supported:
            evidence.append("At least one model has well-supported reasoning")
        integrity_classes = sorted(set(p.reasoning_integrity for p in group_positions if p.reasoning_integrity))
        if integrity_classes:
            evidence.append(f"Reasoning integrity: {', '.join(integrity_classes)}")

        readings.append(AlternativeReading(
            reading_label=reading_fam,
            description=description,
            supporting_models=models,
            plausibility=plausibility,
            evidence=evidence,
        ))

    return readings


def _reading_description(reading_fam: str, labels: list[str], task_family: str) -> str:
    """Generate a human-readable description for a reading family."""
    descriptions = {
        "charitable": (
            "Charitable reading: the study/claim is interpreted as methodologically "
            "sound with no major issues. Hedged language is read as appropriate caution, "
            "not as weakness."
        ),
        "critical": (
            "Critical reading: the study/claim is interpreted as overclaiming — "
            "conclusions go beyond what the evidence supports."
        ),
        "correlation_caution": (
            "Correlation-caution reading: the analysis identifies causal language "
            "applied to correlational evidence. The core issue is the gap between "
            "the study design and the strength of conclusions."
        ),
        "mechanism_focus": (
            "Mechanism-focus reading: the analysis identifies a gap between naming "
            "a mechanism and providing grounded mechanistic evidence. The claim "
            "invokes a mechanism without adequate support."
        ),
    }
    if reading_fam in descriptions:
        return descriptions[reading_fam]
    return f"Reading: models classify this as '{', '.join(labels)}'."


# ---------------------------------------------------------------------------
# Borderline / Gold-review assessment
# ---------------------------------------------------------------------------

def _assess_borderline(
    entropy: float,
    all_high_confidence: bool,
    positions: list[ModelPosition],
    readings: list[AlternativeReading],
) -> bool:
    """Determine if a case is likely borderline.

    Signals:
    1. High entropy (>= 0.4)
    2. Multiple plausible readings with medium+ plausibility
    3. All models confident but disagree
    """
    if entropy >= _BORDERLINE_ENTROPY:
        return True

    # Multiple plausible readings
    credible_readings = [r for r in readings if r.plausibility in ("high", "medium")]
    if len(credible_readings) >= 2:
        return True

    # All confident but disagree
    if all_high_confidence and len(set(p.label for p in positions)) >= 2:
        return True

    return False


def _assess_gold_review(
    entropy: float,
    all_high_confidence: bool,
    positions: list[ModelPosition],
    task_family: str,
) -> bool:
    """Determine if a case should be flagged for gold-label review.

    Signals:
    1. All models incorrect with high confidence
    2. High entropy + well-reasoned disagreement
    3. Majority label differs from task_family (gold label proxy)
    """
    # All incorrect with high confidence
    all_wrong = all(p.correctness < 0.5 for p in positions)
    if all_wrong and all_high_confidence:
        return True

    # High entropy + well-reasoned disagreement
    if entropy >= _BORDERLINE_ENTROPY:
        well_reasoned_wrong = [
            p for p in positions
            if p.correctness < 0.5 and p.total_score >= _HIGH_SCORE
        ]
        if len(well_reasoned_wrong) >= 2:
            return True

    # Majority label ≠ task_family
    if task_family:
        labels = [p.label for p in positions]
        majority = Counter(labels).most_common(1)[0]
        majority_label = majority[0]
        majority_count = majority[1]
        if (majority_label != task_family
                and majority_count > len(positions) / 2
                and all_high_confidence):
            return True

    return False


# ---------------------------------------------------------------------------
# Root issue heuristic
# ---------------------------------------------------------------------------

def _assess_root_issue(
    positions: list[ModelPosition],
    label_dist: dict[str, int],
    entropy: float,
    task_family: str,
    all_high_confidence: bool,
) -> tuple[str, str, list[str]]:
    """Heuristically classify the likely root cause of disagreement.

    Returns: (root_issue, confidence, evidence_list)

    Root issue categories:
    - gold_label: the gold label may be wrong or the case genuinely borderline
    - model_limitation: one or more models have known weaknesses
    - case_design: the input text is ambiguous or poorly constructed
    - category_boundary: the disagreement sits on a taxonomy edge
    - evaluator: the evaluator may be mis-scoring
    - insufficient_data: not enough information to determine
    """
    evidence: list[str] = []
    n = len(positions)

    # All wrong with high confidence → likely gold label issue
    all_wrong = all(p.correctness < 0.5 for p in positions)
    if all_wrong and all_high_confidence and n >= 2:
        evidence.append(f"All {n} models incorrect with high confidence")
        if len(set(p.label for p in positions)) == 1:
            evidence.append("All models agree on the same (wrong) label")
            return "gold_label", "high", evidence
        evidence.append("Models disagree but all are incorrect")
        return "gold_label", "medium", evidence

    # Low scores across the board → possible case design issue
    # (check early: if all models score poorly, the case itself is likely problematic)
    avg_score = sum(p.total_score for p in positions) / n
    if avg_score < 45.0:
        evidence.append(f"Low average score across models: {avg_score:.1f}/100")
        evidence.append("Models may be struggling with case structure or ambiguity")
        return "case_design", "low", evidence

    # Majority disagrees with gold → likely gold/category boundary
    if task_family:
        majority_label, majority_count = Counter(
            p.label for p in positions
        ).most_common(1)[0]
        if majority_label != task_family and majority_count >= n * 0.5:
            evidence.append(
                f"Majority label '{majority_label}' ({majority_count}/{n}) "
                f"differs from expected '{task_family}'"
            )
            # Check if the labels are in adjacent categories
            maj_fam = _label_family(majority_label)
            gold_fam = _label_family(task_family)
            if maj_fam != gold_fam:
                evidence.append(
                    f"Labels cross reading families: '{maj_fam}' vs '{gold_fam}'"
                )
                return "category_boundary", "medium", evidence
            return "gold_label", "medium", evidence

    # One model brittle/accidental, others well_supported → model limitation
    brittle = [p for p in positions if p.reasoning_integrity in ("brittle", "accidental")]
    well_supported = [p for p in positions if p.reasoning_integrity == "well_supported"]
    if brittle and well_supported:
        brittle_models = [p.model for p in brittle]
        evidence.append(
            f"Model(s) {', '.join(brittle_models)} have brittle/accidental reasoning"
        )
        evidence.append(
            f"{len(well_supported)} model(s) have well-supported reasoning"
        )
        return "model_limitation", "medium", evidence

    # High entropy with mixed reading families → category boundary
    reading_families = set(_label_family(p.label) for p in positions)
    if len(reading_families) >= 2 and entropy >= 0.3:
        evidence.append(
            f"Labels span {len(reading_families)} reading families: "
            f"{', '.join(sorted(reading_families))}"
        )
        evidence.append(f"Entropy: {entropy:.2f}")
        return "category_boundary", "heuristic", evidence

    # Default
    evidence.append("No strong signal for root cause classification")
    return "insufficient_data", "low", evidence


# ---------------------------------------------------------------------------
# Model character notes
# ---------------------------------------------------------------------------

def _derive_model_character_notes(
    positions: list[ModelPosition],
    task_family: str,
) -> list[str]:
    """Derive per-model character observations from this case."""
    notes: list[str] = []

    for p in positions:
        label_fam = _label_family(p.label)
        gold_fam = _label_family(task_family) if task_family else ""

        # Charitable reading where gold is not solid
        if label_fam == "charitable" and gold_fam and gold_fam != "charitable":
            notes.append(
                f"{p.model} reads charitably ('{p.label}') where expected "
                f"family is '{task_family}' — possible overcautious/charitable bias"
            )

        # Aggressive flagging where gold is solid
        if label_fam != "charitable" and gold_fam == "charitable":
            notes.append(
                f"{p.model} flags aggressively ('{p.label}') where expected "
                f"family is '{task_family}' — possible overflagging tendency"
            )

        # Brittle reasoning with high confidence
        confidence = confidence_value_if_valid(p.confidence, p.confidence_state)
        if (p.reasoning_integrity in ("brittle", "accidental")
                and confidence is not None and confidence >= _HIGH_CONFIDENCE):
            notes.append(
                f"{p.model}: brittle/accidental reasoning with high confidence "
                f"({confidence:.2f}) — overconfident pattern"
            )

        # Well-supported but incorrect
        if p.reasoning_integrity == "well_supported" and p.correctness < 0.5:
            notes.append(
                f"{p.model}: well-supported reasoning but incorrect — "
                f"plausible alternative reading or gold-label issue"
            )

    return notes


# ---------------------------------------------------------------------------
# Epistemic value assessment
# ---------------------------------------------------------------------------

def _assess_epistemic_value(
    entropy: float,
    readings: list[AlternativeReading],
    likely_borderline: bool,
    root_issue: str,
    positions: list[ModelPosition],
) -> str:
    """Classify the epistemic value of the disagreement.

    - high: disagreement reveals genuine ambiguity, useful for calibration
    - medium: some signal, worth reviewing
    - low: weak signal, probably noise
    - noise: likely spurious (one model broken, parse error, etc.)
    """
    # Check for empty/parse-failure labels
    noise_labels = [p for p in positions if p.label == "(empty)" or p.total_score < 10]
    if len(noise_labels) >= len(positions) - 1:
        return "noise"

    credible_readings = [r for r in readings if r.plausibility in ("high", "medium")]

    if likely_borderline and len(credible_readings) >= 2:
        return "high"

    if root_issue in ("gold_label", "category_boundary") and entropy >= 0.3:
        return "high"

    if entropy >= _BORDERLINE_ENTROPY or len(credible_readings) >= 2:
        return "medium"

    if root_issue == "model_limitation":
        return "low"

    return "low"


# ---------------------------------------------------------------------------
# Review recommendation
# ---------------------------------------------------------------------------

def _build_review_recommendation(
    likely_borderline: bool,
    likely_gold_review: bool,
    epistemic_value: str,
    root_issue: str,
) -> str:
    """Build a human-readable review recommendation."""
    parts: list[str] = []

    if likely_gold_review:
        parts.append("Gold-review recommended: models disagree in ways that suggest "
                      "the gold label may need reconsideration.")

    if likely_borderline and not likely_gold_review:
        parts.append("Case appears borderline: consider adding 'borderline' case_type "
                      "or documenting the alternative reading in gold_alternative_reading.")

    if epistemic_value == "high":
        parts.append("High epistemic value — disagreement reveals genuine category "
                      "ambiguity. Useful for calibration and boundary sharpening.")
    elif epistemic_value == "noise":
        parts.append("Low epistemic value — disagreement appears to be noise "
                      "(parse failures, model errors). No action needed.")

    if root_issue == "category_boundary":
        parts.append("Root issue appears to be a category boundary problem — "
                      "consider whether the taxonomy needs refinement.")
    elif root_issue == "case_design":
        parts.append("Root issue may be case design — consider revising the input text "
                      "to reduce unintended ambiguity.")

    if not parts:
        parts.append("Minor disagreement — no immediate action required. "
                      "Monitor if pattern recurs across runs.")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Family summary
# ---------------------------------------------------------------------------

def _build_family_summary(
    cases: list[DisagreementCaseReport],
) -> dict[str, dict]:
    """Aggregate disagreement stats per family."""
    by_family: dict[str, list[DisagreementCaseReport]] = defaultdict(list)
    for c in cases:
        if c.task_family:
            by_family[c.task_family].append(c)

    summary: dict[str, dict] = {}
    for family, fam_cases in sorted(by_family.items()):
        n = len(fam_cases)
        avg_entropy = sum(c.disagreement_score for c in fam_cases) / n
        n_borderline = sum(1 for c in fam_cases if c.likely_borderline)
        n_gold_review = sum(1 for c in fam_cases if c.likely_gold_review)
        root_issues = Counter(c.likely_root_issue for c in fam_cases)
        epistemic_values = Counter(c.epistemic_value for c in fam_cases)

        summary[family] = {
            "n_cases": n,
            "avg_entropy": round(avg_entropy, 3),
            "n_borderline": n_borderline,
            "n_gold_review": n_gold_review,
            "top_root_issues": dict(root_issues.most_common(3)),
            "epistemic_distribution": dict(epistemic_values),
        }

    return summary


# ---------------------------------------------------------------------------
# Model character summary
# ---------------------------------------------------------------------------

def _build_model_character_summary(
    cases: list[DisagreementCaseReport],
) -> dict[str, list[str]]:
    """Aggregate model character patterns across cases."""
    model_notes: dict[str, Counter[str]] = defaultdict(Counter)

    for case in cases:
        for note in case.model_character_notes:
            # Extract model name (first word before ":")
            if ":" in note:
                model = note.split(":")[0].strip()
            elif " " in note:
                model = note.split(" ")[0].strip()
            else:
                continue

            # Classify the character pattern
            note_lower = note.lower()
            if "charitable" in note_lower or "overcautious" in note_lower:
                model_notes[model]["charitable_reading_tendency"] += 1
            elif "aggressive" in note_lower or "overflagging" in note_lower:
                model_notes[model]["aggressive_flagging_tendency"] += 1
            elif "overconfident" in note_lower or "brittle" in note_lower:
                model_notes[model]["overconfident_pattern"] += 1
            elif "well-supported" in note_lower and "incorrect" in note_lower:
                model_notes[model]["plausible_alternative_reader"] += 1

    result: dict[str, list[str]] = {}
    for model, patterns in sorted(model_notes.items()):
        summaries = []
        for pattern, count in patterns.most_common():
            summaries.append(f"{pattern} ({count}x)")
        result[model] = summaries

    return result


# ---------------------------------------------------------------------------
# Main: analyze_disagreements
# ---------------------------------------------------------------------------

def analyze_disagreements(
    entries: list[RunJournalEntry],
    task_ids: list[str] | None = None,
    families: list[str] | None = None,
    min_entropy: float = 0.0,
) -> DisagreementLabReport:
    """Analyze cross-model disagreements from journal entries.

    Pure observation — no side effects, no mutations.

    Args:
        entries: Journal entries to analyze.
        task_ids: Restrict to specific task IDs. None = all.
        families: Restrict to specific families. None = all.
        min_entropy: Only include cases with entropy >= this threshold.

    Returns:
        DisagreementLabReport with per-case forensic analysis.
    """
    if not entries:
        return DisagreementLabReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            summary="No journal entries — no disagreement analysis.",
        )

    # Group by task_id
    by_task: dict[str, list[RunJournalEntry]] = defaultdict(list)
    analyzed_entries: list[RunJournalEntry] = []
    for e in entries:
        if task_ids and e.task_id not in task_ids:
            continue
        if families and e.task_family not in families:
            continue
        by_task[e.task_id].append(e)
        analyzed_entries.append(e)

    # Analyze each task
    cases: list[DisagreementCaseReport] = []
    n_total = len(by_task)

    for task_id, task_entries in sorted(by_task.items()):
        report = _analyze_case(task_id, task_entries)
        if report and report.disagreement_score >= min_entropy:
            cases.append(report)

    # Sort by disagreement score descending
    cases.sort(key=lambda c: c.disagreement_score, reverse=True)

    # Aggregate
    n_borderline = sum(1 for c in cases if c.likely_borderline)
    n_gold_review = sum(1 for c in cases if c.likely_gold_review)
    family_summary = _build_family_summary(cases)
    model_chars = _build_model_character_summary(cases)
    confidence_values = [
        confidence_value_if_valid(e.confidence, e.confidence_state)
        for e in analyzed_entries
    ]
    n_confidence_eligible = sum(v is not None for v in confidence_values)

    # Summary
    if cases:
        summary = (
            f"Analyzed {n_total} cases, found {len(cases)} with cross-model disagreement. "
            f"{n_borderline} likely borderline, {n_gold_review} gold-review candidates."
        )
    else:
        summary = f"Analyzed {n_total} cases. No cross-model disagreement detected."

    return DisagreementLabReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        n_cases_analyzed=n_total,
        n_confidence_observations=len(analyzed_entries),
        n_confidence_eligible=n_confidence_eligible,
        n_confidence_ineligible=len(analyzed_entries) - n_confidence_eligible,
        n_disagreement_cases=len(cases),
        n_borderline_signals=n_borderline,
        n_gold_review_signals=n_gold_review,
        cases=cases,
        family_summary=family_summary,
        model_character_summary=model_chars,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Report rendering — Markdown
# ---------------------------------------------------------------------------

def render_disagreement_report(report: DisagreementLabReport) -> str:
    """Render DisagreementLabReport as nüchtern, forensic Markdown."""
    lines: list[str] = []

    def _h1(t: str) -> None:
        lines.append(f"# {t}")
        lines.append("")

    def _h2(t: str) -> None:
        lines.append(f"## {t}")
        lines.append("")

    def _h3(t: str) -> None:
        lines.append(f"### {t}")
        lines.append("")

    def _p(t: str) -> None:
        lines.append(t)
        lines.append("")

    _h1("Agent Arena — Gen 5 Disagreement Lab Report")
    _p(f"**Generated:** {report.generated_at}  ")
    _p(f"**Cases analyzed:** {report.n_cases_analyzed}")
    _p(
        f"**Confidence coverage:** {report.n_confidence_eligible}/"
        f"{report.n_confidence_observations} eligible; "
        f"{report.n_confidence_ineligible} ineligible"
    )
    _p(f"**Disagreement cases:** {report.n_disagreement_cases}")
    _p(f"**Borderline signals:** {report.n_borderline_signals}")
    _p(f"**Gold-review signals:** {report.n_gold_review_signals}")
    _p(f"**Summary:** {report.summary}")

    if not report.cases:
        _p("_No cross-model disagreement detected._")
        lines.append("---")
        _p("*Gen 5 Disagreement Lab — observation only. No automatic changes to "
           "gold labels, scores, or evaluator rules.*")
        return "\n".join(lines)

    # Overview table
    _h2("Disagreement Overview")
    lines.append("| Task | Family | Entropy | Models | Labels | Borderline | Gold Review | Root Issue |")
    lines.append("|------|--------|---------|--------|--------|------------|-------------|------------|")
    for c in report.cases:
        labels = ", ".join(f"{l}x{n}" for l, n in sorted(c.label_distribution.items()))
        bl = "yes" if c.likely_borderline else ""
        gr = "yes" if c.likely_gold_review else ""
        lines.append(
            f"| {c.task_id} | {c.task_family} | {c.disagreement_score:.2f} | "
            f"{c.n_models} | {labels} | {bl} | {gr} | {c.likely_root_issue} |"
        )
    lines.append("")

    # Family summary
    if report.family_summary:
        _h2("Family Summary")
        for family, stats in sorted(report.family_summary.items()):
            _h3(family)
            _p(f"**Cases:** {stats['n_cases']} | "
               f"**Avg entropy:** {stats['avg_entropy']:.2f} | "
               f"**Borderline:** {stats['n_borderline']} | "
               f"**Gold review:** {stats['n_gold_review']}")
            if stats.get("top_root_issues"):
                root_parts = [f"{k} ({v})" for k, v in stats["top_root_issues"].items()]
                _p(f"**Root issues:** {', '.join(root_parts)}")
            if stats.get("epistemic_distribution"):
                ep_parts = [f"{k} ({v})" for k, v in stats["epistemic_distribution"].items()]
                _p(f"**Epistemic value:** {', '.join(ep_parts)}")

    # Model character summary
    if report.model_character_summary:
        _h2("Model Character Summary")
        for model, patterns in sorted(report.model_character_summary.items()):
            _p(f"**{model}:** {', '.join(patterns)}")

    # Case details
    _h2("Case Details")
    for c in report.cases:
        _h3(f"{c.task_id} ({c.task_family})")
        avg_confidence = (
            f"{c.avg_confidence:.2f}" if c.avg_confidence is not None else "unavailable"
        )
        confidence_spread = (
            f"{c.confidence_spread:.2f}"
            if c.confidence_spread is not None else "unavailable"
        )
        _p(f"**Disagreement score:** {c.disagreement_score:.2f} | "
           f"**Models:** {c.n_models} | "
           f"**Avg confidence:** {avg_confidence} | "
           f"**Confidence spread:** {confidence_spread} | "
           f"**Confidence eligible:** {c.n_confidence_eligible}/"
           f"{c.n_confidence_observations}")

        # Label distribution
        _p("**Label distribution:**")
        for label, count in sorted(c.label_distribution.items()):
            models_with_label = [p.model for p in c.model_positions if p.label == label]
            lines.append(f"- `{label}` x{count} — {', '.join(models_with_label)}")
        lines.append("")

        # Model positions table
        lines.append("| Model | Label | Confidence | Score | Integrity |")
        lines.append("|-------|-------|------------|-------|-----------|")
        for p in c.model_positions:
            confidence = confidence_value_if_valid(p.confidence, p.confidence_state)
            confidence_text = f"{confidence:.2f}" if confidence is not None else p.confidence_state
            lines.append(
                f"| {p.model} | {p.label} | {confidence_text} | "
                f"{p.total_score:.1f} | {p.reasoning_integrity} |"
            )
        lines.append("")

        # Alternative readings
        if c.plausible_readings:
            _p("**Plausible readings:**")
            for r in c.plausible_readings:
                lines.append(
                    f"- **{r.reading_label}** (plausibility: {r.plausibility}) — "
                    f"{r.description[:120]}"
                )
                for ev in r.evidence[:3]:
                    lines.append(f"  - {ev}")
            lines.append("")

        # Signals
        signals: list[str] = []
        if c.likely_borderline:
            signals.append("BORDERLINE")
        if c.likely_gold_review:
            signals.append("GOLD-REVIEW")
        if signals:
            _p(f"**Signals:** {', '.join(signals)}")

        _p(f"**Root issue:** {c.likely_root_issue} "
           f"(confidence: {c.root_issue_confidence})")
        for ev in c.root_issue_evidence:
            lines.append(f"- {ev}")
        lines.append("")

        _p(f"**Epistemic value:** {c.epistemic_value}")

        if c.model_character_notes:
            _p("**Model character notes:**")
            for note in c.model_character_notes:
                lines.append(f"- {note}")
            lines.append("")

        _p(f"**Review recommendation:** {c.review_recommendation}")

        lines.append("---")
        lines.append("")

    # Footer
    _p("*Gen 5 Disagreement Lab — forensic observation only. No automatic changes "
       "to gold labels, scores, or evaluator rules. All root-issue classifications "
       "are heuristic.*")

    return "\n".join(lines)
