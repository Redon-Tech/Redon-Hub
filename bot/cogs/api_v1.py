"""
    File: /bot/cogs/api.py
    Usage: Responsible for the creation of the API
"""

from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord import app_commands, Interaction
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security.api_key import APIKeyHeader
from starlette.responses import RedirectResponse
from bot import config, Bot
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
    Product as ProductModel,
    User as UserModel,
    Tag as TagModel,
)
from bot.utils import handlePurchase, handleRevoke
from pydantic import BaseModel
from typing import Union, Optional
from datetime import datetime
from .. import __version__ as version
from dotenv import load_dotenv
import uvicorn
import logging
import random
import string

load_dotenv()

_log = logging.getLogger(__name__)
description = """
Redon Hub is a product delivery system (A.K.A. hub) for Roblox. This bot is [open source](https://github.com/Redon-Tech/Redon-Hub)!

* Users (Fully Implemented)
* Products (Fully Implemented)
* Tags (Fully Implemented)

[Official Documentation](https://hub.redon.tech/)
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
app.logger = _log  # type: ignore
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
    name: str
    color: list[int]
    textColor: list[int]


class TagOptional(BaseModel):
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
    price: Union[int, None] = None
    productId: Union[int, None] = None
    stock: Union[int, None] = None
    attachments: Union[list[str], None] = None
    tags: Union[list[int], None] = None


class Verification(BaseModel):
    message: str
    data: Optional[str] = "key123"


class APIStatus(BaseModel):
    message: str
    databaseConnected: bool
    version: str


## Basic Functions
async def getUserOrRaise(user_id: int, discordId: bool = False) -> UserModel:
    try:
        if discordId:
            return await get_user_by_discord_id(user_id)
        else:
            return await get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User Not Found")


async def getProductByIntOrStringOrRaise(product_id: Union[int, str]) -> ProductModel:
    if isinstance(product_id, str):
        if product_id.isdigit():
            product_id = int(product_id)
        else:
            try:
                return await get_product_by_name(product_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail="Product Not Found")

    if isinstance(product_id, int):
        try:
            return await get_product(product_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Product Not Found")

    raise HTTPException(status_code=404, detail="Product Not Found")


## Routes


@app.get("/")
async def root() -> RedirectResponse:
    """
    Redirections to /v1
    """
    return RedirectResponse(url="/v1")


@app.get("/v1")
async def v1() -> APIStatus:
    """
    Returns the status of the API and database as well as the version the bot is running.
    """
    return APIStatus(
        message="Online", databaseConnected=is_connected(), version=version
    )


## Users


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
        results[user.id] = UserDisplay(**user.model_dump())

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
        if product_id.isdigit():
            product_id = int(product_id)
        else:
            try:
                product_info = await get_product_by_name(product_id)
                product_id = product_info.id
            except Exception as e:
                raise HTTPException(status_code=404, detail="Product Not Found")

    if product_id in user.purchases:
        return True

    return False


@app.post(
    "/v1/users/{user_id}/{product_id}",
    dependencies=[Depends(api_auth)],
    tags=["Users"],
    status_code=status.HTTP_202_ACCEPTED,
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
    user = await getUserOrRaise(user_id, discordId)
    product = await getProductByIntOrStringOrRaise(product_id)

    try:
        if product.id not in user.purchases:
            user.purchases.append(product.id)
            await user.push()
            product.owners += 1
            if isPurchase == True:
                product.purchases += 1
            await product.push()

            try:
                await handlePurchase(cog, user, product)  # type: ignore
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
    user = await getUserOrRaise(user_id, discordId)
    product = await getProductByIntOrStringOrRaise(product_id)

    try:
        if product.id in user.purchases:
            user.purchases.remove(product.id)
            await user.push()
            product.owners -= 1
            await product.push()

        try:
            await handleRevoke(cog, user, product)  # type: ignore
        except Exception as e:
            pass

        return UserDisplay(**user.dict())
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post(
    "/v1/users/{user_id}/verify/key",
    dependencies=[Depends(api_auth)],
    tags=["Users"],
    status_code=status.HTTP_201_CREATED,
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
        for key, value in verificationKeys.items():
            if value == user_id:
                return Verification(message="Verification Key Created", data=key)

        key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        verificationKeys[key] = user_id
        return Verification(message="Verification Key Created", data=key)
    else:
        return Verification(message="User Already Verified", data=None)


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
        results[product.id] = ProductDisplay(**product.model_dump())

    return results


@app.get(
    "/v1/products/{product_id}", dependencies=[Depends(api_auth)], tags=["Products"]
)
async def products_get_product(product_id: Union[int, str]) -> ProductDisplay:
    """
    Gets a specific product from the database.
    """
    product = await getProductByIntOrStringOrRaise(product_id)

    return ProductDisplay(**product.dict())


@app.post(
    "/v1/products",
    dependencies=[Depends(api_auth)],
    tags=["Products"],
    status_code=status.HTTP_201_CREATED,
)
async def products_post(product: Product) -> ProductDisplay:
    """
    Creates a new product.
    """
    if product.name is None:
        raise HTTPException(status_code=400, detail="Name is required.")
    if product.price is None:
        raise HTTPException(status_code=400, detail="Price is required.")
    if product.productId is None:
        raise HTTPException(status_code=400, detail="Product ID is required.")

    try:
        createdProduct = await create_product(
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

    return ProductDisplay(**createdProduct.dict())


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

    try:
        updated_product = product.model_dump(exclude_unset=True)
        newProduct = await getProductByIntOrStringOrRaise(product_id)

        print(updated_product)
        for key, value in updated_product.items():
            setattr(product, key, value)

        await newProduct.push()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return ProductDisplay(**newProduct.dict())


@app.delete(
    "/v1/products/{product_id}", dependencies=[Depends(api_auth)], tags=["Products"]
)
async def products_delete(product_id: Union[int, str]) -> bool:
    """
    Deletes a product.

    **CAN NOT BE UNDONE!**
    """

    try:
        if type(product_id) == str:
            if product_id.isdigit():
                await delete_product(int(product_id))
            else:
                try:
                    product_info = await get_product_by_name(product_id)
                    product_id = product_info.id
                except Exception as e:
                    raise HTTPException(status_code=404, detail="Product Not Found")
        elif type(product_id) == int:
            await delete_product(product_id)
    except Exception as e:
        _log.error(e)
        if isinstance(e, HTTPException):
            raise e
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


@app.post(
    "/v1/tags",
    dependencies=[Depends(api_auth)],
    tags=["Tags"],
    status_code=status.HTTP_201_CREATED,
)
async def tags_post(tag: Tag) -> TagDisplay:
    """
    Creates a new tag.
    """
    try:
        newTag = await create_tag(tag.name, tag.color, tag.textColor)
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return TagDisplay(**newTag.dict())


@app.patch("/v1/tags/{tag_id}", dependencies=[Depends(api_auth)], tags=["Tags"])
async def tags_patch(tag_id: int, tag: TagOptional) -> TagDisplay:
    """
    Updates a tag.

    This is a patch meaning you don't have to pass all the data in the tag object.
    """
    try:
        updated_tag = tag.model_dump(exclude_unset=True)
        newTag = await get_tag(tag_id)

        for key, value in updated_tag.items():
            setattr(tag, key, value)

        await newTag.push()
    except Exception as e:
        _log.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return TagDisplay(**newTag.dict())


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
    def __init__(self, bot: Bot):
        self.bot = bot
        self.isRunning.start()

    async def cog_unload(self):
        self.isRunning.cancel()

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

    @loop(seconds=10.0)
    async def isRunning(self):
        if server.should_exit:
            _log.info("Uvicorn server has stopped running, shutting down bot.")
            await self.bot.close()

    @Cog.listener()
    async def on_ready(self):
        global cog
        cog = self
        self.bot.loop.create_task(server.serve())
        self.overwrite_uvicorn_logger()
        _log.info(f"Cog {__name__} ready")


async def setup(bot: Bot):
    await bot.add_cog(API(bot))
