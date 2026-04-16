import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database
from configs import COIN_EMOJI


class Coinflip(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database) -> None:
        self.bot = bot
        self.db = db

    @app_commands.command(description="Flip a coin to win or lose coins")
    @app_commands.describe(wager="Amount of coins to wager", choice="heads or tails")
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="Heads", value="heads"),
            app_commands.Choice(name="Tails", value="tails"),
        ]
    )
    async def coinflip(
        self,
        interaction: discord.Interaction,
        wager: int,
        choice: app_commands.Choice[str],
    ) -> None:
        await interaction.response.defer()

        if wager <= 0:
            await interaction.followup.send(
                "Wager must be at least 1 coin", ephemeral=True
            )
            return

        user = await self.db.get_user(
            interaction.user.id, interaction.user.display_name
        )

        if user["balance"] < wager:
            await interaction.followup.send(
                f"Not enough coins, balance: {user['balance']:,}", ephemeral=True
            )
            return

        result = random.choice(["heads", "tails"])
        won = result == choice.value

        if won:
            await self.db.update_balance(interaction.user.id, wager)
        else:
            await self.db.update_balance(interaction.user.id, -wager)

        await self.db.record_game(interaction.user.id, "coinflip", won)

        color = discord.Color.green() if won else discord.Color.red()
        outcome_text = (
            f"won **{wager:,}** coins!" if won else f"lost **{wager:,}** coins"
        )
        # compute locally since update_balance doesn't return the new value
        new_balance = user["balance"] + (wager if won else -wager)

        embed = discord.Embed(
            title=f"{COIN_EMOJI} Coinflip: {result.capitalize()}!",
            description=(
                f"You chose **{choice.value}**, you {outcome_text}\n"
                f"New balance: **{new_balance:,}** coins"
            ),
            color=color,
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Coinflip(bot, bot.db))
