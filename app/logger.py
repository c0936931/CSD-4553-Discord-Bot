import logging
import asyncio
import time

DISCORD_LIMIT = 2000
BATCH_MAX_CHARS = 1500  # flush when batch reaches this size
BATCH_MAX_AGE = 60  # flush every 60 seconds


class DiscordLogHandler(logging.Handler):
    def __init__(self, bot, channel_id, level=logging.INFO):
        super().__init__(level)
        self.bot = bot
        self.channel_id = channel_id
        self.channel = None

        # Buffers
        self.ready = False
        self.startup_buffer = []  # logs before bot ready
        self.batch = []  # logs after ready
        self.batch_size = 0
        self.last_flush = time.time()

        # Start periodic flush task
        asyncio.create_task(self._periodic_flush())

    async def _ensure_channel(self):
        await self.bot.wait_until_ready()
        self.channel = self.bot.get_channel(self.channel_id)
        self.ready = True

        # Start periodic flush task only once
        if not hasattr(self, "_flush_task_started"):
            self._flush_task_started = True
            asyncio.create_task(self._periodic_flush())

        # Flush startup logs
        if self.startup_buffer:
            for msg in self.startup_buffer:
                await self._send_immediately(msg)
            self.startup_buffer.clear()

    async def _periodic_flush(self):
        """Flush batch every minute."""
        await self.bot.wait_until_ready()
        while True:
            await asyncio.sleep(5)
            if self.ready and (time.time() - self.last_flush >= BATCH_MAX_AGE):
                await self._flush_batch()

    async def _flush_batch(self):
        if not self.batch:
            return

        combined = "\n".join(self.batch)
        self.batch.clear()
        self.batch_size = 0
        self.last_flush = time.time()

        await self._send_immediately(combined)

    async def _send_immediately(self, message):
        if self.channel is None:
            await self._ensure_channel()

        if not self.channel:
            return

        # Split long messages
        for chunk in self._chunk_message(message):
            await self.channel.send(f"```{chunk}```")

    def _chunk_message(self, message):
        max_len = DISCORD_LIMIT - 10
        if len(message) <= max_len:
            return [message]

        chunks = []
        start = 0
        while start < len(message):
            end = start + max_len
            newline = message.rfind("\n", start, end)
            if newline != -1 and newline > start:
                end = newline
            chunks.append(message[start:end])
            start = end
        return chunks

    def emit(self, record):
        try:
            # Determine source label
            if record.name.startswith("discord"):
                source = "DISCORD.PY"
            elif record.name == "root":
                source = "ROOT"
            else:
                source = record.name.upper()

            log_entry = f"[{source}] {self.format(record)}"

            # If bot not ready, store in startup buffer
            if not self.ready:
                self.startup_buffer.append(log_entry)
                return

            # Add to batch
            self.batch.append(log_entry)
            self.batch_size += len(log_entry)

            # Flush if batch too large
            if self.batch_size >= BATCH_MAX_CHARS:
                asyncio.create_task(self._flush_batch())

        except Exception as e:
            print("Logging error:", e)
