#ColinBot 3.0
#John Wood

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

load_dotenv()

DISCORD_TOKEN = str(os.getenv('DISCORD_TOKEN'))

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("Bot is online!")
    
@bot.command(name="ping", help="This command returns the latency")
async def ping(ctx):
    await ctx.send(f"Latency: {round(bot.latency * 1000)}ms")

@bot.command(name="colin", help="Post a random picture of Colin Marie")
async def colin(ctx):
    pictures = []
    for filepath in os.listdir("pictures/colin/"):
        pictures.append("pictures/colin/" + filepath)
    randomColin = random.randint(0, len(pictures) - 1)
    await ctx.send(file=discord.File(pictures[randomColin]))

@bot.command(name="ninja", help="Post epic quote from fortnite ninja")
async def ninja(ctx):
    await ctx.send("The phrase “it's just a game” is such a weak mindset. You are ok with what happened, losing, imperfection of a craft. When you stop getting angry after losing, you've lost twice.\n\nThere's always something to learn, and always room for improvement, never settle.")

@bot.command(name="random", help="chosen by fair dice roll. guaranteed to be random.")
async def getRandomNumber(ctx):
    await ctx.send("4")

bot.run(DISCORD_TOKEN)