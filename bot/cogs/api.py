"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""
from discord.ext.commands import Cog


class Template(Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Template(bot))
