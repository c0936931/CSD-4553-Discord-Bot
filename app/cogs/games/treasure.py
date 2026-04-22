import random
import discord
from discord.ext import commands
from discord import app_commands
from db import Database


class TreasureView(discord.ui.View):
    """
    Button view for the treasure hunt game.
    """

    def __init__(self, author_id: int, db: Database):
        super().__init__(timeout=30)
        self.author_id = author_id
        self.db = db
        self.played = False

    async def disable_buttons(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True

        await interaction.message.edit(view=self)

    async def handle_choice(
        self,
        interaction: discord.Interaction,
        location: str
    ):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This treasure hunt is not yours.",
                ephemeral=True
            )
            return

        if self.played:
            await interaction.response.send_message(
                "You already picked a location.",
                ephemeral=True
            )
            return

        self.played = True
        await interaction.response.defer()
        await self.disable_buttons(interaction)

        outcome = random.randint(1, 100)

        if outcome <= 45:
            reward = random.randint(80, 250)

            await self.db.update_balance(interaction.user.id, reward)
            await self.db.record_game(interaction.user.id, "treasure", True)

            result = f"You searched the **{location}** and found **{reward} coins**!"
            color = discord.Color.green()

        elif outcome <= 75:
            await self.db.record_game(interaction.user.id, "treasure", False)

            result = f"You searched the **{location}**, but found nothing."
            color = discord.Color.yellow()

        else:
            loss = random.randint(30, 100)

            await self.db.update_balance(interaction.user.id, -loss)
            await self.db.record_game(interaction.user.id, "treasure", False)

            result = f"You searched the **{location}**, but fell into a trap and lost **{loss} coins**."
            color = discord.Color.red()

        embed = discord.Embed(
            title="Treasure Hunt Result",
            description=result,
            color=color
        )

        await interaction.followup.send(embed=embed)

    @discord.ui.button(
        label="Forest",
        emoji="🌲",
        style=discord.ButtonStyle.green
    )
    async def forest(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.handle_choice(interaction, "Forest")

    @discord.ui.button(
        label="Cave",
        emoji="⛰️",
        style=discord.ButtonStyle.primary
    )
    async def cave(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.handle_choice(interaction, "Cave")

    @discord.ui.button(
        label="Shipwreck",
        emoji="🚢",
        style=discord.ButtonStyle.blurple
    )
    async def shipwreck(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.handle_choice(interaction, "Shipwreck")


class Treasure(commands.Cog):
    """
    Treasure hunt game where the user chooses a location and gets a random outcome.
    """

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot = bot
        self.db = db

    @app_commands.command(
        name="treasure",
        description="Go on a treasure hunt and try to find coins."
    )
    async def treasure(self, interaction: discord.Interaction):
        await interaction.response.defer()

        await self.db.get_user(
            interaction.user.id,
            interaction.user.display_name
        )

        embed = discord.Embed(
            title="Treasure Hunt",
            description=(
                "Choose one place to search.\n\n"
                "🌲 **Forest**\n"
                "⛰️ **Cave**\n"
                "🚢 **Shipwreck**"
            ),
            color=discord.Color.gold()
        )

        view = TreasureView(interaction.user.id, self.db)

        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Treasure(bot, bot.db))
