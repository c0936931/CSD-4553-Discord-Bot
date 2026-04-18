import discord
from discord import app_commands
from discord.ext import commands
from cards_handler import get_card, Shoe
import asyncio
from db import Database
from configs import COIN_EMOJI

DECKS = 6
DEAL_SPEED = 0.5


class BlackjackView(discord.ui.View):
	def __init__(self, cog, interaction, shoe, dealer_cards, player_cards, wager, msg):
		super().__init__(timeout=30)
		self.cog = cog
		self.interaction = interaction
		self.shoe = shoe
		self.dealer_cards = dealer_cards
		self.player_cards = player_cards
		self.wager = wager
		self.msg = msg

		self.player_value = cog.cards_value(player_cards)
		self.dealer_value = cog.cards_value(dealer_cards)

		self.result = None

	async def update_embed(self, hide_dealer=True):
		embed = self.cog.build_embed(
			self.dealer_cards,
			self.dealer_value,
			self.player_cards,
			self.player_value,
			hide_dealer=hide_dealer
		)
		await self.msg.edit(embed=embed, view=self)

	@discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
	async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		if interaction.user != self.interaction.user:
			return await interaction.response.send_message("This isn't your game!", ephemeral=True)

		await interaction.response.defer()

		self.player_cards, self.player_value = await self.cog.hit(self.player_cards, self.shoe)
		self.result = "hit"
		await self.update_embed(hide_dealer=True)

		if self.player_value >= 21:
			self.stop()

	@discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
	async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		if interaction.user != self.interaction.user:
			return await interaction.response.send_message("This isn't your game!", ephemeral=True)

		await interaction.response.defer()
		self.result = "stand"
		self.stop()

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self.msg.edit(content="⏳ Game timed out.", view=self)


class Blackjack(commands.Cog):
	def __init__(self, bot: commands.Bot, db: Database) -> None:
		self.bot = bot
		self.db = db

	def build_embed(self, dealer_cards, dealer_value, player_cards, player_value, hide_dealer=False):
		shown_dealer_cards = dealer_cards.copy()
		shown_value = dealer_value

		if hide_dealer and dealer_cards:
			shown_dealer_cards = ["--"] + dealer_cards[1:]
			shown_value = self.cards_value(dealer_cards[1:])

		dealer_str = " ".join(get_card(c) for c in shown_dealer_cards)
		player_str = " ".join(get_card(c) for c in player_cards)

		embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.dark_green())
		embed.add_field(name=f"Dealer ({shown_value})", value=dealer_str or "No cards", inline=False)
		embed.add_field(name=f"You ({player_value})", value=player_str or "No cards", inline=False)
		return embed

	def cards_value(self, cards):
		values = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "0": 10, "J": 10, "Q": 10, "K": 10, "-": 0}

		total = 0
		aces = 0

		for card in cards:
			if card[0] == "A":
				aces += 1
			else:
				total += values[card[0]]

		if aces == 0:
			return total
		elif total + aces * 11 <= 21:
			return total + aces * 11
		else:
			return total + aces

	async def hit(self, cards, shoe):
		cards.append(shoe.draw())
		await asyncio.sleep(DEAL_SPEED)
		return cards, self.cards_value(cards)

	@app_commands.command(description="Play Blackjack and wager coins")
	@app_commands.describe(wager="Amount of coins to wager")
	async def blackjack(self, interaction: discord.Interaction, wager: int) -> None:
		if wager <= 0:
			return await interaction.response.send_message("Wager must be at least 1 coin", ephemeral=True)

		user = await self.db.get_user(interaction.user.id, interaction.user.display_name)

		if user["balance"] < wager:
			return await interaction.response.send_message(
				f"Not enough coins, balance: {user['balance']:,}", ephemeral=True
			)

		await interaction.response.defer(thinking=True)

		shoe = Shoe(DECKS)
		dealer_cards = []
		player_cards = []

		# Initial deal using async hit()
		player_cards, _ = await self.hit(player_cards, shoe)
		dealer_cards, _ = await self.hit(dealer_cards, shoe)
		player_cards, _ = await self.hit(player_cards, shoe)
		dealer_cards, _ = await self.hit(dealer_cards, shoe)

		dealer_value = self.cards_value(dealer_cards)
		player_value = self.cards_value(player_cards)

		embed = self.build_embed(dealer_cards, dealer_value, player_cards, player_value, hide_dealer=True)
		msg = await interaction.followup.send(embed=embed)

		view = BlackjackView(self, interaction, shoe, dealer_cards, player_cards, wager, msg)
		await msg.edit(view=view)

		await view.wait()

		# Player bust
		if view.player_value > 21:
			await self.db.update_balance(interaction.user.id, -wager)
			await self.db.record_game(interaction.user.id, "blackjack", False)

			final = self.build_embed(view.dealer_cards, view.dealer_value, view.player_cards, view.player_value)
			final.title = f"💀 Bust! You lost {wager:,} {COIN_EMOJI}"
			final.color = discord.Color.red()

			for child in view.children:
				child.disabled = True

			return await msg.edit(embed=final, view=view)

		# Dealer turn (also async hit)
		while view.dealer_value < 17:
			view.dealer_cards, view.dealer_value = await self.hit(view.dealer_cards, shoe)

		# Determine outcome
		if view.dealer_value > 21:
			won = True
		elif view.dealer_value < view.player_value:
			won = True
		elif view.dealer_value > view.player_value:
			won = False
		else:
			won = None

		# Payouts
		if won is True:
			await self.db.update_balance(interaction.user.id, wager)
			await self.db.record_game(interaction.user.id, "blackjack", True)
			new_balance = user["balance"] + wager
			title = f"🎉 You won {wager:,} {COIN_EMOJI}!"
			color = discord.Color.green()

		elif won is False:
			await self.db.update_balance(interaction.user.id, -wager)
			await self.db.record_game(interaction.user.id, "blackjack", False)
			new_balance = user["balance"] - wager
			title = f"💀 You lost {wager:,} {COIN_EMOJI}"
			color = discord.Color.red()

		else:
			new_balance = user["balance"]
			title = "🤝 Push — no coins won or lost"
			color = discord.Color.yellow()

		final = self.build_embed(view.dealer_cards, view.dealer_value, view.player_cards, view.player_value)
		final.title = title
		final.color = color
		final.set_footer(text=f"New balance: {new_balance:,} coins")

		for child in view.children:
			child.disabled = True

		await msg.edit(embed=final, view=view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Blackjack(bot, bot.db))
