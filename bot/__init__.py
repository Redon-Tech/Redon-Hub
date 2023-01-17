"""
    File: /bot/__init__.py
    Usage: The bot's main file.
"""
from discord import Intents
from discord.ext.commands import Bot as BotBase, when_mentioned_or
from dotenv import load_dotenv
from . import config
import logging
import os

load_dotenv()

_log = logging.getLogger(__name__)


class Bot(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, version):
        self.Version = version

        _log.info("Bot: Run Recieved")
        super().run(os.getenv("token"), reconnect=True)


bot = Bot(when_mentioned_or(config.Bot.Prefix), intents=Intents.all())
