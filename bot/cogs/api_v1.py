"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""
from discord.ext.commands import Cog
from discord import app_commands, Interaction, Embed, utils
from fastapi import FastAPI, HTTPException, Depends, WebSocket, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
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
    get_tags,
    get_tag,
    create_tag,
    delete_tag,
    is_connected,
)
from pydantic import BaseModel
from typing import Union, Optional
from datetime import datetime
from .. import __version__ as version
from dotenv import load_dotenv
import uvicorn
import logging
import random
import string
import os

load_dotenv()

_log = logging.getLogger(__name__)
description = """
Redon Hub is a product delivery system (A.K.A. hub) for Roblox. This bot is [open source](https://github.com/Redon-Tech/Redon-Hub)!

* Users (Fully Implemented)
* Products (Fully Implemented)
* Tags (Fully Implemented)

[Official Documentation](https://hub.redon.tech/docs)
"""
app = FastAPI(
    title="Redon Hub",
    description=description,
    version=version,
    contact={
        "name": "Parker",
        "url": "https://parker02311.redon.tech/contact-me.html",
        "email": "parker02311@redon.tech",
    },
    license_info={"name": "MIT", "url": "https://mit-license.org/"},
    openapi_tags=[
        {
            "name": "Users",
            "description": "Users are the people who use the hub. Users are based around Roblox id and have an optional link to a Discord id.",
        },
        {
            "name": "Products",
            "description": "Products are the items that are sold on the hub. Products are based around id's however most endpoints can retrieve them by name as names have to be unique.",
        },
        {
            "name": "Tags",
            "description": "Tags are used to categorize products. Tags are based around id's however most endpoints can retrieve them by name as names have to be unique.",
        },
    ],
)
app.logger = _log
cog = None
X_API_KEY = APIKeyHeader(name="Authorization", auto_error=False)
verificationKeys = {}


def api_auth(x_api_key: str = Security(X_API_KEY)):
    if x_api_key != f"Bearer {config.API.Key}":
        raise HTTPException(status_code=403, detail="Invalid API Key.")

    return x_api_key


# Schemas


class UserDisplay(BaseModel):
    id: int
    createdAt: datetime
    discordId: int
    verifiedAt: datetime
    purchases: list[int]


class TagDisplay(BaseModel):
    id: int
    name: str
    color: list[int]
    textColor: list[int]


class Tag(BaseModel):
    name: Union[str, None] = None
    color: Union[list[int], None] = None
    textColor: Union[list[int], None] = None


class ProductDisplay(BaseModel):
    id: int
    createdAt: datetime
    name: str
    description: str
    imageId: str
    price: int
    productId: int
    stock: Optional[int]
    attachments: list[str]
    tags: list[int]
    purchases: int
    owners: int


class Product(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    imageId: Union[str, None] = None
    price: Union[float, None] = None
    productId: Union[float, None] = None
    stock: Union[int, None] = None
    attachments: Union[list[str], None] = None
    tags: Union[int, None] = None


class Verification(BaseModel):
    message: str
    data: Optional[str] = "key123"


class APIStatus(BaseModel):
    message: str
    databaseConnected: bool
    version: str


@app.get("/")
async def root() -> APIStatus:
    """
    Returns the status of the API and database as well as the version the bot is running.
    """
    return APIStatus(
        message="Online", databaseConnected=is_connected(), version=version
    )


## Websocket
# @app.websocket("/v1/socket")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     if websocket.headers.get("Authorization") != f"Bearer {config.API.Key}":
#         await websocket.close(code=1008)
#         return
#     while True:
#         data = await websocket.receive_json()
#         if data.get("type") == "verify_user":
#             _log.info(f"Got Verification Request for {data.get('data')}")

#             try:
#                 user = await get_user(data.get("data"))
#             except Exception as e:
#                 user = None

#             if not user or user.discordId == 0:
#                 key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
#                 verificationKeys[key] = data.get("data")
#                 await websocket.send_json({"data": key})
#             else:
#                 await websocket.send_json({"data": "user_verified"})


## Users
@app.get("/v1")
async def v1root() -> APIStatus:
    """
    Redirections to /
    """
    return RedirectResponse(url="/")


@app.get("/v1/cart_enabled", dependencies=[Depends(api_auth)])
async def cart_enabled() -> bool:
    """
    Returns if the cart is enabled or not.

    The cart system has not been implemented yet, so this will always return false.
    """
    return False
    # return os.getenv("roblox_cookie", None) is not None


@app.get("/v1/users", dependencies=[Depends(api_auth)], tags=["Users"])
async def users_get() -> dict[int, UserDisplay]:
    """
    Gets all users in the database.

    If you have a specific user to get data on please use /v1/users/{user_id} it is much faster.
    """
    try:
        users = await get_users()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for user in users:
        results[user.id] = UserDisplay(**user.dict())

    return results


@app.get("/v1/users/{user_id}", dependencies=[Depends(api_auth)], tags=["Users"])
async def users_get_user(user_id: int, discordId: bool = False) -> UserDisplay:
    """
    Gets a specific user by their id or discordId.
    """
    try:
        if discordId:
            user = await get_user_by_discord_id(user_id)
        else:
            user = await get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User Not Found")

    return UserDisplay(**user.dict())


@app.get("/v1/users/{user_id}/owns/{product_id}", tags=["Users"])
async def users_get_user_owns(
    user_id: int, product_id: Union[int, str], discordId: bool = False
) -> bool:
    """
    Returns if a user owns a product, very useful for whitelist systems.

    **Does not require a API Key**
    """
    try:
        if discordId:
            user = await get_user_by_discord_id(user_id)
        else:
            user = await get_user(user_id)
    except Exception as e:
        return False

    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            return False

    if product_id in user.purchases:
        return True

    return False


@app.post(
    "/v1/users/{user_id}/{product_id}", dependencies=[Depends(api_auth)], tags=["Users"]
)
async def users_give_user_product(
    user_id: int,
    product_id: Union[int, str],
    discordId: bool = False,
    isPurchase: bool = False,
) -> UserDisplay:
    """
    Gives a user a specific product, please note this does not increment the purchases counter on the product by default you must enable it.
    """
    try:
        if discordId:
            user = await get_user_by_discord_id(user_id)
        else:
            user = await get_user(user_id)
    except Exception as e:
        return False

    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    try:
        product = await get_product(product_id)

        if product.id not in user.purchases:
            user.purchases.append(product.id)
            await user.push()
            product.owners += 1
            if isPurchase == True:
                product.purchases += 1
            await product.push()

            try:
                if user.discordId != 0:
                    discordUser = await cog.bot.fetch_user(user.discordId)
                    if discordUser.dm_channel is None:
                        await discordUser.create_dm()

                    await discordUser.dm_channel.send(
                        embed=Embed(
                            title="Product Retrieved",
                            description=f"Thanks for purchasing from us! You can find the information link below.",
                            colour=discordUser.accent_color or discordUser.color,
                            timestamp=utils.utcnow(),
                        )
                        .set_footer(text=f"Redon Hub • Version {version}")
                        .add_field(name="Product", value=product.name, inline=True)
                        .add_field(
                            name="Attachments",
                            value="\n".join(product.attachments) or "None",
                            inline=False,
                        )
                    )
            except Exception as e:
                pass

        return UserDisplay(**user.dict())
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete(
    "/v1/users/{user_id}/{product_id}", dependencies=[Depends(api_auth)], tags=["Users"]
)
async def users_revoke_user_product(
    user_id: int, product_id: Union[int, str], discordId: bool = False
) -> UserDisplay:
    """
    Revokes a users product.
    """
    try:
        if discordId:
            user = await get_user_by_discord_id(user_id)
        else:
            user = await get_user(user_id)
    except Exception as e:
        return False

    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    try:
        product = await get_product(product_id)

        if product.id in user.purchases:
            user.purchases.remove(product.id)
            await user.push()
            product.owners -= 1
            await product.push()

        return UserDisplay(**user.dict())
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post(
    "/v1/users/{user_id}/verify", dependencies=[Depends(api_auth)], tags=["Users"]
)
async def users_post_verify(user_id: int) -> Verification:
    """
    Get a verification key for a user.
    """
    try:
        user = await get_user(user_id)
    except Exception as e:
        user = None

    if not user or user.discordId == 0:
        key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        verificationKeys[key] = user_id
        # return {"message": "Verification Key Created", "data": key}
        return Verification(message="Verification Key Created", data=key)
    else:
        # return {"message": "User Already Verified"}
        return Verification(message="User Already Verified")


## Products
@app.get("/v1/products", dependencies=[Depends(api_auth)], tags=["Products"])
async def products_get() -> dict[int, ProductDisplay]:
    """
    Gets all products in the database.

    If you have a specific product to get data on please use /v1/products/{user_id} it is much faster.
    """
    try:
        products = await get_products()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for product in products:
        results[product.id] = ProductDisplay(**product.dict())

    return results


@app.get(
    "/v1/products/{product_id}", dependencies=[Depends(api_auth)], tags=["Products"]
)
async def products_get_product(product_id: Union[int, str]) -> ProductDisplay:
    """
    Gets a specific product from the database.
    """
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

    return ProductDisplay(**product.dict())


@app.post("/v1/products", dependencies=[Depends(api_auth)], tags=["Products"])
async def products_post(product: Product) -> ProductDisplay:
    """
    Creates a new product.
    """
    try:
        product = await create_product(
            product.name,
            product.description,
            product.imageId,
            product.price,
            product.productId,
            product.stock,
            product.attachments,
            product.tags,
        )
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return ProductDisplay(**product.dict())


@app.patch(
    "/v1/products/{product_id}", dependencies=[Depends(api_auth)], tags=["Products"]
)
async def products_patch(
    product_id: Union[int, str], product: Product
) -> ProductDisplay:
    """
    Updates a product.

    This is a patch meaning you don't have to pass all the data in the product object.
    """
    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    try:
        updated_product = product.dict(exclude_unset=True)
        product = await get_product(product_id)

        print(updated_product)
        for key, value in updated_product.items():
            setattr(product, key, value)

        await product.push()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return ProductDisplay(**product.dict())


@app.delete(
    "/v1/products/{product_id}", dependencies=[Depends(api_auth)], tags=["Products"]
)
async def products_delete(product_id: Union[int, str]) -> bool:
    """
    Deletes a product.

    **CAN NOT BE UNDONE!**
    """
    if type(product_id) == str:
        try:
            product_info = await get_product_by_name(product_id)
            product_id = product_info.id
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    try:
        await delete_product(product_id)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return True


## Tags
@app.get("/v1/tags", dependencies=[Depends(api_auth)], tags=["Tags"])
async def tags_get() -> dict[int, TagDisplay]:
    """
    Gets all tags in the database.

    If you have a specific tag to get data on please use /v1/tags/{tag_id} it is much faster.
    """
    try:
        tags = await get_tags()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    results = {}
    for tag in tags:
        results[tag.id] = TagDisplay(**tag.dict())

    return results


@app.get("/v1/tags/{tag_id}", dependencies=[Depends(api_auth)], tags=["Tags"])
async def tags_get_tag(tag_id: int) -> TagDisplay:
    """
    Gets a specific tag from the database.
    """
    try:
        tag = await get_tag(tag_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Tag Not Found")

    return TagDisplay(**tag.dict())


@app.post("/v1/tags", dependencies=[Depends(api_auth)], tags=["Tags"])
async def tags_post(tag: Tag) -> TagDisplay:
    """
    Creates a new tag.
    """
    try:
        tag = await create_tag(tag.name, tag.color, tag.textColor)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return TagDisplay(**tag.dict())


@app.patch("/v1/tags/{tag_id}", dependencies=[Depends(api_auth)], tags=["Tags"])
async def tags_patch(tag_id: int, tag: Tag) -> TagDisplay:
    """
    Updates a tag.

    This is a patch meaning you don't have to pass all the data in the tag object.
    """
    try:
        updated_tag = tag.dict(exclude_unset=True)
        tag = await get_tag(tag_id)

        for key, value in updated_tag.items():
            setattr(tag, key, value)

        await tag.push()

        tag = await get_tag(tag_id)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return TagDisplay(**tag.dict())


@app.delete("/v1/tags/{tag_id}", dependencies=[Depends(api_auth)], tags=["Tags"])
async def tags_delete(tag_id: int) -> bool:
    """
    Deletes a tag.

    **CAN NOT BE UNDONE!**
    """
    try:
        await delete_tag(tag_id)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return True


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

    @verifyGroup.command(
        name="link", description="Link your Discord account to your Roblox account"
    )
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

    @verifyGroup.command(
        name="unlink",
        description="Unlink your Discord account from your Roblox account",
    )
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
