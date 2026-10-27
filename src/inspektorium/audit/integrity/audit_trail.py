"""Gen 6 Audit Trail — decision governance layer of the Inspektorium audit runtime.

Provides structured logging and querying of human decisions on pipeline
recommendations. Every decision is a first-class artifact: gold-review
outcomes, calibration acceptance/rejection, routing overrides, caseforge
reviews, and disagreement resolutions.

v0.6.11.1 (Gen 6.1): Upstream dependency / error propagation hardening.
Each decision can now explicitly document its upstream basis, dependency
confidence, propagation risk, and whether the reviewer overrode the
upstream recommendation.

Does NOT make decisions. Only records and summarizes them.

Persistence: local JSONL file (decisions.jsonl), same pattern as journal.

Answers:
- Which proposals were accepted, rejected, deferred?
- Which modules produce the most useful recommendations?
- Which gold reviews led to actual label changes?
- Where do deferred decisions accumulate?
- What is the overall acceptance rate per module?
- (Gen 6.1) Which decisions relied on weak upstream signals?
- (Gen 6.1) Where did error propagation chains form?
- (Gen 6.1) Where did reviewers override upstream recommendations?
"""

from __future__ import annotations

import json
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from inspektorium.audit.schemas import (
    AuditSummary,
    DecisionEntry,
    DependencySummary,
)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

_DEFAULT_DIR = ".inspektorium"
_DECISIONS_FILE = "decisions.jsonl"

# Valid values
DECISION_TYPES = {
    "gold_review_decision",
    "category_refinement_decision",
    "routing_decision",
    "case_candidate_review",
    "calibration_proposal_decision",
    "disagreement_resolution",
    "workflow_note",
}

DECISION_OUTCOMES = {
    "accepted",
    "rejected",
    "deferred",
    "partially_accepted",
}

TARGET_KINDS = {
    "case",
    "category",
    "model",
    "route",
    "proposal",
    "candidate",
    "workflow",
}

SOURCE_MODULES = {
    "calibrate",
    "caseforge",
    "router",
    "disagreement_lab",
    "insights",
    "manual",
}


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _decisions_path(base_dir: str | Path | None = None) -> Path:
    base = Path(base_dir) if base_dir else Path(_DEFAULT_DIR)
    _ensure_dir(base)
    return base / _DECISIONS_FILE


def generate_decision_id() -> str:
    """Generate a unique decision ID."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short = uuid.uuid4().hex[:6]
    return f"dec_{ts}_{short}"


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def log_decision(
    entry: DecisionEntry,
    base_dir: str | Path | None = None,
) -> Path:
    """Append a single decision entry to the decisions file.

    Returns the file path.
    """
    # Fill timestamp if missing
    if not entry.timestamp:
        entry.timestamp = datetime.now(timezone.utc).isoformat()

    # Fill decision_id if missing
    if not entry.decision_id:
        entry.decision_id = generate_decision_id()

    path = _decisions_path(base_dir)
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry.model_dump_json() + "\n")
    return path


def log_decisions(
    entries: list[DecisionEntry],
    base_dir: str | Path | None = None,
) -> Path:
    """Append multiple decision entries. Returns the file path."""
    path = _decisions_path(base_dir)
    now = datetime.now(timezone.utc).isoformat()
    with open(path, "a", encoding="utf-8") as f:
        for entry in entries:
            if not entry.timestamp:
                entry.timestamp = now
            if not entry.decision_id:
                entry.decision_id = generate_decision_id()
            f.write(entry.model_dump_json() + "\n")
    return path


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def read_decisions(base_dir: str | Path | None = None) -> list[DecisionEntry]:
    """Read all decision entries from the JSONL file."""
    path = _decisions_path(base_dir)
    if not path.exists():
        return []
    entries: list[DecisionEntry] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            entries.append(DecisionEntry(**data))
    return entries


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def query_by_type(
    decision_type: str,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return all decisions of a specific type."""
    return [d for d in read_decisions(base_dir) if d.decision_type == decision_type]


def query_by_target(
    target: str,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return all decisions for a specific target."""
    return [d for d in read_decisions(base_dir) if d.target == target]


def query_by_source(
    source_module: str,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return all decisions from a specific source module."""
    return [d for d in read_decisions(base_dir) if d.source_module == source_module]


def query_by_decision(
    decision: str,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return all decisions with a specific outcome (accepted/rejected/etc)."""
    return [d for d in read_decisions(base_dir) if d.decision == decision]


def query_by_reviewer(
    reviewer: str,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return all decisions by a specific reviewer."""
    return [d for d in read_decisions(base_dir) if d.reviewer == reviewer]


def query_recent(
    n: int = 10,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return the N most recent decisions (by file order, newest last)."""
    all_decisions = read_decisions(base_dir)
    return all_decisions[-n:] if len(all_decisions) > n else all_decisions


# ---------------------------------------------------------------------------
# Summary / analytics
# ---------------------------------------------------------------------------

def build_summary(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
    recent_n: int = 10,
) -> AuditSummary:
    """Build an aggregated summary of all decisions.

    Args:
        decisions: Pre-loaded decisions. If None, reads from disk.
        base_dir: Base directory for decisions file.
        recent_n: Number of recent decisions to include.
    """
    if decisions is None:
        decisions = read_decisions(base_dir)

    if not decisions:
        return AuditSummary(
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    n = len(decisions)

    # By type
    by_type = Counter(d.decision_type for d in decisions)

    # By decision outcome
    by_decision = Counter(d.decision for d in decisions)

    # By source module
    by_source = Counter(d.source_module for d in decisions if d.source_module)

    # Acceptance rate
    accepted = by_decision.get("accepted", 0) + by_decision.get("partially_accepted", 0)
    rejected = by_decision.get("rejected", 0)
    total_resolved = accepted + rejected
    acceptance_rate = round(accepted / total_resolved, 3) if total_resolved > 0 else 0.0

    # Most active targets
    target_ctr = Counter(d.target for d in decisions if d.target)
    most_active = [t for t, _ in target_ctr.most_common(10)]

    # Deferred count
    deferred = by_decision.get("deferred", 0)

    # Recent
    recent = decisions[-recent_n:] if len(decisions) > recent_n else decisions[:]

    return AuditSummary(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_decisions=n,
        by_type=dict(by_type),
        by_decision=dict(by_decision),
        by_source_module=dict(by_source),
        acceptance_rate=acceptance_rate,
        most_active_targets=most_active,
        deferred_count=deferred,
        recent_decisions=recent,
    )


def module_effectiveness(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, dict]:
    """Analyze which source modules produce the most accepted proposals.

    Returns: {module: {total, accepted, rejected, deferred, acceptance_rate}}
    """
    if decisions is None:
        decisions = read_decisions(base_dir)

    by_module: dict[str, list[DecisionEntry]] = defaultdict(list)
    for d in decisions:
        if d.source_module:
            by_module[d.source_module].append(d)

    result: dict[str, dict] = {}
    for module, mod_decisions in sorted(by_module.items()):
        outcomes = Counter(d.decision for d in mod_decisions)
        total = len(mod_decisions)
        accepted = outcomes.get("accepted", 0) + outcomes.get("partially_accepted", 0)
        rejected = outcomes.get("rejected", 0)
        deferred = outcomes.get("deferred", 0)
        resolved = accepted + rejected
        rate = round(accepted / resolved, 3) if resolved > 0 else 0.0

        result[module] = {
            "total": total,
            "accepted": accepted,
            "rejected": rejected,
            "deferred": deferred,
            "acceptance_rate": rate,
        }

    return result


def label_change_history(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return decisions that resulted in actual state changes.

    Filters for decisions where before_state and after_state differ.
    """
    if decisions is None:
        decisions = read_decisions(base_dir)

    return [
        d for d in decisions
        if d.before_state and d.after_state and d.before_state != d.after_state
    ]


def deferred_decisions(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return all deferred decisions — pending human follow-up."""
    if decisions is None:
        decisions = read_decisions(base_dir)

    return [d for d in decisions if d.decision == "deferred"]


# ---------------------------------------------------------------------------
# Report rendering — Markdown
# ---------------------------------------------------------------------------

def render_audit_summary(summary: AuditSummary) -> str:
    """Render AuditSummary as nüchtern, operative Markdown."""
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

    _h1("Inspektorium — Gen 6 Audit Trail Summary")
    _p(f"**Generated:** {summary.generated_at}  ")
    _p(f"**Total decisions:** {summary.total_decisions}")

    if summary.total_decisions == 0:
        _p("_No decisions recorded._")
        return "\n".join(lines)

    _p(f"**Acceptance rate:** {summary.acceptance_rate:.0%}")
    _p(f"**Deferred:** {summary.deferred_count}")

    # By decision outcome
    _h2("Decision Outcomes")
    lines.append("| Outcome | Count |")
    lines.append("|---------|-------|")
    for outcome, count in sorted(summary.by_decision.items(), key=lambda x: -x[1]):
        lines.append(f"| {outcome} | {count} |")
    lines.append("")

    # By type
    _h2("Decision Types")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for dtype, count in sorted(summary.by_type.items(), key=lambda x: -x[1]):
        lines.append(f"| {dtype} | {count} |")
    lines.append("")

    # By source module
    if summary.by_source_module:
        _h2("Source Modules")
        lines.append("| Module | Count |")
        lines.append("|--------|-------|")
        for module, count in sorted(summary.by_source_module.items(), key=lambda x: -x[1]):
            lines.append(f"| {module} | {count} |")
        lines.append("")

    # Most active targets
    if summary.most_active_targets:
        _h2("Most Active Targets")
        for t in summary.most_active_targets[:10]:
            lines.append(f"- {t}")
        lines.append("")

    # Recent decisions
    if summary.recent_decisions:
        _h2("Recent Decisions")
        lines.append("| ID | Type | Target | Decision | Source | Reviewer |")
        lines.append("|----|------|--------|----------|--------|----------|")
        for d in reversed(summary.recent_decisions):
            lines.append(
                f"| {d.decision_id[:20]} | {d.decision_type} | "
                f"{d.target} | **{d.decision}** | {d.source_module} | "
                f"{d.reviewer or '—'} |"
            )
        lines.append("")

    # Footer
    lines.append("---")
    _p("*Gen 6 Audit Trail — decision records only. No automatic changes.*")

    return "\n".join(lines)


def render_module_effectiveness(effectiveness: dict[str, dict]) -> str:
    """Render module effectiveness report as Markdown."""
    lines: list[str] = []
    lines.append("## Module Effectiveness")
    lines.append("")

    if not effectiveness:
        lines.append("_No module-level data available._")
        return "\n".join(lines)

    lines.append("| Module | Total | Accepted | Rejected | Deferred | Rate |")
    lines.append("|--------|-------|----------|----------|----------|------|")
    for module, stats in sorted(effectiveness.items()):
        lines.append(
            f"| {module} | {stats['total']} | {stats['accepted']} | "
            f"{stats['rejected']} | {stats['deferred']} | "
            f"{stats['acceptance_rate']:.0%} |"
        )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gen 6.1: Upstream dependency / error propagation analysis
# ---------------------------------------------------------------------------

def _has_upstream(d: DecisionEntry) -> bool:
    """Check whether a decision has any upstream dependency info."""
    return bool(d.upstream_module or d.upstream_reference
                or d.upstream_dependency_summary or d.upstream_chain)


def build_dependency_summary(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> DependencySummary:
    """Build an aggregated dependency / governance summary.

    Answers:
    - Which decisions have upstream dependencies?
    - What confidence levels do dependencies have?
    - How often do reviewers override upstream signals?
    - Which weak-basis decisions were accepted anyway?
    - Where are potential error propagation chains?
    - Which upstream modules get rejected most?
    """
    if decisions is None:
        decisions = read_decisions(base_dir)

    if not decisions:
        return DependencySummary(
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    n = len(decisions)
    with_upstream = [d for d in decisions if _has_upstream(d)]
    n_upstream = len(with_upstream)

    # By upstream module
    by_upstream = Counter(
        d.upstream_module for d in with_upstream if d.upstream_module
    )

    # By dependency confidence
    by_conf = Counter(
        d.dependency_confidence for d in with_upstream if d.dependency_confidence
    )

    # By propagation risk
    by_risk = Counter(
        d.propagation_risk_level for d in with_upstream if d.propagation_risk_level
    )

    # Overrides
    overrides = [d for d in with_upstream if d.review_override]
    override_count = len(overrides)
    override_rate = (
        round(override_count / n_upstream, 3) if n_upstream > 0 else 0.0
    )

    # Weak-basis accepted: decisions accepted despite low/heuristic confidence
    weak_accepted = [
        d for d in with_upstream
        if d.dependency_confidence in ("low", "heuristic")
        and d.decision in ("accepted", "partially_accepted")
    ]

    # Risky acceptances: accepted with high propagation risk
    risky = [
        d for d in with_upstream
        if d.propagation_risk_level == "high"
        and d.decision in ("accepted", "partially_accepted")
    ]

    # Propagation chains: detect decisions that share targets across modules
    # (i.e., a target was acted on by multiple modules in sequence)
    chains = _detect_propagation_chains(decisions)

    # Rejected upstream patterns: which modules' signals get rejected most?
    rejected_upstream = Counter(
        d.upstream_module for d in with_upstream
        if d.decision == "rejected" and d.upstream_module
    )

    return DependencySummary(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_decisions=n,
        decisions_with_upstream=n_upstream,
        by_upstream_module=dict(by_upstream),
        by_dependency_confidence=dict(by_conf),
        by_propagation_risk=dict(by_risk),
        override_count=override_count,
        override_rate=override_rate,
        weak_basis_accepted=len(weak_accepted),
        risky_acceptances=risky,
        propagation_chains=chains,
        rejected_upstream_patterns=dict(rejected_upstream),
    )


def _detect_propagation_chains(
    decisions: list[DecisionEntry],
) -> list[dict]:
    """Detect potential error propagation chains.

    A chain is detected when:
    - Multiple decisions share the same target
    - They come from different upstream modules
    - At least one was accepted, creating a downstream dependency

    Returns list of chain descriptors.
    """
    # Group decisions by target
    by_target: dict[str, list[DecisionEntry]] = defaultdict(list)
    for d in decisions:
        if d.target:
            by_target[d.target].append(d)

    chains: list[dict] = []
    for target, target_decisions in sorted(by_target.items()):
        if len(target_decisions) < 2:
            continue

        # Check if multiple modules touched this target
        modules = set()
        for d in target_decisions:
            if d.upstream_module:
                modules.add(d.upstream_module)
            if d.source_module:
                modules.add(d.source_module)

        if len(modules) < 2:
            continue

        # Has at least one accepted decision?
        has_accepted = any(
            d.decision in ("accepted", "partially_accepted")
            for d in target_decisions
        )
        if not has_accepted:
            continue

        # Check for risk amplification
        risk_levels = [
            d.propagation_risk_level for d in target_decisions
            if d.propagation_risk_level
        ]
        has_risk = any(r in ("medium", "high") for r in risk_levels)

        # Check for weak links
        weak_links = [
            d for d in target_decisions
            if d.dependency_confidence in ("low", "heuristic")
        ]

        chain = {
            "target": target,
            "n_decisions": len(target_decisions),
            "modules_involved": sorted(modules),
            "has_risk_signal": has_risk,
            "n_weak_links": len(weak_links),
            "decision_ids": [d.decision_id for d in target_decisions],
        }
        chains.append(chain)

    return chains


def trace_decision(
    decision_id: str,
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> dict | None:
    """Build a full trace for a single decision.

    Returns a dict with the decision, its upstream chain, related decisions
    on the same target, and risk assessment. Returns None if not found.
    """
    if decisions is None:
        decisions = read_decisions(base_dir)

    # Find the decision
    target_dec = None
    for d in decisions:
        if d.decision_id == decision_id:
            target_dec = d
            break

    if target_dec is None:
        return None

    # Find related decisions (same target)
    related = [
        d for d in decisions
        if d.target == target_dec.target and d.decision_id != decision_id
    ]

    # Build upstream chain description
    chain_steps = []
    if target_dec.upstream_chain:
        for step in target_dec.upstream_chain:
            chain_steps.append({
                "module": step.module,
                "reference": step.reference,
                "description": step.description,
                "confidence": step.confidence,
            })
    elif target_dec.upstream_module:
        chain_steps.append({
            "module": target_dec.upstream_module,
            "reference": target_dec.upstream_reference,
            "description": target_dec.upstream_dependency_summary,
            "confidence": target_dec.dependency_confidence,
        })

    # Risk assessment
    risk_factors: list[str] = []
    if target_dec.dependency_confidence in ("low", "heuristic"):
        risk_factors.append(
            f"Upstream dependency confidence is '{target_dec.dependency_confidence}'"
        )
    if target_dec.propagation_risk_level in ("medium", "high"):
        risk_factors.append(
            f"Propagation risk level: {target_dec.propagation_risk_level}"
        )
    if target_dec.review_override:
        risk_factors.append("Reviewer overrode upstream recommendation")
    if target_dec.dependency_risk_note:
        risk_factors.append(f"Risk note: {target_dec.dependency_risk_note}")

    return {
        "decision": target_dec,
        "upstream_chain": chain_steps,
        "related_decisions": related,
        "n_related": len(related),
        "risk_factors": risk_factors,
        "has_upstream": _has_upstream(target_dec),
        "is_override": target_dec.review_override,
    }


def query_weak_basis_decisions(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return decisions with low or heuristic dependency confidence."""
    if decisions is None:
        decisions = read_decisions(base_dir)
    return [
        d for d in decisions
        if d.dependency_confidence in ("low", "heuristic")
    ]


def query_overrides(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return decisions where the reviewer overrode the upstream signal."""
    if decisions is None:
        decisions = read_decisions(base_dir)
    return [d for d in decisions if d.review_override]


def query_risky_accepted(
    decisions: list[DecisionEntry] | None = None,
    base_dir: str | Path | None = None,
) -> list[DecisionEntry]:
    """Return accepted decisions with high propagation risk."""
    if decisions is None:
        decisions = read_decisions(base_dir)
    return [
        d for d in decisions
        if d.propagation_risk_level == "high"
        and d.decision in ("accepted", "partially_accepted")
    ]


# ---------------------------------------------------------------------------
# Gen 6.1: Dependency report rendering
# ---------------------------------------------------------------------------

def render_dependency_summary(summary: DependencySummary) -> str:
    """Render DependencySummary as nüchtern, operative Markdown."""
    lines: list[str] = []

    def _h2(t: str) -> None:
        lines.append(f"## {t}")
        lines.append("")

    def _h3(t: str) -> None:
        lines.append(f"### {t}")
        lines.append("")

    def _p(t: str) -> None:
        lines.append(t)
        lines.append("")

    _h2("Upstream Dependency Summary")

    if summary.total_decisions == 0:
        _p("_No decisions recorded._")
        return "\n".join(lines)

    _p(f"**Total decisions:** {summary.total_decisions}")
    _p(f"**With upstream dependency:** {summary.decisions_with_upstream}")
    _p(f"**Override rate:** {summary.override_rate:.0%} "
       f"({summary.override_count} overrides)")
    _p(f"**Weak-basis accepted:** {summary.weak_basis_accepted}")

    # By upstream module
    if summary.by_upstream_module:
        _h3("By Upstream Module")
        lines.append("| Module | Count |")
        lines.append("|--------|-------|")
        for module, count in sorted(summary.by_upstream_module.items(),
                                     key=lambda x: -x[1]):
            lines.append(f"| {module} | {count} |")
        lines.append("")

    # By dependency confidence
    if summary.by_dependency_confidence:
        _h3("Dependency Confidence Distribution")
        lines.append("| Confidence | Count |")
        lines.append("|------------|-------|")
        for conf, count in sorted(summary.by_dependency_confidence.items()):
            lines.append(f"| {conf} | {count} |")
        lines.append("")

    # By propagation risk
    if summary.by_propagation_risk:
        _h3("Propagation Risk Distribution")
        lines.append("| Risk Level | Count |")
        lines.append("|------------|-------|")
        for risk, count in sorted(summary.by_propagation_risk.items()):
            lines.append(f"| {risk} | {count} |")
        lines.append("")

    # Rejected upstream patterns
    if summary.rejected_upstream_patterns:
        _h3("Rejected Upstream Patterns")
        _p("Modules whose signals are frequently rejected:")
        lines.append("| Module | Rejected |")
        lines.append("|--------|----------|")
        for module, count in sorted(summary.rejected_upstream_patterns.items(),
                                     key=lambda x: -x[1]):
            lines.append(f"| {module} | {count} |")
        lines.append("")

    # Propagation chains
    if summary.propagation_chains:
        _h3("Potential Propagation Chains")
        for chain in summary.propagation_chains:
            risk_tag = " **[RISK]**" if chain.get("has_risk_signal") else ""
            weak_tag = (f" ({chain['n_weak_links']} weak link(s))"
                        if chain.get("n_weak_links") else "")
            _p(f"- **{chain['target']}**: {chain['n_decisions']} decisions, "
               f"modules: {', '.join(chain['modules_involved'])}"
               f"{risk_tag}{weak_tag}")
    else:
        _p("_No propagation chains detected._")

    # Risky acceptances
    if summary.risky_acceptances:
        _h3("Risky Acceptances")
        _p("Decisions accepted despite high propagation risk:")
        for d in summary.risky_acceptances:
            _p(f"- [{d.decision_id}] {d.target} ({d.decision_type}) — "
               f"risk: {d.propagation_risk_level}, "
               f"confidence: {d.dependency_confidence}")

    lines.append("---")
    _p("*Gen 6.1 — upstream dependency analysis. All risk classifications "
       "are heuristic. No automatic corrections.*")

    return "\n".join(lines)


def render_trace(trace: dict) -> str:
    """Render a decision trace as Markdown."""
    lines: list[str] = []

    def _p(t: str) -> None:
        lines.append(t)
        lines.append("")

    d = trace["decision"]
    lines.append(f"## Decision Trace: {d.decision_id}")
    lines.append("")

    _p(f"**Type:** {d.decision_type}")
    _p(f"**Target:** {d.target} ({d.target_kind})")
    _p(f"**Decision:** {d.decision}")
    _p(f"**Source module:** {d.source_module}")
    if d.reviewer:
        _p(f"**Reviewer:** {d.reviewer}")
    if d.reason:
        _p(f"**Reason:** {d.reason}")

    # Upstream info
    if trace["has_upstream"]:
        lines.append("### Upstream Dependency")
        lines.append("")
        if d.upstream_module:
            _p(f"**Upstream module:** {d.upstream_module}")
        if d.upstream_reference:
            _p(f"**Upstream reference:** {d.upstream_reference}")
        if d.upstream_dependency_summary:
            _p(f"**Dependency summary:** {d.upstream_dependency_summary}")
        if d.dependency_confidence:
            _p(f"**Dependency confidence:** {d.dependency_confidence}")
        if d.propagation_risk_level:
            _p(f"**Propagation risk:** {d.propagation_risk_level}")
        if d.dependency_risk_note:
            _p(f"**Risk note:** {d.dependency_risk_note}")
        if d.review_override:
            _p("**Override:** Reviewer decided AGAINST upstream recommendation")

    # Upstream chain
    if trace["upstream_chain"]:
        lines.append("### Upstream Chain")
        lines.append("")
        for i, step in enumerate(trace["upstream_chain"], 1):
            _p(f"{i}. **{step['module']}** — {step.get('description', '—')} "
               f"(confidence: {step.get('confidence', '—')})")

    # Risk factors
    if trace["risk_factors"]:
        lines.append("### Risk Factors")
        lines.append("")
        for rf in trace["risk_factors"]:
            lines.append(f"- {rf}")
        lines.append("")

    # Related decisions
    if trace["related_decisions"]:
        lines.append(f"### Related Decisions ({trace['n_related']})")
        lines.append("")
        for rd in trace["related_decisions"]:
            _p(f"- [{rd.decision_id}] {rd.decision_type} — {rd.decision} "
               f"(source: {rd.source_module})")

    return "\n".join(lines)
