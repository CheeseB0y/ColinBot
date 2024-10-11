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
from logging_config import logger

def main():
    
    try:
        load_dotenv()
    except Exception as e:
        logger.critical(f"Unable to load environment variables: {e}")

    DISCORD_TOKEN = str(os.getenv('DISCORD_TOKEN'))
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        misc.on_startup()
    @bot.event
    async def on_message(message):
        await chatbot.reply(message, bot)
    @bot.command(name="thoughts", help="Review the past x messages and give thoughts on the conversation.")
    async def thoughts(ctx, x=None):
        await chatbot.thoughts(ctx, x)
    @bot.command(name="tts", help="Text to speech chatbot response.")
    async def tts(ctx):
        await chatbot.tts(ctx)
    @bot.command(name="ping", help="Latency")
    async def ping(ctx):
        await misc.ping(ctx, bot)
    @bot.command(name="colin", help="Random picture of Colin Marie")
    async def colin(ctx):
        await misc.colin(ctx)
    @bot.command(name="ninja", help="Post the epic quote from fortnite ninja")
    async def ninja(ctx):
        await misc.ninja(ctx)
    @bot.command(name="random", help="Chosen by fair dice roll. Guaranteed to be random.")
    async def get_random_number(ctx):
        await misc.get_random_number(ctx)
    @bot.command(name="waifu", help="Random waifu from waifu.api.")
    async def waifu(ctx):
        await misc.waifu(ctx)
    @bot.command(name="blackjack", help="Blackjack game, bet with Colin Coins.")
    async def blackjack(ctx, bet=None):
        await gamba.blackjack(ctx, bet)  
    @bot.command(name="bj", help="Short for blackjack.")
    async def bj(ctx, bet=None):
        await gamba.blackjack(ctx, bet)
    @bot.command(name="blowjob", help="Long for bj.")
    async def blowjob(ctx, bet=None):
        await gamba.blackjack(ctx, bet)
    @bot.command(name="slots", help="Slot machine game, bet with Colin Coins.")
    async def slots(ctx, bet=None):
        await gamba.slots(ctx, bet)
    @bot.command(name="sluts", help="Short for slots.")
    async def sluts(ctx, bet=None):
        await gamba.slots(ctx, bet)
    @bot.command(name="payout", help="Sends payout amounts for slots game.")
    async def payout(ctx):
        await gamba.payout(ctx)
    @bot.command(name="daily", help="Daily colin coin allowence, resets after 24 hours.")
    async def daily(ctx):
        await econ.daily(ctx)
    @bot.command(name="send", help="Send Colin Coins to another user.")
    async def send(ctx, amount=None, recipient=None):
        await econ.send_points(ctx, amount, recipient)
    @bot.command(name="coins", help="Check your Colin Coin Balance")
    async def coins(ctx):
        await econ.coins(ctx)
    @bot.command(name="leaderboard", help="Colin Coin leaderboard, who has the most coins?")
    async def leaderboard(ctx):
        await econ.leaderboard(ctx)
    @bot.command(name="join", help="Join the current voice channel.")
    async def join(ctx):
        await music.join(ctx)
    @bot.command(name="leave", help="Leave the current voice channel.")
    async def leave(ctx):
        await music.leave(ctx)
    @bot.command(name="play", help="Play a song from a youtube link.")
    async def play(ctx, url=None):
        await music.play(ctx, url)
    @bot.command(name="pause", help="Pause music playback.")
    async def pause(ctx):
        await music.pause(ctx)
    @bot.command(name="resume", help="Resume music playback.")
    async def resume(ctx):
        await music.resume(ctx)
    @bot.command(name="stop", help="End music playback")
    async def stop(ctx):
        await music.stop(ctx)
    @bot.command(name="skip", help="Skip current song in queue.")
    async def skip(ctx):
        await music.skip(ctx)
    @bot.command(name="playing", help="Now playing.")
    async def playing(ctx):
        await music.playing(ctx)
    @bot.command(name="queue", help="Music queue.")
    async def queue(ctx):
        await music.queue(ctx)

    atexit.register(econ.close)
    atexit.register(misc.on_shutdown)
    
    bot.run(DISCORD_TOKEN)

if __name__ =="__main__":
    main()