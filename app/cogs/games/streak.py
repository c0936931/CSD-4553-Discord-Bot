import discord
from discord import app_commands
from discord.ext import commands


class Streaks(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db = bot.db

	@app_commands.command(name="streaks", description="Check your streak")
	async def streaks(self, interaction: discord.Interaction):
		await interaction.response.defer()

		user = await self.db.get_user(
			interaction.user.id,
			interaction.user.display_name
		)

		streak = user.get("streak", 0)

		await interaction.response.send_message(
			f"🔥 Your current streak is: **{streak} days**"
		)

	# 🔧 REQUIRED TO LOAD COG
	async def setup(bot):
		await bot.add_cog(Streaks(bot))
