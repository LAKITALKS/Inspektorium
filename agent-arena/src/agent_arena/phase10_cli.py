"""Supported local audit commands. No provider-name resolution or network fallback.

Offline mode accepts only the built-in recording. Live mode (AA-P10-LIVE/1.0) requires an
authorization directory and a registered profile; replay re-analyses captured live responses
without any model call.
"""
import json
from pathlib import Path

import click

from agent_arena.phase10_bundle import (
    inspect_bundle, release_candidate, review_candidate, run_audit,
)
from agent_arena.phase10_pipeline import preflight
from agent_arena.phase9_runtime import OfflineReviewProvider
from agent_arena.task_loader import load_task

PATH = click.Path(path_type=Path)


def _emit(result):
    # ASCII-escaped JSON: control or bidi characters quoted from model output never reach the terminal raw.
    click.echo(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=True))
    if hasattr(result, "valid"):
        raise click.exceptions.Exit(0 if result.valid else 2)
    raise click.exceptions.Exit(0 if result.status in {"READY_FOR_RELEASE", "RELEASED"} else 2)


def _task(path):
    try:
        return load_task(path)
    except Exception as exc:
        click.echo(json.dumps({"status": "PREFLIGHT_BLOCKED", "errors": [str(exc)]}))
        raise click.exceptions.Exit(2) from exc


@click.group()
def audit():
    """Canonical AA-P10 local audit: recorded offline, authorized live or live replay. No canonical PDF."""


@audit.command("validate")
@click.option("--task", required=True, type=PATH)
def validate(task):
    """Validate input without a provider call. Exit 0: input eligible; 2: blocked."""
    errors = preflight(_task(task))
    click.echo(json.dumps({"input_valid": not errors, "errors": errors,
                           "release_authorized": False}))
    raise click.exceptions.Exit(2 if errors else 0)


@audit.command("run")
@click.option("--offline", is_flag=True, help="Built-in recorded offline response (AA-P10/1.0).")
@click.option("--live", is_flag=True, help="Live generation under an AA-P10-LIVE/1.0 authorization.")
@click.option("--replay", is_flag=True, help="Offline replay of captured live responses; no model call.")
@click.option("--task", required=True, type=PATH)
@click.option("--recording", type=PATH, help="Offline only: recorded response file.")
@click.option("--authorization-dir", type=PATH, help="Live/replay only: authorization, ledger and captures.")
@click.option("--profile", help="Live/replay only: registered profile ID, e.g. claude-haiku-5-5@3.")
@click.option("--output-root", required=True, type=PATH)
def run(offline, live, replay, task, recording, authorization_dir, profile, output_root):
    """Run one case through the real runner/parser/P8/P9/controls. 0: READY; 2: blocked."""
    if [offline, live, replay].count(True) != 1:
        raise click.UsageError("Choose exactly one of --offline, --live or --replay.")
    if offline:
        if recording is None or authorization_dir is not None or profile is not None:
            raise click.UsageError("--offline requires --recording and takes no live options.")
        try:
            # Bytes, not read_text: the stored raw output equals the file exactly (no newline translation).
            provider = OfflineReviewProvider(recording.read_bytes().decode("utf-8"))
        except (OSError, UnicodeError) as exc:
            raise click.ClickException(f"Cannot read recording: {exc}") from exc
        _emit(run_audit(_task(task), provider, output_root=output_root))
    if recording is not None or authorization_dir is None or not profile:
        raise click.UsageError("--live/--replay require --authorization-dir and --profile, not --recording.")
    from uuid import uuid4
    from agent_arena.bounded_harness_mission import MissionError
    from agent_arena.phase10_live import LiveAuditProvider, LiveSession, ReplayProvider
    from agent_arena.providers.anthropic_live import PROFILES
    loaded = _task(task)
    if profile not in PROFILES:
        click.echo(json.dumps({"status": "PREFLIGHT_BLOCKED", "errors": [f"Unknown live profile: {profile}"]}))
        raise click.exceptions.Exit(2)
    try:
        session = LiveSession(authorization_dir, mode="live" if live else "replay")
    except (OSError, ValueError, MissionError, KeyError) as exc:
        click.echo(json.dumps({"status": "PREFLIGHT_BLOCKED", "errors": [f"Live authorization unusable: {exc}"]}))
        raise click.exceptions.Exit(2) from exc
    with session:
        try:
            provider = (LiveAuditProvider if live else ReplayProvider)(
                session, profile, loaded.id, "primary", PROFILES[profile].prompt_versions[0])
        except ValueError as exc:
            click.echo(json.dumps({"status": "PREFLIGHT_BLOCKED", "errors": [str(exc)]}))
            raise click.exceptions.Exit(2) from exc
        # Replay keeps its Phase-9 state next to its output, never inside the (possibly sealed)
        # authorization evidence directory (Package B, P10-F4).
        state = Path(authorization_dir) / "phase9-state" if live else Path(output_root) / f"replay-state/{uuid4()}"
        _emit(run_audit(loaded, provider, output_root=output_root, review_state=state))


@audit.command("inspect")
@click.option("--bundle", required=True, type=PATH)
def inspect(bundle):
    """Revalidate files/raw/history/current controls, zero calls. 0: intact (see status); 2: invalid."""
    _emit(inspect_bundle(bundle))


@audit.command("review")
@click.option("--bundle", required=True, type=PATH)
@click.option("--state-dir", required=True, type=PATH)
@click.option("--output-root", required=True, type=PATH)
@click.option("--select", "selected_position_id", required=True)
@click.option("--reviewer", required=True)
@click.option("--reason", required=True)
@click.option("--correction", type=PATH)
def review(bundle, state_dir, output_root, selected_position_id, reviewer, reason, correction):
    """Explicit host human selection/correction, immutable revision. 0: READY; 2: review blocked."""
    try:
        raw = correction.read_bytes().decode("utf-8") if correction else None
    except (OSError, UnicodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    _emit(review_candidate(bundle, output_root=output_root, state_dir=state_dir,
                           selected_position_id=selected_position_id, reviewer=reviewer,
                           reason=reason, corrected_raw_output=raw))


@audit.command("release")
@click.option("--bundle", required=True, type=PATH)
@click.option("--output-root", required=True, type=PATH)
@click.option("--reviewer", required=True)
@click.option("--reason", required=True)
def release(bundle, output_root, reviewer, reason):
    """Explicit local-artifact release of final checked MD/HTML. 0: RELEASED; 2: blocked."""
    _emit(release_candidate(bundle, output_root=output_root, reviewer=reviewer, reason=reason))
