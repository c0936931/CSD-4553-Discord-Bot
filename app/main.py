import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import Database
import logging

from logger import DiscordLogHandler

load_dotenv()

# Each entry here is the module path to a cog file (relative to the app/ folder).
# To add a new command:
#   1. Create a new file in cogs/economy/ or cogs/games/ following the pattern (see rankings.py for a documented command)
#   2. Add its path to this list (e.g. "cogs.economy.mycommand")
#   3. Restart the bot, it will load automatically
EXTENSIONS = [
    "cogs.economy.stats",
    "cogs.economy.rankings",
    "cogs.economy.cheat",
    "cogs.games.coinflip",
    "cogs.games.trivia",
    "cogs.games.joke",
    "cogs.games.blackjack",
    "cogs.games.rps",
    "cogs.games.diceroll",
    "cogs.games.hangman",
]


# Validate required env
def require_env(key: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise EnvironmentError(f"Missing required environment variable: {key}")

    return value


async def load_extensions(bot: commands.Bot) -> None:
    for extension in EXTENSIONS:
        # Try to load extensions
        try:
            await bot.load_extension(extension)
        except Exception as e:
            logging.warning(f"Failed to load extension {extension}: {e}")


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
    intents.guilds = True  # needed for logging
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Add db to bot
    db = Database(MONGO_URI)
    bot.db = db  # attach db to bot so cogs can access it via bot.db

    if LOG_CHANNEL:
    	# Set root log level
    	logging.getLogger().setLevel(logging.DEBUG)

    	discord_handler = DiscordLogHandler(
    		bot=bot,
    		channel_id=LOG_CHANNEL,
    		level=CHANNEL_LOG_LEVEL
    	)

    	formatter = logging.Formatter("[%(levelname)s] %(message)s")
    	discord_handler.setFormatter(formatter)

    	# Attach to root logger (your logs)
    	root_logger = logging.getLogger()
    	root_logger.addHandler(discord_handler)

    	# Attach to discord.py logger (internal logs)
    	discord_logger = logging.getLogger("discord")
    	discord_logger.addHandler(discord_handler)
    	discord_logger.setLevel(logging.INFO)

    	logging.debug("Discord logging handler attached!")

    @bot.event
    async def on_ready():
        await bot.tree.sync()
        print(f"Bot initialized as: {bot.user}")

        logging.info("Bot online")

    # setup_hook runs before the bot connects, so cogs are ready before on_ready fires
    async def setup_hook():
        await load_extensions(bot)

    bot.setup_hook = setup_hook

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
