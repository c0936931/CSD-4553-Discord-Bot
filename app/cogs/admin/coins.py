import discord
from discord import app_commands
from discord.ext import commands
import logging
from configs import COIN_EMOJI


class Coins(commands.Cog):
	def __init__(self, bot: commands.Bot, db):
		self.bot = bot
		self.db = db

	# /addcoins
	@app_commands.command(description="Add coins to a user (admin only)")
	@app_commands.describe(user="Select the user to add coins to", amount="Amount of coins to add")
	# @app_commands.checks.has_permissions(administrator=True)
	async def addcoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
		await interaction.response.defer(thinking=True)
		logging.info("Command Run: /addcoins")

		if amount <= 0:
			await interaction.followup.send("Amount must be greater than 0.", ephemeral=True)
			return

		db_user = await self.db.get_user(user.id, user.display_name)
		await self.db.update_balance(user.id, amount)
		new_balance = db_user["balance"] + amount

		embed = discord.Embed(
			title="💸 Coins Added",
			description=(
				f"Added **{amount:,}** coins to **{user.mention}**.\n"
				f"New balance: **{new_balance:,}** {COIN_EMOJI}."
			),
			color=discord.Color.green()
		)

		await interaction.followup.send(embed=embed, ephemeral=True)

	# /removecoins
	@app_commands.command(description="Remove coins from a user (admin only)")
	@app_commands.describe(user="Select the user to remove coins from", amount="Amount of coins to remove")
	# @app_commands.checks.has_permissions(administrator=True)
	async def removecoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
		await interaction.response.defer(thinking=True)
		logging.info("Command Run: /removecoins")

		if amount <= 0:
			await interaction.followup.send("Amount must be greater than 0.", ephemeral=True)
			return

		db_user = await self.db.get_user(user.id, user.display_name)

		# Prevent negative balance
		new_balance = max(0, db_user["balance"] - amount)
		await self.db.update_balance(user.id, -amount)

		embed = discord.Embed(
			title="💸 Coins Removed",
			description=(
				f"Removed **{amount:,}** coins from **{user.mention}**.\n"
				f"New balance: **{new_balance:,}** {COIN_EMOJI}."
			),
			color=discord.Color.red()
		)

		await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
	await bot.add_cog(Coins(bot, bot.db))
