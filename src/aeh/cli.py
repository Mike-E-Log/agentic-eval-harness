import click

from aeh import __version__
from aeh import demo as _demo


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
