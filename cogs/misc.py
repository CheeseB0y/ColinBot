"""
Miscellaneous cog.

This cog handles all other miscellaneous ColinBot functions that don't fall into another category.
These functions include !colin !ping !ninja !random and !waifu.
Also handles startup and shutdown messages.
"""

import random
from io import BytesIO
from os import getenv
import boto3
import requests
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from logging_config import logger

load_dotenv()

try:
    s3 = boto3.resource(
        service_name="s3",
        region_name=getenv("AWS_REGION"),
        aws_access_key_id=getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
    )
    bucket = s3.Bucket(getenv("BUCKET_NAME"))
    pictures = [obj.key for obj in bucket.objects.filter(Prefix="img/colin/")]
    logger.info("Sucessfully connected to S3 bucket.")
    S3_CONNECTION_SUCCESS = True
except Exception as e:
    logger.error(f"Unable to establish connection to S3 bucket: {e}")
    logger.warning(
        "S3 bucket connection not established, consider fixing this to access the !colin feature."
    )
    S3_CONNECTION_SUCCESS = False


def on_startup():
    """
    Startup message

    Args:
        None

    Returns:
        None
    """
    logger.info("ColinBot is online.")


def on_shutdown():
    """
    Shutdown message

    Args:
        None

    Returns:
        None
    """
    logger.info("ColinBot is offline.")


async def colin(ctx):
    """
    Colin function
    posts any random picture from an S3 bucket.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !colin in {ctx.guild}")
    async with ctx.typing():
        try:
            random_picture = random.choice(pictures)
            file = File(
                BytesIO(
                    s3.Object(getenv("BUCKET_NAME"), random_picture)
                    .get()["Body"]
                    .read()
                ),
                filename=random_picture.split("/")[-1],
            )
            await ctx.send(file=file)
            logger.info(f"Posted image: {random_picture}")
        except Exception as e:
            logger.error(f"Unable to post random Colin: {e}")


async def ping(ctx, bot):
    """
    Ping test command

    Args:
        ctx: Discord context object.
        bot: Discord bot object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !ping in {ctx.guild}")
    async with ctx.typing():
        latency = round(bot.latency * 1000)
        await ctx.send(f"Latency: {latency}ms")
    logger.info(f"Latency: {latency}ms")


async def ninja(ctx):
    """
    Ninja quote command

    posts an iconic tweet from fortnite ninja.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !ninja in {ctx.guild}")
    async with ctx.typing():
        await ctx.send(
            "The phrase “it's just a game” is such a weak mindset. You are ok with what happened, losing, imperfection of a craft. When you stop getting angry after losing, you've lost twice.\n\nThere's always something to learn, and always room for improvement, never settle."
        )


async def get_random_number(ctx):
    """
    Posts a "random" number (it's always 4)

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !random in {ctx.guild}")
    async with ctx.typing():
        await ctx.send("4")


async def waifu(ctx):
    """
    Random waifu command

    Posts a ranome waifu image from api.waifu.pics.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !waifu in {ctx.guild}")
    async with ctx.typing():
        try:
            response = requests.get("https://api.waifu.pics/sfw/waifu", timeout=10)
            data = response.json()
            logger.info(f"Waifu.pics API Response: {response.status_code} {data}")
        except Exception as e:
            logger.error(f"Unable to complete waifu request: {e}")
        try:
            await ctx.send(data["url"])
            logger.info("Random waifu has been posted successfully.")
        except Exception as e:
            logger.error(f"Unable to post random waifu: {e}")


class Cog(commands.Cog, name="misc"):
    """
    Cog class

    For initalizing all the miscellanious cog functions.

    Attributes:
        bot: Discord bot object.
    """

    def __init__(self, bot):
        try:
            self.bot = bot
            logger.info("Misc cog successfully initialized.")
        except Exception as e:
            logger.error(f"Unable to initialize misc cog: {e}")

    @commands.command(name="ping", help="Latency")
    async def ping(self, ctx):
        """Init ping command"""
        await ping(ctx, self.bot)

    if S3_CONNECTION_SUCCESS:

        @commands.command(name="colin", help="Random picture of Colin Marie")
        async def colin(self, ctx):
            """Init colin command"""
            await colin(ctx)
    else:
        logger.info("Colin command not initalized, no S3 bucket found.")

    @commands.command(name="ninja", help="Post the epic quote from fortnite ninja")
    async def ninja(self, ctx):
        """Init ninja command"""
        await ninja(ctx)

    @commands.command(
        name="random", help="Chosen by fair dice roll. Guaranteed to be random."
    )
    async def get_random_number(self, ctx):
        """Init random command"""
        await get_random_number(ctx)

    @commands.command(name="waifu", help="Random waifu from waifu.api.")
    async def waifu(self, ctx):
        """Init waifu command"""
        await waifu(ctx)
