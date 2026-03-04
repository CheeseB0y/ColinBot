import sqlite3
import atexit
import litellm
from logging_config import logger


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("colin.db")
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.cursor = self.conn.cursor()

        atexit.register(self.close)

    def init_tables(self):
        logger.info("Initializing database tables...")
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    guild_id TEXT,
                    role TEXT,
                    content TEXT,
                    tokens INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            logger.info("Database tables successfully initialized.")
        except Exception as e:
            logger.critical(f"Unable to initialize database tables: {e}")

    def insert_message(self, guild_id, role, content, model):
        token_count = litellm.token_counter(model=model, text=content)
        self.cursor.execute(
            "INSERT INTO messages (guild_id, role, content, tokens) VALUES (?, ?, ?, ?)",
            (str(guild_id), role, content, token_count),
        )
        self.conn.commit()
        logger.info(f"Saved message ({token_count} tokens) to history.")

    def pull_message_history(self):
        pass

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            logger.info("sqlite connection closed.")
