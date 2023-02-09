"""
    File: /bot/__init__.py
    Usage: The bot's main file.
"""
from discord import Intents, Object as DiscordObject
from discord.ext.commands import Bot as BotBase, when_mentioned_or
from dotenv import load_dotenv
from . import config, cogs
from glob import glob
import logging
import os

load_dotenv()

_log = logging.getLogger(__name__)


class Bot(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def load_extensions(self):
        # borrowed from pycord, modified for our usage

        cogs = [
            path.split(os.sep)[-1][:-3]
            for path in glob(f"{os.path.realpath(os.path.dirname(__file__))}/cogs/*.py")
        ]

        for cog in cogs:
            _log.info(f"Bot: Loading Extension {cog}")
            await self.load_extension(f"bot.cogs.{cog}")

        await self.sync_commands()
        # for ext_path in names:
        #     _log.info(f"Bot: Loading Extension {ext_path}")
        #     await self.load_extension(ext_path, package=package)

    async def setup_hook(self):
        await super().setup_hook()

        bot.loop.create_task(self.load_extensions())

    async def sync_commands(self):
        for guildid in config.Bot.Guilds:
            guild = DiscordObject(id=guildid)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    def run(self, version):
        self.Version = version

        _log.info("Bot: Run Recieved")
        super().run(os.getenv("token"), reconnect=True)


bot = Bot(when_mentioned_or(config.Bot.Prefix), intents=Intents.all())
