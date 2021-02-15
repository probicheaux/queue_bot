import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from classes import Queue, QueueDict
from utils import isint

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = '!sq')

queue_dict = QueueDict()

def parse_args(message, cmd_name, arg_names, num_splits=-1, formatters=[lambda z: z]):
    args = message.split(' ', num_splits)
    args = args[1:]
    if isinstance(arg_names, list):
        break_msg = 'Format is {}'.format(cmd_name) + (' <{}> '*len(arg_names)).format(*arg_names) + 'idiote\n'
        if len(args) != len(arg_names):
            raise ValueError(break_msg)
        try:
            args = [formatters[i](arg) for i,arg in enumerate(args)]
        except:
            raise ValueError(break_msg)
    else:
        break_msg = 'Format is {} <{}1> <{}2> <{}3> ... idiote\n'.format(cmd_name, *[arg_names]*3)
        if len(args) == 0:
            raise ValueError(break_msg)
        try:
            args = [formatters[0](arg) for arg in args]
        except:
            raise ValueError(break_msg)

    return tuple(args)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def join(ctx):
    msg = ctx.message.content
    try:
        queue_num = parse_args(msg, '!sqjoin', ['queue_index'], num_splits=1, formatters=[lambda z: z])[0]
    except ValueError as E:
        await ctx.send(E.args[0])
        raise E

    if isint(queue_num):
        try:
            queue = join_by_index(int(queue_num), ctx.author)
        except ValueError as E:
            await ctx.send(E.args[0])
            raise E
    else:
        try:
            queue = join_by_name(queue_num, ctx.author)
        except KeyError as E:
            await ctx.send(E.args[0])
            raise E

    index = queue_dict.index(queue)+1
    await ctx.send(queue.showq(index))

def join_by_index(queue_num, author):
    queue = queue_dict.get_by_ind(queue_num-1)
    queue.append(author)
    return queue

def join_by_name(queue_name, author):
    queue = queue_dict[queue_name]
    queue.append(author)
    return queue
        
@client.command()
async def start(ctx):
    msg = ctx.message.content
    try:
        queue_name = parse_args(msg, '!sqstart', ['queue_name'], num_splits=1, formatters=[lambda z: str(z)])[0]
    except ValueError as E:
        await ctx.send(E.args[0])
        raise E

    try:
        new_queue = Queue(queue_name)
    except ValueError as E:
        await ctx.send(E.args[0])
        raise E

    if new_queue in queue_dict.keys():
        queue = queue_dict[new_queue]
        index = queue_dict.index(queue)+1
        show_str = queue.showq(index)
        await ctx.send("Queue **{}** already started!\n".format(queue) + show_str)
        raise ValueError

    new_queue.append(ctx.author)
    queue_dict[new_queue] = new_queue
    index = queue_dict.index(new_queue)+1
    await ctx.send(queue_dict.show_queue_names() + new_queue.showq(index))

@client.command()
async def leave(ctx):
    msg = ctx.message.content
    queue_name = parse_args(msg, '!sqleave', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])[0]
    if not isint(queue_name):
        try:
            queue = queue_dict[queue_name]
        except KeyError as E:
            await ctx.send(E.args[0])
    else:
        try:
            keys = queue_dict.keys()
            queue_name = keys[int(queue_name) - 1]
            queue = queue_dict[queue_name]
        except KeyError as E:
            await ctx.send(E.args[0])
    queue.remove(ctx.author)
    index = queue_dict.index(queue)+1
    await ctx.send(queue.showq(index))
    if len(queue) == 0:
        del(queue_dict[queue])

@client.command()
async def clear(ctx):
    msg = ctx.message.content
    queue_name = parse_args(msg, '!sqclear', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])[0]
    if not isint(queue_name):
        del(queue_dict[queue_name])
    else:
        keys = queue_dict.keys()
        queue_name = keys[int(queue_name) - 1]
        del(queue_dict[queue_name])
    await ctx.send('Queue **{}** beleted\n'.format(queue_name))

@client.command()
async def pop(ctx):
    msg = ctx.message.content
    num, queue_name = parse_args(msg, '!sqpop', ['num', 'queue_name'], formatters=[lambda z: int(z), lambda z: str(z)], num_splits=2)
    try:
        queue = queue_dict[queue_name]
    except KeyError as E:
        await ctx.send(E.args[0])
        raise E
    try:
        assert (1 <= num <= len(queue))
    except:
        await ctx.send('Format is !sqpop <queue_name> <num> idiote')
        raise ValueError

    s = ''
    for i in range(num):
        kicked = queue.pop(0)
        s = s + kicked.mention + ' '

    index = queue_dict.index(queue)+1
    s = s +'please join the gameo **{}**\n'.format(queue) + queue.showq(index)
    if len(queue) == 0:
        del(queue_dict[queue_name])

    await ctx.send(s)


@client.command()
async def kick(ctx):
    msg = ctx.message.content
    num, queue_name = parse_args(msg, '!sqkick', ['num', 'queue_name'], formatters=[lambda z: int(z), lambda z: str(z)], num_splits=2)
    try:
        queue = queue_dict[queue_name]
    except KeyError as E:
        await ctx.send(E.args[0])
        raise E
    try:
        num = int(num)
        num = num - 1
        assert (0 <= num < len(queue))
    except:
        await ctx.send('Format is !sqkick <num> idiote')
        raise ValueError

    kicked = queue.pop(num)
    string = 'Kicked {}'.format(kicked.name) + '\n'
    index = queue_dict.index(queue)+1
    string = string + queue.showq(index)
    if len(queue) == 0:
        del(queue_dict[queue_name])

    await ctx.send(string)


@client.command()
async def show(ctx):
    await ctx.send(queue_dict.show_all())

@client.command()
async def meme(ctx):
    await ctx.send(file=discord.File('jaydebot.jpg'))

@client.command()
async def remove(ctx):
    await clear(ctx)

@client.command()
async def nuke(ctx):
    for q in queue_dict.keys():
        del(queue_dict[q])

    response = '**DELETED ALL QUEUES**\n'
    response += '*are you happy with the untold devastation you have wrought?*'
    await ctx.send(response)

client.run(TOKEN)

