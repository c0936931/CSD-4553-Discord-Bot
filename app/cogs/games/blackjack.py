import discord
from discord import app_commands
from discord.ext import commands
from db import Database
from configs import COIN_EMOJI
import random
import logging

DECKS = 6            # Number of decks in the shoe
DEAL_SPEED = 0.5     # Delay between card deals for animation

# Unicode based cards
cards = {
	"AS": "🂡", "2S": "🂢", "3S": "🂣", "4S": "🂤", "5S": "🂥", "6S": "🂦", "7S": "🂧", "8S": "🂨", "9S": "🂩", "0S": "🂪", "JS": "🂫", "QS": "🂭", "KS": "🂮",
	"AH": "🂱", "2H": "🂲", "3H": "🂳", "4H": "🂴", "5H": "🂵", "6H": "🂶", "7H": "🂷", "8H": "🂸", "9H": "🂹", "0H": "🂺", "JH": "🂻", "QH": "🂽", "KH": "🂾",
	"AC": "🃑", "2C": "🃒", "3C": "🃓", "4C": "🃔", "5C": "🃕", "6C": "🃖", "7C": "🃗", "8C": "🃘", "9C": "🃙", "0C": "🃚", "JC": "🃛", "QC": "🃝", "KC": "🃞",
	"AD": "🃁", "2D": "🃂", "3D": "🃃", "4D": "🃄", "5D": "🃅", "6D": "🃆", "7D": "🃇", "8D": "🃈", "9D": "🃉", "0D": "🃊", "JD": "🃋", "QD": "🃍", "KD": "🃎",
	"J": "🃏", "--": "🂠"}

# Card values and suits (0 is 10)
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "0", "J", "Q", "K"]
suits = ["H", "D", "S", "C"]


# Get card emoji
def get_card(card):
	if len(card) == 0:
		return ""
	else:
		try:
			return cards[card]
		except KeyError:
			logging.error("Error: card not supported")
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

	def draw(self):
		card = self.cards.pop()
		self.delt.append(card)
		return card


# View class (for buttons)
class BlackjackView(discord.ui.View):
	def __init__(self, cog, interaction, shoe, dealer_cards, player_cards, wager, msg):
		super().__init__(timeout=60)  # 60s timeout
		self.cog = cog
		self.interaction = interaction
		self.shoe = shoe
		self.dealer_cards = dealer_cards
		self.player_cards = player_cards
		self.wager = wager
		self.msg = msg

		# Get current values
		self.player_value = cog.cards_value(player_cards)
		self.dealer_value = cog.cards_value(dealer_cards)

		# To signal the main command when done
		self.finished = False

	# Update the embed
	async def update_embed(self):
		embed = self.cog.build_embed(
			self.dealer_cards,
			self.dealer_value,
			self.player_cards,
			self.player_value,
			hide_dealer=True
		)
		await self.msg.edit(embed=embed, view=self)

	# Hit button
	@discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
	async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		# Not your game
		if interaction.user.id != self.interaction.user.id:
			return await interaction.response.send_message("This is not your game.", ephemeral=True)

		# Deal card
		self.player_cards, self.player_value = self.cog.hit(self.player_cards, self.shoe)

		# Update embed
		await interaction.response.defer()
		await self.update_embed()

		# Check for bust or blackjack
		if self.player_value >= 21:
			self.disable_all()
			self.finished = True
			self.stop()

	# Stand button
	@discord.ui.button(label="Stand", style=discord.ButtonStyle.blurple)
	async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
		# Not your game
		if interaction.user.id != self.interaction.user.id:
			return await interaction.response.send_message("This is not your game.", ephemeral=True)

		await interaction.response.defer()

		# Return to main command
		self.disable_all()
		self.finished = True
		self.stop()

	# Handle timeout
	async def on_timeout(self):
		self.disable_all()
		try:
			await self.msg.edit(content="⏳ Game timed out.", view=self)
		except Exception:
			pass
		self.stop()

	# Disable buttons
	def disable_all(self):
		for child in self.children:
			child.disabled = True


# Main command
class Blackjack(commands.Cog):
	def __init__(self, bot: commands.Bot, db: Database) -> None:
		self.bot = bot
		self.db = db

		# Disctionary to prevent spam
		self.active_games = {}

	def build_embed(self, dealer_cards, dealer_value, player_cards, player_value, hide_dealer=False):
		# Hide dealer's first card
		if hide_dealer:
			shown_cards = ["--"] + dealer_cards[1:]
			dealer_value = self.cards_value(dealer_cards[1:])
		else:
			shown_cards = dealer_cards.copy()

		# Get emoji
		dealer_str = " ".join(get_card(c) for c in shown_cards)
		player_str = " ".join(get_card(c) for c in player_cards)

		# Create embed
		embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.dark_green())
		embed.add_field(name=f"Dealer ({dealer_value})", value=dealer_str or "No cards", inline=False)
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

	def hit(self, cards, shoe):
		# Get a card with deal speed
		cards.append(shoe.draw())

		# Return new hand + updated value
		return cards, self.cards_value(cards)

	@app_commands.command(description="Play Blackjack and wager coins")
	@app_commands.describe(wager="Amount of coins to wager")
	async def blackjack(self, interaction: discord.Interaction, wager: int) -> None:
		# Main command
		await interaction.response.defer(thinking=True)

		# Log command run
		logging.info("Command Run: /blackjack")

		# Anti-spam protection
		if interaction.user.id in self.active_games:
			return await interaction.followup.send_message(
				"You already have a blackjack game running. Finish it first.",
				ephemeral=True
			)

		# Mark user as active
		self.active_games[interaction.user.id] = True

		# Validate wager
		if wager <= 0:
			# Remove from active
			self.active_games.pop(interaction.user.id, None)
			# Post message
			return await interaction.followup.send_message("Wager must be at least 1 coin", ephemeral=True)

		# Fetch user data from database
		user = await self.db.get_user(interaction.user.id, interaction.user.display_name)

		# Check balance
		if user["balance"] < wager:
			# Remove from active
			self.active_games.pop(interaction.user.id, None)
			# Post message
			return await interaction.followup.send_message(
				f"Not enough coins, balance: {user['balance']:,}", ephemeral=True
			)

		# Create shoe and hands
		shoe = Shoe(DECKS)
		dealer_cards = []
		player_cards = []

		# Initial deal (2 cards each)
		player_cards, player_value = self.hit(player_cards, shoe)
		dealer_cards, dealer_value = self.hit(dealer_cards, shoe)
		player_cards, player_value = self.hit(player_cards, shoe)
		dealer_cards, dealer_value = self.hit(dealer_cards, shoe)

		# Send initial embed
		embed = self.build_embed(dealer_cards, dealer_value, player_cards, player_value, hide_dealer=True)
		msg = await interaction.followup.send(embed=embed)

		# Create interactive buttons
		view = BlackjackView(self, interaction, shoe, dealer_cards, player_cards, wager, msg)
		await msg.edit(view=view)

		# Wait for player to finish turn
		await view.wait()

		# Get player cards
		player_cards = view.player_cards
		player_value = self.cards_value(player_cards)

		# Dealer turn
		if player_value < 21:
			# Dealer hits until more than 16
			while dealer_value < 17:
				dealer_cards, dealer_value = self.hit(view.dealer_cards, shoe)

		# Determine winner
		if player_value == 21:
			won = True
			title = f"🃏 Blackjack! You won {wager:,} {COIN_EMOJI}"
		elif player_value > 21:
			won = False
			title = f"🃏 Bust! You lost {wager:,} {COIN_EMOJI}"
		elif dealer_value == 21:
			won = False
			title = f"🃏 Dealer Blackjack! You lost {wager:,} {COIN_EMOJI}"
		elif dealer_value > 21:
			won = True
			title = f"🃏 Dealer Bust! You won {wager:,} {COIN_EMOJI}"
		elif dealer_value < player_value:
			won = True
			title = f"🃏 Player Higher! You won {wager:,} {COIN_EMOJI}"
		elif dealer_value > player_value:
			won = False
			title = f"🃏 Dealer Higher! You lost {wager:,} {COIN_EMOJI}"
		else:
			won = None  # Push
			title = f"🃏 Push! Returned bet of {wager:,} {COIN_EMOJI}"

		# Payout logic
		if won is True:
			# Won
			await self.db.update_balance(interaction.user.id, wager)
			await self.db.record_game(interaction.user.id, "blackjack", True)
			new_balance = user["balance"] + wager
			color = discord.Color.green()
		elif won is False:
			# Lost
			await self.db.update_balance(interaction.user.id, -wager)
			await self.db.record_game(interaction.user.id, "blackjack", False)
			new_balance = user["balance"] - wager
			color = discord.Color.red()
		else:
			# Push
			new_balance = user["balance"]
			color = discord.Color.yellow()

		# Build final embed
		final = self.build_embed(dealer_cards, dealer_value, player_cards, player_value)
		final.title = title
		final.color = color
		final.set_footer(text=f"New balance: {new_balance:,} {COIN_EMOJI}")

		# Disable buttons
		for child in view.children:
			child.disabled = True

		# Remove anti-spam lock
		self.active_games.pop(interaction.user.id, None)

		# Post message
		await msg.edit(embed=final, view=view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Blackjack(bot, bot.db))
