"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""
from discord.ext.commands import Cog
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse
from bot import config
import uvicorn
import logging

_log = logging.getLogger(__name__)
app = FastAPI()
app.logger = _log
cog = None
X_API_KEY = OAuth2PasswordBearer(config.API.Key)


def api_auth(x_api_key: str = Depends(X_API_KEY)):
    if x_api_key != config.API.Key:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

    return x_api_key


@app.get("/")
async def root():
    return {"message": "Online", "Version": cog.bot.Version}


## Users
@app.get("/v1")
async def v1root():
    return RedirectResponse(url="/")


@app.get("/v1/users", dependencies=[Depends(api_auth)])
async def get_users():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.post("/v1/users", dependencies=[Depends(api_auth)])
async def create_user():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.get("/v1/users/{user_id}", dependencies=[Depends(api_auth)])
async def get_user(user_id):
    raise HTTPException(status_code=501, detail="Not Implemented")


## Products
@app.get("/v1/products", dependencies=[Depends(api_auth)])
async def get_products():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.post("/v1/products", dependencies=[Depends(api_auth)])
async def create_product():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.get("/v1/products/{product_id}", dependencies=[Depends(api_auth)])
async def get_product():
    raise HTTPException(status_code=501, detail="Not Implemented")


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
        global cog
        cog = self
        self.bot.loop.create_task(server.serve())
        self.overwrite_uvicorn_logger()
        _log.info(f"Cog {__name__} ready, syncing commands...")
        await self.bot.sync_commands()


async def setup(bot):
    await bot.add_cog(API(bot))
