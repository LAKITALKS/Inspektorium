"""Frozen retry accounting for the registered Phase-5A condition schedule.

This module does not implement retries.  It binds and explains the two retry
layers already active on the guarded condition path: Anthropic SDK transport
retries and the outer provider-error pass loop in ``phase7a_real_run``.
"""

from __future__ import annotations

from agent_arena.providers.anthropic import MAX_TRANSPORT_RETRIES


RETRY_CONTRACT_SCHEMA_VERSION = "agent_arena.condition_retry_contract/v1"
RETRY_CONTRACT_ID = "AA-P5A-RETRY-ACCOUNTING-001"

# Existing Phase-7A behavior, now named once for both execution and accounting.
# The count includes the initial pass; therefore at most two outer reissues occur.
PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION = 3


def build_retry_contract(
    *,
    analytical_slots: int,
    guarded_batch_invocations: int,
    slots_per_batch: int,
) -> dict:
    """Return the finite bound for one invocation of each scheduled batch.

    A later re-entry is deliberately outside this finite schedule: checkpoints
    prevent terminal slots from being called again, but no persistent counter
    caps repeated invocations of authenticated nonterminal provider failures.
    """
    for name, value in (
        ("analytical_slots", analytical_slots),
        ("guarded_batch_invocations", guarded_batch_invocations),
        ("slots_per_batch", slots_per_batch),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if guarded_batch_invocations * slots_per_batch != analytical_slots:
        raise ValueError("batch schedule does not account for every analytical slot")

    sdk_http_attempts = 1 + MAX_TRANSPORT_RETRIES
    outer_passes = PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION
    provider_invocations_per_batch = slots_per_batch * outer_passes
    provider_invocations_schedule = analytical_slots * outer_passes
    return {
        "retry_contract_schema_version": RETRY_CONTRACT_SCHEMA_VERSION,
        "retry_contract_id": RETRY_CONTRACT_ID,
        "layers": [
            {
                "layer_id": "anthropic_sdk_transport",
                "configuration_source": (
                    "agent_arena.providers.anthropic.MAX_TRANSPORT_RETRIES"
                ),
                "initial_attempts_per_provider_invocation": 1,
                "retry_attempts_after_initial_max": MAX_TRANSPORT_RETRIES,
                "http_attempts_per_provider_invocation_max": sdk_http_attempts,
                "retry_scope": "one AnthropicProvider.generate invocation",
                "counter_resets_on": "each provider-method invocation",
            },
            {
                "layer_id": "outer_provider_error_passes",
                "configuration_source": (
                    "agent_arena.condition_retry."
                    "PROVIDER_ERROR_PASSES_PER_GUARDED_INVOCATION"
                ),
                "passes_per_guarded_invocation_max": outer_passes,
                "pass_count_includes_initial_pass": True,
                "provider_reissues_after_initial_max": outer_passes - 1,
                "eligible_for_reissue": "provider/transport error only",
                "terminal_semantic_reissue": "PROHIBITED",
                "retry_scope": "one analytical slot within one guarded invocation",
                "counter_resets_on": "each later guarded invocation or resume",
            },
            {
                "layer_id": "checkpoint_resume",
                "configuration_source": (
                    "agent_arena.phase7a_execution.is_terminal_attempt and "
                    "agent_arena.resume_integrity.validate_resume_checkpoint"
                ),
                "terminal_slots_reused_without_provider_call": True,
                "authenticated_nonterminal_provider_failures_reeligible": True,
                "adds_automatic_attempts_within_invocation": False,
                "persistent_cross_invocation_attempt_counter": "NOT_ENFORCED",
                "counter_resets_on": "not applicable; this layer has no attempt counter",
            },
            {
                "layer_id": "scheduled_reentry",
                "configuration_source": "AA-P5A-MEOV-PAIRED-001",
                "guarded_invocations_per_batch_in_schedule": 1,
                "additional_invocations_or_restarts_in_schedule": 0,
                "additional_invocation_policy": (
                    "REQUIRES_SEPARATELY_REVIEWED_BUDGET_AND_EXECUTION_AUTHORIZATION"
                ),
                "additional_invocation_policy_runtime_enforcement": (
                    "NOT_ENFORCED_BY_A_PERSISTENT_CUMULATIVE_COUNTER"
                ),
                "counter_resets_on": "not applicable; fixed schedule permits one invocation",
            },
        ],
        "schedule": {
            "analytical_slots": analytical_slots,
            "guarded_batch_invocations": guarded_batch_invocations,
            "slots_per_batch": slots_per_batch,
            "provider_method_invocations_per_batch_max": provider_invocations_per_batch,
            "provider_method_invocations_schedule_max": provider_invocations_schedule,
            "sdk_retry_http_attempts_schedule_max": (
                provider_invocations_schedule * MAX_TRANSPORT_RETRIES
            ),
            "http_attempts_per_batch_max": provider_invocations_per_batch * sdk_http_attempts,
            "http_attempts_schedule_max": provider_invocations_schedule * sdk_http_attempts,
        },
        "persistent_cross_invocation_spending_cap_enforced": False,
        "availability_probe_http_attempts_in_guarded_path": 0,
        "additional_automatic_retry_layers": [],
    }
