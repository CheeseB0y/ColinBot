# ColinBot
# John Wood

import atexit
from os import getenv
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from cogs import chatbot, gamba, econ, misc
from logging_config import logger


async def init_cogs(bot):
    await bot.add_cog(chatbot.Cog(bot))
    await bot.add_cog(gamba.Cog(bot))
    await bot.add_cog(econ.Cog(bot))
    await bot.add_cog(misc.Cog(bot))


def main():
    try:
        load_dotenv()
    except Exception as e:
        logger.critical(f"Unable to load environment variables: {e}")

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

    bot.run(discord_token)


if __name__ == "__main__":
    main()
