import yt_dlp as youtube_dl
import asyncio
import discord

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)
ffmpeg_options = {'options': "-vn"}

class Song:
    def __init__(self, url):
        self.url = url
        self.info = self.get_video_info(url)
        self.title = self.info.get('title')
        self.author = self.info.get('uploader')
        self.duration = self.info.get('duration')
        
    def get_video_info(self, url):
        with youtube_dl.YoutubeDL(yt_dl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
        return info_dict

class MusicQueue:
    def __init__(self):
        self.queue = []
        self.active = False

    async def enqueue(self, song: Song, ctx):
        self.queue.append(song)
        await ctx.send(song.title + " has been added to the queue.")

    async def dequeue(self, ctx):
        if self.is_empty():
            await ctx.send("Queue is empty")
            return None
        song = self.queue.pop(0)
        await ctx.send(song.title + " has been removed from the queue.")
        return song

    def get_song(self):
        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0
    
    async def handle_queue(self, ctx):
        self.active = True
        client = await get_client(ctx)
        loop = asyncio.get_event_loop()
        while (not self.is_empty()):
            song = await self.dequeue(ctx)
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(song.url, download=False))
            player = discord.FFmpegPCMAudio(data['url'], **ffmpeg_options, executable="bin/ffmpeg.exe")
            await ctx.send("Now playing: " + song.title)
            client.play(player)
            while client.is_playing():
                await asyncio.sleep(1)
        self.active = False

queue = MusicQueue()

async def get_client(ctx):
    try:
        if (not ctx.voice_client):
            return await join(ctx)
        else:
            return ctx.guild.voice_client
    except Exception as err:
        print(err)
        
async def join(ctx):
    try:
        if (ctx.author.voice):
            channel = ctx.message.author.voice.channel
            return await channel.connect()
        else:
            await ctx.send("User is not in a voice channel.")
    except Exception as err:
        print(err)

async def leave(ctx):
    try:
        if (ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
        else:
            ctx.send("ColinBot is not currently in a voice channel.")
    except Exception as err:
        print(err)

async def play(ctx, url: str):
    try:
        song = Song(url)
        await queue.enqueue(song, ctx)
        if (not queue.active):
            await queue.handle_queue(ctx)
    except Exception as err:
        print(err)

async def pause(ctx):
    try:
        client = await get_client(ctx)
        client.pause()
    except Exception as err:
        print (err)

async def resume(ctx):
    try:
        client = await get_client(ctx)
        client.resume()
    except Exception as err:
        print (err)

async def stop(ctx):
    try:
        client = await get_client(ctx)
        client.stop()
        await leave(ctx)
    except Exception as err:
        print(err)

async def skip(ctx):
    try:
        client = await get_client(ctx)
        client.stop()
    except Exception as err:
        print(err)