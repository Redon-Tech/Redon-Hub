"""
    File: /bot/cogs/product.py
    Usage: Product related commands
"""
from discord import app_commands, Interaction, Member, Embed, utils
from discord.ext.commands import Cog
from bot.data import get_products, product
import logging

_log = logging.getLogger(__name__)


class Template(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="products")
    async def get_products_command(self, interaction: Interaction):
        await interaction.response.defer()

        products = get_products()

        embed = Embed(
            title="Products",
            description=f"Here is all the products I was able to find! To get more information on a individual product run /product (product)",
            colour=interaction.user.colour,
            timestamp=utils.utcnow(),
            footer=f"Redon Hub •　Version {self.bot.version}"
        )

        embed.add_field(name="Products", value="\n".join([product.name for product in products]))

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="product")
    async def get_product_info_command(self, interaction: Interaction, product_name: str):
        try:
            product = get_product_by_name(product_name)
        except Exception:
            product = None
        
        if product:
            embed = Embed(
                title=product.name,
                description=f"Here is all the info I was able to get on {product.name}!",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
                footer=f"Redon Hub •　Version {self.bot.version}"
            )

            embed.add_field(name="Price", value=product.price, inline=True)
            embed.add_field(name="Description", value=product.description, inline=False)
        else:
            await interaction.response.send_message(embed=Embed(
                title="Not Found",
                description=f"I was unable to find any information on {product_name}.",
                colour=interaction.user.colour,
                timestamp=utils.utcnow(),
                footer=f"Redon Hub •　Version {self.bot.version}"
            ))

    @Cog.listener()
    async def on_ready(self):
        _log.info(f"Cog {__name__} ready")


async def setup(bot):
    await bot.add_cog(Template(bot))
