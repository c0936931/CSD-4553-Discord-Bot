import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database


class Slots(commands.Cog):
    """
    Slot machine command.
    The user places a bet and spins three random symbols.
    """

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot = bot
        self.db = db

    @app_commands.command(
        name="slots",
        description="Play the slot machine and bet your coins."
    )
    @app_commands.describe(
        bet="Amount of coins you want to bet"
    )
    async def slots(
        self,
        interaction: discord.Interaction,
        bet: int
    ):
        await interaction.response.defer()

        if bet <= 0:
            await interaction.followup.send(
                "Your bet must be more than 0 coins.",
                ephemeral=True
            )
            return

        user = await self.db.get_user(
            interaction.user.id,
            interaction.user.display_name
        )

        balance = user.get("balance", 0)

        if balance < bet:
            await interaction.followup.send(
                f"You do not have enough coins. Your balance is **{balance}** coins.",
                ephemeral=True
            )
            return

        symbols = ["🍒", "🍋", "🍇", "🔔", "💎"]
        spin = [
            random.choice(symbols),
            random.choice(symbols),
            random.choice(symbols)
        ]

        if spin[0] == spin[1] == spin[2]:
            winnings = bet * 5
            await self.db.update_balance(interaction.user.id, winnings)
            await self.db.record_game(interaction.user.id, "slots", True)

            result_text = f"Jackpot! You won **{winnings} coins**."
            color = discord.Color.green()

        elif spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
            winnings = bet * 2
            await self.db.update_balance(interaction.user.id, winnings)
            await self.db.record_game(interaction.user.id, "slots", True)

            result_text = f"Nice! Two symbols matched. You won **{winnings} coins**."
            color = discord.Color.green()

        else:
            await self.db.update_balance(interaction.user.id, -bet)
            await self.db.record_game(interaction.user.id, "slots", False)

            result_text = f"No match. You lost **{bet} coins**."
            color = discord.Color.red()

        embed = discord.Embed(
            title="Slot Machine",
            description=" | ".join(spin),
            color=color
        )

        embed.add_field(
            name="Bet",
            value=f"{bet} coins",
            inline=True
        )

        embed.add_field(
            name="Result",
            value=result_text,
            inline=False
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Slots(bot, bot.db))
