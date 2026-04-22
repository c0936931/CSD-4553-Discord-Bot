import discord
from discord import app_commands
from discord.ext import commands
from db import Database

# This file is a good starting point to understand how commands work
# Every command in this bot follows the same pattern as this one


# A Cog is just a class that groups related commands together
# The name (Rankings) doesn't affect anything visible to users
class Rankings(commands.Cog):
	# __init__ runs once when the cog is loaded. Always accept bot and db here
	# bot gives you access to Discord, db lets you read/write user data in MongoDB
	def __init__(self, bot: commands.Bot, db: Database) -> None:
		self.bot = bot
		self.db = db

	# @app_commands.command turns this method into a slash command (/rankings)
	# The description shows up in Discord when someone types /
	@app_commands.command(description="List the top 10 richest users")
	async def rankings(self, interaction: discord.Interaction) -> None:
		# interaction represents the user who ran the command
		# Use interaction.user to get their info (id, name, avatar, etc.)
		# For commands that make DB calls, defer first then use followup.send()
		await interaction.response.defer()

		top_users = await self.db.get_rankings()

		if not top_users:
			await interaction.followup.send("No users in the leaderboard yet")
			return

		# Embeds are the rich message cards Discord supports
		# Use them whenever you want a formatted, styled response
		embed = discord.Embed(title="Coin Rankings", color=discord.Color.gold())

		lines = []
		for i, user in enumerate(top_users, start=1):
			lines.append(f"**{i}.** {user['username']}: {user['balance']:,} coins")

		embed.description = "\n".join(lines)
		await interaction.followup.send(embed=embed)


# setup() is required at the bottom of every cog file
# Discord.py calls this automatically when loading the cog, don't rename it
async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Rankings(bot, bot.db))
