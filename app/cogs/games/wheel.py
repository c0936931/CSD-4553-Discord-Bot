import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database


class Wheel(commands.Cog):
	"""
	Simple prize wheel game.
	The user pays coins to spin the wheel.
	"""

	def __init__(self, bot: commands.Bot, db: Database):
		self.bot = bot
		self.db = db

	@app_commands.command(
		name="wheel",
		description="Spin the prize wheel and try to win coins."
	)
	@app_commands.describe(
		bet="Amount of coins you want to bet"
	)
	async def wheel(
		self,
		interaction: discord.Interaction,
		bet: int
	):
		await interaction.response.defer()

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

		wheel_options = [
			"Small Prize",
			"Big Prize",
			"Jackpot",
			"Lose",
			"Lose",
			"Try Again"
		]

		result = random.choice(wheel_options)

		if result == "Jackpot":
			reward = bet * 5

			await self.db.update_balance(interaction.user.id, reward)
			await self.db.record_game(interaction.user.id, "wheel", True)

			result_text = f"The wheel landed on **Jackpot**! You won **{reward} coins**."
			color = discord.Color.green()

		elif result == "Big Prize":
			reward = bet * 3

			await self.db.update_balance(interaction.user.id, reward)
			await self.db.record_game(interaction.user.id, "wheel", True)

			result_text = f"The wheel landed on **Big Prize**! You won **{reward} coins**."
			color = discord.Color.green()

		elif result == "Small Prize":
			reward = bet

			await self.db.update_balance(interaction.user.id, reward)
			await self.db.record_game(interaction.user.id, "wheel", True)

			result_text = f"The wheel landed on **Small Prize**! You won **{reward} coins**."
			color = discord.Color.green()

		elif result == "Try Again":
			await self.db.record_game(interaction.user.id, "wheel", False)

			result_text = "The wheel landed on **Try Again**. No coins were lost."
			color = discord.Color.yellow()

		else:
			await self.db.update_balance(interaction.user.id, -bet)
			await self.db.record_game(interaction.user.id, "wheel", False)

			result_text = f"The wheel landed on **Lose**. You lost **{bet} coins**."
			color = discord.Color.red()

		embed = discord.Embed(
			title="Prize Wheel",
			description=result_text,
			color=color
		)

		embed.add_field(
			name="Your Bet",
			value=f"{bet} coins",
			inline=True
		)

		embed.add_field(
			name="Wheel Result",
			value=result,
			inline=True
		)

		await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
	await bot.add_cog(Wheel(bot, bot.db))
