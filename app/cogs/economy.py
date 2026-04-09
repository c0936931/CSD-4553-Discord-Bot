import discord
from discord import app_commands
from discord.ext import commands


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Check your coin balance")
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.send_message("Balance command")

    @app_commands.command(description="Claim your daily coin reward")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.send_message("Daily command")


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
