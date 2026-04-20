import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import Database
import logging
# from logger import DiscordLogHandler

load_dotenv()


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


# Validate required env
def require_env(key: str) -> str:
	value = os.getenv(key)
	if value is None or value.strip() == "":
		logging.error(f"Missing required environment variable: {key}")

	return value


async def load_extensions(bot: commands.Bot) -> None:
	for extension in EXTENSIONS:
		try:
			await bot.load_extension(extension)
		except Exception as e:
			print(f"Failed to load extension {extension}: {e}")


def main():
	# Validate required environment variables
	MONGO_URI = str(require_env("MONGO_URI"))
	DISCORD_TOKEN = str(require_env("DISCORD_TOKEN"))

	# Optional - If missing skip logging
	LOG_CHANNEL = os.getenv("LOG_CHANNEL")
	CHANNEL_LOG_LEVEL = os.getenv("CHANNEL_LOG_LEVEL", "INFO").upper()

	if LOG_CHANNEL:
		LOG_CHANNEL = int(LOG_CHANNEL)
		CHANNEL_LOG_LEVEL = getattr(logging, CHANNEL_LOG_LEVEL, logging.INFO)

	# Bot setup
	intents = discord.Intents.default()
	bot = commands.Bot(command_prefix="!", intents=intents)

	# Add db to bot
	db = Database(MONGO_URI)
	bot.db = db

	@bot.event
	async def on_ready():
		await bot.tree.sync()
		print(f"Bot initialized as: {bot.user}")

		# # Attach after bot ready
		# if LOG_CHANNEL:
		# 	discord_handler = DiscordLogHandler(
		# 		bot=bot,
		# 		channel_id=LOG_CHANNEL,
		# 		level=CHANNEL_LOG_LEVEL
		# 	)

		# 	formatter = logging.Formatter("[%(levelname)s] %(message)s")
		# 	discord_handler.setFormatter(formatter)

		# 	logging.getLogger().addHandler(discord_handler)

		# 	logging.debug("Discord logging handler attached!")

		# logging.info("Bot online")

	async def setup_hook():
		await load_extensions(bot)

	bot.setup_hook = setup_hook

	bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
	main()
