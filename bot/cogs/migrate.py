"""
    File: /bot/cogs/migrate.py
    Usage: Migrate data from other providers.
"""

from discord import (
    app_commands,
    Interaction,
    ui,
    SelectOption,
    Embed,
    utils,
    TextChannel,
)
from discord.ext.commands import Cog
from bot import config, __version__ as version, Bot
from bot.data import (
    get_user_by_discord_id,
    create_product,
    create_tag,
    create_user,
    get_user,
)
import json
import logging
import requests

_log = logging.getLogger(__name__)
tagColors = {
    "Red": {"color": [184, 71, 67], "textColor": [255, 255, 255]},
    "Yellow": {"color": [217, 164, 6], "textColor": [255, 255, 255]},
    "Orange": {"color": [217, 164, 6], "textColor": [255, 255, 255]},
    "Green": {"color": [78, 156, 78], "textColor": [255, 255, 255]},
    "Blue": {"color": [65, 132, 197], "textColor": [255, 255, 255]},
    "Purple": {"color": [66, 79, 92], "textColor": [255, 255, 255]},
}


async def getUserInput(self, interaction: Interaction, title: str):
    try:
        response = await self.bot.wait_for(
            "message", check=lambda m: m.author == interaction.user, timeout=200
        )
    except TimeoutError:
        await interaction.edit_original_response(
            embed=Embed(
                title=title,
                description="You took too long to respond.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return
    except Exception as e:
        _log.error(e)
        await interaction.edit_original_response(
            embed=Embed(
                title=title,
                description="An unknown error occurred.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    return response


async def myPodMigrate(self, interaction: Interaction):
    user = await get_user_by_discord_id(interaction.user.id)

    if user is None:
        return await interaction.response.edit_message(
            content="You must be verified to use this migration.", view=None
        )

    await interaction.response.edit_message(
        embed=Embed(
            title="myPod Migrate",
            description="Please enter the place ID of your myPod place.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}"),
        view=None,
    )
    placeIdMessage = await getUserInput(self, interaction, "myPod Migrate")
    if placeIdMessage is None:
        return
    placeId = placeIdMessage.content

    await interaction.user.send(
        embed=Embed(
            title="myPod Migrate",
            description="Please enter the secret key of your myPod place.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}")
    )
    secretKeyMessage = await getUserInput(self, interaction, "myPod Migrate")
    if secretKeyMessage is None:
        return
    secretKey = secretKeyMessage.content

    await interaction.user.send(
        embed=Embed(
            title="myPod Migrate",
            description="Migration started.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}")
    )

    try:
        r = requests.get(
            url=f"https://api.mypodhub.com/v2/hub/hubload?placeid={placeId}&userid={user.id}",
            headers={"secretkey": secretKey},
        )
    except Exception as e:
        _log.error(e)
        await interaction.user.send(
            embed=Embed(
                title="myPod Migrate",
                description="An unknown error occurred.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    if r.status_code != 200:
        _log.error(r)
        await interaction.edit_original_response(
            embed=Embed(
                title="myPod Migrate",
                description="An unknown error occurred.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    data = r.json()

    if data["products"] is None:
        await interaction.user.send(
            embed=Embed(
                title="myPod Migrate",
                description="No products found.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    for product in data["products"]:
        try:
            await create_product(
                product["name"],
                product["description"],
                product["image"],
                0,
                int(product["productid"]),
                None,
                [product["file"]],
                None,
            )
        except Exception as e:
            _log.error(e)
            productname = product["name"]
            if interaction.channel is not None and isinstance(
                interaction.channel, TextChannel
            ):
                await interaction.channel.send(
                    f"Unable to create product {productname}."
                )

    await interaction.user.send(
        embed=Embed(
            title="myPod Migrate",
            description="Migration complete.\n**Note:** You will need to reupload your product files.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}")
    )


async def vendrMigrate(self, interaction: Interaction):
    await interaction.response.edit_message(
        embed=Embed(
            title="Vendr Migrate",
            description="Please enter the API token of your Vendr hub.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}"),
        view=None,
    )
    apiTokenMessage = await getUserInput(self, interaction, "Vendr Migrate")
    if apiTokenMessage is None:
        return
    apiToken = apiTokenMessage.content

    await interaction.user.send(
        embed=Embed(
            title="Vendr Migrate",
            description="Migration started.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}")
    )

    try:
        r = requests.get(
            url=f"https://api.onpointrblx.com/vendr/v2/hubs/getinfo?apitoken={apiToken}",
        )
    except Exception as e:
        _log.error(e)
        await interaction.user.send(
            embed=Embed(
                title="Vendr Migrate",
                description="An unknown error occurred.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    if r.status_code != 200:
        _log.error(r)
        await interaction.edit_original_response(
            embed=Embed(
                title="Vendr Migrate",
                description="An unknown error occurred.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    data = r.json()

    if data.get("Products") is None:
        await interaction.user.send(
            embed=Embed(
                title="Vendr Migrate",
                description="No products found.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    linkedTags = {}
    if data.get("Tags") is not None:
        for tag in data["Tags"]:
            try:
                color = tagColors[tag["Color"]]
                newTag = await create_tag(
                    tag["Name"], color["color"], color["textColor"]
                )
                linkedTags[tag["_id"]] = newTag
            except Exception as e:
                _log.error(e)
                if interaction.channel is not None and isinstance(
                    interaction.channel, TextChannel
                ):
                    await interaction.channel.send(
                        f"Unable to create tag {tag['Name']}."
                    )

    for product in data["Products"]:
        try:
            tags = []
            for tag in product["Tags"]:
                if linkedTags[tag] is not None:
                    tags.append(linkedTags[tag].id)

            await create_product(
                product["Name"],
                product["Description"],
                product["Image"],
                0,
                int(product["DevProduct"]),
                None,
                product["File"],
                tags,
            )
        except Exception as e:
            _log.error(e)
            productname = product["Name"]
            if interaction.channel is not None and isinstance(
                interaction.channel, TextChannel
            ):
                await interaction.channel.send(
                    f"Unable to create product {productname}."
                )

    await interaction.user.send(
        embed=Embed(
            title="Vendr Migrate",
            description="Migration complete.\n**Note:** You will need to reupload your product files.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}")
    )


async def parcelMigrate(self, interaction: Interaction):
    await interaction.response.edit_message(
        embed=Embed(
            title="Parcel Migrate",
            description="Please send the exported database json file.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}"),
        view=None,
    )
    databaseMessage = await getUserInput(self, interaction, "Parcel Migrate")
    if databaseMessage is None:
        return
    database = databaseMessage.attachments[0]

    await interaction.user.send(
        embed=Embed(
            title="Parcel Migrate",
            description="Migration started.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}")
    )

    try:
        data = json.loads(await database.read())
    except Exception as e:
        _log.error(e)
        await interaction.user.send(
            embed=Embed(
                title="Parcel Migrate",
                description="An unknown error occurred.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    if data.get("products") is None:
        await interaction.user.send(
            embed=Embed(
                title="Parcel Migrate",
                description="No products found.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {version}")
        )
        return

    cachedUsers = {}
    for product in data["products"]:
        try:
            newProduct = await create_product(
                product["name"],
                product["description"],
                product["decalID"],
                0,
                int(product["devproduct_id"]),
                None,
                [product["filepath"]],
                None,
            )

            if product.get("owners") != []:
                for owner in product["owners"]:
                    try:
                        if cachedUsers.get(owner) is None:
                            try:
                                cachedUsers[owner] = await get_user(int(owner))
                            except Exception as e:
                                cachedUsers[owner] = await create_user(int(owner))

                        cachedUsers[owner].purchases.append(newProduct.id)
                    except Exception as e:
                        _log.error(e)
                        if interaction.channel is not None and isinstance(
                            interaction.channel, TextChannel
                        ):
                            await interaction.channel.send(
                                f"Unable to add product {product['name']} to user {owner}."
                            )
        except Exception as e:
            _log.error(e)
            productname = product["name"]
            if interaction.channel is not None and isinstance(
                interaction.channel, TextChannel
            ):
                await interaction.channel.send(
                    f"Unable to create product {productname}."
                )

    for user in cachedUsers:
        try:
            await cachedUsers[user].push()
        except Exception as e:
            _log.error(e)
            if interaction.channel is not None and isinstance(
                interaction.channel, TextChannel
            ):
                await interaction.channel.send(f"Unable to save user {user}.")

    await interaction.user.send(
        embed=Embed(
            title="Parcel Migrate",
            description="Migration complete.\n**Note:** You will need to reupload your product files.",
            color=interaction.user.color,
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Redon Hub • Version {version}")
    )


class MigrateView(ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @ui.select(
        placeholder="Select a provider",
        options=[
            SelectOption(
                label="myPod",
                description="Migrate from myPod, can't migrate user data.",
                value="myPod",
            ),
            SelectOption(
                label="Vendr",
                description="Migrate from Vendr, can't migrate user data.",
                value="Vendr",
            ),
            SelectOption(
                label="Parcel",
                description="Migrate from Parcel, **can** migrate user data.",
                value="Parcel",
            ),
        ],
    )
    async def provider(self, interaction: Interaction, select: ui.Select):
        if select.values[0] == "myPod":
            await myPodMigrate(self, interaction)
        elif select.values[0] == "Vendr":
            await vendrMigrate(self, interaction)
        elif select.values[0] == "Parcel":
            await parcelMigrate(self, interaction)


class Migrate(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="migrate",
        description="Migrate data from other providers.",
    )
    async def migrate(self, interaction: Interaction):
        if interaction.user.id not in config.Bot.Owners:
            return await interaction.response.send_message(
                "You are not authorized to use this command.", ephemeral=True
            )

        await interaction.response.send_message("Continue in DMs.", ephemeral=True)
        await interaction.user.send(
            embed=Embed(
                title="Migrate",
                description="Select a provider to migrate from.",
                color=interaction.user.color,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=MigrateView(bot=self.bot),
        )

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


async def setup(bot: Bot):
    await bot.add_cog(Migrate(bot))
