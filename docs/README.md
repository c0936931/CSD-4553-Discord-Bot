# Discord Currency & Minigame Bot

[![Deploy python app](https://github.com/c0936931/CSD-4553-Discord-Bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/c0936931/CSD-4553-Discord-Bot/actions/workflows/deploy.yml)

A Discord bot with slash commands, minigames, and persistent coin balances stored in MongoDB Atlas. Runs in Docker.

## Features

- `/stats` — view your full stats (balance, games played, win/loss ratios)
- `/rankings` — top 10 richest users
- `/coinflip` — wager coins on a coin flip
- `/trivia` — answer a trivia question to earn coins (reward scales with difficulty)
- `/dice` — guess a dice roll (1-6) for a 5x payout
- `/blackjack` — play a game of blackjack to earn coins
- `/rps` — play rock paper scissors to earn coins
- `/joke` — get a random joke
- `/cheat` — add coins to yourself (admin)

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
LOG_CHANNEL=channel_id_to_log_to        # optional
CHANNEL_LOG_LEVEL=log_level_to_channel  # optional, defaults to INFO
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

## Project Structure

```
app/
├── main.py                  # entry point, loads all cogs
├── db.py                    # all database logic
├── configs.py               # shared constants (rewards, emojis, API URLs)
└── cogs/
    ├── economy/             # commands pertaining to economy
    │   ├── cheat.py
    │   ├── rankings.py      # /rankings  ← best file to read first
    │   └── stats.py
    └── games/               # commands pertaining to minigames
        ├── blackjack.py
        ├── cards_hanlder.py # shared card deck logic for blackjack
        ├── coinflip.py
        ├── diceroll.py
        ├── joke.py
        ├── rps.py
        └── trivia.py
```

---

## License

Open source, available for educational purposes.
