"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""
from discord.ext.commands import Cog
from discord import app_commands, Interaction
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse
from bot import config
from bot.data import get_user, get_user_by_discord_id, create_user
import uvicorn
import logging
import random
import string

_log = logging.getLogger(__name__)
app = FastAPI()
app.logger = _log
cog = None
X_API_KEY = OAuth2PasswordBearer(config.API.Key)
verificationKeys = {}


def api_auth(x_api_key: str = Depends(X_API_KEY)):
    if x_api_key != config.API.Key:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

    return x_api_key


@app.get("/")
async def root():
    return {"message": "Online", "Version": cog.bot.Version}


## Websocket
@app.websocket("/v1/socket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if websocket.headers.get("Authorization") != f"Bearer {config.API.Key}":
        await websocket.close(code=1008)
        return
    while True:
        data = await websocket.receive_json()
        if data.get("type") == "verify_user":
            _log.info(f"Got Verification Request for {data.get('data')}")

            try:
                user = await get_user(cog.bot.database, data.get("data"))
            except Exception as e:
                user = None

            if not user or user.discordId == 0:
                key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
                verificationKeys[key] = data.get("data")
                await websocket.send_json({"data": key})
            else:
                await websocket.send_json({"data": "user_verified"})


## Users
@app.get("/v1")
async def v1root():
    return RedirectResponse(url="/")


@app.get("/v1/users", dependencies=[Depends(api_auth)])
async def users_get():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.post("/v1/users/{user_id}/verify", dependencies=[Depends(api_auth)])
async def users_post_verify(user_id: int):
    try:
        user = await get_user(cog.bot.database, user_id)
    except Exception as e:
        user = None

    if not user or user.discordId == 0:
        key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        verificationKeys[key] = user_id
        return {"message": "Verification Key Created", "data": key}
    else:
        return {"message": "User Already Verified"}


@app.get("/v1/users/{user_id}", dependencies=[Depends(api_auth)])
async def users_get_user(user_id):
    raise HTTPException(status_code=501, detail="Not Implemented")


## Products
@app.get("/v1/products", dependencies=[Depends(api_auth)])
async def products_get():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.post("/v1/products", dependencies=[Depends(api_auth)])
async def products_post():
    raise HTTPException(status_code=501, detail="Not Implemented")


@app.get("/v1/products/{product_id}", dependencies=[Depends(api_auth)])
async def products_get_product():
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

    verifyGroup = app_commands.Group(
        name="verify", description="Commands regarding verification"
    )

    @verifyGroup.command(name="link")
    async def verify_link(self, interaction: Interaction, key: str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if key in verificationKeys:
            try:
                user = await get_user(self.bot.database, verificationKeys[key])
            except Exception as e:
                user = None

            if user:
                user.discordId = interaction.user.id
                await user.push()
                await interaction.followup.send("User verified!", ephemeral=True)
            else:
                user = await create_user(self.bot.database, verificationKeys[key])
                user.discordId = interaction.user.id
                await user.push()
                await interaction.followup.send("User verified!", ephemeral=True)
        else:
            await interaction.followup.send("Invalid key.", ephemeral=True)

    @verifyGroup.command(name="unlink")
    async def verify_unlink(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            user = await get_user_by_discord_id(self.bot.database, interaction.user.id)
        except Exception as e:
            user = None

        if user and user.discordId != 0:
            user.discordId = 0
            await user.push()
            await interaction.followup.send("User unverified!", ephemeral=True)
        else:
            await interaction.followup.send("User not verified.", ephemeral=True)

    @Cog.listener()
    async def on_ready(self):
        global cog
        cog = self
        self.bot.loop.create_task(server.serve())
        self.overwrite_uvicorn_logger()
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(API(bot))
