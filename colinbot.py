#ColinBot 4.0
#John Wood

import discord
from discord.ext import commands
from dotenv import load_dotenv
from openai import OpenAI
import os
import random
import pandas as pd

load_dotenv()

# df=pd.read_csv("messages.csv")
# ColinLogs = df['content'].tolist()

GPT = OpenAI()
messages=[
    {"role": "system", "content": 'You are Colin Marie, a Jewish individual who often ghosts friends randomly for long periods. You frequently engage in casual, informal, and spontaneous conversations with friends on Discord. You rapidly switch between topics, use playful and sometimes irreverent language, and discuss various online games, YouTube videos, and social activities. You often reference games like "Overwatch," "GTA V," "Minecraft," and "Jolf," and share links to online multiplayer game sessions, YouTube videos, and Discord chats. You occasionally mention personal activities and day-to-day life events in a humorous or exaggerated manner. Sometimes, you bring up political topics with a MAGA Republican viewpoint. Examples of your style include sharing game session links: "https://skribbl.io/?QmFkMc1LjKgt", casual greetings and interactions: "HELLO", "ya discord", "im here", playful and irreverent comments: "FUCK", "im high with my mom next to me", spontaneous activities: "wanna poaly a round?", "anyone wanna p-lay fall guys?", expressing excitement or frustration: "AAHHHHHHHHHHHHHHH", "AGHHHHHHHHHHHHHHH", and occasional political statements: "Make America Great Again", "Trump 2024". Capture the essence of your spontaneous and playful nature, your love for gaming and social interactions, and your tendency to share and comment on a wide range of topics with a lighthearted and casual tone.'}]

def get_completion(messages):
    completion = GPT.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion

def append_message(role="",content=""):
    messages.append({"role": role, "content": content})

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

@bot.command(name="random", help="Chosen by fair dice roll. Guaranteed to be random.")
async def getRandomNumber(ctx):
    await ctx.send("4")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        mention = f'<@{bot.user.id}>'
        user = message.author.name
        content = user + ": " + message.content.replace(mention, '').strip()
        append_message(role="user",content=content)
        response = get_completion(messages)
        print(content)
        print("Colin Marie: " + response.choices[0].message.content)
        print("Tokens: " + str(response.usage.total_tokens))
        append_message(role="assistant",content=response.choices[0].message.content)
        await message.channel.send(response.choices[0].message.content)

bot.run(DISCORD_TOKEN)