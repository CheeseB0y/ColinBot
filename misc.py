import os
import random
import discord

async def colin(ctx):
    pictures = []
    for filepath in os.listdir("pictures/colin/"):
        pictures.append(f"pictures/colin/{filepath}")
    randomColin = random.randint(0, len(pictures) - 1)
    await ctx.send(file=discord.File(pictures[randomColin]))

async def ninja(ctx):
    await ctx.send("The phrase “it's just a game” is such a weak mindset. You are ok with what happened, losing, imperfection of a craft. When you stop getting angry after losing, you've lost twice.\n\nThere's always something to learn, and always room for improvement, never settle.")

async def getRandomNumber(ctx):
    await ctx.send("4")