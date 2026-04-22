import motor.motor_asyncio
from datetime import datetime, timezone, timedelta

# Database wraps all MongoDB operations. Import and use it inside your cog via self.db
# Methods:
#   get_user(user_id, username)        — fetch a user, creates them if they don't exist yet
#   get_stats(user_id)                 — same as get_user but returns None if not found
#   get_rankings()                     — top 10 users sorted by balance
#   update_balance(user_id, amount)    — add or subtract coins (pass negative to subtract)
#   record_game(user_id, game, won)    — log a game result, increments games_played
#   is_on_cooldown(user_id, cmd, dur)  — returns remaining timedelta if on cooldown, else None
#   set_cooldown(user_id, cmd)         — stamp the current time as last used for a command


class Database:
	def __init__(self, uri: str) -> None:
		client = motor.motor_asyncio.AsyncIOMotorClient(uri)
		self.users = client["currency-bot"]["users"]

	async def get_user(self, user_id: int, username: str | None = None) -> dict:
		"""Fetch a user document or create a default one"""
		user = await self.users.find_one({"_id": str(user_id)})
		if not user:
			user = {
				"_id": str(user_id),
				"username": username or "Unknown",
				"balance": 0,
				"total_earned": 0,
				"games_played": 0,
				"coinflip": {"wins": 0, "losses": 0},
				"trivia": {"wins": 0, "losses": 0},
				"dice": {"wins": 0, "losses": 0},
				"cooldowns": {},
			}
			await self.users.insert_one(user)
		return user

	async def update_balance(self, user_id: int, amount: int) -> None:
		"""Add or subtract coins, tracks total_earned for positive amounts only"""
		# max(0, amount) ensures losses don't reduce total_earned
		await self.users.update_one(
			{"_id": str(user_id)},
			{"$inc": {"balance": amount, "total_earned": max(0, amount)}},
		)

	async def is_on_cooldown(
		self, user_id: int, command: str, duration: timedelta
	) -> timedelta | None:
		"""Returns remaining cooldown if active, None if not on cooldown"""
		user = await self.users.find_one(
			{"_id": str(user_id)}, {f"cooldowns.{command}": 1}
		)
		if not user:
			return None
		last_used = user.get("cooldowns", {}).get(command)
		if not last_used:
			return None
		# Motor returns naive datetimes from MongoDB, so we attach UTC if missing
		if last_used.tzinfo is None:
			last_used = last_used.replace(tzinfo=timezone.utc)
		remaining = duration - (datetime.now(timezone.utc) - last_used)
		return remaining if remaining.total_seconds() > 0 else None

	async def set_cooldown(self, user_id: int, command: str) -> None:
		"""Use current time as the last used time for a command"""
		await self.users.update_one(
			{"_id": str(user_id)},
			{"$set": {f"cooldowns.{command}": datetime.now(timezone.utc)}},
		)

	async def get_rankings(self) -> list[dict]:
		"""Return top 10 users sorted by balance in desc order"""
		cursor = (
			self.users.find({}, {"username": 1, "balance": 1})
			.sort("balance", -1)
			.limit(10)
		)
		return await cursor.to_list(length=10)

	async def get_stats(self, user_id: int) -> dict | None:
		"""Return the full user document"""
		return await self.users.find_one({"_id": str(user_id)})

	async def record_game(self, user_id: int, game: str, won: bool) -> None:
		"""Increment games_played and the win or loss for games with w/l"""
		result_field = f"{game}.wins" if won else f"{game}.losses"
		await self.users.update_one(
			{"_id": str(user_id)},
			{"$inc": {"games_played": 1, result_field: 1}},
		)
