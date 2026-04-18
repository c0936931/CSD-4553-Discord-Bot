import logging
import discord  # noqa: F401


class DiscordLogHandler(logging.Handler):
	def __init__(self, bot, channel_id):
		super().__init__()
		self.bot = bot
		self.channel_id = channel_id

	async def send_log(self, record):
		channel = self.bot.get_channel(self.channel_id)
		if not channel:
			return

		level = record.levelname
		message = record.getMessage()

		formatted = (
			f"📝 **{level}** log entry:\n"
			f"```{message}```"
		)

		await channel.send(formatted)

	def emit(self, record):
		try:
			self.bot.loop.create_task(self.send_log(record))
		except RuntimeError:
			pass
