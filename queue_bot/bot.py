import os

import discord
import functools

from discord.ext import commands
from dotenv import load_dotenv
from queue_bot.utils import SmusError
from queue_bot.api import DiscordBotApi

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = '!sq')

api = DiscordBotApi()
def trying(func):
    @functools.wraps(func)
    async def wrapper_function(ctx):
        try:
            response = func(ctx)
        except SmusError as E:
            response = E.user_message

        await ctx.send(response)

    return wrapper_function

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@trying
@client.command()
async def join(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.join(msg, author)
    return response

@trying
@client.command()
async def start(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.start(msg, author)
    return response

@trying
@client.command()
async def leave(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.leave(msg, author)
    return response

@trying
@client.command()
async def clear(ctx):
    msg = ctx.message.content
    response = api.clear(msg)
    return response

@trying
@client.command()
async def pop(ctx):
    msg = ctx.message.content
    response = api.pop(msg)
    return response

@trying
@client.command()
async def kick(ctx):
    msg = ctx.message.content
    response = api.kick(msg)
    return response

@trying
@client.command()
async def show(ctx):
    response = api.show_all()
    return response

@client.command()
async def meme(ctx):
    await ctx.send(file=discord.File('jaydebot.jpg'))

@client.command()
async def remove(ctx):
    clear(ctx)

@trying
@client.command()
async def nuke(ctx):
    response = api.nuke()
    return response

client.run(TOKEN)
