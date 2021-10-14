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

api = DiscordBotApi(client)
def trying(func):
    @functools.wraps(func)
    async def wrapper_function(ctx):
        try:
            response = await func(ctx)
        except SmusError as E:
            response = E.user_message

        await ctx.send(response)

    return wrapper_function

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
@trying
async def join(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.join(msg, author)
    return response

@client.command()
@trying
async def start(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.start(msg, author)
    return response

@client.command()
@trying
async def leave(ctx):
    msg = ctx.message.content
    author = ctx.message.author
    response = api.leave(msg, author)
    return response

@client.command()
@trying
async def clear(ctx):
    msg = ctx.message.content
    response = api.clear(msg)
    return response

@client.command()
@trying
async def pop(ctx):
    msg = ctx.message.content
    response = api.pop(msg)
    return response

@client.command()
@trying
async def popall(ctx):
    msg = ctx.message.content
    response = api.popall(msg)
    return response

@client.command()
@trying
async def kick(ctx):
    msg = ctx.message.content
    response = api.kick(msg)
    return response

@client.command()
@trying
async def show(ctx):
    response = api.show_all()
    return response

@client.command()
async def meme(ctx):
    await ctx.send(file=discord.File('jaydebot.jpg'))

@client.command()
async def remove(ctx):
    clear(ctx)

@client.command()
@trying
async def nuke(ctx):
    response = api.nuke()
    return response

client.run(TOKEN)
