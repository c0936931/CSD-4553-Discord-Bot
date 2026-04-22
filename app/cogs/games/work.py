import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database
import logging


class Work(commands.Cog):
	"""
	Work command.
	The user gets a random job message and earns coins.
	"""

	def __init__(self, bot: commands.Bot, db: Database):
		self.bot = bot
		self.db = db

	@app_commands.command(
		name="work",
		description="Work a random job and earn coins."
	)
	async def work(self, interaction: discord.Interaction):
		await interaction.response.defer()

		logging.info("Command Run: /work")

		await self.db.get_user(
			interaction.user.id,
			interaction.user.display_name
		)

		jobs = [
			"You fixed a broken cloud server",
			"You helped a customer at the help desk",
			"You cleaned the data center",
			"You delivered food to a hungry programmer",
			"You tested a new Discord bot feature",
			"You repaired a gaming computer",
			"You worked as a junior developer",
			"You solved a networking issue"
		]

		job = random.choice(jobs)

		reward = random.randint(50, 150)

		await self.db.update_balance(interaction.user.id, reward)

		await self.db.record_game(interaction.user.id, "work", True)

		embed = discord.Embed(
			title="Work Complete", description=job,
			color=discord.Color.green()
		)

		embed.add_field(
			name="Payment",
			value=f"You earned **{reward} coins**.",
			inline=False
		)

		await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
	await bot.add_cog(Work(bot, bot.db))
