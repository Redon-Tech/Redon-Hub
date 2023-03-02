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
from bot.data import (
    get_user,
    get_users,
    get_user_by_discord_id,
    create_user,
    get_products,
    get_product_by_name,
    get_product,
    create_product,
    delete_product,
)
from pydantic import BaseModel
from typing import Union
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


# Schemas


class Tag(BaseModel):
    name: str
    color: list
    textColor: list


class Product(BaseModel):
    name: str
    description: Union[str, None]
    price: float
    productId: float
    attachments: list
    tags: list


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
                user = await get_user(data.get("data"))
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
    try:
        users = await get_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for user in users:
        results[user.id] = user.to_dict()

    return results


@app.get("/v1/users/{user_id}", dependencies=[Depends(api_auth)])
async def users_get_user(user_id: int, discordId: bool = False):
    try:
        if discordId:
            user = await get_user_by_discord_id(user_id)
        else:
            user = await get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user.to_dict()


@app.post("/v1/users/{user_id}/verify", dependencies=[Depends(api_auth)])
async def users_post_verify(user_id: int):
    try:
        user = await get_user(user_id)
    except Exception as e:
        user = None

    if not user or user.discordId == 0:
        key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        verificationKeys[key] = user_id
        return {"message": "Verification Key Created", "data": key}
    else:
        return {"message": "User Already Verified"}


## Products
@app.get("/v1/products", dependencies=[Depends(api_auth)])
async def products_get():
    try:
        products = await get_products()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for product in products:
        results[product.id] = product.to_dict()

    return results


@app.get("/v1/products/{product_id}", dependencies=[Depends(api_auth)])
async def products_get_product(product_id: Union[int, str]):
    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found (By Name)")

    try:
        product = await get_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Product Not Found")

    return product.to_dict()


@app.post("/v1/products", dependencies=[Depends(api_auth)])
async def products_post(product: Product):
    try:
        product = await create_product(
            product.name,
            product.description,
            product.price,
            product.productId,
            product.attachments,
            product.tags,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return product.to_dict()


@app.delete("/v1/products/{product_id}", dependencies=[Depends(api_auth)])
async def products_delete(product_id: Union[int, str]):
    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    try:
        await delete_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Product Deleted"}


## Tags
@app.get("/v1/tags", dependencies=[Depends(api_auth)])
async def tags_get():
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
                user = await get_user(verificationKeys[key])
            except Exception as e:
                user = None

            if user:
                user.discordId = interaction.user.id
                await user.push()
                await interaction.followup.send("User verified!", ephemeral=True)
            else:
                user = await create_user(verificationKeys[key])
                user.discordId = interaction.user.id
                await user.push()
                await interaction.followup.send("User verified!", ephemeral=True)
        else:
            await interaction.followup.send("Invalid key.", ephemeral=True)

    @verifyGroup.command(name="unlink")
    async def verify_unlink(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            user = await get_user_by_discord_id(interaction.user.id)
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
