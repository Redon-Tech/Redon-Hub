"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""
from discord.ext.commands import Cog
from fastapi import FastAPI
from bot import config
import uvicorn
import logging

_log = logging.getLogger(__name__)
app = FastAPI()
app.logger = _log

server = uvicorn.Server(
    uvicorn.Config(
        app,
        host=config.API.IP,
        port=config.API.Port,
        loop="none",
    )
)


class API(Cog):
    def __init__(self, bot):
        self.bot = bot

    def overwrite_uvicorn_logger(self):
        for name in logging.root.manager.loggerDict.keys():
            if name.startswith("uvicorn"):
                logging.getLogger(name).handlers = []
                logging.getLogger(name).propagate = True

    @Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(server.serve())
        self.overwrite_uvicorn_logger()


async def setup(bot):
    await bot.add_cog(API(bot))
