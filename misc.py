import os
import random
import discord
import boto3
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

s3 = boto3.resource(service_name='s3', region_name=os.getenv('AWS_REGION'), aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
bucket = s3.Bucket(os.getenv('BUCKET_NAME'))

async def colin(ctx):
    async with ctx.typing():
        pictures = [obj.key for obj in bucket.objects.filter(Prefix='img/colin/')]
        randomColin = random.choice(pictures)
        file_obj = s3.Object(os.getenv('BUCKET_NAME'), randomColin)
        file_content = file_obj.get()['Body'].read()
        file = discord.File(BytesIO(file_content), filename=randomColin.split('/')[-1])
        await ctx.send(file=file)

async def ping(ctx, bot):
    async with ctx.typing():
            await ctx.send(f"Latency: {round(bot.latency * 1000)}ms")

async def ninja(ctx):
    async with ctx.typing():
        await ctx.send("The phrase “it's just a game” is such a weak mindset. You are ok with what happened, losing, imperfection of a craft. When you stop getting angry after losing, you've lost twice.\n\nThere's always something to learn, and always room for improvement, never settle.")

async def getRandomNumber(ctx):
    async with ctx.typing():
        await ctx.send("4")

def on_shutdown():
    print("Bot is offline.")