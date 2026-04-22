import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from db import Database
from configs import COIN_EMOJI
import random									# Used for shuffle

DECKS = 6            # Number of decks in the shoe
DEAL_SPEED = 0.5     # Delay between card deals for animation

# Unicode based cards
cards = {
	"AS": "🂡", "2S": "🂢", "3S": "🂣", "4S": "🂤", "5S": "🂥", "6S": "🂦", "7S": "🂧", "8S": "🂨", "9S": "🂩", "0S": "🂪", "JS": "🂫", "QS": "🂭", "KS": "🂮",
	"AH": "🂱", "2H": "🂲", "3H": "🂳", "4H": "🂴", "5H": "🂵", "6H": "🂶", "7H": "🂷", "8H": "🂸", "9H": "🂹", "0H": "🂺", "JH": "🂻", "QH": "🂽", "KH": "🂾",
	"AC": "🃑", "2C": "🃒", "3C": "🃓", "4C": "🃔", "5C": "🃕", "6C": "🃖", "7C": "🃗", "8C": "🃘", "9C": "🃙", "0C": "🃚", "JC": "🃛", "QC": "🃝", "KC": "🃞",
	"AD": "🃁", "2D": "🃂", "3D": "🃃", "4D": "🃄", "5D": "🃅", "6D": "🃆", "7D": "🃇", "8D": "🃈", "9D": "🃉", "0D": "🃊", "JD": "🃋", "QD": "🃍", "KD": "🃎",
	"J": "🃏", "--": "🂠"}

# Values and suits (0 is 10)
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "0", "J", "Q", "K"]
suits = ["H", "D", "S", "C"]

# Get card emoji
def get_card(card):
	if len(card) == 0:
		return ""
	else:
		try:
			return small[card]
		except KeyError:
			print("Error: card not supported")
			raise
		else:
			pass


# Card Deck Holder
class Deck():
	def __init__(self):
		self.cards = []
		self.delt = []
		for suit in suits:
			for value in values:
				self.cards.append(f"{value}{suit}")
		self.shuffle()

	def shuffle(self):
		self.cards.extend(self.delt)
		self.delt = []
		random.shuffle(self.cards)

	def print(self):
		for self.card in self.cards:
			print(get_card(self.card), end="")
		print()

	def draw(self):
		card = self.cards.pop()
		self.delt.append(card)
		return card
		

# Card Shoe Holder
class Shoe():
	def __init__(self, count):
		self.cards = []
		self.delt = []
		for self.i in range(count):
			deck = Deck()
			self.cards.extend(deck.cards)
		self.shuffle()

	def shuffle(self):
		self.cards.extend(self.delt)
		self.delt = []
		random.shuffle(self.cards)

	def print(self):
		for self.card in self.cards:
			print(get_card(self.card), end="")
		print()

	def draw(self):
		card = self.cards.pop()
		self.delt.append(card)
		return card


class BlackjackView(discord.ui.View):
	# Blackjack UI
	def __init__(self, cog, interaction, shoe, dealer_cards, player_cards, wager, msg):
		super().__init__(timeout=30)

		# Store references needed
		self.cog = cog
		self.interaction = interaction
		self.shoe = shoe
		self.dealer_cards = dealer_cards
		self.player_cards = player_cards
		self.wager = wager
		self.msg = msg

	async def update_embed(self, hide_dealer=True):
		# Update embed including values
		dealer_value = self.cog.cards_value(self.dealer_cards)
		player_value = self.cog.cards_value(self.player_cards)

		embed = self.cog.build_embed(
			self.dealer_cards,
			dealer_value,
			self.player_cards,
			player_value,
			hide_dealer=hide_dealer
		)

		await self.msg.edit(embed=embed, view=self)

	@discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
	async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		# Hit button
		
		# Prevent other users from clicking
		if interaction.user != self.interaction.user:
			return await interaction.response.send_message("This isn't your game!", ephemeral=True)

		await interaction.response.defer()

		# Deal a card to the player
		self.player_cards, _ = await self.cog.hit(self.player_cards, self.shoe)

		# Update embed with hidden dealer card
		await self.update_embed(hide_dealer=True)

		# If player hits 21 or busts stop the view
		if self.cog.cards_value(self.player_cards) >= 21:
			self.stop()

	@discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
	async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		# Stand button
		
		if interaction.user != self.interaction.user:
			return await interaction.response.send_message("This isn't your game!", ephemeral=True)

		await interaction.response.defer()
		self.stop()

	async def on_timeout(self):
		# Timeout so games don't keep waiting
		
		for child in self.children:
			child.disabled = True

		embed = discord.Embed(
			title="⏳ Game timed out.",
			description="Buttons disabled.",
			color=discord.Color.dark_grey()
		)

		await self.msg.edit(embed=embed, view=self)

		# Remove lock so user can play again
		self.cog.active_games.pop(self.interaction.user.id, None)


class Blackjack(commands.Cog):
	# Main logic
	def __init__(self, bot: commands.Bot, db: Database) -> None:
		self.bot = bot
		self.db = db

		# Disctionary to prevent spam
		self.active_games = {}

	def build_embed(self, dealer_cards, dealer_value, player_cards, player_value, hide_dealer=False):
		# Create embed
		shown_cards = dealer_cards.copy()
		shown_value = dealer_value

		# Hide dealer's first card only if they have at least 2 cards
		if hide_dealer and len(dealer_cards) >= 2:
			shown_cards = ["--"] + dealer_cards[1:]
			shown_value = self.cards_value(dealer_cards[1:])

		dealer_str = " ".join(get_card(c) for c in shown_cards)
		player_str = " ".join(get_card(c) for c in player_cards)

		embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.dark_green())
		embed.add_field(name=f"Dealer ({shown_value})", value=dealer_str or "No cards", inline=False)
		embed.add_field(name=f"You ({player_value})", value=player_str or "No cards", inline=False)
		return embed

	def cards_value(self, cards):
		# Calculate values

		# Card to value dict
		values = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "0": 10, "J": 10, "Q": 10, "K": 10, "-": 0}

		total = 0
		aces = 0

		# Count non-aces first
		for card in cards:
			if card[0] == "A":
				aces += 1
			else:
				total += values[card[0]]

		# Add aces optimally
		if aces == 0:
			return total
		elif total + aces * 11 <= 21:
			return total + aces * 11
		else:
			return total + aces

	async def hit(self, cards, shoe):
		# Get a card with deal speed
		cards.append(shoe.draw())
		await asyncio.sleep(DEAL_SPEED)
		return cards

	@app_commands.command(description="Play Blackjack and wager coins")
	@app_commands.describe(wager="Amount of coins to wager")
	async def blackjack(self, interaction: discord.Interaction, wager: int) -> None:
		# Main command

		# Anti-spam protection
		if interaction.user.id in self.active_games:
			return await interaction.response.send_message(
				"You already have a blackjack game running. Finish it first.",
				ephemeral=True
			)

		# Mark user as active
		self.active_games[interaction.user.id] = True

		# Validate wager
		if wager <= 0:
			self.active_games.pop(interaction.user.id, None)
			return await interaction.response.send_message("Wager must be at least 1 coin", ephemeral=True)

		# Fetch user from database
		user = await self.db.get_user(interaction.user.id, interaction.user.display_name)

		# Check balance
		if user["balance"] < wager:
			self.active_games.pop(interaction.user.id, None)
			return await interaction.response.send_message(
				f"Not enough coins, balance: {user['balance']:,}", ephemeral=True
			)

		await interaction.response.defer(thinking=True)

		# Create shoe and hands
		shoe = Shoe(DECKS)
		dealer_cards = []
		player_cards = []

		# Initial deal (2 cards each)
		player_cards = await self.hit(player_cards, shoe)
		dealer_cards = await self.hit(dealer_cards, shoe)
		player_cards = await self.hit(player_cards, shoe)
		dealer_cards = await self.hit(dealer_cards, shoe)

		dealer_value = self.cards_value(dealer_cards)
		player_value = self.cards_value(player_cards)

		# Send initial embed
		embed = self.build_embed(dealer_cards, dealer_value, player_cards, player_value, hide_dealer=True)
		msg = await interaction.followup.send(embed=embed)

		# Create interactive buttons
		view = BlackjackView(self, interaction, shoe, dealer_cards, player_cards, wager, msg)
		await msg.edit(view=view)

		# Wait for player to finish turn
		await view.wait()

		# PLAYER BUST
		if self.cards_value(view.player_cards) > 21:
			await self.db.update_balance(interaction.user.id, -wager)
			await self.db.record_game(interaction.user.id, "blackjack", False)

			final = self.build_embed(
				view.dealer_cards,
				self.cards_value(view.dealer_cards),
				view.player_cards,
				self.cards_value(view.player_cards)
			)
			final.title = f"💀 Bust! You lost {wager:,} {COIN_EMOJI}"
			final.color = discord.Color.red()

			for child in view.children:
				child.disabled = True

			self.active_games.pop(interaction.user.id, None)
			return await msg.edit(embed=final, view=view)

		# DEALER TURN — dealer hits until 17+
		while self.cards_value(view.dealer_cards) < 17:
			view.dealer_cards = await self.hit(view.dealer_cards, shoe)

		dealer_value = self.cards_value(view.dealer_cards)
		player_value = self.cards_value(view.player_cards)

		# Determine winner
		if dealer_value > 21:
			won = True
		elif dealer_value < player_value:
			won = True
		elif dealer_value > player_value:
			won = False
		else:
			won = None  # Push

		# Payout logic
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

		# Build final embed
		final = self.build_embed(view.dealer_cards, dealer_value, view.player_cards, player_value)
		final.title = title
		final.color = color
		final.set_footer(text=f"New balance: {new_balance:,} coins")

		# Disable buttons
		for child in view.children:
			child.disabled = True

		# Remove anti-spam lock
		self.active_games.pop(interaction.user.id, None)

		await msg.edit(embed=final, view=view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Blackjack(bot, bot.db))
