import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database) -> None:
        self.bot = bot
        self.db = db

    @app_commands.command(description="Bet on a dice roll (1-6) to win big")
    @app_commands.describe(
        wager="Amount of coins to wager",
        guess="Your guess for the dice roll (1-6)",
    )
    async def dice(
        self,
        interaction: discord.Interaction,
        wager: int,
        guess: int,
    ) -> None:
        await interaction.response.defer()

        # Validate wager
        if wager <= 0:
            await interaction.followup.send(
                "Wager must be at least 1 coin", ephemeral=True
            )
            return

        # Validate guess
        if guess < 1 or guess > 6:
            await interaction.followup.send(
                "You must guess a number between 1 and 6", ephemeral=True
            )
            return

        # Fetch user
        user = await self.db.get_user(
            interaction.user.id, interaction.user.display_name
        )

        if user["balance"] < wager:
            await interaction.followup.send(
                f"Not enough coins, balance: {user['balance']:,}", ephemeral=True
            )
            return

        # Roll dice
        roll = random.randint(1, 6)
        won = guess == roll

        # Calculate winnings (5x payout)
        if won:
            winnings = wager * 5
            await self.db.update_balance(interaction.user.id, winnings)
        else:
            await self.db.update_balance(interaction.user.id, -wager)

        await self.db.record_game(interaction.user.id, "dice", won)

        # Compute new balance locally
        new_balance = user["balance"] + (winnings if won else -wager)

        color = discord.Color.green() if won else discord.Color.red()

        embed = discord.Embed(
            title=f"Dice Roll: {roll}",
            description=(
                f"You guessed **{guess}**\n"
                + (
                    f"You won **{winnings:,}** coins! \n"
                    if won
                    else f"You lost **{wager:,}** coins.\n"
                )
                + f"New balance: **{new_balance:,}** coins"
            ),
            color=color,
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dice(bot, bot.db))
