import os
import random
import discord
import boto3
import requests
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

s3 = boto3.resource(service_name='s3', region_name=os.getenv('AWS_REGION'),
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
bucket = s3.Bucket(os.getenv('BUCKET_NAME'))
pictures = [obj.key for obj in bucket.objects.filter(Prefix='img/colin/')]

async def colin(ctx):
    async with ctx.typing():
        random_picture = random.choice(pictures)
        file = discord.File(BytesIO(s3.Object(os.getenv('BUCKET_NAME'), random_picture).get()['Body'].read()), filename=random_picture.split('/')[-1])
        print(f"Posed image {random_picture}")
        await ctx.send(file=file)

async def ping(ctx, bot):
    async with ctx.typing():
            await ctx.send(f"Latency: {round(bot.latency * 1000)}ms")

async def ninja(ctx):
    async with ctx.typing():
        await ctx.send("The phrase “it's just a game” is such a weak mindset. You are ok with what happened, losing, imperfection of a craft. When you stop getting angry after losing, you've lost twice.\n\nThere's always something to learn, and always room for improvement, never settle.")

async def get_random_number(ctx):
    async with ctx.typing():
        await ctx.send("4")

async def waifu(ctx):
    async with ctx.typing():    
        response = requests.get('https://api.waifu.pics/sfw/waifu')
        data = response.json()
        print(f"Waifu.pics API Response: {response.status_code} {data}")
        await ctx.send(data['url'])

def on_startup():
    print("ColinBot is online.")

def on_shutdown():
    print("ColinBot is offline.")