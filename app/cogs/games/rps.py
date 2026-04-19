import random
import discord
from discord import app_commands
from discord.ext import commands


class RockPaperScissors(commands.Cog):
    """
    Rock Paper Scissors game command.
    The user chooses rock, paper, or scissors, and the bot randomly chooses one.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="rps",
        description="Play Rock Paper Scissors against the bot."
    )
    @app_commands.describe(choice="Choose rock, paper, or scissors")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Rock", value="rock"),
        app_commands.Choice(name="Paper", value="paper"),
        app_commands.Choice(name="Scissors", value="scissors"),
    ])
    async def rps(
        self,
        interaction: discord.Interaction,
        choice: app_commands.Choice[str]
    ):
        user_choice = choice.value
        bot_choice = random.choice(["rock", "paper", "scissors"])

        if user_choice == bot_choice:
            result = "It's a tie!"
        elif (
            user_choice == "rock" and bot_choice == "scissors"
            or user_choice == "paper" and bot_choice == "rock"
            or user_choice == "scissors" and bot_choice == "paper"
        ):
            result = "You win!"
        else:
            result = "You lose!"

        embed = discord.Embed(
            title="Rock Paper Scissors",
            description="You played against the bot.",
            color=discord.Color.blue()
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

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(RockPaperScissors(bot))
