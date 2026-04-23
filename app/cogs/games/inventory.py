import discord
from discord import app_commands
from discord.ext import commands
import logging


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    # 🎒 INVENTORY COMMAND
    @app_commands.command(name="inventory", description="Check your inventory")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Log command run
        logging.info("Command Run: /inventory")

        user = await self.db.get_user(
            interaction.user.id,
            interaction.user.display_name
        )

        if not user:
            await interaction.followup.send("👜 You do not have any saved data yet.")
            return

        inventory = user.get("inventory", [])

        if not inventory:
            await interaction.followup.send("👜 Your inventory is empty.")
        else:
            await interaction.followup.send(
                "👜 Your inventory:\n" + ", ".join(inventory)
            )


# 🔧 REQUIRED TO LOAD COG
async def setup(bot):
    await bot.add_cog(Inventory(bot))
