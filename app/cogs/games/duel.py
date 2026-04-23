import random
import discord
from discord import app_commands
from discord.ext import commands
from db import Database
import logging


class Duel(commands.Cog):
	"""
	PvP duel game.
	One user challenges another user and both risk coins.
	"""

	def __init__(self, bot: commands.Bot, db: Database):
		self.bot = bot
		self.db = db

	@app_commands.command(
		name="duel",
		description="Challenge another user to a PvP duel."
	)
	@app_commands.describe(
		member="The user you want to duel",
		bet="Amount of coins to bet"
	)
	async def duel(
		self,
		interaction: discord.Interaction,
		member: discord.Member,
		bet: int
	):
		await interaction.response.defer()

		# Log command run
		logging.info("Command Run: /duel")

		challenger_id = interaction.user.id
		challenger_name = interaction.user.display_name

		opponent_id = member.id
		opponent_name = member.display_name

		if member.bot:
			await interaction.followup.send(
				"You cannot duel a bot.",
				ephemeral=True
			)
			return

		if challenger_id == opponent_id:
			await interaction.followup.send(
				"You cannot duel yourself.",
				ephemeral=True
			)
			return

		if bet <= 0:
			await interaction.followup.send(
				"Bet amount must be more than 0 coins.",
				ephemeral=True
			)
			return

		challenger = await self.db.get_user(challenger_id, challenger_name)
		opponent = await self.db.get_user(opponent_id, opponent_name)

		challenger_balance = challenger.get("balance", 0)
		opponent_balance = opponent.get("balance", 0)

		if challenger_balance < bet:
			await interaction.followup.send(
				f"You do not have enough coins. Your balance is **{challenger_balance}** coins.",
				ephemeral=True
			)
			return

		if opponent_balance < bet:
			await interaction.followup.send(
				f"{opponent_name} does not have enough coins to duel. Their balance is **{opponent_balance}** coins.",
				ephemeral=True
			)
			return

		winner = random.choice(["challenger", "opponent"])

		if winner == "challenger":
			winner_user = interaction.user
			loser_user = member

			await self.db.update_balance(challenger_id, bet)
			await self.db.update_balance(opponent_id, -bet)

			await self.db.record_game(challenger_id, "duel", True)
			await self.db.record_game(opponent_id, "duel", False)

		else:
			winner_user = member
			loser_user = interaction.user

			await self.db.update_balance(opponent_id, bet)
			await self.db.update_balance(challenger_id, -bet)

			await self.db.record_game(opponent_id, "duel", True)
			await self.db.record_game(challenger_id, "duel", False)

		final_moves = [
			"landed a perfect arrow shot",
			"dodged the attack and countered",
			"used a surprise move",
			"hit a clean final strike",
			"outplayed the opponent",
			"won with a powerful finishing move"
		]

		final_move = random.choice(final_moves)

		embed = discord.Embed(
			title="🏹 PvP Duel",
			description=(
				f"{interaction.user.mention} challenged {member.mention} to a duel!\n\n"
				f"Both players risked **{bet} coins**."
			),
			color=discord.Color.gold()
		)

		embed.add_field(
			name="⚔️ Final Move",
			value=f"{winner_user.mention} {final_move}.",
			inline=False
		)

		embed.add_field(
			name="🏆 Winner",
			value=winner_user.mention,
			inline=True
		)

		embed.add_field(
			name="💀 Loser",
			value=loser_user.mention,
			inline=True
		)

		embed.add_field(
			name="💰 Reward",
			value=f"{winner_user.mention} won **{bet} coins**.",
			inline=False
		)

		embed.set_thumbnail(url=winner_user.display_avatar.url)

		embed.set_footer(
			text=f"Duel requested by {interaction.user.display_name}",
			icon_url=interaction.user.display_avatar.url
		)

		await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
	await bot.add_cog(Duel(bot, bot.db))
