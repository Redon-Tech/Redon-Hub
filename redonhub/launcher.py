"""
    File: /launcher.py
    Usage: Sets up logging and runs the bot.
"""

from redonhub import Bot, config, __version__ as version
from redonhub.utils.logging import setup_logging
from discord import Intents
from discord.ext.commands import when_mentioned_or
from dotenv import load_dotenv
from logging import getLogger
import os
import sys
import asyncio

load_dotenv(os.getcwd() + "/.env")

_log = getLogger(__name__)
handler = None
bot = Bot(
    when_mentioned_or(config.Bot.Prefix),
    intents=Intents.all(),
    # Everything below is only required for the cogs to run, not the bot itself.
    version=version,
    owner_ids=config.Bot.Owners,
)


async def run():
    with setup_logging():
        token = os.getenv("token")
        if token is None:
            _log.critical("No token found in .env file.")
            sys.exit(1)

        if os.getenv("database") is None:
            _log.critical("No database found in .env file.")
            sys.exit(1)

        try:
            await bot.start(token)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            _log.error("An error occurred while running the bot.")
            _log.exception(e)
        finally:
            sys.exit(0)


if __name__ == "__main__":
    asyncio.run(run())
