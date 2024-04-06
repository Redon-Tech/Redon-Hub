"""
    File: /bot/__init__.py
    Usage: The bot's main file.
"""

from discord import Object as DiscordObject
from discord.ext.commands import Bot as BotBase
from . import config
from .data import database
from glob import glob
import logging
import os

_log = logging.getLogger(__name__)
__version__ = "1.0.0"


class Bot(BotBase):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.get("version", "N/A")
        self.ready = False
        super().__init__(*args, **kwargs)

    async def load_extensions(self):
        # Original code from pycord

        cogs = [
            path.split(os.sep)[-1][:-3]
            for path in glob(f"{os.path.realpath(os.path.dirname(__file__))}/cogs/*.py")
        ]

        for cog in cogs:
            _log.info(f"Bot: Loading Extension {cog}")
            await self.load_extension(f"bot.cogs.{cog}")

        await self.sync_commands()

    async def setup_hook(self):
        await super().setup_hook()

        self.loop.create_task(self.load_extensions())

    async def sync_commands(self):
        for guildid in config.Bot.Guilds:
            guild = await self.fetch_guild(guildid)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            _log.info(f"Bot Online | {self.user} | {self.user.id}")

            await database.connect()

            _log.info("Database Connected")
