"""
    File: /launcher.py
    Usage: Sets up logging and runs the bot.
"""

from bot import Bot, config
from bot.utils.logging import setup_logging
from discord import Intents
from discord.ext.commands import when_mentioned_or
from dotenv import load_dotenv
import os

load_dotenv()

version = "1.0-alpha.1"
handler = None
bot = Bot(
    when_mentioned_or(config.Bot.Prefix),
    intents=Intents.all(),
    # Everything below is only required for the cogs to run, not the bot itself.
    version=version,
    owner_ids=config.Bot.Owners,
)


def main():
    with setup_logging():
        bot.run(os.getenv("token"))


if __name__ == "__main__":
    main()
