"""Supported local audit commands. No provider-name resolution or network fallback."""
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
    click.echo(result.model_dump_json(indent=2))
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
    """Canonical AA-P10 local audit; recorded OFFLINE only. No canonical PDF."""


@audit.command("validate")
@click.option("--task", required=True, type=PATH)
def validate(task):
    """Validate input without a provider call. Exit 0: input eligible; 2: blocked."""
    errors = preflight(_task(task))
    click.echo(json.dumps({"input_valid": not errors, "errors": errors,
                           "release_authorized": False}))
    raise click.exceptions.Exit(2 if errors else 0)


@audit.command("run")
@click.option("--offline", is_flag=True, required=True)
@click.option("--task", required=True, type=PATH)
@click.option("--recording", required=True, type=PATH)
@click.option("--output-root", required=True, type=PATH)
def run(offline, task, recording, output_root):
    """Run captured response bytes through real runner/parser/controls. 0: READY; 2: blocked."""
    try:
        provider = OfflineReviewProvider(recording.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise click.ClickException(f"Cannot read recording: {exc}") from exc
    _emit(run_audit(_task(task), provider, output_root=output_root))


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
        raw = correction.read_text(encoding="utf-8") if correction else None
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
