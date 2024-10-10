import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

class StreamToLogger(object):
    """
    Custom class to redirect sys.stdout or sys.stderr to a logger.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, message):
        if message.rstrip():  # Avoid logging empty messages
            # Send stderr messages to ERROR level, everything else to INFO
            if self.log_level == logging.ERROR and "[INFO    ]" in message:
                self.logger.log(logging.INFO, message.rstrip())  # Fix for Discord INFO messages showing as ERROR
            else:
                self.logger.log(self.log_level, message.rstrip())

    def flush(self):
        pass  # Flush is required, but we don't need it to do anything

# Create a 'logs' folder if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create a logger
logger = logging.getLogger('colinbot')

# Create a TimedRotatingFileHandler that rotates the log file daily and keeps 30 days of logs
log_file_handler = TimedRotatingFileHandler('logs/bot.log', when='midnight', interval=1, backupCount=30, encoding='utf-8')
log_file_handler.setLevel(logging.INFO)

# Define the format for log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file_handler.setFormatter(formatter)

# Also log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(log_file_handler)
logger.addHandler(console_handler)

# Set the logging level for the logger
logger.setLevel(logging.INFO)

# Redirect stdout (print statements) to the logger
sys.stdout = StreamToLogger(logger, logging.INFO)

# Redirect stderr (error prints) to the logger as errors
sys.stderr = StreamToLogger(logger, logging.ERROR)