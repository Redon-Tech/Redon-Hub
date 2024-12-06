"""
    File: /bot/models/cog.py
    Usage: A custom cog class that defines a "bot"
"""

from discord.ext.commands import Cog
from redonhub import Bot


class CustomCog(Cog):
    bot: Bot
