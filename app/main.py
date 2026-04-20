import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import Database
import logging
from logger import DiscordLogHandler

load_dotenv()

# Validate required env
def require_env(key: str) -> str:
	value = os.getenv(key)
	if value is None or value.strip() == "":
		raise EnvironmentError(f"Missing required environment variable: {key}")
	return value


EXTENSIONS = [
	"cogs.economy.stats",
	"cogs.economy.rankings",
	"cogs.economy.cheat",
	"cogs.games.coinflip",
	"cogs.games.trivia",
	"cogs.games.joke",
	"cogs.games.blackjack",
	"cogs.games.rps",
]


async def load_extensions(bot: commands.Bot) -> None:
	for extension in EXTENSIONS:
		try:
			await bot.load_extension(extension)
		except Exception as e:
			print(f"Failed to load extension {extension}: {e}")


def main():
	# Validate required environment variables
	MONGO_URI = require_env("MONGO_URI")
	DISCORD_TOKEN = require_env("DISCORD_TOKEN")

	# Optional - If missing skip logging
	LOG_CHANNEL = os.getenv("LOG_CHANNEL")
	LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
	LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.ERROR)

	intents = discord.Intents.default()

	db = Database(MONGO_URI)
	bot = commands.Bot(command_prefix="!", intents=intents)
	bot.db = db

	@bot.event
	async def on_ready():
		await bot.tree.sync()
		print(f"Bot initialized as: {bot.user}")

	async def setup_hook():
		await load_extensions(bot)

		# Only attach Discord logging if LOG_CHANNEL is set
		if LOG_CHANNEL:
			handler = DiscordLogHandler(bot, LOG_CHANNEL)
			handler.setLevel(logging.ERROR)

			logger = logging.getLogger("discord")
			logger.setLevel(logging.ERROR)
			logger.addHandler(handler)
		else:
			print("LOG_CHANNEL not set — Discord logging disabled.")

	bot.setup_hook = setup_hook

	bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
	main()
