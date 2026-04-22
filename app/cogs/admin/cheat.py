import discord
from discord import app_commands
from discord.ext import commands
import logging


class Cheat(commands.Cog):
	def __init__(self, bot: commands.Bot, db):
		self.bot = bot
		self.db = db

	@app_commands.command(description="Add coins to yourself (admin only)")
	@app_commands.describe(amount="Amount of coins to add")
	# @app_commands.checks.has_permissions(administrator=True)
	async def cheat(self, interaction: discord.Interaction, amount: int):
		await interaction.response.defer(thinking=True)

		logging.info("Command Run: /cheat")

		if amount <= 0:
			await interaction.followup.send("Amount must be greater than 0.", ephemeral=True)
			return

		user = await self.db.get_user(interaction.user.id, interaction.user.display_name)

		await self.db.update_balance(interaction.user.id, amount)
		new_balance = user["balance"] + amount

		embed = discord.Embed(
			title="💸 Cheat Activated",
			description=(
				f"Added **{amount:,}** coins to your balance.\n"
				f"New balance: **{new_balance:,}** coins."
			),
			color=discord.Color.gold()
		)

		await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
	await bot.add_cog(Cheat(bot, bot.db))
