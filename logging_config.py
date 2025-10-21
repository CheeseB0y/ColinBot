import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys


class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, message):
        if message.rstrip():
            if self.log_level == logging.ERROR and "[INFO    ]" in message:
                self.logger.log(logging.INFO, message.rstrip())
            else:
                self.logger.log(self.log_level, message.rstrip())

    def flush(self):
        pass


os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists("logs"):
    os.makedirs("logs")
logger = logging.getLogger("colinbot")
log_file_handler = TimedRotatingFileHandler(
    "logs/bot.log", when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
log_file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)
sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)
