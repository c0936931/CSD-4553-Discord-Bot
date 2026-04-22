import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database


class RockPaperScissors(commands.Cog):
    """
    Rock Paper Scissors game command.
    The user chooses rock, paper, or scissors, and the bot randomly chooses one.
    The user can bet coins, win coins, lose coins, and stats are recorded.
    """

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot = bot
        self.db = db

    @app_commands.command(
        name="rps",
        description="Play Rock Paper Scissors against the bot."
    )
    @app_commands.describe(
        choice="Choose rock, paper, or scissors",
        bet="Amount of coins to bet"
    )
    @app_commands.choices(choice=[
        app_commands.Choice(name="Rock", value="rock"),
        app_commands.Choice(name="Paper", value="paper"),
        app_commands.Choice(name="Scissors", value="scissors"),
    ])
    async def rps(
        self,
        interaction: discord.Interaction,
        choice: app_commands.Choice[str],
        bet: int
    ):
        if bet <= 0:
            await interaction.response.send_message(
                "Bet amount must be more than 0 coins.",
                ephemeral=True
            )
            return

        user = await self.db.get_user(
            interaction.user.id,
            interaction.user.display_name
        )

        balance = user.get("balance", 0)

        if balance < bet:
            await interaction.response.send_message(
                f"You do not have enough coins. Your balance is **{balance}** coins.",
                ephemeral=True
            )
            return

        user_choice = choice.value
        bot_choice = random.choice(["rock", "paper", "scissors"])

        if user_choice == bot_choice:
            result = "It's a tie!"
            coins_text = "No coins were won or lost."
            color = discord.Color.yellow()

        elif (
            user_choice == "rock" and bot_choice == "scissors"
            or user_choice == "paper" and bot_choice == "rock"
            or user_choice == "scissors" and bot_choice == "paper"
        ):
            result = "You win!"
            await self.db.update_balance(interaction.user.id, bet)
            await self.db.record_game(interaction.user.id, "rps", True)
            coins_text = f"You won **{bet}** coins."
            color = discord.Color.green()

        else:
            result = "You lose!"
            await self.db.update_balance(interaction.user.id, -bet)
            await self.db.record_game(interaction.user.id, "rps", False)
            coins_text = f"You lost **{bet}** coins."
            color = discord.Color.red()

        embed = discord.Embed(
            title="Rock Paper Scissors",
            description="You played against the bot.",
            color=color
        )

        embed.add_field(
            name="Your Choice",
            value=user_choice.capitalize(),
            inline=True
        )

        embed.add_field(
            name="Bot Choice",
            value=bot_choice.capitalize(),
            inline=True
        )

        embed.add_field(
            name="Result",
            value=result,
            inline=False
        )

        embed.add_field(
            name="Coins",
            value=coins_text,
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(RockPaperScissors(bot, bot.db))
