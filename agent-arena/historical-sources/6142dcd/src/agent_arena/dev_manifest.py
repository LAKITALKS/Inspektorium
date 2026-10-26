"""Private development-pool manifest tooling (Phase 6.1).

Supports the curator-controlled private development manifest without ever requiring
the real one in-repo. Provides:

- deterministic canonical serialization,
- a **salted** cryptographic commitment (SHA-256 over ``salt || canonical_bytes``),
- schema/aggregate validation of a manifest dict,
- a minimal public projection that strips all case identities and the salt,
- leakage guards asserting the public side carries no canonical/blind ids or salt.

Why salted: the canonical case universe is small and the aggregate label composition
is public, so a plain unsalted digest of the manifest would enable an offline
enumeration/membership attack. A ≥32-byte private random salt (kept outside Git with
the private manifest) makes the public commitment membership-hiding. Public
verification (without the salt) cannot reveal membership; private verification (with
the salt) can confirm the manifest is unchanged.

The PRIVATE manifest (with canonical ids) and the salt live outside Git. The PUBLIC
tracked manifest stores only: opaque manifest id, commitment algorithm+version,
commitment value, aggregate label counts, total, provisioning status. This module is
deterministic, offline, and makes no model calls. See
`analysis/phase6_1_confidence_protocol/private_manifest_schema.json`.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from collections.abc import Mapping

SCHEMA_VERSION = "6.1.0"
EXCLUSION_RULE_ID = "active_and_not_holdout_eligible"
PENDING_SENTINEL = "PENDING_CURATOR_PROVISIONING"

COMMITMENT_ALGORITHM = "salted-sha256"
COMMITMENT_VERSION = "v1"
SALT_MIN_BYTES = 32

FROZEN_AGGREGATE = {
    "solid": 8,
    "overclaim": 15,
    "correlation_vs_causation": 2,
    "mechanism_vs_evidence": 2,
    "total": 27,
}
GOLD_LABELS = ("solid", "overclaim", "correlation_vs_causation", "mechanism_vs_evidence")
STRATA = ("clear", "borderline", "development_only")

_MANIFEST_ID_RE = re.compile(r"^AA-DEVPOOL-[0-9]{3,6}$")
_DEV_ID_RE = re.compile(r"^DEV-[0-9]{3}$")
_CANONICAL_ID_RE = re.compile(r"^study-forensics-[0-9]+$")

# Keys that must never appear anywhere in the PUBLIC projection.
_PUBLIC_FORBIDDEN_KEYS = ("cases", "canonical_id", "canonical_ids", "biaa_id",
                          "biaa", "hld", "holdout_map", "mapping", "salt", "salt_hex")


class CommitmentError(ValueError):
    """Raised for an invalid salt or commitment operation."""


# ---------------------------------------------------------------------------
# Canonical serialization + salted commitment
# ---------------------------------------------------------------------------

def canonical_serialization(manifest: Mapping) -> str:
    """Deterministic JSON serialization (sorted keys, tight separators)."""
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def generate_salt(nbytes: int = SALT_MIN_BYTES) -> bytes:
    """Return a cryptographically random salt of at least 32 bytes."""
    if nbytes < SALT_MIN_BYTES:
        raise CommitmentError(f"salt must be >= {SALT_MIN_BYTES} bytes")
    return secrets.token_bytes(nbytes)


def salt_to_hex(salt: bytes) -> str:
    return salt.hex()


def salt_from_hex(salt_hex: str) -> bytes:
    salt = bytes.fromhex(salt_hex)
    if len(salt) < SALT_MIN_BYTES:
        raise CommitmentError(f"salt must be >= {SALT_MIN_BYTES} bytes")
    return salt


def commitment(manifest: Mapping, salt: bytes) -> str:
    """Salted commitment = SHA-256( salt || canonical_manifest_bytes ), hex.

    The salt must be at least 32 bytes and is never stored in the public side.
    """
    if not isinstance(salt, (bytes, bytearray)) or len(salt) < SALT_MIN_BYTES:
        raise CommitmentError(f"salt must be >= {SALT_MIN_BYTES} random bytes")
    h = hashlib.sha256()
    h.update(bytes(salt))
    h.update(canonical_serialization(manifest).encode("utf-8"))
    return h.hexdigest()


def verify_commitment(manifest: Mapping, salt: bytes, commitment_value: str) -> bool:
    """True iff the salted commitment of (manifest, salt) equals commitment_value."""
    return secrets.compare_digest(commitment(manifest, salt), commitment_value)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_manifest(manifest: Mapping) -> list[str]:
    """Validate a PRIVATE manifest dict against the frozen schema. [] == valid.

    Error messages are structural (counts/indices/fields) and never echo a
    canonical/dev id value.
    """
    errors: list[str] = []

    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    mid = manifest.get("manifest_id", "")
    if not isinstance(mid, str) or not _MANIFEST_ID_RE.match(mid):
        errors.append("manifest_id must match ^AA-DEVPOOL-[0-9]{3,6}$")
    if manifest.get("exclusion_rule_id") != EXCLUSION_RULE_ID:
        errors.append(f"exclusion_rule_id must be {EXCLUSION_RULE_ID!r}")

    agg = manifest.get("aggregate")
    if agg != FROZEN_AGGREGATE:
        errors.append(f"aggregate must equal frozen {FROZEN_AGGREGATE}")

    cases = manifest.get("cases")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        return errors
    if len(cases) != FROZEN_AGGREGATE["total"]:
        errors.append(f"cases must have exactly {FROZEN_AGGREGATE['total']} entries, got {len(cases)}")

    dev_ids: set[str] = set()
    canon_ids: set[str] = set()
    label_counts = {lbl: 0 for lbl in GOLD_LABELS}
    for i, c in enumerate(cases):
        if not isinstance(c, Mapping):
            errors.append(f"cases[{i}] must be an object")
            continue
        dev = c.get("dev_id", "")
        can = c.get("canonical_id", "")
        lbl = c.get("gold_label", "")
        gct = c.get("gold_case_type", "")
        strat = c.get("stratum", "")
        if not isinstance(dev, str) or not _DEV_ID_RE.match(dev):
            errors.append(f"cases[{i}].dev_id must match ^DEV-[0-9]{{3}}$")
        elif dev in dev_ids:
            errors.append(f"cases[{i}].dev_id is a duplicate")
        else:
            dev_ids.add(dev)
        if not isinstance(can, str) or not _CANONICAL_ID_RE.match(can):
            errors.append(f"cases[{i}].canonical_id must match ^study-forensics-[0-9]+$")
        elif can in canon_ids:
            errors.append(f"cases[{i}].canonical_id is a duplicate")
        else:
            canon_ids.add(can)
        if lbl not in GOLD_LABELS:
            errors.append(f"cases[{i}].gold_label invalid")
        else:
            label_counts[lbl] += 1
        if gct not in ("clear", "borderline"):
            errors.append(f"cases[{i}].gold_case_type invalid")
        if strat not in STRATA:
            errors.append(f"cases[{i}].stratum invalid")

    for lbl in GOLD_LABELS:
        if label_counts[lbl] != FROZEN_AGGREGATE[lbl]:
            errors.append(f"label count mismatch for {lbl}: "
                          f"{label_counts[lbl]} != {FROZEN_AGGREGATE[lbl]}")
    return errors


# ---------------------------------------------------------------------------
# Public projection + leakage guards
# ---------------------------------------------------------------------------

def public_projection(manifest: Mapping, commitment_value: str | None = None) -> dict:
    """Project a private manifest to the minimal PUBLIC tracked side.

    Contains only: schema/artifact tags, opaque manifest id, commitment
    algorithm+version+value, aggregate, and status. No cases, no salt, no ids.
    ``commitment_value`` defaults to the PENDING sentinel.
    """
    cv = commitment_value or PENDING_SENTINEL
    provisioned = cv != PENDING_SENTINEL
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact": "development_pool_public_manifest",
        "manifest_id": manifest.get("manifest_id"),
        "commitment_algorithm": COMMITMENT_ALGORITHM,
        "commitment_version": COMMITMENT_VERSION,
        "commitment": cv,
        "aggregate": dict(FROZEN_AGGREGATE),
        "status": ("aggregate_frozen; identity_provisioned" if provisioned
                   else "aggregate_frozen; identity_pending_provisioning"),
    }


def _iter_strings(obj: object):
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            yield str(k)
            yield from _iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _iter_strings(v)
    elif isinstance(obj, str):
        yield obj


def assert_public_clean(public: Mapping) -> list[str]:
    """Return errors if the public projection leaks identities or salt. [] == clean."""
    errors: list[str] = []

    def _scan_keys(obj):
        if isinstance(obj, Mapping):
            for k, v in obj.items():
                if str(k).lower() in _PUBLIC_FORBIDDEN_KEYS:
                    errors.append(f"forbidden key in public manifest: {k}")
                _scan_keys(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                _scan_keys(v)

    _scan_keys(public)
    for s in _iter_strings(public):
        if _CANONICAL_ID_RE.match(s):
            errors.append("canonical id leaked in public manifest")
        if re.search(r"\bBIAA-[0-9]+", s, re.IGNORECASE):
            errors.append("BIAA id leaked in public manifest")
    return errors


def verify_public_against_private(public: Mapping, private: Mapping, salt: bytes) -> list[str]:
    """Check the public manifest matches the private one (with salt) and is provisioned.

    Errors if: aggregate mismatch, commitment still PENDING, or the salted commitment
    of the private manifest does not equal the public commitment.
    """
    errors: list[str] = []
    if public.get("aggregate") != FROZEN_AGGREGATE:
        errors.append("public aggregate does not equal frozen aggregate")
    cv = public.get("commitment")
    if cv == PENDING_SENTINEL:
        errors.append("commitment is still PENDING_CURATOR_PROVISIONING (Phase 6.2 gate not satisfied)")
    elif not verify_commitment(private, salt, cv):
        errors.append("public commitment does not match private manifest + salt")
    return errors


_COMMITMENT_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_public_manifest_state(public: Mapping) -> list[str]:
    """Enforce that the public manifest is in exactly one valid paired state. [] == valid.

    Valid pairs only:
      - commitment == PENDING sentinel  ↔  status contains "pending";
      - commitment == 64-hex sha256     ↔  status contains "provisioned".
    Any other commitment value, or a mismatched commitment/status pairing, is an error.
    """
    errors: list[str] = []
    cv = public.get("commitment")
    status = str(public.get("status", "")).lower()
    if cv == PENDING_SENTINEL:
        if "pending" not in status:
            errors.append("PENDING commitment must pair with a pending-provisioning status")
    elif isinstance(cv, str) and _COMMITMENT_HEX_RE.match(cv):
        if "provisioned" not in status:
            errors.append("64-hex commitment must pair with a provisioned status")
    else:
        errors.append("commitment must be the PENDING sentinel or a 64-hex sha256 digest")
    return errors
