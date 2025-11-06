"""
Music cog

This cog handles all the music funcitonality for ColinBot.
"""

import asyncio
import os
import random
from discord import FFmpegPCMAudio
from discord.ext import commands
from logging_config import logger

MUSIC_PATH = "music/"
FFMPEG_OPTIONS = {"options": "-vn"}


class Song:
    """
    Song class for playing music via FFMPEG.

    Attributes:
        file: Path to music file as a string.
        title: Song title pulled from file name.
        file_type: file extension from file name.
    """

    def __init__(self, file_path):
        self.file = file_path
        name, ext = os.path.splitext(os.path.basename(file_path))
        self.title = name
        self.file_type = ext

    def __str__(self):
        return f"{self.title}"


class Player:
    """
    Player class for playing and managing music.

    Attributes:
        queue: List of song objects to be played in order.
        active: Bool; true if a song is currently playing.
        playing: Curringly playing song object.
        pause: Bool; true if music player is currently paused.
        channel: Voice channel discord object.
        guild: Discord guild ID.
    """

    def __init__(self, ctx):
        self.queue = []
        self.active = False
        self.playing = None
        self.pause = False
        self.channel = ctx.author.voice.channel
        self.guild = ctx.guild.id

    def __str__(self):
        i = 1
        queue_str = f"{i}: {self.playing.title} (Now Playing)"
        for song in self.queue:
            i += 1
            queue_str = f"{queue_str}\n{i}: {song.title}"
        return queue_str

    def is_empty(self):
        """
        Check if the queue is empty.

        Args:
            None

        Returns:
            True if queue is empty.
        """
        return len(self.queue) == 0

    async def enqueue(self, song: Song, ctx):
        """
        Add a song to the queue.

        Args:
            song: Song object.
            ctx: Discord context object.

        Returns:
            None
        """
        async with ctx.typing():
            self.queue.append(song)
            await ctx.send(f"{song.title} has been added to the queue.")
        logger.info(f"{song.title} has been added to the queue in {ctx.guild}")

    async def dequeue(self, ctx):
        """
        Removes the next song from the queue.

        Args:
            ctx: Discord context object.

        Returns:
            song: song object removed from the queue.
        """
        if self.is_empty():
            async with ctx.typing():
                await ctx.send("Queue is empty")
            return None
        song = self.queue.pop(0)
        logger.info(f"{song.title} has been removed from the queue in {ctx.guild}")
        return song

    async def clear(self, ctx):
        """
        Empty the entire queue.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        async with ctx.typing():
            self.queue = []
            self.playing = None
            self.active = False
            await ctx.send("Queue has been emptied.")
        logger.info(f"Queue has been emptied in {ctx.guild}")

    async def handle_queue(self, ctx):
        """
        Queue handler, ensures that songs start and stop cleanly.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        self.active = True
        while not self.is_empty():
            async with ctx.typing():
                song = await self.dequeue(ctx)
                self.playing = song
                FFmpegPCMAudio(song.file, **FFMPEG_OPTIONS)
                await ctx.send(f"Now playing: {song.title}")
            while self.pause:
                await asyncio.sleep(1)
        self.active = False
        self.playing = None


players = {}


async def join(ctx):
    """
    Joins the discord voice channel that the user is currently in.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !join in {ctx.guild}")
    if ctx.author.voice:
        players[ctx.guild.id] = Player(ctx)
        players[ctx.guild.id].client = await players[ctx.guild.id].channel.connect()
        logger.info(f"Joined voice channel in {ctx.guild}")
    else:
        async with ctx.typing():
            await ctx.send("User is not in a voice channel.")
        logger.warning(
            f"{ctx.author.name} attempted to call join but was not in a voice channel."
        )


async def leave(ctx):
    """
    Leave the current discord voice channel.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !leave in {ctx.guild}")
    if ctx.voice_client:
        if players[ctx.guild.id].active:
            async with ctx.typing():
                await ctx.send(
                    "Cannot leave channel while queue is active. Try !stop instead."
                )
            logger.warning(
                f"{ctx.author.name} attempted to call leave while the queue was active."
            )
            return
        await players[ctx.guild.id].client.disconnect()
        del players[ctx.guild.id]
        logger.info(f"Left voice channel in {ctx.guild}")
    else:
        async with ctx.typing():
            await ctx.send("ColinBot is not currently in a voice channel.")
        logger.warning(
            f"{ctx.author.name} attempted to call leave while the bot was not in any voice channel."
        )


async def ram_ranch(ctx):
    """
    Plays a random Ram Ranch song.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !ramranch in {ctx.guild}")
    songs = []
    for filepath in os.listdir(MUSIC_PATH):
        songs.append(f"{MUSIC_PATH}{filepath}")
    random_int = random.randint(0, len(songs) - 1)
    song = Song(songs[random_int])
    if ctx.guild.id not in players:
        await join(ctx)
    await players[ctx.guild.id].enqueue(song, ctx)
    if not players[ctx.guild.id].active:
        await players[ctx.guild.id].handle_queue(ctx)


async def pause(ctx):
    """
    Pauses the current music player.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !pause in {ctx.guild}")
    players[ctx.guild.id].pause = True
    players[ctx.guild.id].client.pause()
    logger.info(f"Player has been paused in {ctx.guild}")


async def resume(ctx):
    """
    Resume the current music player, if paused.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !resume in {ctx.guild}")
    players[ctx.guild.id].pause = False
    await players[ctx.guild.id].client.resume()
    logger.info(f"Player has been resumed in {ctx.guild}")


async def stop(ctx):
    """
    Stops the current music player and clears the queue.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !stop in {ctx.guild}")
    await players[ctx.guild.id].clear(ctx)
    players[ctx.guild.id].client.stop()
    await leave(ctx)
    logger.info(f"Player has been stopped in {ctx.guild}")


async def skip(ctx):
    """
    Skips the currently playing song.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !skip in {ctx.guild}")
    await players[ctx.guild.id].client.stop()


async def playing(ctx):
    """
    Sends information about the currently playing song.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !playing in {ctx.guild}")
    await ctx.send(players[ctx.guild.id].playing)


async def queue(ctx):
    """
    Sends information about the current music queue.

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !queue in {ctx.guild}")
    await ctx.send(players[ctx.guild.id])


class Cog(commands.Cog, name="music"):
    """
    Cog class

    For initalizing all the music cog functions.

    Attributes:
        bot: Discord bot object.
    """

    def __init__(self, bot):
        try:
            self.bot = bot
            logger.info("Music cog successfully initialized.")
        except Exception as e:
            logger.error(f"Unable to initialize music cog: {e}")

    @commands.command(name="join", help="Join the current voice channel.")
    async def join(self, ctx):
        """Init join command"""
        await join(ctx)

    @commands.command(name="leave", help="Leave the current voice channel.")
    async def leave(self, ctx):
        """Init leave command"""
        await leave(ctx)

    @commands.command(
        name="ramranch", help="Play a random Ram Ranch in the current voice channel."
    )
    async def ram_ranch(self, ctx):
        """Init ramranch command"""
        await ram_ranch(ctx)

    @commands.command(name="rr", help="Short for Ram Ranch.")
    async def rr(self, ctx):
        """Init rr command"""
        await ram_ranch(ctx)

    @commands.command(name="pause", help="Pause music playback.")
    async def pause(self, ctx):
        """Init pause command"""
        await pause(ctx)

    @commands.command(name="play", help="Resume music playback.")
    async def play(self, ctx):
        """Init play command"""
        await resume(ctx)

    @commands.command(name="resume", help="Resume music playback.")
    async def resume(self, ctx):
        """Init resume command"""
        await resume(ctx)

    @commands.command(name="stop", help="End music playback")
    async def stop(self, ctx):
        """Init stop command"""
        await stop(ctx)

    @commands.command(name="skip", help="Skip current song in queue.")
    async def skip(self, ctx):
        """Init skip command"""
        await skip(ctx)

    @commands.command(name="playing", help="Now playing.")
    async def playing(self, ctx):
        """Init playing command"""
        await playing(ctx)

    @commands.command(name="queue", help="Music queue.")
    async def queue(self, ctx):
        """Init queue command"""
        await queue(ctx)
