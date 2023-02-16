"""
    File: /bot/__init__.py
    Usage: The bot's main file.
"""
from discord import Object as DiscordObject
from discord.ext.commands import Bot as BotBase
from . import config
from glob import glob
import logging
import os

_log = logging.getLogger(__name__)


class Bot(BotBase):
    def __init__(self, *args, **kwargs):
        self.Version = kwargs.get("version")
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
            guild = DiscordObject(id=guildid)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
