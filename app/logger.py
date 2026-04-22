import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = "bot.log"


def setup_file_logger(level=logging.INFO):
	log_dir = os.path.dirname(LOG_FILE)
	if log_dir and not os.path.exists(log_dir):
		os.makedirs(log_dir)

	root_logger = logging.getLogger()

	# Avoid duplicate handlers
	if any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
		return LOG_FILE

	handler = RotatingFileHandler(
		LOG_FILE,
		maxBytes=2_000_000,   # 2 MB
		encoding="utf-8"
	)

	formatter = logging.Formatter(
		"[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
	)
	handler.setFormatter(formatter)

	root_logger.setLevel(level)
	root_logger.addHandler(handler)

	return LOG_FILE
