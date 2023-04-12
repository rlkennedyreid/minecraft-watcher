from logging import getLogger

from tenacity import RetryError
from typer import Exit, Option, Typer

from .settings import get_settings
from .utils import console, version
from .watch import get_status, wait_for_no_players

_logger = getLogger(__name__)
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
    try:
        wait_for_no_players(settings.host, settings.port)
    except RetryError:
        _logger.error(
            "Watch command failed due to a retry error. Check that server is running and that webhook is correct."
        )
        raise Exit(1)


@interface.command()
def status():
    settings = get_settings()
    try:
        status = get_status(settings.host, settings.port)
    except RetryError:
        _logger.error(
            "Status command failed due to a retry error. Check that server is running and that webhook is correct."
        )
        raise Exit(1)
    console.print_json(data=status.raw)


def cli():
    """Run the CLI tool"""
    interface()
