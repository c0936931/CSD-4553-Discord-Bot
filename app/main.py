import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

EXTENSIONS = [
    "cogs.economy",
    "cogs.games",
]


async def load_extensions(bot: commands.Bot):
    for extension in EXTENSIONS:
        await bot.load_extension(extension)


def main():
    intents = discord.Intents.default()

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        await bot.tree.sync()  # slash command functionality
        print(f"Bot initialized as: {bot.user}")

    # hook into bot before events, load our cogs
    async def setup_hook():
        await load_extensions(bot)

    bot.setup_hook = setup_hook

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
