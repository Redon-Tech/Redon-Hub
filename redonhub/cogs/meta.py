"""
    File: /bot/cogs/meta.py
    Usage: Meta bot things, like status.
"""

from discord.ext.commands import Cog
from discord import Activity, ActivityType, Status
from redonhub import config, Bot
import logging

_log = logging.getLogger(__name__)


class Meta(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @property
    def presence(self):
        return self._presence.format(
            users=len(self.bot.users),
            prefix=config.Bot.Prefix,
            guilds=len(self.bot.guilds),
            version=self.bot.version,
        )

    @presence.setter
    def presence(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Invalid activity type")

        self._presence = value

    def status(self, value):
        if value not in (
            "online",
            "offline",
            "idle",
            "dnd",
            "do_not_disturb",
            "invisible",
        ):
            raise ValueError("Invalid status")

        self._status = value

    async def set_status(self):
        _data = self.presence.split(" ", maxsplit=1)
        if len(_data) > 1:
            await self.bot.change_presence(
                status=Status[self._status],
                activity=Activity(
                    name=_data[1],
                    type=getattr(ActivityType, _data[0], ActivityType.playing),
                ),
            )
        else:
            await self.bot.change_presence(status=Status[self._status])

    @Cog.listener()
    async def on_member_join(self, member):
        await self.set_status()

    @Cog.listener()
    async def on_raw_member_remove(self, member):
        await self.set_status()

    @Cog.listener()
    async def on_ready(self):
        self._presence = config.Activity.Presence
        self._status = config.Activity.Status
        await self.set_status()
        _log.info(f"Cog {__name__} ready")


async def setup(bot: Bot):
    await bot.add_cog(Meta(bot))
