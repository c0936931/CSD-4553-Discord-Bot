import discord
from discord import app_commands
from discord.ext import commands
import random


# All playable fantasy creatures
CREATURES = {
    "Fire Dragon": {
        "emoji": "🔥🐉",
        "hp": 120,
        "attack": 25,
        "defense": 8,
        "special": 45,
        "element": "Fire",
        "class": "Dragon",
        "rarity": "Rare",
        "special_name": "Fire Blast",
        "description": "A powerful dragon with strong fire attacks."
    },

    "Cyber Snake": {
        "emoji": "🐍⚡",
        "hp": 105,
        "attack": 32,
        "defense": 6,
        "special": 50,
        "element": "Electric Poison",
        "class": "Snake",
        "rarity": "Epic",
        "special_name": "Electric Venom",
        "description": "A futuristic snake that shocks and poisons enemies."
    },

    "Fox Shapeshifter": {
        "emoji": "🦊✨",
        "hp": 115,
        "attack": 24,
        "defense": 9,
        "special": 42,
        "element": "Magic",
        "class": "Shapeshifter",
        "rarity": "Epic",
        "special_name": "Form Shift",
        "description": "A magical fox that can transform during battle."
    },

    "Crystal Unicorn": {
        "emoji": "🦄💎",
        "hp": 125,
        "attack": 20,
        "defense": 10,
        "special": 40,
        "element": "Crystal Light",
        "class": "Magic Beast",
        "rarity": "Rare",
        "special_name": "Healing Light",
        "description": "A unicorn that heals itself and damages enemies."
    },

    "Shadow Wolf": {
        "emoji": "🐺🌑",
        "hp": 110,
        "attack": 30,
        "defense": 7,
        "special": 48,
        "element": "Shadow",
        "class": "Animal Warrior",
        "rarity": "Rare",
        "special_name": "Dark Bite",
        "description": "A dark wolf with fast and dangerous attacks."
    },

    "Phoenix": {
        "emoji": "🔥🕊️",
        "hp": 115,
        "attack": 26,
        "defense": 8,
        "special": 44,
        "element": "Flame",
        "class": "Legendary Bird",
        "rarity": "Legendary",
        "special_name": "Rebirth Flame",
        "description": "A fire bird that can recover health while attacking."
    },

    "Robot Griffin": {
        "emoji": "🤖🦅",
        "hp": 130,
        "attack": 23,
        "defense": 12,
        "special": 43,
        "element": "Metal",
        "class": "Futuristic Beast",
        "rarity": "Epic",
        "special_name": "Laser Claw",
        "description": "A robotic griffin with strong metal defense."
    },

    "Venom Scorpion": {
        "emoji": "🦂☠️",
        "hp": 100,
        "attack": 34,
        "defense": 5,
        "special": 52,
        "element": "Poison",
        "class": "Poison Beast",
        "rarity": "Rare",
        "special_name": "Toxic Sting",
        "description": "A poisonous scorpion with deadly sting attacks."
    }
}


class BeastSelect(discord.ui.Select):
    def __init__(self):
        options = []

        for creature_name, creature_data in CREATURES.items():
            options.append(
                discord.SelectOption(
                    label=creature_name,
                    description=f"{creature_data['class']} | {creature_data['rarity']}",
                    emoji=creature_data["emoji"]
                )
            )

        super().__init__(
            placeholder="Choose your mythic beast...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_creature = self.values[0]

        enemy_creature = random.choice(
            [creature for creature in CREATURES.keys() if creature != selected_creature]
        )

        view = BeastBattleView(
            player=interaction.user,
            player_creature=selected_creature,
            enemy_creature=enemy_creature
        )

        embed = view.create_battle_embed("⚔️ The battle has started!")

        await interaction.response.edit_message(embed=embed, view=view)


class BeastChooseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BeastSelect())


class BeastBattleView(discord.ui.View):
    def __init__(self, player, player_creature, enemy_creature):
        super().__init__(timeout=120)

        self.player = player

        self.player_creature = player_creature
        self.enemy_creature = enemy_creature

        self.player_hp = CREATURES[player_creature]["hp"]
        self.enemy_hp = CREATURES[enemy_creature]["hp"]

        self.defending = False

    def create_battle_embed(self, message):
        player_data = CREATURES[self.player_creature]
        enemy_data = CREATURES[self.enemy_creature]

        embed = discord.Embed(
            title="🧬 Mythic Beast Arena",
            description=message,
            color=discord.Color.purple()
        )

        embed.add_field(
            name=f"{player_data['emoji']} Your Beast",
            value=(
                f"**{self.player_creature}**\n"
                f"Class: `{player_data['class']}`\n"
                f"Element: `{player_data['element']}`\n"
                f"HP: `{max(self.player_hp, 0)}`"
            ),
            inline=True
        )

        embed.add_field(
            name=f"{enemy_data['emoji']} Enemy Beast",
            value=(
                f"**{self.enemy_creature}**\n"
                f"Class: `{enemy_data['class']}`\n"
                f"Element: `{enemy_data['element']}`\n"
                f"HP: `{max(self.enemy_hp, 0)}`"
            ),
            inline=True
        )

        embed.set_footer(text="Use the buttons below to fight.")

        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.player:
            await interaction.response.send_message(
                "This is not your battle.",
                ephemeral=True
            )
            return False

        return True

    def enemy_attack(self):
        enemy_data = CREATURES[self.enemy_creature]

        enemy_damage = random.randint(
            enemy_data["attack"] - 7,
            enemy_data["attack"] + 7
        )

        if self.defending:
            enemy_damage = enemy_damage // 2
            self.defending = False

        self.player_hp -= enemy_damage

        return enemy_damage

    def check_winner(self):
        if self.player_hp <= 0:
            return "enemy"

        if self.enemy_hp <= 0:
            return "player"

        return None

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Attack", emoji="⚔️", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player_data = CREATURES[self.player_creature]

        damage = random.randint(
            player_data["attack"] - 5,
            player_data["attack"] + 5
        )

        self.enemy_hp -= damage

        winner = self.check_winner()

        if winner == "player":
            self.disable_buttons()
            embed = self.create_battle_embed(
                f"⚔️ You attacked and dealt `{damage}` damage!\n\n🏆 You won the battle!"
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return

        enemy_damage = self.enemy_attack()

        winner = self.check_winner()

        if winner == "enemy":
            self.disable_buttons()
            embed = self.create_battle_embed(
                f"⚔️ You dealt `{damage}` damage.\n"
                f"The enemy dealt `{enemy_damage}` damage.\n\n💀 You lost the battle."
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return

        embed = self.create_battle_embed(
            f"⚔️ You attacked and dealt `{damage}` damage.\n"
            f"The enemy attacked and dealt `{enemy_damage}` damage."
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Defend", emoji="🛡️", style=discord.ButtonStyle.primary)
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.defending = True

        enemy_damage = self.enemy_attack()

        winner = self.check_winner()

        if winner == "enemy":
            self.disable_buttons()
            embed = self.create_battle_embed(
                f"🛡️ You defended, but the enemy still dealt `{enemy_damage}` damage.\n\n💀 You lost the battle."
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return

        embed = self.create_battle_embed(
            f"🛡️ You defended!\n"
            f"The enemy damage was reduced to `{enemy_damage}`."
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Special Power", emoji="✨", style=discord.ButtonStyle.success)
    async def special_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player_data = CREATURES[self.player_creature]

        special_name = player_data["special_name"]

        # Shapeshifter gets a special random transformation
        if player_data["class"] == "Shapeshifter":
            form = random.choice([
                "Dragon Form",
                "Wolf Form",
                "Snake Form",
                "Shadow Form",
                "Healing Form"
            ])

            if form == "Dragon Form":
                damage = random.randint(38, 55)
                self.enemy_hp -= damage
                action_message = f"🦊✨ `{special_name}` activated!\nIt changed into **Dragon Form** and dealt `{damage}` damage."

            elif form == "Wolf Form":
                damage = random.randint(30, 45)
                self.enemy_hp -= damage
                action_message = f"🦊✨ `{special_name}` activated!\nIt changed into **Wolf Form** and dealt `{damage}` damage."

            elif form == "Snake Form":
                damage = random.randint(25, 40)
                poison_damage = 10
                total_damage = damage + poison_damage
                self.enemy_hp -= total_damage
                action_message = f"🦊✨ `{special_name}` activated!\nIt changed into **Snake Form** and dealt `{total_damage}` poison damage."

            elif form == "Shadow Form":
                damage = random.randint(25, 35)
                self.enemy_hp -= damage
                self.defending = True
                action_message = f"🦊✨ `{special_name}` activated!\nIt changed into **Shadow Form**, dealt `{damage}` damage, and prepared defense."

            else:
                heal = random.randint(15, 25)
                damage = random.randint(20, 30)
                self.player_hp += heal
                self.enemy_hp -= damage
                action_message = f"🦊✨ `{special_name}` activated!\nIt changed into **Healing Form**, healed `{heal}` HP, and dealt `{damage}` damage."

        # Unicorn heals and attacks
        elif self.player_creature == "Crystal Unicorn":
            heal = random.randint(15, 25)
            damage = random.randint(25, player_data["special"])

            self.player_hp += heal
            self.enemy_hp -= damage

            action_message = (
                f"🦄💎 `{special_name}` activated!\n"
                f"You healed `{heal}` HP and dealt `{damage}` damage."
            )

        # Phoenix heals and attacks
        elif self.player_creature == "Phoenix":
            heal = random.randint(10, 22)
            damage = random.randint(28, player_data["special"])

            self.player_hp += heal
            self.enemy_hp -= damage

            action_message = (
                f"🔥🕊️ `{special_name}` activated!\n"
                f"You restored `{heal}` HP and dealt `{damage}` fire damage."
            )

        # Cyber Snake does poison damage
        elif self.player_creature == "Cyber Snake":
            damage = random.randint(30, player_data["special"])
            poison_damage = random.randint(8, 15)

            total_damage = damage + poison_damage
            self.enemy_hp -= total_damage

            action_message = (
                f"🐍⚡ `{special_name}` activated!\n"
                f"You dealt `{damage}` electric damage and `{poison_damage}` poison damage."
            )

        # Venom Scorpion does toxic damage
        elif self.player_creature == "Venom Scorpion":
            damage = random.randint(30, player_data["special"])
            toxic_damage = random.randint(10, 18)

            total_damage = damage + toxic_damage
            self.enemy_hp -= total_damage

            action_message = (
                f"🦂☠️ `{special_name}` activated!\n"
                f"You dealt `{damage}` sting damage and `{toxic_damage}` toxic damage."
            )

        # Normal special attack for other creatures
        else:
            hit_chance = random.randint(1, 100)

            if hit_chance <= 75:
                damage = random.randint(
                    player_data["special"] - 10,
                    player_data["special"] + 10
                )

                self.enemy_hp -= damage

                action_message = (
                    f"✨ `{special_name}` hit successfully!\n"
                    f"You dealt `{damage}` special damage."
                )
            else:
                action_message = f"✨ `{special_name}` missed!"

        winner = self.check_winner()

        if winner == "player":
            self.disable_buttons()
            embed = self.create_battle_embed(
                f"{action_message}\n\n🏆 You won the battle!"
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return

        enemy_damage = self.enemy_attack()

        winner = self.check_winner()

        if winner == "enemy":
            self.disable_buttons()
            embed = self.create_battle_embed(
                f"{action_message}\n"
                f"The enemy dealt `{enemy_damage}` damage.\n\n💀 You lost the battle."
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return

        embed = self.create_battle_embed(
            f"{action_message}\n"
            f"The enemy attacked and dealt `{enemy_damage}` damage."
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Surrender", emoji="🏳️", style=discord.ButtonStyle.secondary)
    async def surrender_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.disable_buttons()

        embed = self.create_battle_embed(
            "🏳️ You surrendered the battle."
        )

        await interaction.response.edit_message(embed=embed, view=self)


class BeastWar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="beastwar",
        description="Choose a mythic beast and fight in the arena"
    )
    async def beastwar(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🧬 Mythic Beast Arena",
            description=(
                "Choose your fantasy creature and enter the arena.\n\n"
                "You can choose dragons, snakes, shapeshifters, unicorns, wolves, phoenixes, and more."
            ),
            color=discord.Color.purple()
        )

        for creature_name, creature_data in CREATURES.items():
            embed.add_field(
                name=f"{creature_data['emoji']} {creature_name}",
                value=(
                    f"Class: `{creature_data['class']}`\n"
                    f"Element: `{creature_data['element']}`\n"
                    f"Rarity: `{creature_data['rarity']}`\n"
                    f"Special: `{creature_data['special_name']}`"
                ),
                inline=False
            )

        view = BeastChooseView()

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(BeastWar(bot))
