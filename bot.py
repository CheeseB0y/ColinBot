"""
ColinBot: A multifunctional discord bot.
https://github.com/CheeseB0y/ColinBot
"""

import atexit
import sys
from os import getenv
from discord import Intents, LoginFailure
from discord.ext import commands
from dotenv import load_dotenv
from cogs import chatbot, gamba, econ, misc, music
from logging_config import logger


async def init_cogs(bot):
    """
    Attempt to initialize all colinbot cogs

    Args:
        bot: Discord bot object

    Returns:
        None
    """
    await bot.add_cog(chatbot.Cog(bot))
    await bot.add_cog(gamba.Cog(bot))
    await bot.add_cog(econ.Cog(bot))
    await bot.add_cog(misc.Cog(bot))
    await bot.add_cog(music.Cog(bot))


def main():
    """
    Main function

    Args:
        None

    Returns:
        None
    """
    load_dotenv()

    discord_token = str(getenv("DISCORD_TOKEN"))
    intents = Intents().all()
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        await init_cogs(bot)
        misc.on_startup()

    @bot.event
    async def on_message(message):
        if not message.mention_everyone:
            await chatbot.reply(message, bot)

    atexit.register(econ.close)
    atexit.register(misc.on_shutdown)

    try:
        bot.run(discord_token)
    except LoginFailure:
        logger.critical("Unable to find valid discord token, exiting program.")
        sys.exit(1)


if __name__ == "__main__":
    main()
