import html
import random
import aiohttp
import discord
from collections.abc import Callable, Coroutine
from typing import Any
from discord import app_commands
from discord.ext import commands
from db import Database
from configs import TRIVIA_API, TRIVIA_REWARDS


class TriviaView(discord.ui.View):
	def __init__(
		self, author_id: int, correct_label: str, reward: int, db: Database
	) -> None:
		super().__init__(timeout=30)
		self.author_id = author_id
		self.correct_label = correct_label
		self.reward = reward
		self.db = db
		self.answered = False

	async def disable_all(self, interaction: discord.Interaction) -> None:
		for item in self.children:
			item.disabled = True
		await interaction.message.edit(view=self)

	def make_callback(
		self, label: str
	) -> Callable[[discord.Interaction], Coroutine[Any, Any, None]]:
		# closure so each button captures its own label at creation time
		async def callback(interaction: discord.Interaction) -> None:
			if interaction.user.id != self.author_id:
				await interaction.response.send_message(
					"That's not your question", ephemeral=True
				)
				return

			if self.answered:
				await interaction.response.send_message(
					"Already answered", ephemeral=True
				)
				return

			self.answered = True
			await interaction.response.defer()
			await self.disable_all(interaction)

			if label == self.correct_label:
				await self.db.update_balance(interaction.user.id, self.reward)
				await self.db.record_game(interaction.user.id, "trivia", True)
				await interaction.followup.send(
					f"You won! Correct answer, you earned **{self.reward}** coins"
				)
			else:
				await self.db.record_game(interaction.user.id, "trivia", False)
				await interaction.followup.send(
					f"You lost! The correct answer was **{self.correct_label}**"
				)

		return callback


class Trivia(commands.Cog):
	def __init__(self, bot: commands.Bot, db: Database) -> None:
		self.bot = bot
		self.db = db

	@app_commands.command(description="Answer a trivia question to earn coins")
	async def trivia(self, interaction: discord.Interaction) -> None:
		await interaction.response.defer()

		# ensure the user document exists before the callback tries to update balance
		await self.db.get_user(interaction.user.id, interaction.user.display_name)

		async with aiohttp.ClientSession() as session:
			async with session.get(TRIVIA_API) as resp:
				if resp.status != 200:
					await interaction.followup.send(
						"Failed to fetch a question, try again"
					)
					return
				data = await resp.json()

		if data["response_code"] != 0:
			await interaction.followup.send(
				"No questions available right now, try again"
			)
			return

		q = data["results"][0]
		question = html.unescape(q["question"])
		correct = html.unescape(q["correct_answer"])
		wrong = [html.unescape(a) for a in q["incorrect_answers"]]
		reward = TRIVIA_REWARDS[q["difficulty"]]

		# shuffle all 4 answers and track which label lands on the correct one
		answers = wrong + [correct]
		random.shuffle(answers)
		labels = ["A", "B", "C", "D"]

		correct_label = labels[answers.index(correct)]

		view = TriviaView(interaction.user.id, correct_label, reward, self.db)

		for label, answer in zip(labels, answers):
			display_answer = answer if len(answer) <= 75 else answer[:72] + "..."
			button = discord.ui.Button(
				label=f"{label}: {display_answer}",
				style=discord.ButtonStyle.primary,
				custom_id=label,
			)
			button.callback = view.make_callback(label)
			view.add_item(button)

		embed = discord.Embed(
			title="Trivia",
			description=f"**{question}**\n\nReward: {reward} coins",
			color=discord.Color.blurple(),
		)
		embed.set_footer(
			text=f"Category: {q['category']} | Difficulty: {q['difficulty'].capitalize()}"
		)

		await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Trivia(bot, bot.db))
