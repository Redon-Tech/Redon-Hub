"""
    File: /bot/__init__.py
    Usage: The bot's main file.
"""
from discord import Intents
from discord.ext.commands import Bot as BotBase, when_mentioned_or
from dotenv import load_dotenv
from . import config, cogs
import logging
import os

load_dotenv()

_log = logging.getLogger(__name__)


class Bot(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_extensions(self, *names, package=None):
        # borrowed from pycord, modified for discord.py
        loaded_extensions = {} if store else []

        for ext_path in names:
            _log.info(f"Bot: Loading Extension {ext_path}")
            loaded = self.load_extension(
                ext_path, package=package
            )
            loaded_extensions.update(loaded) if store else loaded_extensions.extend(
                loaded
            )

        return loaded_extensions

    async def setup_hook(self):
        await super().setup_hook()

        self.bot.loop.create_task(self.load_extensions(cogs))

    def run(self, version):
        self.Version = version

        _log.info("Bot: Run Recieved")
        super().run(os.getenv("token"), reconnect=True)


bot = Bot(when_mentioned_or(config.Bot.Prefix), intents=Intents.all())
