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

version = "0.1"
handler = None
bot = Bot(
    when_mentioned_or(config.Bot.Prefix),
    intents=Intents.all(),
    # None required by client, but required by our cogs
    version=version,
    owner_ids=config.Bot.Owners,
)


with setup_logging():
    bot.run(os.getenv("token"))
