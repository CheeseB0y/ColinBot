"""
Econ cog

This cog handles all the Economy funcitonality for ColinBot.
"""

from os import getenv
from datetime import datetime, timedelta, timezone
from functools import wraps
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from discord.ext import commands
from logging_config import logger

try:
    load_dotenv()
except Exception as e:
    logger.critical(f"Unable to load environment variables: {e}")

try:
    uri = getenv("MONGODB_URI")
    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client[getenv("MONGODB_DB")]
    collection = db["users"]
    logger.info("MongoDB client connection has been established successfully.")
    MONGODB_CONNECTION_SUCCESS = True
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    MONGODB_CONNECTION_SUCCESS = False


def close():
    """
    Close connection to MongoDB

    Cleanly end connection to MongoDB on client stop.

    Args:
        None

    Returns:
        None
    """
    try:
        client.close()
        logger.info("MongoDB client connection has been closed successfully.")
    except Exception as e:
        logger.error(f"Failed to close MongoDB connection: {e}")


def verify_user(func):
    """Decorator to check if a user exists in the database or not."""

    @wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        user_data = get_user_data(ctx)
        if user_data is None:
            await add_user(ctx)
        return await func(ctx, *args, **kwargs)

    return wrapper


async def add_user(ctx):
    """
    Add a new user to the database

    Each database entry stores: user_id, username, points, and daily_reset.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info("New user detected, adding to Colin Coin database.")
    user_id = ctx.author.id
    username = ctx.author.name
    starting_points = 500
    document = {
        "user_id": user_id,
        "username": username,
        "points": starting_points,
        "daily_reset": datetime.now(timezone.utc),
    }
    try:
        collection.insert_one(document)
        logger.info(
            f"{username} user_id:{user_id} has been added to the Colin Coin database."
        )
    except Exception as e:
        logger.error(
            f"Unable to add {username} user_id:{user_id} to Colin Coin database: {e}"
        )
    async with ctx.typing():
        await ctx.send(
            f"New user detected. Welcome to the Colin Coin economy {username}! You start with {starting_points} Colin Coins. Come back in 24 hours for your daily allowance."
        )


def get_user_data(ctx):
    """
    Gets user data from MongoDB and returns it.

    Args:
        ctx: Discord context object.

    Returns:
        user data from MongoDB or None if none exists.
    """
    user_id = ctx.author.id
    user = {"user_id": user_id}
    try:
        return collection.find_one(user)
    except Exception as e:
        logger.error(f"Could not get user data: {e}")
        return None


def get_points(ctx):
    """
    Gets points value from user data in MongoDB.

    Args:
        ctx: Discord context object.

    Returns:
        Points value for user from MongoDB.
    """
    try:
        return get_user_data(ctx).get("points")
    except Exception as e:
        logger.error(f"Could not get points: {e}")
        return None


def change_points(ctx, amount: int):
    """
    Change points value for a user.

    Args:
        ctx: Discord context object.
        amount: Amount to increment users points (can be negative.)

    Returns:
        None
    """
    username = ctx.author.name
    user_id = ctx.author.id
    user = {"user_id": user_id}
    update = {"$inc": {"points": amount}}
    try:
        collection.update_one(user, update)
        logger.info(f"{username} had {amount} Colin Coins added to their account.")
    except Exception as e:
        logger.error(f"Could not adjust points for {username}: {e}")


async def wager(ctx, bet: int, min_bet=10, max_bet=10000):
    """
    Set an amount for a user to wager in a betting game.

    Args:
        ctx: Discord context object.
        bet: Amount to wager.
        min_bet: Minimum bet amount, 10 by default.
        max_bet: Maximum bet amount, 10000 by default.

    Returns:
        Success: True if successful wager, false if not.
    """
    username = ctx.author.name
    async with ctx.typing():
        if get_points(ctx) >= bet and min_bet <= bet <= max_bet:
            await ctx.send(f"You have wagered {bet} Colin Coins, good luck!")
            logger.info(f"{username} has wagered {bet} Colin Coins.")
            return True
        await ctx.send(
            f"That is an invalid bet, you have {get_points(ctx)} Colin Coins. Minimum bet is {min_bet} Colin Coins, and max bet is {max_bet} Colin Coins."
        )
        logger.warning(
            f"{username} attempted to wager an invalid amount ({bet}) minimum bet is {min_bet} Colin Coins, and max bet is {max_bet} Colin Coins."
        )
        return False


async def leaderboard(ctx):
    """
    Outputs a leaderboard to discord showing which users have the most points.

    Args:
        cts: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !leaderboard in {ctx.guild}")
    async with ctx.typing():
        top_users = collection.find().sort("points", -1).limit(10)
        leaderboard_message = "```\nColin Coins Leaderboard\n\n"
        rank = 1
        for user in top_users:
            username = user.get("username", "Unknown")
            points = user.get("points", 0)
            leaderboard_message += f"{rank}. {username}: {points} Colin Coins\n"
            rank += 1
        leaderboard_message += "```"
        await ctx.send(leaderboard_message)


async def eligable_for_daily(ctx):
    """
    Checks if a user is eligible for their daily check in points.

    Args:
        ctx: Discord context object.

    Returns:
        True if their daily cooldown is up, false if not.
    """
    return get_user_data(ctx).get("daily_reset").replace(
        tzinfo=timezone.utc
    ) <= datetime.now(timezone.utc) - timedelta(days=1)


async def time_remaining(ctx):
    """
    Checks how much time is left until a users daily check in points are avalible.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    async with ctx.typing():
        daily_reset = get_user_data(ctx).get("daily_reset")
        next_reset = daily_reset.replace(tzinfo=timezone.utc) + timedelta(days=1)
        remaining = next_reset - datetime.now(timezone.utc)
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes = remainder // 60
            await ctx.send(
                f"Your daily Colin Coin allowance is on cooldown, try again in {hours} hours, {minutes} minutes."
            )
        else:
            await ctx.send(
                "You are eligable for your daily Colin Coin allowance! Please try again."
            )


@verify_user
async def send_points(ctx, amount, recipient):
    """
    Sends points from one user to another.

    Args:
        ctx: Discord context object.
        amount: Amount of points to send.
        recipient: User to send points to, parsed from discord @ mention.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !send in {ctx.guild}")
    async with ctx.typing():
        if amount is None or recipient is None:
            await ctx.send(
                "You must provide an amount and a recipient in that order, try again."
            )
            logger.warning(
                f"User {ctx.author.name} in {ctx.guild} attempted to call !send without providing an amount and/or recipient."
            )
            return False
        if get_points(ctx) >= amount > 0:
            user_id = int(recipient.replace("<@", "").replace(">", ""))
            user = {"user_id": user_id}
            update = {"$inc": {"points": amount}}
            if collection.find_one(user) is None:
                await ctx.send(
                    f"User user_id:{user_id} does not exist in the Colin Coin Economy."
                )
                return False
            change_points(ctx, -amount)
            collection.update_one(user, update)
            await ctx.send(f"{amount} Colin Coins has been sent to {recipient}")
            return True
        await ctx.send(
            f"{amount} is an invalid amount, you have {get_points(ctx)} Colin Coins."
        )
        logger.warning(
            f"User {ctx.author.name} in {ctx.guild} attempted to send an invalid amount of Colin Coins to another user."
        )
        return False


@verify_user
async def daily(ctx, points=100):
    """
    Daily check in command, grants a user a certain number of points per day.

    Args:
        ctx: Discord context object.
        points: Amount of points a user earns for daily check in, 100 by default.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !daily in {ctx.guild}")
    daily_points = points
    username = ctx.author.name
    user_id = ctx.author.id
    if await eligable_for_daily(ctx):
        async with ctx.typing():
            change_points(ctx, daily_points)
            await ctx.send(
                f"{daily_points} Colin Coins have been added to your wallet."
            )
            await ctx.send(f"You now have {get_points(ctx)} Colin Coins.")
            user = {"user_id": user_id}
            try:
                reset = {"$set": {"daily_reset": datetime.now(timezone.utc)}}
            except Exception as e:
                logger.error(f"Unable to update daily_reset timer: {e}")
            collection.update_one(user, reset)
            logger.info(f"{username} has claimed their daily.")
    else:
        await time_remaining(ctx)
        logger.warning(
            f"{username} tried to claim their daily but it is still on cooldown."
        )


@verify_user
async def coins(ctx):
    """
    Tells the user how many points they currently have.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !coins in {ctx.guild}")
    async with ctx.typing():
        num_coins = get_points(ctx)
        logger.info(f"{ctx.author.name} has {num_coins} Colin Coins")
        await ctx.send(f"You have {num_coins} Colin Coins.")


class Cog(commands.Cog, name="econ"):
    """
    Cog class

    For initalizing all the economy cog functions.

    Attributes:
        bot: Discord bot object.
    """

    def __init__(self, bot):
        if MONGODB_CONNECTION_SUCCESS:
            try:
                self.bot = bot
                logger.info("Econ cog successfully initialized.")
            except Exception as e:
                logger.error(f"Unable to initialize econ cog: {e}")
        else:
            logger.warning("Econ cog was not initalized.")

    @commands.command(
        name="daily", help="Daily colin coin allowence, resets after 24 hours."
    )
    async def daily(self, ctx):
        """Init daily command"""
        await daily(ctx)

    @commands.command(name="send", help="Send Colin Coins to another user.")
    async def send(self, ctx, amount: int = None, recipient: str = None):
        """Init send command"""
        await send_points(ctx, amount, recipient)

    @commands.command(name="coins", help="Check your Colin Coin Balance")
    async def coins(self, ctx):
        """Init coins command"""
        await coins(ctx)

    @commands.command(
        name="leaderboard", help="Colin Coin leaderboard, who has the most coins?"
    )
    async def leaderboard(self, ctx):
        """Init leaderboard command"""
        await leaderboard(ctx)
