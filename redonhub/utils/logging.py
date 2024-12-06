"""
    File: /bot/utils/logging.py
    Usage: Sets up logging handler.
"""

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from discord.utils import _ColourFormatter, stream_supports_colour
import logging
import discord
import contextlib


class RemoveNoise(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelname == "WARNING" and "referencing an unknown" in record.msg:
            return False
        if record.levelname == "INFO" and record.name == "httpx":
            return False
        if (
            record.levelname == "INFO"
            and record.name == "discord.gateway"
            and "RESUMED" in record.msg
        ):
            return False
        return True


max_bytes = 1 * 1024 * 1024  # 1 MiB
dt_fmt = "%Y-%m-%d %H:%M:%S"
fmt = logging.Formatter(
    "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
)


@contextlib.contextmanager
def cli_logger():
    cliHander = StreamHandler()
    cliHander.setFormatter(fmt)

    if stream_supports_colour(cliHander.stream):
        cliHander.setFormatter(_ColourFormatter())

    log = logging.getLogger("CLI")

    try:
        log.setLevel(logging.INFO)
        log.addHandler(cliHander)
        yield
    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


@contextlib.contextmanager
def setup_logging():
    handler = RotatingFileHandler(
        filename="redonhub.log",
        encoding="utf-8",
        mode="w",
        maxBytes=max_bytes,
        backupCount=2,
    )
    handler.setFormatter(fmt)

    log = logging.getLogger()
    fastapi = logging.getLogger("fastapi")

    try:
        discord.utils.setup_logging()
        # __enter__
        # logging.getLogger("discord").setLevel(logging.INFO)
        # logging.getLogger("discord.http").setLevel(logging.WARNING)
        # logging.getLogger("discord.state").addFilter(RemoveNoise())
        # logging.getLogger("httpx").addFilter(RemoveNoise())
        # logging.getLogger("discord.gateway").addFilter(RemoveNoise())

        log.setLevel(logging.INFO)
        fastapi.setLevel(logging.INFO)

        log.addHandler(handler)
        fastapi.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)
