"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""
from discord.ext.commands import Cog
from fastapi import FastAPI
from bot import config
import uvicorn

app = FastAPI()

server = uvicorn.Server(
    uvicorn.Config(
        app,
        host=config.API.IP,
        port=config.API.Port,
        loop="none"
    )
)

class API(Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(API(bot))
