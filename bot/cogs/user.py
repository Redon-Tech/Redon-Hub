"""
    File: /bot/cogs/user.py
    Usage: User related commands
"""
from discord import app_commands, Interaction, Member, Embed, utils, Forbidden
from discord.ext.commands import Cog
from bot.data import (
    get_user_by_discord_id,
    get_product,
    get_product_by_name,
    get_products,
)
from bot.utils import ConfirmView, JumpToMessageView, handlePurchase, handleRevoke
from typing import Optional
import logging

_log = logging.getLogger(__name__)


class User(Cog):
    def __init__(self, bot):
        self.bot = bot

    user_commands = app_commands.Group(name="user", description="User Commands")

    user_admin = app_commands.Group(
        name="admin",
        description="User Admin Commands",
        parent=user_commands,
        default_permissions=None,
    )

    @app_commands.command(name="profile", description="View a user's profile")
    async def user_profile(self, interaction: Interaction, member: Optional[Member]):
        member = member or interaction.user
        try:
            user = await get_user_by_discord_id(member.id)
        except Exception as e:
            _log.error(e)
            user = None

        if user:
            embed = (
                Embed(
                    title="User Profile",
                    # description=f"Here is the information I was able to find on {member.mention}",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                )
                .set_footer(text=f"Redon Hub • Version {self.bot.version}")
                .set_author(name=member.name, icon_url=member.avatar.url)
            )

            embed.add_field(
                name="Linked Account",
                value=f"[{user.id}](https://roblox.com/users/{user.id}/profile)",
                inline=True,
            )
            embed.add_field(name="Discord Account", value=member.mention, inline=True)
            products = []
            for product in user.purchases:
                try:
                    product_data = await get_product(product)
                    products.append(product_data.name)
                except Exception:
                    products.append(f"{product} (Unable To Get Name)")

            embed.add_field(
                name="Owned Products",
                value="\n".join(products) or "None",
                inline=False,
            )

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                embed=Embed(
                    title="Not Found",
                    description=f"I was unable to find any information on {member.mention}.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                )
                .set_footer(text=f"Redon Hub • Version {self.bot.version}")
                .set_author(name=member.name, icon_url=member.avatar.url)
            )

    @app_commands.command(name="retrieve", description="Retrieve your product")
    async def user_retrieve(self, interaction: Interaction, product_name: str):
        await interaction.response.defer()

        try:
            product = await get_product_by_name(product_name)
        except Exception:
            product = None

        try:
            user = await get_user_by_discord_id(interaction.user.id)
        except Exception as e:
            _log.error(e)
            user = None

        if product and user and product.id in user.purchases:
            try:
                if interaction.user.dm_channel is None:
                    await interaction.user.create_dm()

                message = await interaction.user.dm_channel.send(
                    embed=Embed(
                        title="Product Retrieved",
                        description=f"Thanks for purchasing from us! You can find the information link below.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    )
                    .set_footer(text=f"Redon Hub • Version {self.bot.version}")
                    .add_field(name="Product", value=product.name, inline=True)
                    .add_field(
                        name="Attachments",
                        value="\n".join(product.attachments) or "None",
                        inline=False,
                    )
                )

                await interaction.followup.send(
                    embed=Embed(
                        title="Product Retrieved",
                        description=f"Please check your DMs for the product!",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                    view=JumpToMessageView(message),
                )
            except Forbidden:
                await interaction.followup.send(
                    embed=Embed(
                        title="DMs Disabled",
                        description=f"I was unable to send you a DM. Please enable DMs from server members.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
                )
            except Exception as e:
                _log.error(e)
                await interaction.followup.send(
                    embed=Embed(
                        title="Unknown Error",
                        description=f"An unknown error has occured.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
                )
        elif product and user and product.id not in user.purchases:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Owned",
                    description=f"You do not own this product.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif not product:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Found",
                    description=f"I was unable to find any product to retrieve with the name `{product_name}`.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif not user:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Linked",
                    description=f"You are not linked with the bot.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        else:
            await interaction.followup.send(
                embed=Embed(
                    title="Unknown Error",
                    description=f"An unknown error has occured. (Debug: 1)",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @user_retrieve.autocomplete("product_name")
    async def user_retrieve_autocomplete(
        self, interaction: Interaction, current_product_name: str
    ):
        try:
            user = await get_user_by_discord_id(interaction.user.id)
        except Exception as e:
            _log.error(e)
            user = None

        if not user:
            return []

        products = []
        for purchase in user.purchases:
            try:
                products.append(await get_product(purchase))
            except Exception:
                pass

        return [
            app_commands.Choice(name=product.name, value=product.name)
            for product in products
            if current_product_name.lower() in product.name.lower()
        ]

    @app_commands.command(
        name="transfer", description="Transfer your product to another user"
    )
    async def user_transfer(
        self, interaction: Interaction, product_name: str, membertotransfer: Member
    ):
        await interaction.response.defer()

        if membertotransfer == interaction.user:
            await interaction.followup.send(
                embed=Embed(
                    title="Error",
                    description="You cannot transfer a product to yourself.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
            return

        try:
            product = await get_product_by_name(product_name)
        except Exception:
            product = None

        try:
            user = await get_user_by_discord_id(interaction.user.id)
        except Exception as e:
            _log.error(e)
            user = None

        try:
            userToTransfer = await get_user_by_discord_id(membertotransfer.id)
        except Exception as e:
            _log.error(e)
            userToTransfer = None

        if (
            product
            and user
            and userToTransfer
            and product.id in user.purchases
            and product.id not in userToTransfer.purchases
        ):
            view = ConfirmView(interaction.user)

            await interaction.followup.send(
                embed=Embed(
                    title="Confirm Transfer",
                    description=f"Are you sure you would like to transfer `{product.name}` to {membertotransfer.mention}!",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                view=view,
            )

            await view.wait()

            if view.value:
                try:
                    user.purchases.remove(product.id)
                    userToTransfer.purchases.append(product.id)
                    await user.push()
                    await userToTransfer.push()
                    await interaction.edit_original_response(
                        embed=Embed(
                            title="Product Transferred",
                            description="The product has transfered successfully.",
                            colour=interaction.user.colour,
                            timestamp=utils.utcnow(),
                        ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                        view=None,
                    )
                except Exception as e:
                    _log.error(e)
                    await interaction.edit_original_response(
                        embed=Embed(
                            title="Error",
                            description="An error occurred while updating the database.",
                            colour=interaction.user.colour,
                            timestamp=utils.utcnow(),
                        ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                        view=None,
                    )
            else:
                await interaction.edit_original_response(
                    embed=Embed(
                        title="Cancelled",
                        description="The transfer has been cancelled.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}"),
                    view=None,
                )
        elif product and user and userToTransfer and product.id not in user.purchases:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Owned",
                    description=f"You do not own this product.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif (
            product
            and user
            and userToTransfer
            and product.id in userToTransfer.purchases
        ):
            await interaction.followup.send(
                embed=Embed(
                    title="Already Owned",
                    description=f"The user you are trying to transfer to already owns this product.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif not userToTransfer:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Linked",
                    description=f"The user you are trying to transfer to is not linked with the bot.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif not user:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Linked",
                    description=f"You are not linked with the bot.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif not product:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Found",
                    description=f"I was unable to find any product to transfer with the name `{product_name}`.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        else:
            await interaction.followup.send(
                embed=Embed(
                    title="Unknown Error",
                    description=f"An unknown error has occured. (Debug: 1)",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @user_transfer.autocomplete("product_name")
    async def user_transfer_autocomplete(
        self, interaction: Interaction, current_product_name: str
    ):
        try:
            user = await get_user_by_discord_id(interaction.user.id)
        except Exception as e:
            _log.error(e)
            user = None

        if not user:
            return []

        products = []
        for purchase in user.purchases:
            try:
                products.append(await get_product(purchase))
            except Exception:
                pass

        return [
            app_commands.Choice(name=product.name, value=product.name)
            for product in products
            if current_product_name.lower() in product.name.lower()
        ]

    @user_admin.command(name="give", description="Give a user a product")
    async def user_admin_give(
        self, interaction: Interaction, product_name: str, member: Member
    ):
        await interaction.response.defer()

        try:
            product = await get_product_by_name(product_name)
        except Exception:
            product = None

        try:
            user = await get_user_by_discord_id(member.id)
        except Exception as e:
            _log.error(e)
            user = None

        if product and user and product.id not in user.purchases:
            try:
                user.purchases.append(product.id)
                await user.push()
                product.owners -= 1
                await product.push()
                await interaction.followup.send(
                    embed=Embed(
                        title="Product Given",
                        description="The product has been given successfully.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
                )

                try:
                    await handlePurchase(self, user, product)
                    # if interaction.user.dm_channel is None:
                    #     await interaction.user.create_dm()

                    # await interaction.user.dm_channel.send(
                    #     embed=Embed(
                    #         title="Product Retrieved",
                    #         description=f"Thanks for purchasing from us! You can find the information link below.",
                    #         colour=interaction.user.colour,
                    #         timestamp=utils.utcnow(),
                    #     )
                    #     .set_footer(text=f"Redon Hub • Version {self.bot.version}")
                    #     .add_field(name="Product", value=product.name, inline=True)
                    #     .add_field(
                    #         name="Attachments",
                    #         value="\n".join(product.attachments) or "None",
                    #         inline=False,
                    #     )
                    # )
                except Exception as e:
                    pass
            except Exception as e:
                _log.error(e)
                await interaction.followup.send(
                    embed=Embed(
                        title="Error",
                        description="An error occurred while updating the database.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
                )
        elif product and user and product.id in user.purchases:
            await interaction.followup.send(
                embed=Embed(
                    title="Already Owned",
                    description=f"The user you are trying to give to already owns this product.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif not user:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Linked",
                    description=f"The user you are trying to give to is not linked with the bot.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        else:
            await interaction.followup.send(
                embed=Embed(
                    title="Unknown Error",
                    description=f"An unknown error has occured. (Debug: 1)",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @user_admin_give.autocomplete("product_name")
    async def user_admin_give_autocomplete(
        self, interaction: Interaction, current_product_name: str
    ):
        try:
            products = await get_products()
        except Exception:
            products = []

        return [
            app_commands.Choice(name=product.name, value=product.name)
            for product in products
            if current_product_name.lower() in product.name.lower()
        ]

    @user_admin.command(name="revoke", description="Revoke a product from a user")
    async def user_admin_revoke(
        self, interaction: Interaction, product_name: str, member: Member
    ):
        await interaction.response.defer()

        try:
            product = await get_product_by_name(product_name)
        except Exception:
            product = None

        try:
            user = await get_user_by_discord_id(member.id)
        except Exception as e:
            _log.error(e)
            user = None

        if product and user and product.id in user.purchases:
            try:
                user.purchases.remove(product.id)
                await user.push()
                product.owners -= 1
                await product.push()
                await interaction.followup.send(
                    embed=Embed(
                        title="Product Revoked",
                        description="The product has been revoked successfully.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
                )

                try:
                    await handleRevoke(self, user, product)
                except Exception as e:
                    pass
            except Exception as e:
                _log.error(e)
                await interaction.followup.send(
                    embed=Embed(
                        title="Error",
                        description="An error occurred while updating the database.",
                        colour=interaction.user.colour,
                        timestamp=utils.utcnow(),
                    ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
                )
        elif product and user and product.id not in user.purchases:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Owned",
                    description=f"The user you are trying to revoke from does not own this product.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        elif not user:
            await interaction.followup.send(
                embed=Embed(
                    title="Not Linked",
                    description=f"The user you are trying to revoke from is not linked with the bot.",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )
        else:
            await interaction.followup.send(
                embed=Embed(
                    title="Unknown Error",
                    description=f"An unknown error has occured. (Debug: 1)",
                    colour=interaction.user.colour,
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"Redon Hub • Version {self.bot.version}")
            )

    @user_admin_revoke.autocomplete("product_name")
    async def user_admin_revoke_autocomplete(
        self, interaction: Interaction, current_product_name: str
    ):
        try:
            products = await get_products()
        except Exception:
            products = []

        return [
            app_commands.Choice(name=product.name, value=product.name)
            for product in products
            if current_product_name.lower() in product.name.lower()
        ]

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(User(bot))
