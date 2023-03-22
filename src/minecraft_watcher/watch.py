#!/usr/bin/env python3
from json import loads
from struct import pack
from socket import socket, AF_INET, SOCK_STREAM
from logging import getLogger
from .settings import get_settings
from time import sleep
from requests import post
from tenacity import (
    retry,
    wait_fixed,
    wait_random,
    stop_after_attempt,
    before_sleep_log,
)
from logging import ERROR

_logger = getLogger(__name__)


def popint(s):
    acc = 0
    b = ord(s.recv(1))
    while b & 0x80:
        acc = (acc << 7) + (b & 0x7F)
        b = ord(s.recv(1))
    return (acc << 7) + (b & 0x7F)


def pack_varint(d):
    return bytes(
        [
            (0x40 * (i != d.bit_length() // 7)) + ((d >> (7 * (i))) % 128)
            for i in range(1 + d.bit_length() // 7)
        ]
    )


def pack_data(d):
    return pack_varint(len(d)) + d


@retry(wait=wait_fixed(10) + wait_random(0, 2))
def get_info(host: str, port: int) -> dict:
    # https://wiki.vg/Server_List_Ping#Current

    s = socket(AF_INET, SOCK_STREAM)

    try:
        s.connect((host, port))
    except ConnectionRefusedError as err:
        _logger.error(f"Connection refused error for host {host}:{port}")
        raise err

    s.send(
        pack_data(
            bytes(2) + pack_data(bytes(host, "utf8")) + pack(">H", port) + bytes([1])
        )
        + bytes([1, 0])
    )

    popint(s)  # Packet length
    popint(s)  # Packet ID

    l, d = popint(s), bytes()

    while len(d) < l:
        d += s.recv(1024)

    s.close()

    info = loads(d.decode("utf8"))

    if not isinstance(info, dict):
        e = TypeError("Server info did not parse to dict")
        _logger.error(e)
        raise e

    return info


@retry(
    wait=wait_fixed(10) + wait_random(0, 2),
)
def get_num_players(host: str, port: int) -> int:
    info = get_info(host, port)

    _logger.debug(info)

    try:
        num_players = info["players"]["online"]
    except KeyError as err:
        _logger.error("could not extract player number from dictionary")
        raise err

    if not isinstance(num_players, int):
        e = TypeError("num players in not an integer")
        _logger.error(e)
        raise e

    return num_players


def wait_for_no_players(host: str, port: int):
    """Method to repeatedly poll server until there has been no players for a given amount of time"""
    _logger.info("waiting for no players")
    settings = get_settings()
    countdown = False

    while True:
        no_players = get_num_players(host, port) == 0

        _logger.info(f"No players: {no_players}, countdown: {countdown}")

        if no_players and countdown:
            kill_server()
            break
        elif no_players:
            countdown = True

        sleep(settings.timeout_s)


@retry(
    wait=wait_fixed(10) + wait_random(0, 2),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(_logger, ERROR),
)
def kill_server():
    url = get_settings().kill_webhook
    _logger.info("Initiating shutdown webhook")
    response = post(url)
    response.raise_for_status()
    _logger.info(response.text)
