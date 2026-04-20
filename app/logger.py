import logging
import asyncio


class DiscordLogHandler(logging.Handler):
	def __init__(self, bot, channel_id, level=logging.INFO):
		super().__init__(level)
		self.bot = bot
		self.channel_id = channel_id
		self.channel = None

	async def _send(self, message):
		if self.channel is None:
			self.channel = self.bot.get_channel(self.channel_id)
		if self.channel:
			await self.channel.send(f"```{message}```")

	def emit(self, record):
		log_entry = self.format(record)
		asyncio.create_task(self._send(log_entry))
