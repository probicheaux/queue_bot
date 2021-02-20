import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from queue_bot.classes import Queue, QueueList
from queue_bot.utils import isint
from queue_bot.api import DiscordBotApi

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = '!sq')

api = DiscordBotApi()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def join(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.join(msg, author)
    await ctx.send(response)


@client.command()
async def start(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.start(msg, author)
    await ctx.send(response)


@client.command()
async def leave(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.leave(msg, author)
    await ctx.send(response)

@client.command()
async def clear(ctx):
    msg = ctx.message.content
    response = api.clear(msg)
    await ctx.send(response)

@client.command()
async def pop(ctx):
    msg = ctx.message.content
    response = api.pop(msg)
    await ctx.send(response)


@client.command()
async def kick(ctx):
    msg = ctx.message.content
    response = api.kick(msg)
    await ctx.send(response)

@client.command()
async def show(ctx):
    response = api.show_all()
    await ctx.send(response)

@client.command()
async def meme(ctx):
    await ctx.send(file=discord.File('jaydebot.jpg'))

@client.command()
async def remove(ctx):
    await clear(ctx)

@client.command()
async def nuke(ctx):
    response = api.nuke()
    await ctx.send(response)

client.run(TOKEN)

