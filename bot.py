#ColinBot 4.2
#John Wood

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import music
import chatbot
import misc

def main():
    load_dotenv()

    DISCORD_TOKEN = str(os.getenv('DISCORD_TOKEN'))
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print("Bot is online!")

    @bot.event
    async def on_message(message):
        await chatbot.reply(message, bot)

    @bot.command(name="thoughts", help="This command will have colinbot review the past x messages and give his thoughts on the conversation.")
    async def thoughts(ctx, x: int):
        await chatbot.thoughts(ctx, x)

    @bot.command(name="ping", help="This command returns the latency")
    async def ping(ctx):
        await misc.ping(ctx, bot)

    @bot.command(name="colin", help="Post a random picture of Colin Marie")
    async def colin(ctx):
        await misc.colin(ctx)

    @bot.command(name="ninja", help="Post epic quote from fortnite ninja")
    async def ninja(ctx):
        await misc.ninja(ctx)

    @bot.command(name="random", help="Chosen by fair dice roll. Guaranteed to be random.")
    async def getRandomNumber(ctx):
        await misc.getRandomNumber(ctx)

    @bot.command(name="join", help="ColinBot will join the current voice channel the user who sent the command is in.")
    async def join(ctx):
        await music.join(ctx)

    @bot.command(name="leave", help="ColinBot will leave the voice channel.")
    async def leave(ctx):
        await music.leave(ctx)

    @bot.command(name="play", help="ColinBot will play a song from a youtube link.")
    async def play(ctx, url: str):
        await music.play(ctx, url)

    @bot.command(name="pause", help="")
    async def pause(ctx):
        await music.pause(ctx)

    @bot.command(name="resume", help="")
    async def resume(ctx):
        await music.resume(ctx)
    
    @bot.command(name="stop", help="")
    async def stop(ctx):
        await music.stop(ctx)

    @bot.command(name="skip", help="")
    async def skip(ctx):
        await music.skip(ctx)

    @bot.command(name="playing", help="")
    async def playing(ctx):
        await music.playing(ctx)

    @bot.command(name="queue", help="")
    async def queue(ctx):
        await music.queue(ctx)
    
    bot.run(DISCORD_TOKEN)

if __name__ =="__main__":
    main()