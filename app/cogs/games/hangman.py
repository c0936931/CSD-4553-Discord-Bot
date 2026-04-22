import discord
from discord import app_commands
from discord.ext import commands
import random
from db import Database
from configs import COIN_EMOJI
import logging

WORDS = [
	"python",
	"discord",
	"database",
	"programming",
	"hangman",
	"developer",
	"async",
	"function"
]

MAX_LIVES = 6
REWARD = 50


class HangmanView(discord.ui.View):
	def __init__(self, cog, interaction, word, msg):
		super().__init__(timeout=60)

		self.cog = cog
		self.interaction = interaction
		self.word = word
		self.msg = msg

		self.guessed = set()
		self.used_letters = set()
		self.lives = MAX_LIVES

		# Discord allows max 25 components, so we use dropdowns instead of 26 buttons
		self.add_item(HangmanSelect("A-I", "ABCDEFGHI"))
		self.add_item(HangmanSelect("J-R", "JKLMNOPQR"))
		self.add_item(HangmanSelect("S-Z", "STUVWXYZ"))

	def get_display_word(self):
		return " ".join([letter if letter in self.guessed else "_" for letter in self.word])

	def get_used_letters(self):
		if not self.used_letters:
			return "None"
		return ", ".join(sorted(self.used_letters)).upper()

	async def update_embed(self):
		embed = discord.Embed(
			title="🪓 Hangman",
			description=(
				f"Word: `{self.get_display_word()}`\n\n"
				f"Lives: ❤️ x{self.lives}\n"
				f"Used Letters: `{self.get_used_letters()}`"
			),
			color=discord.Color.blurple()
		)

		await self.msg.edit(embed=embed, view=self)

	def check_win(self):
		return all(letter in self.guessed for letter in self.word)

	async def end_game(self, won: bool):
		for child in self.children:
			child.disabled = True

		user_id = self.interaction.user.id

		if won:
			await self.cog.db.update_balance(user_id, REWARD)
			await self.cog.db.record_game(user_id, "hangman", True)

			embed = discord.Embed(
				title="🎉 You won!",
				description=(
					f"You guessed the word: **{self.word}**\n"
					f"You earned **{REWARD} {COIN_EMOJI}**"
				),
				color=discord.Color.green()
			)

		else:
			await self.cog.db.record_game(user_id, "hangman", False)

			embed = discord.Embed(
				title="💀 You lost!",
				description=f"The word was **{self.word}**\nBetter luck next time!",
				color=discord.Color.red()
			)

		await self.msg.edit(embed=embed, view=self)

		# Remove active game lock
		self.cog.active_games.pop(user_id, None)

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True

		embed = discord.Embed(
			title="⏳ Game timed out",
			description=f"The word was **{self.word}**",
			color=discord.Color.dark_grey()
		)

		await self.msg.edit(embed=embed, view=self)

		self.cog.active_games.pop(self.interaction.user.id, None)


class HangmanSelect(discord.ui.Select):
	def __init__(self, label, letters):
		options = []

		for letter in letters:
			options.append(
				discord.SelectOption(
					label=letter,
					value=letter.lower()
				)
			)

		super().__init__(
			placeholder=f"Choose a letter: {label}",
			min_values=1,
			max_values=1,
			options=options
		)

	async def callback(self, interaction: discord.Interaction):
		view: HangmanView = self.view

		# Only the person who started the game can play
		if interaction.user != view.interaction.user:
			return await interaction.response.send_message(
				"This isn't your game!",
				ephemeral=True
			)

		letter = self.values[0]

		# Prevent same letter from being used again
		if letter in view.used_letters:
			return await interaction.response.send_message(
				f"You already guessed `{letter.upper()}`.",
				ephemeral=True
			)

		await interaction.response.defer()

		view.used_letters.add(letter)

		if letter in view.word:
			view.guessed.add(letter)
		else:
			view.lives -= 1

		if view.check_win():
			view.stop()
			return await view.end_game(True)

		if view.lives <= 0:
			view.stop()
			return await view.end_game(False)

		await view.update_embed()


class Hangman(commands.Cog):
	def __init__(self, bot: commands.Bot, db: Database):
		self.bot = bot
		self.db = db
		self.active_games = {}

	@app_commands.command(description="Play Hangman and guess the word", name="hangman")
	async def hangman(self, interaction: discord.Interaction):

		logging.info("Command Run: /hangman")

		user_id = interaction.user.id

		# Anti-spam system
		if user_id in self.active_games:
			return await interaction.response.send_message(
				"You already have a game running.",
				ephemeral=True
			)

		self.active_games[user_id] = True

		await interaction.response.defer(thinking=True)

		word = random.choice(WORDS)

		embed = discord.Embed(
			title="🪓 Hangman",
			description=(
				f"Word: `{' '.join('_' for _ in word)}`\n\n"
				f"Lives: ❤️ x{MAX_LIVES}\n"
				f"Used Letters: `None`"
			),
			color=discord.Color.blurple()
		)

		msg = await interaction.followup.send(embed=embed)

		view = HangmanView(self, interaction, word, msg)

		await msg.edit(view=view)


async def setup(bot: commands.Bot):
	await bot.add_cog(Hangman(bot, bot.db))
