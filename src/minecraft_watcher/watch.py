from logging import ERROR, getLogger
from time import sleep

from mcstatus import JavaServer
from mcstatus.pinger import PingResponse
from requests import post
from tenacity import (
    RetryError,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_fixed,
    wait_random,
)

from .settings import get_settings

_logger = getLogger(__name__)


@retry(
    wait=wait_fixed(10) + wait_random(0, 2),
    stop=stop_after_attempt(60),
    before_sleep=before_sleep_log(_logger, ERROR),
)
def get_status(host: str, port: int) -> PingResponse:
    server = JavaServer.lookup(host, port)

    _logger.debug(f"Parsed server: {server.address.host}:{server.address.port}")

    return server.status()


def get_num_players(host: str, port: int) -> int:
    status = get_status(host, port)

    _logger.debug(status)

    return status.players.online


def wait_for_no_players(host: str, port: int):
    """Method to repeatedly poll server until there has been no players for a given amount of time"""
    _logger.info("waiting for no players")
    settings = get_settings()
    countdown = False

    while True:
        sleep(settings.timeout_s)

        _logger.debug("getting number of players")

        try:
            no_players = get_num_players(host, port) == 0
        except RetryError as err:
            _logger.error(
                "Failed to get number of players for server due to retry error"
            )
            raise err

        _logger.info(f"No players: {no_players}, countdown: {countdown}")

        if no_players and countdown:
            try:
                kill_server()
            except RetryError as err:
                _logger.error("Retry error when attempting to kill server")
                raise err
            break
        elif no_players:
            countdown = True
        elif not no_players:
            countdown = False


@retry(
    wait=wait_fixed(10) + wait_random(0, 2),
    stop=stop_after_attempt(6),
    before_sleep=before_sleep_log(_logger, ERROR),
)
def kill_server():
    url = get_settings().kill_webhook
    _logger.info("Initiating shutdown webhook")
    response = post(url)
    response.raise_for_status()
    _logger.info(response.text)
