# Discord Currency & Minigame Bot

[![Deploy python app](https://github.com/c0936931/CSD-4553-Discord-Bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/c0936931/CSD-4553-Discord-Bot/actions/workflows/deploy.yml)

A Discord bot with slash commands, minigames, and persistent coin balances stored in MongoDB Atlas. Runs in Docker.

## Features
#### Admin
- `/cheat` — add coins to yourself (admin)
- `/downloadlogs` — get current log file

#### Economy
- `/rankings` — top 10 richest users
- `/stats` — view your full stats (balance, games played, win/loss ratios)

#### Games
- `/blackjack` — play a game of blackjack to earn coins
- `/coinflip` — wager coins on a coin flip
- `/dice` — guess a dice roll (1-6) for a 5x payout
- `/hangman` — play hangman game
- `/joke` — get a random joke
- `/rps` — play rock paper scissors to earn coins
- `/trivia` — answer a trivia question to earn coins (reward scales with difficulty)

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
LOG_FILE_LEVEL=log_level_here  # optional, defaults to INFO
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
├── configs.py               # shared constants (rewards, emojis, API URLs)
├── db.py                    # all database logic
├── logger.py                # logging setup to log to file
├── main.py                  # entry point, loads all cogs
└── cogs/
    ├───admin/               # commands related to admin
    │   ├── cheat.py
    │   ├── downloadlogs.py
    ├── economy/             # commands pertaining to economy
    │   ├── rankings.py      # /rankings  ← best file to read first
    │   └── stats.py
    └── games/               # commands pertaining to minigames
        ├── blackjack.py
        ├── casino.py
        ├── coinflip.py
        ├── diceroll.py
        ├── duel.py
        ├── hangman.py
        ├── joke.py
        ├── treasure.py
        ├── trivia.py
        ├── wheel.py
        └── work.py
```

---

## License

Open source, available for educational purposes.
