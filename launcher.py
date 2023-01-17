"""
    File: /launcher.py
    Usage: Sets up logging and runs the bot.
"""

from bot import bot
from logging.handlers import RotatingFileHandler
import asyncio
import logging
import discord
import contextlib

version = "0.1"


class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name="discord.state")

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelname == "WARNING" and "referencing an unknown" in record.msg:
            return False
        return True


@contextlib.contextmanager
def setup_logging():
    log = logging.getLogger()

    try:
        discord.utils.setup_logging()
        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("discord.state").addFilter(RemoveNoise())

        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename="redonhub.log",
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=5,
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
        )
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


with setup_logging():
    bot.run(version)
