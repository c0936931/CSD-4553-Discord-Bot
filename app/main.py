import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import Database

load_dotenv()

# Each entry here is the module path to a cog file (relative to the app/ folder).
# To add a new command:
#   1. Create a new file in cogs/economy/ or cogs/games/ following the pattern (see rankings.py for a documented command)
#   2. Add its path to this list (e.g. "cogs.economy.mycommand")
#   3. Restart the bot, it will load automatically
EXTENSIONS = [
    "cogs.economy.balance",
    "cogs.economy.stats",
    "cogs.economy.rankings",
    "cogs.games.coinflip",
    "cogs.games.trivia",
]


async def load_extensions(bot: commands.Bot) -> None:
    for extension in EXTENSIONS:
        await bot.load_extension(extension)


def main():
    intents = discord.Intents.default()

    db = Database(os.getenv("MONGO_URI"))
    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.db = db  # attach db to bot so cogs can access it via bot.db

    @bot.event
    async def on_ready():
        # sync registers slash commands with Discord globally
        await bot.tree.sync()
        print(f"Bot initialized as: {bot.user}")

    # setup_hook runs before the bot connects, so cogs are ready before on_ready fires
    async def setup_hook():
        await load_extensions(bot)

    bot.setup_hook = setup_hook

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
