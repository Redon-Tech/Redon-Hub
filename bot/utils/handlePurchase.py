"""
    File: /bot/utils/handlePurchase.py
    Usage: A util to send products to a user, log the purchase, and give the user roles
"""

from discord import Embed, utils, TextChannel
from bot.models import CustomCog
from bot.data import User, Product
from bot import config


async def handlePurchase(cog: CustomCog, user: User, product: Product):
    try:
        if user.discordId != 0:
            discordUser = await cog.bot.fetch_user(user.discordId)
            dm_channel = discordUser.dm_channel
            if dm_channel is None:
                dm_channel = await discordUser.create_dm()

            await dm_channel.send(
                embed=Embed(
                    title="Product Retrieved",
                    description=f"Thanks for purchasing from us! You can find the information link below.",
                    colour=discordUser.accent_color or discordUser.color,
                    timestamp=utils.utcnow(),
                )
                .set_footer(text=f"Redon Hub • Version {cog.bot.version}")
                .add_field(name="Product", value=product.name, inline=True)
                .add_field(
                    name="Attachments",
                    value="\n".join(product.attachments) or "None",
                    inline=False,
                )
            )
    except Exception as e:
        pass

    try:
        if user.discordId != 0:
            guild = cog.bot.get_guild(config.Bot.Guilds[0])
            assert guild is not None
            member = await guild.fetch_member(user.discordId)

            if product.role != None:
                role = guild.get_role(product.role)
                if role is not None:
                    await member.add_roles(role, reason="User purchased a product")

            if config.Logging.GlobalCustomerRole != 1234567890:
                role = guild.get_role(config.Logging.GlobalCustomerRole)
                if role is not None:
                    await member.add_roles(role, reason="User purchased a product")

            if config.Logging.PurchasesChannel != 1234567890:
                channel = guild.get_channel(config.Logging.PurchasesChannel)
                if channel is not None and isinstance(channel, TextChannel):
                    await channel.send(
                        embed=Embed(
                            title="Product Purchased",
                            description=f"{member.mention} purchased a product!",
                            colour=member.accent_color or member.color,
                            timestamp=utils.utcnow(),
                        )
                        .set_footer(text=f"Redon Hub • Version {cog.bot.version}")
                        .add_field(name="Product", value=product.name, inline=True)
                    )
    except Exception as e:
        pass


async def handleRevoke(cog: CustomCog, user: User, product: Product):
    try:
        if user.discordId != 0:
            guild = cog.bot.get_guild(config.Bot.Guilds[0])
            assert guild is not None
            member = await guild.fetch_member(user.discordId)

            if product.role != None:
                role = guild.get_role(product.role)
                if role in member.roles:
                    await member.remove_roles(role, reason="User product revoked")

            if config.Logging.GlobalCustomerRole != 1234567890 and user.purchases == []:
                role = guild.get_role(config.Logging.GlobalCustomerRole)
                if role in member.roles:
                    await member.remove_roles(role, reason="User product revoked")
    except Exception as e:
        pass
