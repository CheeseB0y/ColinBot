import yt_dlp
import asyncio
import discord

yt_dl_opts = {'format': 'bestaudio/best', 'cookiefile': '~/.yt-dlp-cookies.txt'}
ytdl = yt_dlp.YoutubeDL(yt_dl_opts)
ffmpeg_options = {'options': "-vn"}

class Song:
    def __init__(self, url):
        self.url = url
        self.info = self.get_video_info(url)
        self.title = self.info.get('title')
        self.author = self.info.get('uploader')
        self.duration = self.info.get('duration')
        self.stream = self.info.get('url')

    def __str__(self):
        return f"Title: {self.title}\nUploader: {self.author}\nDuration: {self.duration}s"
        
    def get_video_info(self, url):
        with yt_dlp.YoutubeDL(yt_dl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
        return info_dict

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

    async def dequeue(self, ctx):
        if self.is_empty():
            async with ctx.typing():
                await ctx.send("Queue is empty")
            return None
        song = self.queue.pop(0)
        return song
    
    async def clear(self, ctx):
        async with ctx.typing():
            self.queue = []
            self.playing = None
            self.active = False
            await ctx.send("Queue has been emptied.")
    
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
    if (ctx.author.voice):
        players[ctx.guild.id] = Player(ctx)
        players[ctx.guild.id].client = await players[ctx.guild.id].channel.connect()
    else:
        async with ctx.typing():
            await ctx.send("User is not in a voice channel.")

async def leave(ctx):
    if (players[ctx.guild.id].active):
        async with ctx.typing():
            await ctx.send("Cannot leave channel while queue is active. Try !stop instead.")
        return
    if (ctx.voice_client):
        await players[ctx.guild.id].client.disconnect()
        del players[ctx.guild.id]
    else:
        async with ctx.typing():
            ctx.send("ColinBot is not currently in a voice channel.")

async def play(ctx, url: str):
    song = Song(url)
    if (ctx.guild.id not in players):
        await join(ctx)
    await players[ctx.guild.id].enqueue(song, ctx)
    if (not players[ctx.guild.id].active):
        await players[ctx.guild.id].handle_queue(ctx)

async def pause(ctx):
    players[ctx.guild.id].pause = True
    players[ctx.guild.id].client.pause()

async def resume(ctx):
    players[ctx.guild.id].pause = False
    await players[ctx.guild.id].client.resume()

async def stop(ctx):
    await players[ctx.guild.id].clear(ctx)
    players[ctx.guild.id].client.stop()
    await leave(ctx)

async def skip(ctx):
    await players[ctx.guild.id].client.stop()

async def playing(ctx):
    await ctx.send(players[ctx.guild.id].playing)

async def queue(ctx):
    await ctx.send(players[ctx.guild.id])