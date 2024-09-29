from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from functools import wraps
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone

load_dotenv()

uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client[os.getenv('MONGODB_DB')]
collection = db["users"]

def close():
    client.close()

def verify_user(func):
    @wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        user_data = get_user_data(ctx)
        if user_data is None:
            await add_user(ctx)
        return await func(ctx, *args, **kwargs)
    return wrapper

async def add_user(ctx):
    user_id = ctx.author.id
    username = ctx.author.name
    starting_points = 500
    document = {"user_id": user_id,
                "username": username,
                "points": starting_points,
                "daily_reset": datetime.now(timezone.utc)}
    collection.insert_one(document)
    async with ctx.typing():
        await ctx.send(f"New user detected. Welcome to the Colin Coin economy {username}! You start with {starting_points} Colin Coins. Come back in 24 hours for your daily allowance.")

def get_user_data(ctx):
    user_id = ctx.author.id
    user = {"user_id": user_id}
    return collection.find_one(user)

def get_points(ctx):
    return get_user_data(ctx).get("points")

def change_points(ctx, amount: int):
    user_id = ctx.author.id
    user = {"user_id": user_id}
    update = {"$inc": {"points": amount}}
    collection.update_one(user, update)

async def wager(ctx, bet: int, min_bet=10, max_bet=10000):
    async with ctx.typing():
        if get_points(ctx) >= bet and min_bet <= bet <= max_bet:
            await ctx.send(f"you have wagered {bet} Colin Coins, good luck!")
            return True
        else:
            await ctx.send(f"that is an invalid bet, you have {get_points(ctx)} Colin Coins. Minimum bet is {min_bet} Colin Coins, and max bet is {max_bet} Colin Coins.")
            return False

async def leaderboard(ctx):
    async with ctx.typing():
        top_users = collection.find().sort("points", -1).limit(10)
        leaderboard_message = "**Colin Coins Leaderboard**\n\n"
        rank = 1
        for user in top_users:
            username = user.get("username", "Unknown")
            points = user.get("points", 0)
            leaderboard_message += f"{rank}. {username}: {points} Colin Coins\n"
            rank += 1
        await ctx.send(leaderboard_message)

async def eligable_for_daily(ctx):
    if get_user_data(ctx).get("daily_reset").replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc) - timedelta(days=1):
        return True
    else:
        return False

async def time_remaining(ctx):
        async with ctx.typing():
            daily_reset = get_user_data(ctx).get("daily_reset")
            next_reset = daily_reset.replace(tzinfo=timezone.utc) + timedelta(days=1)
            time_remaining = next_reset - datetime.now(timezone.utc)
            if time_remaining.total_seconds() > 0:
                hours, remainder = divmod(time_remaining.seconds, 3600)
                minutes = remainder // 60
                await ctx.send(f"Your daily Colin Coin allowance is on cooldown, try again in {hours} hours, {minutes} minutes.")
            else:
                await ctx.send("You are eligable for your daily Colin Coin allowance! Please try again.")

@verify_user
async def send_points(ctx, amount: int, recipient):
    async with ctx.typing():
        if get_points(ctx) >= amount > 0:
            user_id = int(recipient.replace('<@', '').replace('>', ''))
            user = {"user_id": user_id}
            update = {"$inc": {"points": amount}}
            if collection.find_one(user) is None:
                await ctx.send(f"User user_id:{user_id} does not exist in the Colin Coin Economy.")
                return False
            change_points(ctx, -amount)
            collection.update_one(user, update)
            await ctx.send(f"{amount} Colin Coins has been sent to {recipient}")
            return True
        else:
            await ctx.send(f"{amount} is an invalid amount, you have {get_points(ctx)} Colin Coins.")
            return False

@verify_user
async def daily(ctx):
    daily_points = 100 
    if await eligable_for_daily(ctx):
        async with ctx.typing():
            change_points(ctx, daily_points)
            await ctx.send(f"{daily_points} Colin Coins have been added to your wallet.")
            await ctx.send(f"You now have {get_points(ctx)} Colin Coins.")
            user_id = ctx.author.id
            user = {"user_id": user_id}
            reset = {"$set": {"daily_reset": datetime.now(timezone.utc)}}
            collection.update_one(user, reset)
    else:
        await time_remaining(ctx)

@verify_user
async def coins(ctx):
    async with ctx.typing():
        await ctx.send(f"You have {get_points(ctx)} Colin Coins.")