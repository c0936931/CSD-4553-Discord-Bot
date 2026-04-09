import discord
from discord import app_commands
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Flip a coin to win or lose coins")
    @app_commands.describe(amount="Amount of coins to wager")
    async def coinflip(self, interaction: discord.Interaction, amount: int):
        await interaction.response.send_message("Coinflip command")


async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
