import discord
from discord import app_commands
from discord.ext import commands

@app_commands.command(name="streaks", description="Check your streak")
async def streaks(self, interaction: discord.Interaction):
    user = await self.db.get_user(
        interaction.user.id,
        interaction.user.display_name
    )

    streak = user.get("streak", 0)

    await interaction.response.send_message(
        f"🔥 Your current streak is: **{streak} days**"
    )