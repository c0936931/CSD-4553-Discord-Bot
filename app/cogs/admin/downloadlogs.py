import discord
from discord import app_commands
from discord.ext import commands
import os
import logging


class Logs(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="downloadlogs", description="Send the bot log file.")
	async def downloadlogs(self, interaction: discord.Interaction):
		await interaction.response.defer(thinking=True, ephemeral=True)

		logging.info("Command Run: /downloadlogs")

		# Get log file path
		log_path = getattr(self.bot, "log_file", "bot.log")

		# Check existence
		if not os.path.exists(log_path):
			return await interaction.followup.send("Log file not found.", ephemeral=True)

		# Send file
		try:
			await interaction.followup.send(
				content="Here is the current log file:",
				file=discord.File(log_path),
				ephemeral=True
			)
		except Exception as e:
			await interaction.followup.send(
				f"Failed to send log file: `{e}`",
				ephemeral=True
			)


async def setup(bot):
	await bot.add_cog(Logs(bot))
