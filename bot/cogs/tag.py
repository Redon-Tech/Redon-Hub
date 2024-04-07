"""
    File: /bot/cogs/tags.py
    Usage: Tag related commands
"""

from discord import (
    app_commands,
    Interaction,
    Embed,
    utils,
    ui,
    SelectOption,
)
from discord.ext.commands import Cog
from bot.data import get_tag, get_tag_by_name, get_tags, create_tag, delete_tag, Tag
from PIL import ImageColor
import logging

_log = logging.getLogger(__name__)


class createTag(ui.Modal, title="Create Tag"):
    name = ui.TextInput(label="Tag Name")
    color = ui.TextInput(
        label="Color", placeholder="In RGB. For example: rgb(255,255,255)"
    )
    textColor = ui.TextInput(
        label="Text Color", placeholder="In RGB. For example: rgb(255,255,255)"
    )

    def __init__(self, bot, **kwargs):
        self.bot = bot
        super().__init__(**kwargs)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        try:
            color = ImageColor.getrgb(self.color.value)
            textColor = ImageColor.getrgb(self.textColor.value)
            tag = await create_tag(
                name=self.name.value,
                color=color,
                textColor=textColor,
            )

            await interaction.followup.send(
                embed=Embed(
                    title="Tag Created",
                    description=f"Your tag has been created!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )
        except Exception as e:
            _log.error(e)
            await interaction.followup.send(
                embed=Embed(
                    title="Error",
                    description="An unknown error has occured during creation.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )


class deleteTagSelect(ui.Select):
    def __init__(self, tags, **kwargs):
        options = []
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        for tag in tags:
            options.append(SelectOption(label=tag.name, value=tag.id))

        super().__init__(
            placeholder="Select tag",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        deletedTags = []
        failedTags = []
        for tag in self.values:
            tag_name = tag
            try:
                tag_data = await get_tag(int(tag))
                tag_name = tag_data.name
            except Exception as e:
                _log.error(e)

            try:
                await delete_tag(int(tag))
                deletedTags.append(tag_name)
            except Exception as e:
                _log.error(e)
                failedTags.append(tag_name)

        if len(deletedTags) > 0:
            await interaction.edit_original_response(
                embed=Embed(
                    title="Tag Deleted",
                    description=f"Succesfully deleted:\n{', '.join(deletedTags)}",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=None,
            )

        if len(failedTags) > 0:
            await interaction.followup.send(
                embed=Embed(
                    title="Error",
                    description=f"Failed to delete:\n{', '.join(failedTags)}",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )


class deleteTagView(ui.View):
    def __init__(self, tags, **kwargs):
        super().__init__()
        self.add_item(deleteTagSelect(tags, **kwargs))


class updateTag(ui.Modal, title="Update Tag"):
    def __init__(self, bot, tag: Tag):
        self.bot = bot
        self.tag = tag
        super().__init__()

        self.add_item(ui.TextInput(label="Tag Name", default=tag.name))
        self.add_item(
            ui.TextInput(
                label="Color",
                placeholder="In RGB. For example: rgb(255,255,255)",
                default=f"rgb({tag.color[0]},{tag.color[1]},{tag.color[2]})",
            )
        )
        self.add_item(
            ui.TextInput(
                label="Text Color",
                placeholder="In RGB. For example: rgb(255,255,255)",
                default=f"rgb({tag.textColor[0]},{tag.textColor[1]},{tag.textColor[2]})",
            )
        )

    async def on_submit(self, interaction: Interaction) -> None:
        try:
            for item in self.children:
                if item.label == "Tag Name":
                    self.tag.name = item.value
                elif item.label == "Color":
                    self.tag.color = ImageColor.getrgb(item.value)
                elif item.label == "Text Color":
                    self.tag.textColor = ImageColor.getrgb(item.value)

            await self.tag.push()

            await interaction.response.send_message(
                embed=Embed(
                    title="Tag Updated",
                    description=f"Your tag has been updated!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )
        except Exception as e:
            _log.error(e)
            # await interaction.followup.send(
            await interaction.response.send_message(
                embed=Embed(
                    title="Error",
                    description="An unknown error has occured while updating.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            )


class TagCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    tag_commands = app_commands.Group(name="tag", description="Tag Commands")
    tag_admin = app_commands.Group(
        name="admin",
        description="Tag Admin Commands",
        parent=tag_commands,
    )

    @app_commands.command(name="tags", description="View all the tags this server has")
    async def get_tags_command(self, interaction: Interaction):
        await interaction.response.defer()

        tags = await get_tags()

        await interaction.followup.send(
            embed=Embed(
                title="Tags",
                description=f"Here is all the tags I was able to find! To get more information on a individual tag run `/tag (tag)`",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            )
            .set_footer(text=f"Redon Hub • Version {self.bot.version}")
            .add_field(
                name="Tags",
                value="\n".join([tag.name for tag in tags]) or "None",
            )
        )

    @tag_commands.command(name="info", description="Get information on a specific tag")
    async def get_tag_info_command(self, interaction: Interaction, tag_name: str):
        try:
            tag = await get_tag_by_name(tag_name)
        except Exception:
            tag = None

        if tag:
            await interaction.response.send_message(
                embed=Embed(
                    title=tag.name,
                    description=f"Here is all the info I was able to get on `{tag.name}`!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                )
                .set_footer(text=f"Redon Hub • Version {self.bot.version}")
                .add_field(name="Color", value=tag.color, inline=True)
                .add_field(name="Text Color", value=tag.textColor, inline=False)
            )
        else:
            await interaction.response.send_message(
                embed=Embed(
                    title="Not Found",
                    description=f"I was unable to find any information on `{tag_name}`.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @get_tag_info_command.autocomplete("tag_name")
    async def get_tag_info_command_autocomplete(
        self, interaction: Interaction, current_tag_name: str
    ):
        try:
            tags = await get_tags()
        except Exception:
            tags = []

        return [
            app_commands.Choice(name=tag.name, value=tag.name)
            for tag in tags
            if current_tag_name.lower() in tag.name.lower()
        ]

    @tag_admin.command(name="create", description="Create a new tag")
    @app_commands.checks.has_permissions(administrator=True)
    async def create_tag_command(self, interaction: Interaction):
        await interaction.response.send_modal(createTag(bot=self.bot))

    @tag_admin.command(name="delete", description="Delete a tag")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete_tag_command(self, interaction: Interaction):
        await interaction.response.defer()

        tags = await get_tags()

        await interaction.followup.send(
            embed=Embed(
                title="Delete tag",
                description="Select the tag you want to delete",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
            ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
            view=deleteTagView(tags, bot=self.bot),
        )

    @tag_admin.command(name="update", description="Update a tag")
    @app_commands.checks.has_permissions(administrator=True)
    async def update_tag_command(self, interaction: Interaction, tag_name: str):
        try:
            tag = await get_tag_by_name(tag_name)
        except Exception:
            tag = None

        if tag:
            await interaction.response.send_modal(updateTag(bot=self.bot, tag=tag))
        else:
            await interaction.response.send_message(
                embed=Embed(
                    title="Not Found",
                    description=f"I was unable to find any tag to update with the name `{tag_name}`.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @update_tag_command.autocomplete("tag_name")
    async def update_tag_command_autocomplete(
        self, interaction: Interaction, current_tag_name: str
    ):
        try:
            tags = await get_tags()
        except Exception:
            tags = []

        return [
            app_commands.Choice(name=tag.name, value=tag.name)
            for tag in tags
            if current_tag_name.lower() in tag.name.lower()
        ]

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(TagCog(bot))
