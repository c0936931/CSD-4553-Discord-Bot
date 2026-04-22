import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database


class BeastWar(commands.Cog):
    """
    Simple beast war game.
    The user fights a random beast and bets coins.
    """

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot = bot
        self.db = db

    @app_commands.command(
        name="beastwar",
        description="Fight a beast and try to win coins."
    )
    @app_commands.describe(
        bet="Amount of coins you want to bet"
    )
    async def beastwar(
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

        beasts = [
            "Shadow Wolf",
            "Fire Dragon",
            "Stone Golem",
            "Dark Panther",
            "Thunder Beast"
        ]

        beast = random.choice(beasts)

        player_power = random.randint(1, 100)
        beast_power = random.randint(1, 100)

        if player_power > beast_power:
            reward = bet * 2

            await self.db.update_balance(interaction.user.id, reward)
            await self.db.record_game(interaction.user.id, "beastwar", True)

            result_text = f"You defeated the **{beast}** and won **{reward} coins**!"
            color = discord.Color.green()

        elif player_power < beast_power:
            await self.db.update_balance(interaction.user.id, -bet)
            await self.db.record_game(interaction.user.id, "beastwar", False)

            result_text = f"The **{beast}** defeated you. You lost **{bet} coins**."
            color = discord.Color.red()

        else:
            await self.db.record_game(interaction.user.id, "beastwar", False)

            result_text = f"You and the **{beast}** had equal power. No coins were lost."
            color = discord.Color.yellow()

        embed = discord.Embed(
            title="🐺 Beast War",
            description=result_text,
            color=color
        )

        embed.add_field(
            name="Your Power",
            value=str(player_power),
            inline=True
        )

        embed.add_field(
            name="Beast Power",
            value=str(beast_power),
            inline=True
        )

        embed.add_field(
            name="Beast",
            value=beast,
            inline=False
        )

        embed.set_footer(
            text=f"Played by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(BeastWar(bot, bot.db))
