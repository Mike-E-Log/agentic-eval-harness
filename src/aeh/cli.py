import uuid
from pathlib import Path

import click

from aeh import __version__
from aeh import demo as _demo
from aeh import preflight
from aeh.state_store import StateError, StateStore


@click.group(invoke_without_command=True)
@click.version_option(__version__, "--version", prog_name="aeh")
@click.pass_context
def main(ctx):
    """aeh - eval-gated runner for coding agents."""
    if ctx.invoked_subcommand is None:
        click.echo("aeh - eval-gated runner for coding agents.\n")
        click.echo("Start here:\n  aeh demo            replay a recorded gate (no CLI, no keys)\n")
        click.echo("Commands:\n  run <project>   resume <id>   status <id>   show <id>")
        click.echo("  list            cleanup <id>  demo")


@main.command(name="demo")
def demo_cmd():
    """Replay a recorded gate run (no claude CLI, no API keys)."""
    _demo.run_demo()


@main.command()
@click.argument("project", type=click.Path(exists=True, file_okay=False), default=".")
def run(project):
    """Drive a project through the phases (creates a new run)."""
    ok, msg = preflight.check_claude()
    if not ok:
        raise SystemExit(msg)
    present, missing = preflight.available_judges()
    if missing:
        click.echo(f"note: no key for {', '.join(missing)} - those judges are disabled. "
                   f"Running with: {', '.join(present) or 'none'}.")
    run_id = uuid.uuid4().hex[:8]
    click.echo(f"run started: {run_id} - resume with 'aeh resume {run_id}'")
    StateStore(Path(project), run_id).write(
        {"project": str(project), "phase": None, "status": "running"})


@main.command(name="list")
def list_runs():
    """List known runs."""
    base = Path(".aeh") / "runs"
    if not base.is_dir():
        click.echo("no runs yet - `aeh run <project>` to start one")
        return
    for d in sorted(base.iterdir()):
        try:
            st = StateStore(Path("."), d.name).read()
            click.echo(f"{d.name}  {st.get('project', '?')}  {st.get('phase', '-')}  {st.get('status', '-')}")
        except StateError as e:
            click.echo(f"{d.name}  <unreadable: {e}>")


@main.command()
@click.argument("run_id")
def status(run_id):
    """Show a run's current state."""
    click.echo(StateStore(Path("."), run_id).read())


@main.command()
@click.argument("run_id")
def show(run_id):
    """Re-print the gate scorecard for a run's last gated phase."""
    from aeh.models import GateResult
    from aeh.renderer import render_gate
    st = StateStore(Path("."), run_id).read()
    if st.get("last_gate"):
        click.echo(render_gate(GateResult.from_dict(st["last_gate"])))
    else:
        click.echo("no gate output recorded yet for this run")


@main.command()
@click.argument("run_id")
@click.option("--force", is_flag=True, help="actually delete (default is dry-run)")
def cleanup(run_id, force):
    """Remove a run's worktree (state.json is preserved)."""
    from aeh.worktree_manager import remove_worktree
    wt = Path(".aeh") / "worktrees" / run_id
    if not force:
        click.echo(f"dry-run: would remove worktree {wt}. state.json survives. "
                   f"re-run with --force to delete.")
        return
    remove_worktree(Path("."), run_id)
    click.echo(f"removed worktree for {run_id}; state preserved at .aeh/runs/{run_id}/state.json")


@main.command()
@click.argument("run_id")
def resume(run_id):
    """Resume a run from its persisted state."""
    from aeh.orchestrator import resume_action
    st = StateStore(Path("."), run_id).read()
    click.echo(f"resume {run_id}: action={resume_action(st)} "
               f"(phase={st.get('phase')}, status={st.get('status')})")
