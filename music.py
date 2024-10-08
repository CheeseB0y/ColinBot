import yt_dlp
import asyncio
import discord
from urllib.parse import urlparse
from logging_config import logger

yt_dl_opts = {'format': 'bestaudio/best', 'cookiefile': '~/.yt-dlp-cookies.txt', 'noplaylist': True, }
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)
ffmpeg_options = {'options': "-vn"}

class Song:
    def __init__(self, query):
        self.query = query
        self.info = self.get_video_info()
        self.title = self.info.get('title')
        self.author = self.info.get('uploader')
        self.duration = self.info.get('duration')
        self.stream = self.info.get('url')

    def __str__(self):
        return f"Title: {self.title}\nUploader: {self.author}\nDuration: {self.duration}s"
        
    def get_video_info(self):
        try:
            with yt_dlp.YoutubeDL(yt_dl_opts) as ydl:
                if self.is_url():
                    info_dict = ydl.extract_info(self.query, download=False)
                else:
                    info_dict = ydl.extract_info(f"ytsearch:{self.query}", download=False)
            return info_dict
        except Exception as e:
            logger.error(f"Unable to get video info: {e}")

    def is_url(self) -> bool:
        parsed_url = urlparse(self.query)
        if parsed_url.scheme in ("http", "https") and parsed_url.netloc:
            return True
        else:
            return False
        
class Player:
    def __init__(self, ctx):
        self.queue = []
        self.active = False
        self.playing = None
        self.pause = False
        self.channel = ctx.author.voice.channel
        self.client = None
        self.guild = ctx.guild.id

    def __str__(self):
        i = 1
        queue_str = f"{i}: {self.playing.title} (Now Playing)"
        for song in self.queue:
            i+=1
            queue_str = f"{queue_str}\n{i}: {song.title}"
        return queue_str

    def is_empty(self):
        return len(self.queue) == 0

    async def enqueue(self, song: Song, ctx):
        async with ctx.typing():
            self.queue.append(song)
            await ctx.send(f"{song.title} has been added to the queue.")
        logger.info(f"{song.title} has been added to the queue in {ctx.guild}")

    async def dequeue(self, ctx):
        if self.is_empty():
            async with ctx.typing():
                await ctx.send("Queue is empty")
            return None
        song = self.queue.pop(0)
        logger.info(f"{song.title} has been removed from the queue in {ctx.guild}")
        return song
    
    async def clear(self, ctx):
        async with ctx.typing():
            self.queue = []
            self.playing = None
            self.active = False
            await ctx.send("Queue has been emptied.")
        logger.info(f"Queue has been emptied in {ctx.guild}")
    
    async def handle_queue(self, ctx):
        self.active = True
        while (not self.is_empty()):
            async with ctx.typing():
                song = await self.dequeue(ctx)
                self.playing = song
                player = discord.FFmpegPCMAudio(song.stream, **ffmpeg_options)
                await ctx.send(f"Now playing: {song.title}")
                self.client.play(player)
            while (self.client.is_playing() or self.pause):
                await asyncio.sleep(1)
        self.active = False
        self.playing = None

players = {}
        
async def join(ctx):
    logger.info(f"{ctx.author.name} called !join in {ctx.guild}")
    if (ctx.author.voice):
        players[ctx.guild.id] = Player(ctx)
        players[ctx.guild.id].client = await players[ctx.guild.id].channel.connect()
        logger.info(f"Joined voice channel in {ctx.guild}")
    else:
        async with ctx.typing():
            await ctx.send("User is not in a voice channel.")
        logger.warning(f"{ctx.author.name} attempted to call join but was not in a voice channel.")

async def leave(ctx):
    logger.info(f"{ctx.author.name} called !leave in {ctx.guild}")
    if (ctx.voice_client):
        if (players[ctx.guild.id].active):
            async with ctx.typing():
                await ctx.send("Cannot leave channel while queue is active. Try !stop instead.")
            logger.warning(f"{ctx.author.name} attempted to call leave while the queue was active.")
            return
        await players[ctx.guild.id].client.disconnect()
        del players[ctx.guild.id]
        logger.info(f"Left voice channel in {ctx.guild}")
    else:
        async with ctx.typing():
            await ctx.send("ColinBot is not currently in a voice channel.")
        logger.warning(f"{ctx.author.name} attempted to call leave while the bot was not in any voice channel.")

async def play(ctx, url: str):
    logger.info(f"{ctx.author.name} called !play in {ctx.guild}")
    song = Song(url)
    if (ctx.guild.id not in players):
        await join(ctx)
    await players[ctx.guild.id].enqueue(song, ctx)
    if (not players[ctx.guild.id].active):
        await players[ctx.guild.id].handle_queue(ctx)

async def pause(ctx):
    logger.info(f"{ctx.author.name} called !pause in {ctx.guild}")
    players[ctx.guild.id].pause = True
    players[ctx.guild.id].client.pause()
    logger.info(f"Player has been paused in {ctx.guild}")

async def resume(ctx):
    logger.info(f"{ctx.author.name} called !resume in {ctx.guild}")
    players[ctx.guild.id].pause = False
    await players[ctx.guild.id].client.resume()
    logger.info(f"Player has been resumed in {ctx.guild}")

async def stop(ctx):
    logger.info(f"{ctx.author.name} called !stop in {ctx.guild}")
    await players[ctx.guild.id].clear(ctx)
    players[ctx.guild.id].client.stop()
    await leave(ctx)
    logger.info(f"Player has been stopped in {ctx.guild}")

async def skip(ctx):
    logger.info(f"{ctx.author.name} called !skip in {ctx.guild}")
    await players[ctx.guild.id].client.stop()

async def playing(ctx):
    logger.info(f"{ctx.author.name} called !playing in {ctx.guild}")
    await ctx.send(players[ctx.guild.id].playing)

async def queue(ctx):
    logger.info(f"{ctx.author.name} called !queue in {ctx.guild}")
    await ctx.send(players[ctx.guild.id])