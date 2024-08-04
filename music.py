import yt_dlp
import asyncio
import discord

yt_dl_opts = {'format': 'bestaudio/best'}
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

class MusicQueue:
    def __init__(self):
        self.queue = []
        self.active = False
        self.playing = None
        self.pause = False

    def __str__(self):
        i = 0
        queue_str = ""
        for song in self.queue:
            i+=1
            queue_str = f"{queue_str}\n{i}: {song}"
        return queue_str

    def get_song(self):
        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0

    async def enqueue(self, song: Song, ctx):
        self.queue.append(song)
        await ctx.send("{song.title} has been added to the queue.")

    async def dequeue(self, ctx):
        if self.is_empty():
            await ctx.send("Queue is empty")
            return None
        song = self.queue.pop(0)
        return song
    
    async def clear(self, ctx):
        self.queue = []
        self.playing = None
        await ctx.send("Queue has been emptied.")
    
    async def handle_queue(self, ctx):
        self.active = True
        client = await get_client(ctx)
        while (not self.is_empty()):
            song = await self.dequeue(ctx)
            self.playing = song
            player = discord.FFmpegPCMAudio(song.stream, **ffmpeg_options, executable="bin/ffmpeg.exe")
            await ctx.send(f"Now playing: {song.title}")
            client.play(player)
            while (client.is_playing() or self.pause):
                await asyncio.sleep(1)
        self.active = False
        self.playing = None

queue = MusicQueue()

async def get_client(ctx):
    if (not ctx.voice_client):
        return await join(ctx)
    else:
        return ctx.guild.voice_client
        
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        return await channel.connect()
    else:
        await ctx.send("User is not in a voice channel.")

async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
    else:
        ctx.send("ColinBot is not currently in a voice channel.")

async def play(ctx, url: str):
    song = Song(url)
    if (ctx.author.voice):
        await queue.enqueue(song, ctx)
        if (not queue.active):
            await queue.handle_queue(ctx)

async def pause(ctx):
    client = await get_client(ctx)
    queue.pause = True
    client.pause()

async def resume(ctx):
    client = await get_client(ctx)
    queue.pause = False
    client.resume()

async def stop(ctx):
    client = await get_client(ctx)
    await queue.clear(ctx)
    client.stop()
    await leave(ctx)

async def skip(ctx):
    client = await get_client(ctx)
    client.stop()

async def playing(ctx):
    await ctx.send(queue.playing)

async def print_queue(ctx):
    await ctx.send(queue)