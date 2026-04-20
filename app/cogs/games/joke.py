import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
import logging


class Joke(commands.Cog):
	def __init__(self, bot: commands.Bot, db) -> None:
		self.bot = bot
		self.db = db

	@app_commands.command(description="Get a random joke")
	async def joke(self, interaction: discord.Interaction) -> None:
		# Defer the response
		await interaction.response.defer(thinking=True)

		# Test
		logging.debug("Joke command run")

		# Create session
		async with aiohttp.ClientSession() as session:
			async with session.get(
				"https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
			) as response:

				if response.status != 200:
					await interaction.followup.send(
						"I couldn't fetch a joke right now.", ephemeral=True
					)
					return

				data = await response.json()

		# Handle joke
		if data.get("type") == "single":
			joke_text = data.get("joke", "No joke found.")
		else:
			setup = data.get("setup", "No setup found.")
			delivery = data.get("delivery", "No punchline found.")
			joke_text = f"**{setup}**\n\n{delivery}"

		# Create embed
		embed = discord.Embed(
			title="💻 Programming Joke",
			description=joke_text,
			color=discord.Color.blurple(),
		)

		# Record game
		await self.db.record_game(interaction.user.id, "joke", True)

		# Send final message
		await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Joke(bot, bot.db))
