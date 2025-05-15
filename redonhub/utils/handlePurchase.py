"""
    File: /bot/utils/handlePurchase.py
    Usage: A util to send products to a user, log the purchase, and give the user roles
"""

from discord import Embed, utils, TextChannel, File
from redonhub.models import CustomCog
from redonhub.data import User, Product
from redonhub import config
from typing import TypedDict, Optional
from logging import getLogger
from urllib.parse import urlparse
import aiohttp
import aiofiles
import os

_log = getLogger(__name__)


class AttachmentData(TypedDict):
    files: list[str]
    nonDownloadable: list[str]


async def shouldDownload(url) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            headers = response.headers
            content_length = headers.get("Content-Length", None)
        
            if "Content-Disposition" in headers and headers["Content-Disposition"].startswith(
                "attachment"
            ):
                if content_length and int(content_length) < 10**7:
                    return True
            else:
                accepted_formats = [
                    "application/gzip",
                    "application/vnd.rar",
                    "application/x-7z-compressed",
                    "application/zip",
                    "application/x-tar",
                    "image/bmp",
                    "image/gif",
                    "image/jpeg",
                    "image/png",
                    "image/svg+xml",
                    "image/tiff",
                    "image/webp",
                    "application/rtf",
                    "text/plain",
                ]
        
                if headers["Content-Type"] in accepted_formats or (
                    content_length and int(content_length) > 0
                ):
                    if content_length and int(content_length) < 10**7:
                        return True
        
            return False


async def getAttachments(product: Product) -> AttachmentData:
    files: list[str] = []
    nonDownloadable: list[str] = []

    async with aiohttp.ClientSession() as session:
        for attachment in product.attachments:
            if await shouldDownload(session, attachment):
                try:
                    fileName = urlparse(attachment).path.split("/")[-1]
                    async with session.get(attachment) as resp:
                        resp.raise_for_status()
                        async with aiofiles.open(fileName, "wb") as f:
                            async for chunk in resp.content.iter_chunked(8192):
                                await f.write(chunk)

                    files.append(fileName)
                except Exception as e:
                    _log.error(f"Error downloading {attachment}: {e}")
            else:
                nonDownloadable.append(attachment)

    return {
        "files": files,
        "nonDownloadable": nonDownloadable,
    }


async def handlePurchase(cog: CustomCog, user: User, product: Product):
    try:
        if user.discordId != 0:
            discordUser = await cog.bot.fetch_user(user.discordId)
            dm_channel = discordUser.dm_channel
            if dm_channel is None:
                dm_channel = await discordUser.create_dm()

            attachments = await getAttachments(product)

            embed = Embed(
                title="Product Retrieved",
                description=f"Thanks for purchasing from us! You can find the information link below.",
                colour=discordUser.accent_color or discordUser.color,
                timestamp=utils.utcnow(),
            )
            embed.set_footer(text=f"Redon Hub • Version {cog.bot.version}")
            embed.add_field(name="Product", value=product.name, inline=True)
            if len(attachments["nonDownloadable"]) > 0:
                embed.add_field(
                    name="Other Links",
                    value="\n".join(attachments["nonDownloadable"]),
                    inline=False,
                )

            files = []
            for file in attachments["files"]:
                files.append(File(file))

            await dm_channel.send(embed=embed, files=files)

            for file in attachments["files"]:
                if os.path.exists(file):
                    os.remove(file)
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
