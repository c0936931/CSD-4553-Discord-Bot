# Discord Currency & Minigame Bot

A Discord bot with slash commands, minigames, and persistent coin balances stored in MongoDB Atlas. Runs in Docker.

## Features

- `/stats` — view your full stats (balance, games played, win/loss ratios)
- `/rankings` — top 10 richest users
- `/coinflip` — wager coins on a coin flip
- `/trivia` — answer a trivia question to earn coins (reward scales with difficulty)
- `/blackjack` — play a game of blackjack to earn coins
- `/joke` — get told a random joke

## Tech Stack

- [discord.py](https://discordpy.readthedocs.io/) — Python library for the Discord API
- [MongoDB Atlas](https://www.mongodb.com/atlas) — cloud database for storing user data
- [Docker](https://www.docker.com/) — runs the bot in a container so it works the same everywhere

---

## Setup

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) installed

### 1. Clone the repo

```bash
git clone <repo-url>
cd python-bot-currency
```

### 2. Create a `.env` file in the project root

```bash
DISCORD_TOKEN=your_token_here
MONGO_URI=your_mongo_uri_here
```

### 3. Start the bot

```bash
docker compose up --build
```

You should see `Bot initialized as: YourBotName#0000` in the terminal
To stop it, press `Ctrl+C`. To run it in the background, add `-d`

```bash
docker compose up --build -d
docker compose logs -f   # view logs while running in background
```

---

## Project Structure - Needs updating

```
app/
├── main.py              # entry point, loads all cogs
├── db.py                # all database logic
├── configs.py           # shared constants (rewards, emojis, API URLs)
└── cogs/
    ├── economy/         # commands pertaining to economy
    │   ├── stats.py
    │   └── rankings.py  # /rankings  ← best file to read first
    └── games/           # commands pertaining to minigames
        ├── coinflip.py
        └── trivia.py
```

---

## License

Open source, available for educational purposes.
