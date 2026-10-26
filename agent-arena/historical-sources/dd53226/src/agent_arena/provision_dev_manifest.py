"""Deterministic development-pool provisioning workflow (Phase 6.1 design).

This tool is built now but is intended to run **later, once, in a separate
curator-controlled private execution**. It derives the 27-case development pool from
the tracked active canonical library minus a private list of the 21 holdout-eligible
canonical ids, writes the private manifest and salt outside Git, and emits a clean
public commitment.

Hard privacy guarantee: this module **never** prints or embeds canonical ids,
eligible ids, development ids, or any mapping into stdout, stderr, logs, exception
messages, or return values. Every diagnostic is structural (counts/labels only).
Callers receive an id-free :class:`ProvisioningSummary`; identities exist only inside
the private manifest file written to the caller-supplied out-of-Git path.

In-session use is restricted to SYNTHETIC fixture ids (see tests). Do not run real
provisioning here; do not access internal_only material or the private holdout.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from agent_arena.dev_manifest import (
    EXCLUSION_RULE_ID,
    FROZEN_AGGREGATE,
    GOLD_LABELS,
    SCHEMA_VERSION,
    commitment,
    generate_salt,
    public_projection,
    validate_manifest,
)
from agent_arena.packet_integrity import assert_path_allowed


class ProvisioningError(RuntimeError):
    """Raised on a provisioning failure. Messages are id-free (counts/labels only)."""


@dataclass(frozen=True)
class CaseRec:
    """Minimal case record consumed by provisioning (no free-text/gold content)."""
    canonical_id: str
    gold_label: str
    gold_case_type: str          # "clear" | "borderline"
    is_retired: bool


@dataclass
class ProvisioningSummary:
    """Id-free result. Safe to print/log/return."""
    manifest_id: str
    aggregate: dict
    commitment_algorithm: str
    commitment_version: str
    commitment: str
    private_manifest_path: str
    salt_path: str
    public_manifest_path: str

    def as_dict(self) -> dict:
        return {
            "manifest_id": self.manifest_id,
            "aggregate": self.aggregate,
            "commitment_algorithm": self.commitment_algorithm,
            "commitment_version": self.commitment_version,
            "commitment": self.commitment,
            "wrote_private_manifest": self.private_manifest_path,
            "wrote_salt": self.salt_path,
            "wrote_public_manifest": self.public_manifest_path,
        }


def load_active_library(task_dir: str | Path | None = None) -> list[CaseRec]:
    """Load the tracked canonical library as id-only CaseRecs (no gold text).

    Uses the same discovery as the library harness (includes retired so they can be
    excluded here). Refuses sealed paths. Returns records; prints nothing.
    """
    from agent_arena.run_library import TASK_DIR, discover_cases, is_retired

    resolved = assert_path_allowed(task_dir) if task_dir is not None else TASK_DIR
    recs: list[CaseRec] = []
    for _path, task in discover_cases(task_dir=Path(resolved), include_retired=True):
        recs.append(CaseRec(
            canonical_id=task.id,
            gold_label=task.gold_label or "",
            gold_case_type=task.gold_case_type or "clear",
            is_retired=is_retired(task),
        ))
    return recs


def derive_development_pool(
    active_library: Iterable[CaseRec],
    eligible_ids: Iterable[str],
    development_only_ids: Iterable[str] = (),
) -> list[dict]:
    """dev pool = (active, non-retired) minus eligible; deterministic DEV ids.

    Returns a list of manifest case dicts (with canonical ids — PRIVATE). Raises
    ProvisioningError (id-free) if the derived aggregate does not match the frozen
    composition. DEV ids are assigned by sorted canonical id for determinism.
    """
    eligible = set(eligible_ids)
    devonly = set(development_only_ids)

    pool = [r for r in active_library if not r.is_retired and r.canonical_id not in eligible]
    pool_sorted = sorted(pool, key=lambda r: r.canonical_id)

    cases: list[dict] = []
    label_counts = {lbl: 0 for lbl in GOLD_LABELS}
    for i, r in enumerate(pool_sorted, start=1):
        if r.gold_label not in GOLD_LABELS:
            raise ProvisioningError(f"case index {i}: gold_label not in frozen taxonomy")
        label_counts[r.gold_label] += 1
        if r.canonical_id in devonly:
            stratum = "development_only"
        elif r.gold_case_type == "borderline":
            stratum = "borderline"
        else:
            stratum = "clear"
        cases.append({
            "dev_id": f"DEV-{i:03d}",
            "canonical_id": r.canonical_id,
            "gold_label": r.gold_label,
            "gold_case_type": r.gold_case_type,
            "stratum": stratum,
        })

    # Aggregate validation — id-free error messages only.
    if len(cases) != FROZEN_AGGREGATE["total"]:
        raise ProvisioningError(
            f"derived pool size {len(cases)} != expected {FROZEN_AGGREGATE['total']}")
    for lbl in GOLD_LABELS:
        if label_counts[lbl] != FROZEN_AGGREGATE[lbl]:
            raise ProvisioningError(
                f"derived {lbl} count {label_counts[lbl]} != expected {FROZEN_AGGREGATE[lbl]}")
    return cases


def build_private_manifest(cases: list[dict], manifest_id: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": manifest_id,
        "exclusion_rule_id": EXCLUSION_RULE_ID,
        "aggregate": dict(FROZEN_AGGREGATE),
        "cases": cases,
    }


# The single tracked public-manifest path this tool is allowed to write.
APPROVED_PUBLIC_MANIFEST_RELPATH = (
    "analysis/phase6_1_confidence_protocol/development_pool_public_manifest.json"
)
# Fixed private artifact filenames written under the approved private output root.
PRIVATE_MANIFEST_FILENAME = "private_manifest.json"
PRIVATE_SALT_FILENAME = "salt.hex"


def _detect_repo_root() -> Path:
    """Repository root, derived from this module's location (not from the environment)."""
    # src/agent_arena/provision_dev_manifest.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_private_output_root(private_output_root, repo_root: Path) -> Path:
    """Validate the curator-approved private output root (structural, not env-inferred).

    Must be an explicitly supplied, absolute path to an existing directory that
    resolves strictly outside the repository (neither the repo root, a descendant of
    it, nor an ancestor of it). The generic sealed-path guard is intentionally NOT
    applied here — the approved private root legitimately lives outside the repo.
    """
    if private_output_root is None:
        raise ProvisioningError("private output root must be explicitly supplied")
    p = Path(private_output_root)
    if not p.is_absolute():
        raise ProvisioningError("private output root must be an absolute path")
    resolved = p.resolve()
    repo = repo_root.resolve()
    if resolved == repo:
        raise ProvisioningError("private output root must not be the repository root")
    if _is_relative_to(resolved, repo):
        raise ProvisioningError("private output root must resolve outside the repository")
    if _is_relative_to(repo, resolved):
        raise ProvisioningError("private output root must not be an ancestor of the repository")
    if not resolved.is_dir():
        raise ProvisioningError("private output root must be an existing curator-approved directory")
    return resolved


def _validate_public_output_path(public_output_path, repo_root: Path) -> Path:
    """Validate the public output path equals the one approved tracked manifest path.

    Prevents caller-expansion to an arbitrary repository file. Resolving equal to the
    approved path also guarantees the output stays inside the repository.
    """
    if public_output_path is None:
        raise ProvisioningError("public output path must be explicitly supplied")
    resolved = Path(public_output_path).resolve()
    approved = (repo_root.resolve() / APPROVED_PUBLIC_MANIFEST_RELPATH).resolve()
    if resolved != approved:
        raise ProvisioningError("public output path must equal the approved tracked public-manifest path")
    return resolved


def run_provisioning(
    active_library: Iterable[CaseRec],
    eligible_ids: Iterable[str],
    private_output_root: str | Path,
    public_output_path: str | Path,
    manifest_id: str = "AA-DEVPOOL-6100",
    development_only_ids: Iterable[str] = (),
    salt: bytes | None = None,
    repo_root: str | Path | None = None,
) -> ProvisioningSummary:
    """Derive, validate, and write the private manifest + salt + public commitment.

    ``private_output_root`` is an explicitly supplied, curator-approved absolute
    directory **outside** the repository; the private manifest and salt are written
    there as ``private_manifest.json`` / ``salt.hex``. ``public_output_path`` must
    equal the single approved tracked public-manifest path inside the repository.
    Returns an id-free summary. Raises ProvisioningError (id-free) on any failure.
    """
    repo = Path(repo_root).resolve() if repo_root is not None else _detect_repo_root()
    priv_root = _validate_private_output_root(private_output_root, repo)
    pub_path = _validate_public_output_path(public_output_path, repo)
    priv_manifest_path = priv_root / PRIVATE_MANIFEST_FILENAME
    salt_path = priv_root / PRIVATE_SALT_FILENAME

    cases = derive_development_pool(active_library, eligible_ids, development_only_ids)
    manifest = build_private_manifest(cases, manifest_id)

    errs = validate_manifest(manifest)
    if errs:
        # Do not echo any id; report only that validation failed and how many issues.
        raise ProvisioningError(f"private manifest failed schema validation ({len(errs)} issue(s))")

    if salt is None:
        salt = generate_salt()
    commit = commitment(manifest, salt)
    public = public_projection(manifest, commitment_value=commit)

    # Write artifacts. The private manifest + salt live under the external private root.
    priv_manifest_path.write_text(json.dumps(manifest, indent=2))
    salt_path.write_text(salt.hex())
    pub_path.write_text(json.dumps(public, indent=2))

    return ProvisioningSummary(
        manifest_id=manifest_id,
        aggregate=dict(FROZEN_AGGREGATE),
        commitment_algorithm=public["commitment_algorithm"],
        commitment_version=public["commitment_version"],
        commitment=commit,
        private_manifest_path=str(priv_manifest_path),
        salt_path=str(salt_path),
        public_manifest_path=str(pub_path),
    )
