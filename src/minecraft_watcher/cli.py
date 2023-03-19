from typer import Exit, Option, Typer

from .settings import get_settings
from .utils import console, version
from .watch import wait_for_no_players

# Allow invocation without subcommand so --version option does not produce an error
interface = Typer(invoke_without_command=True, no_args_is_help=True)


@interface.callback()
def version_callback(
    print_version: bool = Option(False, "--version", "-v", is_eager=True),
):
    if print_version:
        console.print(version())
        raise Exit()


@interface.command()
def watch():
    settings = get_settings()
    # console.print(get_num_players(settings.host, settings.port))
    wait_for_no_players(settings.host, settings.port)


def cli():
    """Run the CLI tool"""
    interface()
