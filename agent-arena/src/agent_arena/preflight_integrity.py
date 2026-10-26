"""Prospective production-QA and source-binding controls for Phase-7A.

This module deliberately separates two concepts:

* diagnostic pytest execution, whose result may be inspected offline; and
* the internally selected, fresh canonical QA execution that is the only QA
  evidence eligible for a real Phase-7A adjudication.

The hashes here are integrity checks, not trust credentials.  Production trust
comes from the guarded call path launching the canonical executor itself and
revalidating the exact source state before provider construction.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import os
import platform
import re
import site
import subprocess
import sys
import sysconfig
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


CANONICAL_QA_VERSION = "phase7a-production-qa/v1"
CANONICAL_QA_TEST_PATHS = (
    "tests/test_runtime_contract.py",
    "tests/test_packet_integrity.py",
    "tests/test_output_contract.py",
    "tests/test_confidence_validity.py",
    "tests/test_provider_contract.py",
    "tests/test_provider_runtime.py",
    "tests/test_run_library.py",
    "tests/test_phase7a_boundary_pool.py",
    "tests/test_phase7a_adversarial_pool.py",
    "tests/test_phase7a_perturbation_pool.py",
)
CANONICAL_QA_EXPECTED_COLLECTED = 246
CANONICAL_QA_FLAGS = (
    "--tb=no",
    "-p",
    "no:cacheprovider",
    "-o",
    "addopts=",
)
CANONICAL_QA_TIMEOUT_SECONDS = 3600

# The legacy Phase-7A production scope remains byte-for-byte represented above.
# Condition-aware plans use this fixed, non-caller-selectable superset.  The exact
# count is pinned after the deliberately enumerated Phase-5A test modules are added.
CONDITION_CONTRACT_QA_VERSION = "phase5a-condition-contract-production-qa/v2"
CONDITION_CONTRACT_QA_TEST_PATHS = CANONICAL_QA_TEST_PATHS + (
    "tests/test_condition_contract.py",
    "tests/test_condition_analysis_contract.py",
    "tests/test_scientific_contract_alignment.py",
)
# Deliberate inventory: 246 legacy canonical tests + 66 condition/scientific tests.
CONDITION_CONTRACT_QA_EXPECTED_COLLECTED = 312

# Phase-5B has a separate profile so extending its execution-contract coverage
# cannot change the immutable Phase-5A paired-plan specification fingerprint.
FULL_REPLICATION_QA_VERSION = "phase5b-full-replication-production-qa/v2"
FULL_REPLICATION_QA_TEST_PATHS = CONDITION_CONTRACT_QA_TEST_PATHS + (
    "tests/test_preflight_integrity.py",
    "tests/test_full_replication_contract.py",
)
# Deliberate v2 inventory: 324 prior Phase-5B tests + 44 Phase-2 preflight tests
# + 1 registered consumed-plan migration test.
FULL_REPLICATION_QA_EXPECTED_COLLECTED = 369

QA_PASSED = "QA_EXECUTED_AND_PASSED"
QA_FAILED = "QA_EXECUTED_AND_FAILED"
QA_COULD_NOT_EXECUTE = "QA_COULD_NOT_EXECUTE"
QA_NOT_EXECUTED = "TESTS_NOT_EXECUTED"
QA_NON_AUTHORIZING = "NON_AUTHORIZING_QA"

_QA_KIND = "canonical_pytest_execution"
_QA_PRODUCER = "agent_arena.preflight_integrity.execute_canonical_qa"
_CONDITION_QA_KIND = "condition_contract_canonical_pytest_execution"
_CONDITION_QA_PRODUCER = "agent_arena.preflight_integrity.execute_condition_contract_qa"
_FULL_REPLICATION_QA_KIND = "full_replication_canonical_pytest_execution"
_FULL_REPLICATION_QA_PRODUCER = "agent_arena.preflight_integrity.execute_full_replication_qa"
_CONTROL_ENV_VARS = ("PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS", "PYTEST_PLUGINS")
_MATERIAL_ENVIRONMENT_SCHEMA_VERSION = "agent_arena.material_python_environment/v1"
_MATERIAL_UNTRACKED_PATHS = (
    "conftest.py",
    "sitecustomize.py",
    "usercustomize.py",
    "pytest.ini",
    "tox.ini",
    "setup.cfg",
    ":(glob)*.pth",
    ":(glob)src/**/*.py",
    ":(glob)tests/**/conftest.py",
)
_CRITICAL_MODULES = (
    "agent_arena",
    "agent_arena.phase7a_execution",
    "agent_arena.phase7a_real_run",
    "agent_arena.runtime_contract",
    "agent_arena.robustness_pool",
    "agent_arena.output_contract",
    "agent_arena.run_library",
    "agent_arena.providers.anthropic",
    "agent_arena.condition_analysis",
    "agent_arena.condition_contract",
    "agent_arena.condition_retry",
    "agent_arena.full_replication_contract",
    "agent_arena.full_replication_analysis",
)
_COUNT_KEYS = (
    "tests_collected",
    "tests_passed",
    "tests_failed",
    "tests_errors",
    "tests_skipped",
    "tests_xfailed",
    "tests_xpassed",
    "tests_deselected",
)
_FINGERPRINT_FIELDS = (
    "qa_kind",
    "produced_by",
    "authorization_source",
    "canonical_specification",
    "canonical_specification_fingerprint",
    "command",
    "repository_root",
    "repository_identity",
    "commit",
    "tree",
    "tracked_source_fingerprint",
    "tracked_config_fingerprint",
    "python_executable",
    "python_version",
    "python_prefix",
    "python_base_prefix",
    "python_environment_fingerprint",
    "material_environment",
    "material_environment_fingerprint",
    "package_origins",
    "subprocess_probe",
    "environment_isolation",
    "execution_status",
    "exit_code",
    *_COUNT_KEYS,
    "log_sha256",
)

_PYTEST_COUNT_RE = re.compile(
    r"(\d+)\s+(passed|failed|skipped|error|errors|xfailed|xpassed|deselected)"
)
_PYTEST_COLLECTED_RE = re.compile(r"collected\s+(\d+)\s+item")


def _canon(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fingerprint(value: object) -> str:
    return _sha256(_canon(value).encode("utf-8"))


def canonical_qa_specification() -> dict:
    return {
        "version": CANONICAL_QA_VERSION,
        "pytest_flags": list(CANONICAL_QA_FLAGS),
        "test_paths": list(CANONICAL_QA_TEST_PATHS),
        "expected_collected": CANONICAL_QA_EXPECTED_COLLECTED,
        "required_terminal_state": "all_collected_tests_passed",
        "caller_selectable": False,
    }


def canonical_qa_specification_fingerprint() -> str:
    return _fingerprint(canonical_qa_specification())


def condition_contract_qa_specification() -> dict:
    return {
        "version": CONDITION_CONTRACT_QA_VERSION,
        "pytest_flags": list(CANONICAL_QA_FLAGS),
        "test_paths": list(CONDITION_CONTRACT_QA_TEST_PATHS),
        "expected_collected": CONDITION_CONTRACT_QA_EXPECTED_COLLECTED,
        "required_terminal_state": "all_collected_tests_passed",
        "caller_selectable": False,
        "supplements_legacy_scope": True,
    }


def condition_contract_qa_specification_fingerprint() -> str:
    return _fingerprint(condition_contract_qa_specification())


def full_replication_qa_specification() -> dict:
    return {
        "version": FULL_REPLICATION_QA_VERSION,
        "pytest_flags": list(CANONICAL_QA_FLAGS),
        "test_paths": list(FULL_REPLICATION_QA_TEST_PATHS),
        "expected_collected": FULL_REPLICATION_QA_EXPECTED_COLLECTED,
        "required_terminal_state": "all_collected_tests_passed",
        "caller_selectable": False,
        "supplements_condition_contract_scope": True,
    }


def full_replication_qa_specification_fingerprint() -> str:
    return _fingerprint(full_replication_qa_specification())


def condition_contract_qa_command(python_executable: str) -> list[str]:
    return [
        python_executable,
        "-m",
        "pytest",
        *CANONICAL_QA_FLAGS,
        *CONDITION_CONTRACT_QA_TEST_PATHS,
    ]


def full_replication_qa_command(python_executable: str) -> list[str]:
    return [
        python_executable,
        "-m",
        "pytest",
        *CANONICAL_QA_FLAGS,
        *FULL_REPLICATION_QA_TEST_PATHS,
    ]


def canonical_qa_command(python_executable: str) -> list[str]:
    return [
        python_executable,
        "-m",
        "pytest",
        *CANONICAL_QA_FLAGS,
        *CANONICAL_QA_TEST_PATHS,
    ]


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=False,
        check=False,
    )


def _git_text(root: Path, *args: str) -> str:
    proc = _run_git(root, *args)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or b"").decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or f"git {' '.join(args)} failed")
    return proc.stdout.decode("utf-8", errors="strict").strip()


def _critical_module_origins() -> dict[str, str]:
    origins: dict[str, str] = {}
    for name in _CRITICAL_MODULES:
        module = importlib.import_module(name)
        origin = getattr(module, "__file__", None)
        origins[name] = str(Path(origin).resolve()) if origin else ""
    return origins


def _python_executable_identity() -> str:
    """Preserve the invoked interpreter path; resolving would erase a venv symlink."""
    return str(Path(sys.executable).absolute())


def _canonical_sys_path(
    entries: list[str],
    *,
    repository_root: Path,
    invoked_executable: Path,
) -> tuple[list[str], list[dict]]:
    """Normalize only launcher representations while preserving effective order."""
    normalized: list[str] = []
    observations: list[dict] = []
    launcher_dir = invoked_executable.absolute().parent.resolve()
    for index, raw in enumerate(entries):
        if raw in ("", "."):
            resolved = repository_root
        else:
            candidate = Path(raw).expanduser()
            if not candidate.is_absolute():
                candidate = repository_root / candidate
            resolved = candidate.resolve()
        canonical = str(resolved)
        reason = None
        if resolved == repository_root:
            reason = "authenticated_working_directory_representation"
        elif index == 0 and resolved == launcher_dir:
            reason = "console_script_launcher_directory"
        if reason:
            observations.append({"index": index, "raw": raw, "canonical": canonical, "reason": reason})
            continue
        normalized.append(canonical)
    return normalized, observations


def _installed_distribution_identity() -> dict:
    try:
        distribution = importlib.metadata.distribution("agent-arena")
    except importlib.metadata.PackageNotFoundError:
        return {
            "distribution_name": None,
            "distribution_version": None,
            "distribution_root": None,
            "direct_url": None,
            "direct_url_sha256": None,
            "editable_path_files": [],
        }
    files = list(distribution.files or [])
    direct_url_path = next(
        (Path(distribution.locate_file(item)) for item in files if str(item).endswith("direct_url.json")),
        None,
    )
    direct_url = None
    direct_url_sha256 = None
    if direct_url_path is not None and direct_url_path.is_file():
        direct_url_bytes = direct_url_path.read_bytes()
        direct_url = json.loads(direct_url_bytes.decode("utf-8"))
        direct_url_sha256 = _sha256(direct_url_bytes)
    editable_paths = []
    for item in files:
        if not str(item).endswith(".pth"):
            continue
        path = Path(distribution.locate_file(item)).resolve()
        if path.is_file():
            editable_paths.append({
                "path": str(path),
                "sha256": _sha256(path.read_bytes()),
            })
    return {
        "distribution_name": distribution.metadata.get("Name"),
        "distribution_version": distribution.version,
        "distribution_root": str(Path(distribution.locate_file("")).resolve()),
        "direct_url": direct_url,
        "direct_url_sha256": direct_url_sha256,
        "editable_path_files": editable_paths,
    }


def _distribution_repository_root(distribution_identity: dict) -> str | None:
    direct_url = distribution_identity.get("direct_url") or {}
    url = direct_url.get("url")
    if not isinstance(url, str) or not url.startswith("file://"):
        return None
    from urllib.parse import unquote, urlparse

    return str(Path(unquote(urlparse(url).path)).resolve())


def _runtime_contract_binding(root: Path) -> dict:
    from agent_arena import runtime_contract as rc

    contracts = {key: rc.build_contract(key, root) for key in sorted(rc.MODELS)}
    return {
        "contract_source": "agent_arena.runtime_contract.build_contract",
        "contract_fingerprints": {
            key: _fingerprint(contract) for key, contract in contracts.items()
        },
        "shared_runtime_fingerprint": _fingerprint(rc.SHARED_RUNTIME),
    }


def _repository_material_binding(root: Path) -> dict:
    git_root = Path(_git_text(root, "rev-parse", "--show-toplevel")).resolve()
    git_dir = Path(_git_text(root, "rev-parse", "--git-common-dir"))
    if not git_dir.is_absolute():
        git_dir = (root / git_dir).resolve()
    tracked_index = _run_git(root, "ls-files", "-s", "-z")
    if tracked_index.returncode != 0:
        raise RuntimeError("could not fingerprint tracked source index")
    config_path = root / "pyproject.toml"
    return {
        "repository_root": str(root),
        "authenticated_git_root": str(git_root),
        "repository_identity": _fingerprint({
            "repository_root": str(root),
            "git_common_dir": str(git_dir),
        }),
        "commit": _git_text(root, "rev-parse", "HEAD"),
        "tree": _git_text(root, "rev-parse", "HEAD^{tree}"),
        "tracked_source_fingerprint": _sha256(tracked_index.stdout),
        "tracked_config_fingerprint": (
            _sha256(config_path.read_bytes()) if config_path.is_file() else ""
        ),
        "clean_tracked": not bool(
            _git_text(root, "status", "--porcelain=v1", "--untracked-files=no")
        ),
    }


def canonical_material_environment(
    repo_root: str | Path,
    qa_specification_fingerprint: str | None,
    *,
    _sys_path_entries: list[str] | None = None,
    _python_executable: str | Path | None = None,
    _python_prefix: str | Path | None = None,
    _python_base_prefix: str | Path | None = None,
    _environ: dict[str, str] | None = None,
    _package_origins: dict[str, str] | None = None,
    _distribution_identity: dict | None = None,
    _repository_binding: dict | None = None,
    _runtime_binding: dict | None = None,
    _site_package_roots: list[str] | None = None,
    _user_site_enabled: bool | None = None,
) -> dict:
    """Build one material environment payload for both parent and QA child.

    Raw launcher observations remain available for audit, but only the narrowly
    normalized material payload is fingerprinted and compared.
    """
    root = Path(repo_root).resolve()
    executable = Path(_python_executable or sys.executable).absolute()
    prefix = Path(_python_prefix or sys.prefix).absolute()
    base_prefix = Path(_python_base_prefix or sys.base_prefix).absolute()
    environment = dict(os.environ if _environ is None else _environ)
    raw_sys_path = list(sys.path if _sys_path_entries is None else _sys_path_entries)
    normalized_sys_path, normalization = _canonical_sys_path(
        raw_sys_path,
        repository_root=root,
        invoked_executable=executable,
    )
    canonical_venv_executable = prefix / "bin/python"
    if not canonical_venv_executable.exists() or canonical_venv_executable.resolve() != executable.resolve():
        canonical_venv_executable = executable
    resolved_binary = executable.resolve()
    pyvenv_cfg = prefix / "pyvenv.cfg"
    package_origins = _package_origins or _critical_module_origins()
    distribution_identity = _distribution_identity or _installed_distribution_identity()
    repository_binding = _repository_binding or _repository_material_binding(root)
    runtime_binding = _runtime_binding or _runtime_contract_binding(root)
    site_roots = _site_package_roots or [str(Path(path).resolve()) for path in site.getsitepackages()]
    user_site_root = str(Path(site.getusersitepackages()).resolve())
    user_site_enabled = site.ENABLE_USER_SITE if _user_site_enabled is None else _user_site_enabled
    src_root = (root / "src").resolve()
    source_index = normalized_sys_path.index(str(src_root)) if str(src_root) in normalized_sys_path else None
    standard_roots = {
        str(base_prefix.resolve()),
        *(str(Path(path).resolve()) for path in site_roots),
    }
    for key in ("stdlib", "platstdlib", "purelib", "platlib"):
        path = sysconfig.get_paths().get(key)
        if path:
            standard_roots.add(str(Path(path).resolve()))

    def is_allowed_precedence_path(path_text: str) -> bool:
        path = Path(path_text)
        if path == src_root:
            return True
        return any(path == Path(allowed) or Path(allowed) in path.parents for allowed in standard_roots)

    before_source = normalized_sys_path if source_index is None else normalized_sys_path[:source_index]
    unexpected_precedence = [path for path in before_source if not is_allowed_precedence_path(path)]
    control_overrides = {
        name: environment[name]
        for name in _CONTROL_ENV_VARS
        if environment.get(name)
    }
    virtual_env_override = environment.get("VIRTUAL_ENV")
    if virtual_env_override:
        virtual_env_override = str(Path(virtual_env_override).resolve())
    payload = {
        "material_environment_schema_version": _MATERIAL_ENVIRONMENT_SCHEMA_VERSION,
        "repository": repository_binding,
        "canonical_qa_specification_fingerprint": qa_specification_fingerprint,
        "python": {
            "canonical_invoked_executable": str(canonical_venv_executable.absolute()),
            "resolved_python_binary": str(resolved_binary),
            "resolved_python_binary_sha256": _sha256(resolved_binary.read_bytes()),
            "implementation": platform.python_implementation(),
            "version": sys.version,
            "version_info": list(sys.version_info[:5]),
            "prefix": str(prefix),
            "base_prefix": str(base_prefix),
            "virtual_environment_active": prefix.resolve() != base_prefix.resolve(),
            "virtual_environment_identity": _fingerprint({
                "prefix": str(prefix),
                "pyvenv_cfg_sha256": _sha256(pyvenv_cfg.read_bytes()) if pyvenv_cfg.is_file() else None,
            }),
        },
        "site_packages": {
            "applicable_roots": site_roots,
            "user_site_root": user_site_root,
            "user_site_enabled": bool(user_site_enabled),
        },
        "distribution": distribution_identity,
        "distribution_repository_root": _distribution_repository_root(distribution_identity),
        "package_origins": package_origins,
        "effective_import_precedence": normalized_sys_path,
        "unexpected_import_precedence_paths": unexpected_precedence,
        "environment_controls": {
            "caller_overrides": control_overrides,
            "virtual_env_override": virtual_env_override,
            "user_site_enabled": bool(user_site_enabled),
        },
        "runtime_contract": runtime_binding,
    }
    return {
        "material_environment": payload,
        "material_environment_fingerprint": _fingerprint(payload),
        "launcher_observation": {
            "observed_python_executable": str(executable),
            "observed_sys_path": raw_sys_path,
            "normalizations": normalization,
            "working_directory": str(Path.cwd().resolve()),
            "working_directory_matches_repository": Path.cwd().resolve() == root,
        },
    }


def material_environment_policy_errors(
    material: dict,
    repo_root: str | Path,
    qa_specification_fingerprint: str | None,
) -> list[str]:
    """Recompute structural policy over a canonical material-environment record."""
    root = Path(repo_root).resolve()
    errors: list[str] = []
    payload = material.get("material_environment") if isinstance(material, dict) else None
    if not isinstance(payload, dict):
        return ["material environment payload missing"]
    if material.get("material_environment_fingerprint") != _fingerprint(payload):
        errors.append("material environment fingerprint does not reproduce")
    if payload.get("material_environment_schema_version") != _MATERIAL_ENVIRONMENT_SCHEMA_VERSION:
        errors.append("material environment schema version mismatch")
    repository = payload.get("repository") or {}
    if repository.get("repository_root") != str(root):
        errors.append("material environment repository root mismatch")
    if repository.get("authenticated_git_root") != str(root):
        errors.append("material environment authenticated Git root mismatch")
    if repository.get("clean_tracked") is not True:
        errors.append("material environment tracked source is dirty")
    if payload.get("canonical_qa_specification_fingerprint") != qa_specification_fingerprint:
        errors.append("material environment canonical QA specification mismatch")
    if payload.get("distribution_repository_root") != str(root):
        errors.append("editable distribution points to another checkout")
    distribution = payload.get("distribution") or {}
    if distribution.get("distribution_name") != "agent-arena":
        errors.append("agent-arena distribution identity is missing or incorrect")
    if (distribution.get("direct_url") or {}).get("dir_info", {}).get("editable") is not True:
        errors.append("agent-arena distribution is not the authenticated editable installation")
    if payload.get("package_origins") != _expected_module_origins(root):
        errors.append("material runtime module origin differs from authenticated checkout")
    if payload.get("unexpected_import_precedence_paths"):
        errors.append("unexpected import-shadowing path precedes authenticated source")
    controls = payload.get("environment_controls") or {}
    if controls.get("caller_overrides"):
        errors.append("caller-controlled Python or pytest environment override present")
    python = payload.get("python") or {}
    virtual_override = controls.get("virtual_env_override")
    if virtual_override and virtual_override != python.get("prefix"):
        errors.append("VIRTUAL_ENV refers to another virtual environment")
    if controls.get("user_site_enabled") is not False:
        errors.append("Python user site is enabled")
    if python.get("virtual_environment_active") is not True:
        errors.append("production Python is not running in the bound virtual environment")
    if str((root / "src").resolve()) not in payload.get("effective_import_precedence", []):
        errors.append("authenticated package source is absent from import precedence")
    distribution_root = distribution.get("distribution_root")
    if distribution_root not in (payload.get("site_packages") or {}).get("applicable_roots", []):
        errors.append("installed distribution root is outside applicable site-packages")
    observation = material.get("launcher_observation") or {}
    if observation.get("working_directory_matches_repository") is not True:
        errors.append("QA working directory differs from authenticated repository")
    return errors


def _expected_module_origins(root: Path) -> dict[str, str]:
    expected = {"agent_arena": root / "src/agent_arena/__init__.py"}
    for name in _CRITICAL_MODULES[1:]:
        expected[name] = root / ("src/" + name.replace(".", "/") + ".py")
    return {name: str(path.resolve()) for name, path in expected.items()}


def _material_untracked_overrides(root: Path) -> list[str]:
    found: set[str] = set()
    for ignored_args in ((), ("--ignored",)):
        proc = _run_git(
            root,
            "ls-files",
            "--others",
            *ignored_args,
            "--exclude-standard",
            "--",
            *_MATERIAL_UNTRACKED_PATHS,
        )
        if proc.returncode != 0:
            raise RuntimeError("could not inspect untracked runtime overrides")
        found.update(
            line for line in proc.stdout.decode("utf-8", errors="strict").splitlines() if line
        )
    return sorted(found)


def inspect_source_state(repo_root: str | Path | None = None) -> dict:
    """Resolve the exact clean tracked source and runtime identity.

    A production-authorizing source state must be the authenticated Git root,
    have no staged/unstaged tracked changes, import every critical module from
    that root, and have no environment or untracked override capable of
    changing Python/pytest behavior.
    """
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    errors: list[str] = []
    result: dict[str, object] = {
        "repository_root": str(root),
        "valid": False,
        "errors": errors,
    }
    try:
        git_root = Path(_git_text(root, "rev-parse", "--show-toplevel")).resolve()
        git_dir_text = _git_text(root, "rev-parse", "--git-common-dir")
        git_dir = Path(git_dir_text)
        if not git_dir.is_absolute():
            git_dir = (root / git_dir).resolve()
        if git_root != root:
            errors.append(f"repository root mismatch: authenticated={git_root} requested={root}")

        commit = _git_text(root, "rev-parse", "HEAD")
        tree = _git_text(root, "rev-parse", "HEAD^{tree}")
        tracked_status = _git_text(root, "status", "--porcelain=v1", "--untracked-files=no")
        clean_tracked = not tracked_status
        if not clean_tracked:
            errors.append("tracked source tree is dirty")

        tracked_index = _run_git(root, "ls-files", "-s", "-z")
        if tracked_index.returncode != 0:
            raise RuntimeError("could not fingerprint tracked source index")

        overrides = _material_untracked_overrides(root)
        if overrides:
            errors.append("material untracked/ignored runtime override present")
        control_env = {name: os.environ[name] for name in _CONTROL_ENV_VARS if os.environ.get(name)}
        if control_env:
            errors.append("caller-controlled Python/pytest environment override present")

        actual_origins = _critical_module_origins()
        expected_origins = _expected_module_origins(root)
        origin_mismatches = {
            name: {"expected": expected_origins[name], "actual": actual_origins.get(name, "")}
            for name in expected_origins
            if actual_origins.get(name) != expected_origins[name]
        }
        if origin_mismatches:
            errors.append("critical package imports do not originate from authenticated repository")

        config_path = root / "pyproject.toml"
        if not config_path.is_file() or not config_path.read_bytes():
            errors.append("tracked runtime configuration is missing or empty")
            config_fingerprint = ""
        else:
            config_fingerprint = _sha256(config_path.read_bytes())

        repository_identity = _fingerprint({
            "repository_root": str(root),
            "git_common_dir": str(git_dir),
        })
        repository_binding = {
            "repository_root": str(root),
            "authenticated_git_root": str(git_root),
            "repository_identity": repository_identity,
            "commit": commit,
            "tree": tree,
            "tracked_source_fingerprint": _sha256(tracked_index.stdout),
            "tracked_config_fingerprint": config_fingerprint,
            "clean_tracked": clean_tracked,
        }
        material = canonical_material_environment(
            root,
            None,
            _package_origins=actual_origins,
            _repository_binding=repository_binding,
        )
        material_payload = material["material_environment"]
        material_python = material_payload["python"]
        errors.extend(material_environment_policy_errors(material, root, None))
        binding_fields = {
            "repository_root": str(root),
            "repository_identity": repository_identity,
            "commit": commit,
            "tree": tree,
            "tracked_source_fingerprint": _sha256(tracked_index.stdout),
            "tracked_config_fingerprint": config_fingerprint,
            "clean_tracked": clean_tracked,
            "python_executable": _python_executable_identity(),
            "python_resolved_executable": material_python["resolved_python_binary"],
            "python_implementation": material_python["implementation"],
            "python_version": material_python["version"],
            "python_prefix": material_python["prefix"],
            "python_base_prefix": material_python["base_prefix"],
            "virtual_environment_identity": material_python["virtual_environment_identity"],
            "site_packages_roots": material_payload["site_packages"]["applicable_roots"],
            "effective_import_precedence": material_payload["effective_import_precedence"],
            "installed_distribution": material_payload["distribution"],
            "python_environment_fingerprint": material["material_environment_fingerprint"],
            "material_environment": material_payload,
            "material_environment_fingerprint": material["material_environment_fingerprint"],
            "launcher_observation": material["launcher_observation"],
            "package_origins": actual_origins,
            "material_untracked_overrides": overrides,
            "control_environment_overrides": sorted(control_env),
        }
        result.update(binding_fields)
        result["origin_mismatches"] = origin_mismatches
        result["source_state_fingerprint"] = _fingerprint(binding_fields)
        result["valid"] = not errors
    except (OSError, RuntimeError, UnicodeError) as exc:
        errors.append(f"source state unavailable: {type(exc).__name__}: {exc}")
    return result


def compare_source_binding(expected: dict, observed: dict) -> list[str]:
    errors: list[str] = []
    if not expected.get("valid"):
        errors.append("tested source binding was not valid")
    if not observed.get("valid"):
        errors.extend(observed.get("errors") or ["executed source binding is not valid"])
    for field in (
        "repository_root",
        "repository_identity",
        "commit",
        "tree",
        "tracked_source_fingerprint",
        "tracked_config_fingerprint",
        "python_executable",
        "python_resolved_executable",
        "python_implementation",
        "python_version",
        "python_prefix",
        "python_base_prefix",
        "virtual_environment_identity",
        "site_packages_roots",
        "effective_import_precedence",
        "installed_distribution",
        "python_environment_fingerprint",
        "material_environment_fingerprint",
        "package_origins",
        "source_state_fingerprint",
    ):
        if expected.get(field) != observed.get(field):
            errors.append(f"source binding mismatch: {field}")
    return errors


def verify_source_binding(expected: dict) -> dict:
    observed = inspect_source_state(expected.get("repository_root"))
    errors = compare_source_binding(expected, observed)
    return {"matches": not errors, "errors": errors, "observed": observed}


def _parse_pytest_summary(stdout: str) -> dict:
    counts = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "xfailed": 0,
        "xpassed": 0,
        "deselected": 0,
    }
    for number, kind in _PYTEST_COUNT_RE.findall(stdout):
        key = "errors" if kind in ("error", "errors") else kind
        counts[key] = int(number)
    match = _PYTEST_COLLECTED_RE.search(stdout)
    collected = int(match.group(1)) if match else sum(
        counts[key] for key in ("passed", "failed", "skipped", "errors", "xfailed", "xpassed")
    )
    return {"collected": collected, **counts}


def _sanitized_qa_environment(
    source_binding: dict,
    qa_specification_fingerprint: str | None = None,
) -> tuple[dict[str, str], dict]:
    env = dict(os.environ)
    removed = []
    for name in _CONTROL_ENV_VARS:
        if name in env:
            removed.append(name)
            env.pop(name, None)
    env.update(
        {
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "AGENT_ARENA_CANONICAL_QA_ROOT": str(source_binding["repository_root"]),
            "AGENT_ARENA_CANONICAL_QA_SPEC": (
                qa_specification_fingerprint or canonical_qa_specification_fingerprint()
            ),
        }
    )
    isolation = {
        "removed_environment_variables": sorted(removed),
        "python_no_user_site": True,
        "python_no_bytecode": True,
        "pytest_addopts_cleared_by_command": True,
    }
    return env, isolation


def _subprocess_origin_probe(
    source_binding: dict,
    env: dict[str, str],
    runner: Callable = subprocess.run,
) -> tuple[dict, str | None]:
    script = (
        "import json,os;"
        "from agent_arena.preflight_integrity import canonical_material_environment;"
        "value=canonical_material_environment("
        "os.environ['AGENT_ARENA_CANONICAL_QA_ROOT'],"
        "os.environ['AGENT_ARENA_CANONICAL_QA_SPEC']);"
        "print(json.dumps(value,sort_keys=True))"
    )
    command = [str(source_binding["python_executable"]), "-c", script]
    try:
        proc = runner(
            command,
            cwd=str(source_binding["repository_root"]),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command}, f"{type(exc).__name__}: {exc}"
    probe = {
        "command": command,
        "exit_code": proc.returncode,
        "stderr": (proc.stderr or "").strip(),
    }
    if proc.returncode != 0:
        return probe, "subprocess import-origin probe failed"
    try:
        probe.update(json.loads((proc.stdout or "").strip()))
    except (json.JSONDecodeError, TypeError) as exc:
        return probe, f"subprocess import-origin probe malformed: {exc}"
    return probe, None


def _qa_record_fingerprint(record: dict) -> str:
    return _fingerprint({field: record.get(field) for field in _FINGERPRINT_FIELDS})


def execute_canonical_qa(
    repo_root: str | Path,
    source_binding: dict,
    *,
    _runner: Callable = subprocess.run,
    _condition_contract: bool = False,
    _full_replication: bool = False,
) -> dict:
    """Execute the fixed production QA specification against one source binding.

    The public production preflight supplies no caller-controlled test arguments.
    ``_runner`` is private and exists only for deterministic failure-path tests.
    """
    root = Path(repo_root).resolve()
    if _condition_contract and _full_replication:
        raise ValueError("canonical QA profile selection is ambiguous")
    if _full_replication:
        specification = full_replication_qa_specification()
    elif _condition_contract:
        specification = condition_contract_qa_specification()
    else:
        specification = canonical_qa_specification()
    specification_fp = _fingerprint(specification)
    if _full_replication:
        command_builder = full_replication_qa_command
    elif _condition_contract:
        command_builder = condition_contract_qa_command
    else:
        command_builder = canonical_qa_command
    command = command_builder(str(source_binding.get("python_executable", sys.executable)))
    env, environment_isolation = _sanitized_qa_environment(source_binding, specification_fp)
    expected_material = canonical_material_environment(root, specification_fp)
    probe, probe_error = _subprocess_origin_probe(source_binding, env, _runner)
    if probe_error is None:
        probe_payload = probe.get("material_environment")
        if not isinstance(probe_payload, dict):
            probe_error = "subprocess material environment payload is missing"
        elif probe.get("material_environment_fingerprint") != _fingerprint(probe_payload):
            probe_error = "subprocess material environment fingerprint does not reproduce"
        elif probe_payload != expected_material["material_environment"]:
            probe_error = "subprocess material Python environment differs from tested parent"
        elif probe.get("material_environment_fingerprint") != expected_material[
            "material_environment_fingerprint"
        ]:
            probe_error = "subprocess material Python environment fingerprint mismatch"
    started = time.perf_counter()
    stdout = ""
    stderr = ""
    exit_code: int | None = None
    execution_status = QA_COULD_NOT_EXECUTE

    if probe_error is None:
        try:
            proc = _runner(
                command,
                cwd=str(root),
                env=env,
                capture_output=True,
                text=True,
                timeout=CANONICAL_QA_TIMEOUT_SECONDS,
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            exit_code = proc.returncode
            execution_status = QA_PASSED if proc.returncode == 0 else QA_FAILED
        except (OSError, subprocess.TimeoutExpired) as exc:
            stderr = f"{type(exc).__name__}: {exc}"
    else:
        stderr = probe_error

    log_output = (stdout + "\n" + stderr).strip()
    counts = _parse_pytest_summary(stdout)
    record = {
        "qa_kind": (
            _FULL_REPLICATION_QA_KIND
            if _full_replication
            else _CONDITION_QA_KIND if _condition_contract else _QA_KIND
        ),
        "produced_by": (
            _FULL_REPLICATION_QA_PRODUCER
            if _full_replication
            else _CONDITION_QA_PRODUCER if _condition_contract else _QA_PRODUCER
        ),
        "authorization_source": "fresh_internal_canonical_executor",
        "canonical_specification": specification,
        "canonical_specification_fingerprint": specification_fp,
        "command": command,
        "repository_root": str(root),
        "repository_identity": source_binding.get("repository_identity"),
        "commit": source_binding.get("commit"),
        "tree": source_binding.get("tree"),
        "tracked_source_fingerprint": source_binding.get("tracked_source_fingerprint"),
        "tracked_config_fingerprint": source_binding.get("tracked_config_fingerprint"),
        "python_executable": source_binding.get("python_executable"),
        "python_version": source_binding.get("python_version"),
        "python_prefix": source_binding.get("python_prefix"),
        "python_base_prefix": source_binding.get("python_base_prefix"),
        "python_environment_fingerprint": source_binding.get("python_environment_fingerprint"),
        "material_environment": expected_material["material_environment"],
        "material_environment_fingerprint": expected_material[
            "material_environment_fingerprint"
        ],
        "package_origins": source_binding.get("package_origins"),
        "subprocess_probe": probe,
        "environment_isolation": environment_isolation,
        "execution_status": execution_status,
        "exit_code": exit_code,
        "tests_collected": counts["collected"],
        "tests_passed": counts["passed"],
        "tests_failed": counts["failed"],
        "tests_errors": counts["errors"],
        "tests_skipped": counts["skipped"],
        "tests_xfailed": counts["xfailed"],
        "tests_xpassed": counts["xpassed"],
        "tests_deselected": counts["deselected"],
        "log_output": log_output,
        "log_sha256": _sha256(log_output.encode("utf-8")),
        "summary_line": log_output.splitlines()[-1] if log_output else "",
        "runtime_seconds": round(time.perf_counter() - started, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    record["qa_record_fingerprint"] = _qa_record_fingerprint(record)
    return record


def execute_condition_contract_qa(
    repo_root: str | Path,
    source_binding: dict,
    *,
    _runner: Callable = subprocess.run,
) -> dict:
    """Execute the fixed condition-contract superset; no caller-selected scope."""
    return execute_canonical_qa(
        repo_root,
        source_binding,
        _runner=_runner,
        _condition_contract=True,
    )


def execute_full_replication_qa(
    repo_root: str | Path,
    source_binding: dict,
    *,
    _runner: Callable = subprocess.run,
) -> dict:
    """Execute the fixed Phase-5B superset; no caller-selected scope."""
    return execute_canonical_qa(
        repo_root,
        source_binding,
        _runner=_runner,
        _full_replication=True,
    )


def validate_canonical_qa_record(
    qa: dict | None,
    source_binding: dict,
    *,
    _condition_contract: bool = False,
    _full_replication: bool = False,
) -> tuple[str, list[str]]:
    """Validate canonical QA accounting and provenance; no record is trusted by its hash alone."""
    if not qa:
        return QA_NOT_EXECUTED, ["canonical QA record missing"]
    errors: list[str] = []
    if not source_binding.get("valid"):
        errors.append("canonical QA source binding is not valid")
    if _condition_contract and _full_replication:
        return QA_FAILED, ["canonical QA profile selection is ambiguous"]
    if _full_replication:
        expected_kind = _FULL_REPLICATION_QA_KIND
        expected_producer = _FULL_REPLICATION_QA_PRODUCER
    elif _condition_contract:
        expected_kind = _CONDITION_QA_KIND
        expected_producer = _CONDITION_QA_PRODUCER
    else:
        expected_kind = _QA_KIND
        expected_producer = _QA_PRODUCER
    if qa.get("qa_kind") != expected_kind:
        errors.append("QA kind is not canonical")
    if qa.get("produced_by") != expected_producer:
        errors.append("QA producer is not the guarded canonical executor")
    if qa.get("authorization_source") != "fresh_internal_canonical_executor":
        errors.append("QA authorization source is not fresh/internal")
    if _full_replication:
        spec = full_replication_qa_specification()
    elif _condition_contract:
        spec = condition_contract_qa_specification()
    else:
        spec = canonical_qa_specification()
    if qa.get("canonical_specification") != spec:
        errors.append("canonical QA specification mismatch")
    if qa.get("canonical_specification_fingerprint") != _fingerprint(spec):
        errors.append("canonical QA specification fingerprint mismatch")
    if _full_replication:
        command_builder = full_replication_qa_command
    elif _condition_contract:
        command_builder = condition_contract_qa_command
    else:
        command_builder = canonical_qa_command
    expected_command = command_builder(str(source_binding.get("python_executable", "")))
    if qa.get("command") != expected_command:
        errors.append("canonical QA command mismatch")

    for field in (
        "repository_root",
        "repository_identity",
        "commit",
        "tree",
        "tracked_source_fingerprint",
        "tracked_config_fingerprint",
        "python_executable",
        "python_version",
        "python_prefix",
        "python_base_prefix",
        "python_environment_fingerprint",
        "package_origins",
    ):
        if qa.get(field) != source_binding.get(field):
            errors.append(f"QA source provenance mismatch: {field}")

    material_payload = qa.get("material_environment")
    material_fingerprint = qa.get("material_environment_fingerprint")
    if not isinstance(material_payload, dict):
        errors.append("canonical QA material environment payload missing")
    elif material_fingerprint != _fingerprint(material_payload):
        errors.append("canonical QA material environment fingerprint mismatch")
    else:
        if material_payload.get("canonical_qa_specification_fingerprint") != _fingerprint(spec):
            errors.append("material environment QA specification mismatch")
        repository = material_payload.get("repository") or {}
        for source_field in (
            "repository_root",
            "repository_identity",
            "commit",
            "tree",
            "tracked_source_fingerprint",
            "tracked_config_fingerprint",
        ):
            if repository.get(source_field) != source_binding.get(source_field):
                errors.append(f"material environment source mismatch: {source_field}")
        if material_payload.get("package_origins") != source_binding.get("package_origins"):
            errors.append("material environment package origins mismatch")
        source_material = source_binding.get("material_environment") or {}
        for section in (
            "python",
            "site_packages",
            "distribution",
            "distribution_repository_root",
            "effective_import_precedence",
            "environment_controls",
            "runtime_contract",
        ):
            if material_payload.get(section) != source_material.get(section):
                errors.append(f"material environment source mismatch: {section}")

    probe = qa.get("subprocess_probe")
    if not isinstance(probe, dict) or probe.get("exit_code") != 0:
        errors.append("canonical QA subprocess import probe did not pass")
    else:
        probe_payload = probe.get("material_environment")
        if not isinstance(probe_payload, dict):
            errors.append("canonical QA subprocess material environment missing")
        elif probe.get("material_environment_fingerprint") != _fingerprint(probe_payload):
            errors.append("canonical QA subprocess material fingerprint mismatch")
        elif probe_payload != material_payload:
            errors.append("canonical QA subprocess material environment mismatch")

    for key in _COUNT_KEYS:
        value = qa.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"invalid QA counter: {key}")
    if not any(error.startswith("invalid QA counter") for error in errors):
        terminal_total = sum(
            qa[key]
            for key in (
                "tests_passed",
                "tests_failed",
                "tests_errors",
                "tests_skipped",
                "tests_xfailed",
                "tests_xpassed",
            )
        )
        if terminal_total != qa["tests_collected"]:
            errors.append("QA counters do not account for the collected population")
        if qa["tests_deselected"] != 0:
            errors.append("canonical QA scope was deselected/reduced")
        if _full_replication:
            expected_collected = FULL_REPLICATION_QA_EXPECTED_COLLECTED
        elif _condition_contract:
            expected_collected = CONDITION_CONTRACT_QA_EXPECTED_COLLECTED
        else:
            expected_collected = CANONICAL_QA_EXPECTED_COLLECTED
        if qa["tests_collected"] != expected_collected:
            errors.append("canonical QA collected count mismatch")
        if qa["tests_passed"] != expected_collected:
            errors.append("not every canonical QA test passed")
        for key in (
            "tests_failed",
            "tests_errors",
            "tests_skipped",
            "tests_xfailed",
            "tests_xpassed",
            "tests_deselected",
        ):
            if qa[key] != 0:
                errors.append(f"canonical QA contains non-pass terminal category: {key}")

    if qa.get("execution_status") != QA_PASSED:
        errors.append(f"canonical QA execution status is {qa.get('execution_status')}")
    if qa.get("exit_code") != 0:
        errors.append("canonical QA process exit was not zero")
    log_output = qa.get("log_output")
    if not isinstance(log_output, str):
        errors.append("canonical QA log output missing")
    elif qa.get("log_sha256") != _sha256(log_output.encode("utf-8")):
        errors.append("canonical QA log hash mismatch")
    if qa.get("qa_record_fingerprint") != _qa_record_fingerprint(qa):
        errors.append("canonical QA record fingerprint mismatch")

    if qa.get("execution_status") == QA_COULD_NOT_EXECUTE:
        status = QA_COULD_NOT_EXECUTE
    elif errors:
        status = QA_FAILED
    else:
        status = QA_PASSED
    return status, errors


def validate_condition_contract_qa_record(
    qa: dict | None,
    source_binding: dict,
) -> tuple[str, list[str]]:
    """Validate the fixed condition-contract QA profile and its full accounting."""
    return validate_canonical_qa_record(qa, source_binding, _condition_contract=True)


def validate_full_replication_qa_record(
    qa: dict | None,
    source_binding: dict,
) -> tuple[str, list[str]]:
    """Validate the fixed Phase-5B QA profile and its full accounting."""
    return validate_canonical_qa_record(qa, source_binding, _full_replication=True)


def execute_diagnostic_qa(
    pytest_args: list[str] | None = None,
    repo_root: str | Path | None = None,
    timeout: int = 3600,
) -> dict:
    """Run caller-selected pytest for diagnostics; this record can never authorize production."""
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    args = list(pytest_args) if pytest_args is not None else []
    command = [sys.executable, "-m", "pytest", "--tb=no", "-p", "no:cacheprovider", *args]
    started = time.perf_counter()
    proc = subprocess.run(command, cwd=str(root), capture_output=True, text=True, timeout=timeout)
    output = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    counts = _parse_pytest_summary(proc.stdout or "")
    return {
        "qa_kind": "pytest_diagnostic_non_authorizing",
        "produced_by": "agent_arena.preflight_integrity.execute_diagnostic_qa",
        "authorization_source": "non_authorizing_diagnostic",
        "command": command,
        "exit_code": proc.returncode,
        "tests_collected": counts["collected"],
        "tests_passed": counts["passed"],
        "tests_failed": counts["failed"],
        "tests_skipped": counts["skipped"],
        "tests_errors": counts["errors"],
        "summary_line": output.splitlines()[-1] if output else "",
        "log_sha256": _sha256(output.encode("utf-8")),
        "runtime_seconds": round(time.perf_counter() - started, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def classify_diagnostic_qa(qa: dict | None) -> str:
    if not qa:
        return QA_NOT_EXECUTED
    if qa.get("qa_kind") not in (
        "pytest_diagnostic_non_authorizing",
        "pytest_execution",  # historical/offline compatibility only
    ):
        return QA_NON_AUTHORIZING
    if qa.get("exit_code") != 0 or qa.get("tests_failed", 1) or qa.get("tests_errors", 1):
        return QA_FAILED
    if qa.get("tests_collected", 0) <= 0:
        return QA_FAILED
    return QA_NON_AUTHORIZING
