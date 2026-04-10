import discord
from discord import app_commands
from discord.ext import commands
from db import Database


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot, db: Database) -> None:
        self.bot = bot
        self.db = db

    @app_commands.command(description="Check your stats")
    async def stats(self, interaction: discord.Interaction) -> None:
        user = await self.db.get_stats(interaction.user.id)

        if not user:
            await interaction.response.send_message(
                "No stats yet, play some games first"
            )
            return

        coinflip = user.get("coinflip", {})
        cf_wins = coinflip.get("wins", 0)
        cf_losses = coinflip.get("losses", 0)
        cf_ratio = f"{cf_wins}/{cf_losses}" if (cf_wins + cf_losses) > 0 else "N/A"

        trivia = user.get("trivia", {})
        tv_wins = trivia.get("wins", 0)
        tv_losses = trivia.get("losses", 0)
        tv_ratio = f"{tv_wins}/{tv_losses}" if (tv_wins + tv_losses) > 0 else "N/A"

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Stats",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Balance", value=f"{user.get('balance', 0):,} coins", inline=True
        )
        embed.add_field(
            name="Total Earned",
            value=f"{user.get('total_earned', 0):,} coins",
            inline=True,
        )
        embed.add_field(
            name="Games Played", value=str(user.get("games_played", 0)), inline=True
        )
        embed.add_field(name="Coinflip W/L", value=cf_ratio, inline=True)
        embed.add_field(name="Trivia W/L", value=tv_ratio, inline=True)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Stats(bot, bot.db))
