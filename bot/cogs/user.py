"""
    File: /bot/cogs/user.py
    Usage: User related commands
"""
from discord import app_commands, Interaction, Member, Embed, utils
from discord.ext.commands import Cog
from bot.data import get_user_by_discord_id, get_product
from typing import Optional
import logging

_log = logging.getLogger(__name__)


class User(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile")
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
                    products.append(get_product(product).name)
                except Exception:
                    pass

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

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(User(bot))
