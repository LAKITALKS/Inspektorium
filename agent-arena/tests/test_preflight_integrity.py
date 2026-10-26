"""Adversarial Phase-2 production-preflight and provider-boundary tests.

All providers and QA executors are sentinels/fakes.  No external provider or
model call is made.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from agent_arena import phase7a_execution as p7
from agent_arena import phase7a_real_run as rr
from agent_arena import preflight_integrity as pi


REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE7_ARTIFACTS = REPO_ROOT / "analysis/phase7a_execution"
RUNTIME_ARTIFACTS = REPO_ROOT / "analysis/phase6_2_runtime_freeze"


class ProviderBoundaryReached(RuntimeError):
    pass


def _source_binding(marker: str = "a") -> dict:
    package_origins = {
        name: str(REPO_ROOT / f"synthetic/{name.replace('.', '/')}.py")
        for name in pi._CRITICAL_MODULES
    }
    binding = {
        "valid": True,
        "errors": [],
        "repository_root": str(REPO_ROOT),
        "repository_identity": f"repo-{marker}",
        "commit": marker * 40,
        "tree": marker * 40,
        "tracked_source_fingerprint": marker * 64,
        "tracked_config_fingerprint": marker * 64,
        "clean_tracked": True,
        "python_executable": str(Path(sys.executable).absolute()),
        "python_version": sys.version,
        "python_prefix": str(Path(sys.prefix).absolute()),
        "python_base_prefix": str(Path(sys.base_prefix).absolute()),
        "package_origins": package_origins,
        "material_untracked_overrides": [],
        "control_environment_overrides": [],
        "source_state_fingerprint": f"source-{marker}",
    }
    material_payload = {
        "material_environment_schema_version": pi._MATERIAL_ENVIRONMENT_SCHEMA_VERSION,
        "repository": {
            "repository_root": binding["repository_root"],
            "authenticated_git_root": binding["repository_root"],
            "repository_identity": binding["repository_identity"],
            "commit": binding["commit"],
            "tree": binding["tree"],
            "tracked_source_fingerprint": binding["tracked_source_fingerprint"],
            "tracked_config_fingerprint": binding["tracked_config_fingerprint"],
            "clean_tracked": True,
        },
        "canonical_qa_specification_fingerprint": None,
        "python": {
            "canonical_invoked_executable": binding["python_executable"],
            "resolved_python_binary": str(Path(sys.executable).resolve()),
            "resolved_python_binary_sha256": marker * 64,
            "implementation": "CPython",
            "version": binding["python_version"],
            "version_info": [3, 11, 0, "final", 0],
            "prefix": binding["python_prefix"],
            "base_prefix": binding["python_base_prefix"],
            "virtual_environment_active": True,
            "virtual_environment_identity": f"venv-{marker}",
        },
        "site_packages": {
            "applicable_roots": [str(REPO_ROOT / ".venv/site-packages")],
            "user_site_root": str(REPO_ROOT / "user-site"),
            "user_site_enabled": False,
        },
        "distribution": {"distribution_name": "agent-arena", "marker": marker},
        "distribution_repository_root": str(REPO_ROOT),
        "package_origins": package_origins,
        "effective_import_precedence": [str(REPO_ROOT / "src")],
        "unexpected_import_precedence_paths": [],
        "environment_controls": {
            "caller_overrides": {},
            "virtual_env_override": None,
            "user_site_enabled": False,
        },
        "runtime_contract": {"marker": marker},
    }
    material_fingerprint = pi._fingerprint(material_payload)
    binding.update({
        "python_resolved_executable": material_payload["python"]["resolved_python_binary"],
        "python_implementation": material_payload["python"]["implementation"],
        "virtual_environment_identity": material_payload["python"][
            "virtual_environment_identity"
        ],
        "site_packages_roots": material_payload["site_packages"]["applicable_roots"],
        "effective_import_precedence": material_payload["effective_import_precedence"],
        "installed_distribution": material_payload["distribution"],
        "python_environment_fingerprint": material_fingerprint,
        "material_environment": material_payload,
        "material_environment_fingerprint": material_fingerprint,
        "launcher_observation": {"synthetic": True},
    })
    return binding


def _canonical_qa(binding: dict, **changes) -> dict:
    log_output = f"{pi.CANONICAL_QA_EXPECTED_COLLECTED} passed in 0.01s"
    material_payload = copy.deepcopy(binding["material_environment"])
    material_payload["canonical_qa_specification_fingerprint"] = (
        pi.canonical_qa_specification_fingerprint()
    )
    material_fingerprint = pi._fingerprint(material_payload)
    record = {
        "qa_kind": "canonical_pytest_execution",
        "produced_by": "agent_arena.preflight_integrity.execute_canonical_qa",
        "authorization_source": "fresh_internal_canonical_executor",
        "canonical_specification": pi.canonical_qa_specification(),
        "canonical_specification_fingerprint": pi.canonical_qa_specification_fingerprint(),
        "command": pi.canonical_qa_command(binding["python_executable"]),
        "repository_root": binding["repository_root"],
        "repository_identity": binding["repository_identity"],
        "commit": binding["commit"],
        "tree": binding["tree"],
        "tracked_source_fingerprint": binding["tracked_source_fingerprint"],
        "tracked_config_fingerprint": binding["tracked_config_fingerprint"],
        "python_executable": binding["python_executable"],
        "python_version": binding["python_version"],
        "python_prefix": binding["python_prefix"],
        "python_base_prefix": binding["python_base_prefix"],
        "python_environment_fingerprint": binding["python_environment_fingerprint"],
        "material_environment": material_payload,
        "material_environment_fingerprint": material_fingerprint,
        "package_origins": binding["package_origins"],
        "subprocess_probe": {
            "exit_code": 0,
            "material_environment": material_payload,
            "material_environment_fingerprint": material_fingerprint,
            "launcher_observation": {"synthetic": True},
        },
        "environment_isolation": {
            "removed_environment_variables": [],
            "python_no_user_site": True,
            "python_no_bytecode": True,
            "pytest_addopts_cleared_by_command": True,
        },
        "execution_status": pi.QA_PASSED,
        "exit_code": 0,
        "tests_collected": pi.CANONICAL_QA_EXPECTED_COLLECTED,
        "tests_passed": pi.CANONICAL_QA_EXPECTED_COLLECTED,
        "tests_failed": 0,
        "tests_errors": 0,
        "tests_skipped": 0,
        "tests_xfailed": 0,
        "tests_xpassed": 0,
        "tests_deselected": 0,
        "log_output": log_output,
        "log_sha256": pi._sha256(log_output.encode("utf-8")),
    }
    record.update(changes)
    record["qa_record_fingerprint"] = pi._qa_record_fingerprint(record)
    return record


def _production_preflight_with_qa(qa_mutator=None, source_states=None):
    binding = _source_binding()
    qa = _canonical_qa(binding)
    if qa_mutator:
        qa_mutator(qa, binding)
        qa["qa_record_fingerprint"] = pi._qa_record_fingerprint(qa)
    states = iter(source_states or [binding, binding])
    calls = {"qa": 0}

    def qa_executor(root, tested_binding):
        calls["qa"] += 1
        assert tested_binding == binding
        return qa

    result = p7._production_preflight(
        REPO_ROOT,
        qa_executor=qa_executor,
        source_inspector=lambda root: next(states),
        gate_verifier=lambda root: {"passes": True, "errors": []},
    )
    return result, calls


def _assert_provider_boundary(
    monkeypatch, preflight: dict, expected_count: int, *, credential=True, out_dir=None
):
    count = {"provider": 0}
    monkeypatch.setattr(rr.p7, "real_run_preflight", lambda root: preflight)
    monkeypatch.setattr(
        rr.pi,
        "verify_source_binding",
        lambda binding: {"matches": True, "errors": [], "observed": binding},
    )
    if credential:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-phase2-sentinel")
    else:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def provider_builder(model_key):
        count["provider"] += 1
        raise ProviderBoundaryReached(model_key)

    monkeypatch.setattr(rr, "provider_factory_for", provider_builder)
    if preflight.get("go") and credential:
        with pytest.raises(ProviderBoundaryReached):
            rr.run_haiku_batch(repo_root=REPO_ROOT, out_dir=out_dir)
    else:
        with pytest.raises(rr.ProviderUnavailable):
            rr.run_haiku_batch(repo_root=REPO_ROOT, out_dir=out_dir)
    assert count["provider"] == expected_count


def _copy_required_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    frozen_dir = tmp_path / "phase7a"
    runtime_dir = tmp_path / "runtime"
    frozen_dir.mkdir()
    runtime_dir.mkdir()
    for filename in (p7.EXECUTION_MANIFEST_FILE, p7.CALL_PLAN_FILE):
        shutil.copy2(PHASE7_ARTIFACTS / filename, frozen_dir / filename)
    for filename in p7.RUNTIME_CONTRACT_FILES.values():
        shutil.copy2(RUNTIME_ARTIFACTS / filename, runtime_dir / filename)
    return frozen_dir, runtime_dir


def _gate_preflight(gate: dict) -> dict:
    return {
        "go": False,
        "gate_passes": gate["passes"],
        "gate_errors": gate["errors"],
        "qa_status": pi.QA_NOT_EXECUTED,
        "qa_errors": [],
        "source_binding": _source_binding(),
    }


def _material_variant(**overrides) -> dict:
    base = pi.canonical_material_environment(
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
    )
    payload = base["material_environment"]
    repository = copy.deepcopy(payload["repository"])
    repository["clean_tracked"] = True
    kwargs = {
        "_repository_binding": repository,
        "_runtime_binding": copy.deepcopy(payload["runtime_contract"]),
        "_distribution_identity": copy.deepcopy(payload["distribution"]),
        "_package_origins": copy.deepcopy(payload["package_origins"]),
        "_site_package_roots": copy.deepcopy(payload["site_packages"]["applicable_roots"]),
        "_environ": {},
        "_user_site_enabled": False,
    }
    kwargs.update(overrides)
    return pi.canonical_material_environment(
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
        **kwargs,
    )


def test_A_all_artifacts_fresh_qa_binding_credentials_go(monkeypatch, tmp_path):
    preflight, calls = _production_preflight_with_qa()
    assert preflight["go"] is True
    assert calls["qa"] == 1
    _assert_provider_boundary(monkeypatch, preflight, 1, out_dir=tmp_path)


@pytest.mark.parametrize("missing_kind", ["directory", "individual_file"])
def test_B_required_artifact_missing_is_no_go(tmp_path, monkeypatch, missing_kind):
    frozen_dir, runtime_dir = _copy_required_artifacts(tmp_path)
    if missing_kind == "directory":
        frozen_dir = tmp_path / "absent"
    else:
        (frozen_dir / p7.CALL_PLAN_FILE).unlink()
    gate = p7.verify_pre_run(REPO_ROOT, frozen_dir, runtime_dir)
    assert gate["passes"] is False
    assert any("required artifact missing" in error for error in gate["errors"])
    _assert_provider_boundary(monkeypatch, _gate_preflight(gate), 0)


@pytest.mark.parametrize("damage", ["empty", "malformed", "partial", "unreadable"])
def test_C_required_artifact_invalid_is_no_go(tmp_path, monkeypatch, damage):
    frozen_dir, runtime_dir = _copy_required_artifacts(tmp_path)
    target = frozen_dir / p7.EXECUTION_MANIFEST_FILE
    if damage == "empty":
        target.write_bytes(b"")
    elif damage == "malformed":
        target.write_text("{not-json")
    elif damage == "partial":
        target.write_text(json.dumps({"execution_plan_version": "7A.1"}))
    else:
        original = p7.Path.read_bytes

        def unreadable(path):
            if path == target:
                raise PermissionError("controlled unreadable fixture")
            return original(path)

        monkeypatch.setattr(p7.Path, "read_bytes", unreadable)
    gate = p7.verify_pre_run(REPO_ROOT, frozen_dir, runtime_dir)
    assert gate["passes"] is False
    _assert_provider_boundary(monkeypatch, _gate_preflight(gate), 0)


def test_D_artifact_fingerprint_mismatch_is_no_go(tmp_path, monkeypatch):
    frozen_dir, runtime_dir = _copy_required_artifacts(tmp_path)
    path = frozen_dir / p7.EXECUTION_MANIFEST_FILE
    data = json.loads(path.read_text())
    data["execution_manifest_fingerprint"] = "0" * 64
    path.write_text(json.dumps(data))
    gate = p7.verify_pre_run(REPO_ROOT, frozen_dir, runtime_dir)
    assert gate["passes"] is False
    assert any("execution manifest fingerprint" in error for error in gate["errors"])
    _assert_provider_boundary(monkeypatch, _gate_preflight(gate), 0)


def test_D_runtime_contract_fingerprint_mismatch_is_no_go(tmp_path, monkeypatch):
    frozen_dir, runtime_dir = _copy_required_artifacts(tmp_path)
    path = runtime_dir / p7.RUNTIME_CONTRACT_FILES["haiku"]
    data = json.loads(path.read_text())
    data["temperature"] = 0.5
    path.write_text(json.dumps(data))
    gate = p7.verify_pre_run(REPO_ROOT, frozen_dir, runtime_dir)
    assert gate["passes"] is False
    assert any("runtime contract" in error for error in gate["errors"])
    _assert_provider_boundary(monkeypatch, _gate_preflight(gate), 0)


def test_E_call_plan_mismatch_is_no_go(tmp_path, monkeypatch):
    frozen_dir, runtime_dir = _copy_required_artifacts(tmp_path)
    path = frozen_dir / p7.CALL_PLAN_FILE
    data = json.loads(path.read_text())
    data["planned_analytical_calls"] = 1
    path.write_text(json.dumps(data))
    gate = p7.verify_pre_run(REPO_ROOT, frozen_dir, runtime_dir)
    assert gate["passes"] is False
    assert any("call plan" in error for error in gate["errors"])
    _assert_provider_boundary(monkeypatch, _gate_preflight(gate), 0)


def test_F_scientific_manifest_mismatch_is_no_go(tmp_path, monkeypatch):
    frozen_dir, runtime_dir = _copy_required_artifacts(tmp_path)
    path = frozen_dir / p7.EXECUTION_MANIFEST_FILE
    data = json.loads(path.read_text())
    data["scientific_manifest_fingerprint"] = "f" * 64
    path.write_text(json.dumps(data))
    gate = p7.verify_pre_run(REPO_ROOT, frozen_dir, runtime_dir)
    assert gate["passes"] is False
    assert any("scientific manifest" in error for error in gate["errors"])
    _assert_provider_boundary(monkeypatch, _gate_preflight(gate), 0)


def test_G_qa_could_not_execute_is_distinct_no_go(monkeypatch):
    binding = _source_binding()

    def cannot_launch(*args, **kwargs):
        raise OSError("controlled launch failure")

    qa = pi.execute_canonical_qa(REPO_ROOT, binding, _runner=cannot_launch)
    status, errors = pi.validate_canonical_qa_record(qa, binding)
    assert status == pi.QA_COULD_NOT_EXECUTE
    preflight = {"go": False, "gate_passes": True, "gate_errors": [],
                 "qa_status": status, "qa_errors": errors, "source_binding": binding}
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_H_qa_executed_and_failed_is_distinct_no_go(monkeypatch):
    binding = _source_binding()
    calls = 0

    def failing_runner(command, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            probe = pi.canonical_material_environment(
                REPO_ROOT,
                pi.canonical_qa_specification_fingerprint(),
            )
            return subprocess.CompletedProcess(command, 0, json.dumps(probe), "")
        return subprocess.CompletedProcess(
            command, 1, "collected 246 items\n245 passed, 1 failed", ""
        )

    qa = pi.execute_canonical_qa(REPO_ROOT, binding, _runner=failing_runner)
    status, errors = pi.validate_canonical_qa_record(qa, binding)
    assert status == pi.QA_FAILED
    assert qa["execution_status"] == pi.QA_FAILED
    preflight = {"go": False, "gate_passes": True, "gate_errors": [],
                 "qa_status": status, "qa_errors": errors, "source_binding": binding}
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_I_zero_collection_is_no_go(monkeypatch):
    def mutate(qa, binding):
        qa.update(tests_collected=0, tests_passed=0)

    preflight, _ = _production_preflight_with_qa(mutate)
    assert preflight["go"] is False
    _assert_provider_boundary(monkeypatch, preflight, 0)


@pytest.mark.parametrize("source", ["caller", "stored"])
def test_J_K_supplied_or_stored_green_qa_cannot_authorize(monkeypatch, source):
    count = {"provider": 0}
    monkeypatch.setattr(
        rr,
        "provider_factory_for",
        lambda key: count.__setitem__("provider", count["provider"] + 1),
    )
    fabricated = {"qa_kind": "pytest_execution", "exit_code": 0, "tests_collected": 1,
                  "tests_passed": 1, "tests_failed": 0, "tests_errors": 0,
                  "source": source}
    with pytest.raises(rr.ProviderUnavailable):
        rr.run_haiku_batch(repo_root=REPO_ROOT, qa_record=fabricated)
    assert count["provider"] == 0


def test_L_qa_fingerprint_mismatch_is_no_go(monkeypatch):
    binding = _source_binding()
    qa = _canonical_qa(binding)
    qa["qa_record_fingerprint"] = "0" * 64
    status, errors = pi.validate_canonical_qa_record(qa, binding)
    assert status == pi.QA_FAILED
    assert "canonical QA record fingerprint mismatch" in errors
    preflight = {"go": False, "gate_passes": True, "gate_errors": [],
                 "qa_status": status, "qa_errors": errors, "source_binding": binding}
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_M_internally_inconsistent_qa_counters_are_no_go(monkeypatch):
    def mutate(qa, binding):
        qa.update(tests_collected=10, tests_passed=3)

    preflight, _ = _production_preflight_with_qa(mutate)
    assert any("collected population" in error for error in preflight["qa_errors"])
    _assert_provider_boundary(monkeypatch, preflight, 0)


@pytest.mark.parametrize("credential", [None, "DEIN_KEY"])
def test_N_missing_or_placeholder_credentials_are_no_go(monkeypatch, credential):
    preflight, _ = _production_preflight_with_qa()
    count = {"provider": 0}
    monkeypatch.setattr(rr.p7, "real_run_preflight", lambda root: preflight)
    monkeypatch.setattr(
        rr, "provider_factory_for",
        lambda key: count.__setitem__("provider", count["provider"] + 1),
    )
    if credential is None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    else:
        monkeypatch.setenv("ANTHROPIC_API_KEY", credential)
    with pytest.raises(rr.ProviderUnavailable):
        rr.run_haiku_batch(repo_root=REPO_ROOT)
    assert count["provider"] == 0


def test_O_caller_cannot_select_trivial_qa_scope(monkeypatch):
    assert "qa_pytest_args" not in p7.real_run_preflight.__code__.co_varnames
    assert "-k" not in pi.canonical_qa_command(sys.executable)
    with pytest.raises(TypeError):
        p7.real_run_preflight(REPO_ROOT, qa_pytest_args=["-k", "trivial"])
    preflight = {"go": False, "gate_passes": True, "gate_errors": [],
                 "qa_status": pi.QA_NOT_EXECUTED, "qa_errors": ["caller scope rejected"],
                 "source_binding": _source_binding()}
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_P_qa_from_another_commit_is_no_go(monkeypatch):
    binding = _source_binding("a")
    qa = _canonical_qa(binding, commit="b" * 40)
    qa["qa_record_fingerprint"] = pi._qa_record_fingerprint(qa)
    status, errors = pi.validate_canonical_qa_record(qa, binding)
    assert status == pi.QA_FAILED
    assert "QA source provenance mismatch: commit" in errors
    preflight = {"go": False, "gate_passes": True, "gate_errors": [],
                 "qa_status": status, "qa_errors": errors, "source_binding": binding}
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_Q_source_change_after_qa_is_no_go(monkeypatch):
    before = _source_binding("a")
    after = _source_binding("b")
    qa = _canonical_qa(before)
    states = iter([before, after])
    preflight = p7._production_preflight(
        REPO_ROOT,
        qa_executor=lambda root, binding: qa,
        source_inspector=lambda root: next(states),
        gate_verifier=lambda root: {"passes": True, "errors": []},
    )
    assert preflight["go"] is False
    assert any("source binding mismatch" in error for error in preflight["gate_errors"])
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_Q_source_change_after_preflight_before_provider_is_no_go(monkeypatch, tmp_path):
    preflight, _ = _production_preflight_with_qa()
    count = {"provider": 0}
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-phase2-sentinel")
    monkeypatch.setattr(rr.p7, "real_run_preflight", lambda root: preflight)
    monkeypatch.setattr(
        rr.pi,
        "verify_source_binding",
        lambda binding: {"matches": False, "errors": ["tracked source changed"]},
    )
    monkeypatch.setattr(
        rr, "provider_factory_for",
        lambda key: count.__setitem__("provider", count["provider"] + 1),
    )
    with pytest.raises(rr.ProviderUnavailable, match="tested source changed"):
        rr.run_haiku_batch(repo_root=REPO_ROOT, out_dir=tmp_path)
    assert count["provider"] == 0


def test_R_wrong_root_interpreter_or_import_origin_is_no_go(tmp_path, monkeypatch):
    wrong_root = pi.inspect_source_state(tmp_path)
    assert wrong_root["valid"] is False
    binding = _source_binding()
    qa = _canonical_qa(binding, python_executable="/wrong/python")
    qa["qa_record_fingerprint"] = pi._qa_record_fingerprint(qa)
    status, errors = pi.validate_canonical_qa_record(qa, binding)
    assert status == pi.QA_FAILED
    assert any("python_executable" in error or "command mismatch" in error for error in errors)
    preflight = {"go": False, "gate_passes": False,
                 "gate_errors": wrong_root["errors"], "qa_status": status,
                 "qa_errors": errors, "source_binding": binding}
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_S_untracked_runtime_override_is_no_go(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("src/agent_arena/override.py\n")
    override = tmp_path / "src/agent_arena/override.py"
    override.parent.mkdir(parents=True)
    override.write_text("OVERRIDE = True\n")
    assert "src/agent_arena/override.py" in pi._material_untracked_overrides(tmp_path)
    preflight = {"go": False, "gate_passes": False,
                 "gate_errors": ["material untracked/ignored runtime override present"],
                 "qa_status": pi.QA_NOT_EXECUTED, "qa_errors": [],
                 "source_binding": _source_binding()}
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_T_every_valid_condition_reaches_provider_once(monkeypatch, tmp_path):
    preflight, _ = _production_preflight_with_qa()
    _assert_provider_boundary(monkeypatch, preflight, 1, out_dir=tmp_path)


def test_U01_material_parent_and_real_subprocess_probe_match():
    binding = pi.inspect_source_state(REPO_ROOT)
    specification_fp = pi.full_replication_qa_specification_fingerprint()
    env, _ = pi._sanitized_qa_environment(binding, specification_fp)
    probe, error = pi._subprocess_origin_probe(binding, env)
    parent = pi.canonical_material_environment(REPO_ROOT, specification_fp)
    assert error is None
    assert probe["material_environment"] == parent["material_environment"]
    assert probe["material_environment_fingerprint"] == parent[
        "material_environment_fingerprint"
    ]


def test_U02_direct_venv_and_console_launcher_resolve_same_material_environment():
    tail = list(sys.path[1:])
    direct = _material_variant(
        _sys_path_entries=["", *tail],
        _python_executable=Path(sys.prefix) / "bin/python",
    )
    console = _material_variant(
        _sys_path_entries=[str(Path(sys.prefix) / "bin"), *tail],
        _python_executable=Path(sys.prefix) / "bin/python3",
    )
    assert direct["material_environment_fingerprint"] == console[
        "material_environment_fingerprint"
    ]
    assert direct["launcher_observation"] != console["launcher_observation"]


def test_U03_empty_and_authenticated_root_sys_path_zero_are_cosmetic():
    tail = list(sys.path[1:])
    empty = _material_variant(_sys_path_entries=["", *tail])
    rooted = _material_variant(_sys_path_entries=[str(REPO_ROOT), *tail])
    assert empty["material_environment_fingerprint"] == rooted[
        "material_environment_fingerprint"
    ]


def test_U04_only_authenticated_root_duplicates_are_cosmetic():
    tail = list(sys.path[1:])
    single = _material_variant(_sys_path_entries=["", *tail])
    duplicate_root = _material_variant(
        _sys_path_entries=["", str(REPO_ROOT), str(REPO_ROOT / "."), *tail]
    )
    duplicate_arbitrary = _material_variant(
        _sys_path_entries=["", *tail, tail[-1]]
    )
    assert single["material_environment_fingerprint"] == duplicate_root[
        "material_environment_fingerprint"
    ]
    assert single["material_environment_fingerprint"] != duplicate_arbitrary[
        "material_environment_fingerprint"
    ]


def test_U05_foreign_repository_root_fails_material_policy():
    material = _material_variant()
    material["material_environment"]["repository"]["repository_root"] = "/foreign/repo"
    material["material_environment_fingerprint"] = pi._fingerprint(
        material["material_environment"]
    )
    errors = pi.material_environment_policy_errors(
        material,
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
    )
    assert "material environment repository root mismatch" in errors


def test_U06_import_from_another_checkout_fails_material_policy():
    material = _material_variant()
    material["material_environment"]["package_origins"]["agent_arena"] = (
        "/foreign/checkout/src/agent_arena/__init__.py"
    )
    material["material_environment_fingerprint"] = pi._fingerprint(
        material["material_environment"]
    )
    errors = pi.material_environment_policy_errors(
        material,
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
    )
    assert "material runtime module origin differs from authenticated checkout" in errors


def test_U07_editable_install_pointing_elsewhere_fails_material_policy():
    distribution = copy.deepcopy(_material_variant()["material_environment"]["distribution"])
    distribution["direct_url"] = {
        "url": "file:///foreign/checkout",
        "dir_info": {"editable": True},
    }
    material = _material_variant(_distribution_identity=distribution)
    errors = pi.material_environment_policy_errors(
        material,
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
    )
    assert "editable distribution points to another checkout" in errors


def test_U08_injected_pythonpath_fails_material_policy():
    material = _material_variant(_environ={"PYTHONPATH": "/foreign/injected"})
    errors = pi.material_environment_policy_errors(
        material,
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
    )
    assert "caller-controlled Python or pytest environment override present" in errors


def test_U09_unexpected_import_shadowing_path_fails_material_policy(tmp_path):
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    material = _material_variant(_sys_path_entries=[str(shadow), *sys.path])
    errors = pi.material_environment_policy_errors(
        material,
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
    )
    assert "unexpected import-shadowing path precedes authenticated source" in errors


def test_U10_wrong_interpreter_or_virtual_environment_changes_material_identity():
    correct = _material_variant()
    wrong = _material_variant(
        _python_executable=Path(sys.executable).resolve(),
        _python_prefix=sys.base_prefix,
        _python_base_prefix=sys.base_prefix,
    )
    assert correct["material_environment_fingerprint"] != wrong[
        "material_environment_fingerprint"
    ]
    errors = pi.material_environment_policy_errors(
        wrong,
        REPO_ROOT,
        pi.full_replication_qa_specification_fingerprint(),
    )
    assert "production Python is not running in the bound virtual environment" in errors


def test_U11_wrong_package_origin_changes_fingerprint_and_fails():
    correct = _material_variant()
    origins = copy.deepcopy(correct["material_environment"]["package_origins"])
    origins["agent_arena.preflight_integrity"] = "/tmp/shadow/preflight_integrity.py"
    wrong = _material_variant(_package_origins=origins)
    assert correct["material_environment_fingerprint"] != wrong[
        "material_environment_fingerprint"
    ]
    assert "material runtime module origin differs from authenticated checkout" in (
        pi.material_environment_policy_errors(
            wrong,
            REPO_ROOT,
            pi.full_replication_qa_specification_fingerprint(),
        )
    )


def test_U12_tracked_source_change_after_qa_still_fails_closed():
    before = _source_binding("a")
    after = _source_binding("b")
    assert any(
        error.startswith("source binding mismatch")
        for error in pi.compare_source_binding(before, after)
    )


def test_U13_changed_canonical_qa_command_or_scope_fails_validation():
    binding = _source_binding()
    qa = _canonical_qa(binding)
    qa["command"] = [binding["python_executable"], "-m", "pytest", "-k", "one_test"]
    qa["canonical_specification"] = {"caller_selected": True}
    qa["qa_record_fingerprint"] = pi._qa_record_fingerprint(qa)
    status, errors = pi.validate_canonical_qa_record(qa, binding)
    assert status == pi.QA_FAILED
    assert "canonical QA specification mismatch" in errors
    assert "canonical QA command mismatch" in errors


def test_U14_genuine_qa_launch_failure_remains_could_not_execute():
    binding = _source_binding()

    def cannot_launch(*args, **kwargs):
        raise OSError("controlled launch failure")

    qa = pi.execute_canonical_qa(REPO_ROOT, binding, _runner=cannot_launch)
    assert qa["execution_status"] == pi.QA_COULD_NOT_EXECUTE


def test_U15_executed_failing_qa_remains_executed_and_failed():
    binding = _source_binding()
    calls = 0

    def failing_runner(command, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            probe = pi.canonical_material_environment(
                REPO_ROOT,
                pi.canonical_qa_specification_fingerprint(),
            )
            return subprocess.CompletedProcess(command, 0, json.dumps(probe), "")
        return subprocess.CompletedProcess(
            command,
            1,
            "collected 246 items\n245 passed, 1 failed",
            "",
        )

    qa = pi.execute_canonical_qa(REPO_ROOT, binding, _runner=failing_runner)
    assert qa["execution_status"] == pi.QA_FAILED
    assert qa["exit_code"] == 1


def test_U16_every_preflight_failure_keeps_provider_construction_zero(monkeypatch):
    preflight = {
        "go": False,
        "gate_passes": False,
        "gate_errors": ["material environment mismatch"],
        "qa_status": pi.QA_COULD_NOT_EXECUTE,
        "qa_errors": ["controlled failure"],
        "source_binding": _source_binding(),
    }
    _assert_provider_boundary(monkeypatch, preflight, 0)


def test_U17_materially_correct_environment_reaches_provider_sentinel_once(
    monkeypatch, tmp_path
):
    preflight, _ = _production_preflight_with_qa()
    _assert_provider_boundary(monkeypatch, preflight, 1, out_dir=tmp_path)
