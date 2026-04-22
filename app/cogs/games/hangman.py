import discord
from discord import app_commands
from discord.ext import commands
import random
from db import Database
from configs import COIN_EMOJI
import logging

WORDS = ["python", "discord", "database", "programming", "hangman", "developer", "async", "function"]

MAX_LIVES = 6
REWARD = 50


class HangmanView(discord.ui.View):
	def __init__(self, cog, interaction, word, guessed, lives, msg):
		super().__init__(timeout=60)

		self.cog = cog
		self.interaction = interaction
		self.word = word
		self.guessed = guessed
		self.lives = lives
		self.msg = msg

		# Create letter buttons
		for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
			self.add_item(HangmanButton(letter, self))

	def get_display_word(self):
		return " ".join([c if c in self.guessed else "_" for c in self.word])

	async def update_embed(self):
		embed = discord.Embed(
			title="🪓 Hangman",
			description=f"Word: `{self.get_display_word()}`\n\nLives: ❤️ x{self.lives}",
			color=discord.Color.blurple()
		)
		await self.msg.edit(embed=embed, view=self)

	def check_win(self):
		return all(c in self.guessed for c in self.word)

	async def end_game(self, won: bool):
		for child in self.children:
			child.disabled = True

		user_id = self.interaction.user.id

		if won:
			await self.cog.db.update_balance(user_id, REWARD)
			await self.cog.db.record_game(user_id, "hangman", True)

			title = f"🎉 You guessed the word: **{self.word}**!"
			desc = f"You earned {REWARD} {COIN_EMOJI}"
			color = discord.Color.green()

		else:
			await self.cog.db.record_game(user_id, "hangman", False)

			title = f"💀 You lost! The word was **{self.word}**"
			desc = "Better luck next time!"
			color = discord.Color.red()

		embed = discord.Embed(title=title, description=desc, color=color)

		await self.msg.edit(embed=embed, view=self)

		# Remove lock
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


class HangmanButton(discord.ui.Button):
	def __init__(self, letter, view):
		super().__init__(label=letter, style=discord.ButtonStyle.secondary)
		self.letter = letter.lower()
		self.view_ref = view

	async def callback(self, interaction: discord.Interaction):
		view = self.view_ref

		# Only allow original user
		if interaction.user != view.interaction.user:
			return await interaction.response.send_message("This isn't your game!", ephemeral=True)

		await interaction.response.defer()

		self.disabled = True

		# Guess logic
		if self.letter in view.word:
			view.guessed.add(self.letter)
		else:
			view.lives -= 1

		await view.update_embed()

		# Check win
		if view.check_win():
			view.stop()
			return await view.end_game(True)

		# Check lose
		if view.lives <= 0:
			view.stop()
			return await view.end_game(False)


class Hangman(commands.Cog):
	def __init__(self, bot: commands.Bot, db: Database):
		self.bot = bot
		self.db = db
		self.active_games = {}

	@app_commands.command(description="Play Hangman and guess the word", name="hangman")
	async def hangman(self, interaction: discord.Interaction):

		logging.info("Command Run: /hangman")

		# Anti-spam
		if interaction.user.id in self.active_games:
			return await interaction.response.send_message(
				"You already have a game running.",
				ephemeral=True
			)

		self.active_games[interaction.user.id] = True

		await interaction.response.defer(thinking=True)

		word = random.choice(WORDS)
		guessed = set()
		lives = MAX_LIVES

		embed = discord.Embed(
			title="🪓 Hangman",
			description=f"Word: `{' '.join('_' for _ in word)}`\n\nLives: ❤️ x{lives}",
			color=discord.Color.blurple()
		)

		msg = await interaction.followup.send(embed=embed)

		view = HangmanView(self, interaction, word, guessed, lives, msg)
		await msg.edit(view=view)

		await view.wait()


async def setup(bot: commands.Bot):
	await bot.add_cog(Hangman(bot, bot.db))
