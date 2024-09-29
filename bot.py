#ColinBot 4.3
#John Wood

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import atexit
import music
import chatbot
import gamba
import econ
import misc

def main():
    
    load_dotenv()

    DISCORD_TOKEN = str(os.getenv('DISCORD_TOKEN'))
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        misc.on_startup()

    @bot.event
    async def on_message(message):
        await chatbot.reply(message, bot)

    @bot.command(name="thoughts", help="This command will have colinbot review the past x messages and give his thoughts on the conversation.")
    async def thoughts(ctx, x: int):
        await chatbot.thoughts(ctx, x)

    @bot.command(name="tts", help="")
    async def tts(ctx):
        await chatbot.tts(ctx)

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
    async def get_random_number(ctx):
        await misc.get_random_number(ctx)

    @bot.command(name="waifu", help="")
    async def waifu(ctx):
        await misc.waifu(ctx)

    @bot.command(name="blackjack", help="")
    async def blackjack(ctx, bet: int):
        await gamba.blackjack(ctx, bet)
    
    @bot.command(name="bj", help="")
    async def bj(ctx, bet: int):
        await gamba.blackjack(ctx, bet)

    @bot.command(name="blowjob", help="")
    async def blowjob(ctx, bet: int):
        await gamba.blackjack(ctx, bet)

    @bot.command(name="slots", help="")
    async def slots(ctx, bet: int):
        await gamba.slots(ctx, bet)

    @bot.command(name="daily", help="")
    async def daily(ctx):
        await econ.daily(ctx)

    @bot.command(name="send", help="")
    async def send(ctx, amount: int, recipient):
        await econ.send_points(ctx, amount, recipient)

    @bot.command(name="coins", help="")
    async def coins(ctx):
        await econ.coins(ctx)

    @bot.command(name="leaderboard", help="")
    async def leaderboard(ctx):
        await econ.leaderboard(ctx)

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

    atexit.register(misc.on_shutdown)
    atexit.register(econ.close)
    
    bot.run(DISCORD_TOKEN)

if __name__ =="__main__":
    main()