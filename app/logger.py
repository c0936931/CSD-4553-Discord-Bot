import logging
import asyncio


class DiscordLogHandler(logging.Handler):
	def __init__(self, bot, channel_id, level=logging.INFO):
		super().__init__(level)
		self.bot = bot
		self.channel_id = channel_id
		self.channel = None

	async def _ensure_channel(self):
		await self.bot.wait_until_ready()
		self.channel = self.bot.get_channel(self.channel_id)

	async def _send(self, message):
		if self.channel is None:
			await self._ensure_channel()

		if self.channel:
			await self.channel.send(f"```{message}```")

	def emit(self, record):
		try:
			# Determine source label
			if record.name.startswith("discord"):
				source = "DISCORD.PY"
			elif record.name == "root":
				source = "ROOT"
			else:
				# For cogs or custom modules
				source = record.name.upper()

			log_entry = f"[{source}] {self.format(record)}"
			asyncio.create_task(self._send(log_entry))

		except Exception as e:
			print("Logging error:", e)
