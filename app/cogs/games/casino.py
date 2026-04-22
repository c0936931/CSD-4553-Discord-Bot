import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database
import logging


class Casino(commands.Cog):
	"""
	Simple casino game.
	The user bets coins and the bot gives a random casino result.
	"""

	def __init__(self, bot: commands.Bot, db: Database):
		self.bot = bot
		self.db = db

	@app_commands.command(
		name="casino",
		description="Play a simple casino game and bet coins."
	)
	@app_commands.describe(
		bet="Amount of coins you want to bet"
	)
	async def casino(
		self,
		interaction: discord.Interaction,
		bet: int
	):
		await interaction.response.defer()

		logging.info("Command Run: /casino")

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

		casino_roll = random.randint(1, 100)

		if casino_roll <= 10:
			winnings = bet * 4

			await self.db.update_balance(interaction.user.id, winnings)
			await self.db.record_game(interaction.user.id, "casino", True)

			result_text = f"You hit the lucky casino bonus and won **{winnings} coins**!"
			color = discord.Color.green()

		elif casino_roll <= 45:
			winnings = bet * 2

			await self.db.update_balance(interaction.user.id, winnings)
			await self.db.record_game(interaction.user.id, "casino", True)

			result_text = f"You won this round and earned **{winnings} coins**!"
			color = discord.Color.green()

		else:
			await self.db.update_balance(interaction.user.id, -bet)
			await self.db.record_game(interaction.user.id, "casino", False)

			result_text = f"You lost this round and lost **{bet} coins**."
			color = discord.Color.red()

		embed = discord.Embed(
			title="Casino Game",
			description=result_text,
			color=color
		)

		embed.add_field(
			name="Bet",
			value=f"{bet} coins",
			inline=True
		)

		embed.add_field(
			name="Roll Number",
			value=str(casino_roll),
			inline=True
		)

		await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
	await bot.add_cog(Casino(bot, bot.db))
