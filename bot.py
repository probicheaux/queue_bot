import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = '!sq')
class Queue:
    def __init__(self, game):
        assert isinstance(game, str)
        assert game
        self.game = game
        self.queue = list()

    def showq(self):
        string = self.game + ' queue:\n'
        if self.queue:
            for ind, s in enumerate(self.queue):
                string += str(ind+1)+': '+ s.name + '\n'
        else:
            string = "{} queue currently empty idiote".format(self.game)
        return string

    def __eq__(self, x):
        return self.game == x

    def __hash__(self):
        return self.game

    def __str__(self):
        return self.game

    def add(self, person):
        if person not in self.queue:
            self.queue.append(person)

    def remove(self, person):
        if person in self.queue:
            self.queue.remove(person)

    def clear(self):
        for i in range(len(self.queue)):
            self.pop(0)

    def __len__(self):
        return len(self.queue)

    def pop(self, index):
        return self.queue.pop(index)


class QueueDict:
    def __init__(self):
        self.dict = dict()
    async def get(self, item, ctx):
        queue_names = list(self.dict.keys())
        if item not in queue_names:
            if len(queue_names) > 0:
                if len(queue_names) > 1:
                    qstr = (' {}, '*len(queue_names)).format(queue_names)
                else:
                    qstr = ' ' + str(queue_names[0])
                await ctx.send('Queue name {} not found, your options are:'.format(item) + qstr)
            else:
                await ctx.send('No currently active queues, try starting one with !sqjoin <game_name>')
            raise ValueError('Item not found')
        else:
            return self.dict[item]

    def set(self, index, value):
        assert isinstance(value, Queue)
        self.dict[index] = value

    def keys(self):
        return list(self.dict.keys())

    async def delete(self, item, ctx):
        await self.get(item, ctx)
        del(self.dict[item])

queue_dict = QueueDict()

async def parse_args(ctx, cmd_name, arg_names, num_splits=-1, formatters=[lambda z: z]):
    args = ctx.message.content.split(' ', num_splits)
    args = args[1:]
    if isinstance(arg_names, list):
        break_msg = 'Format is {}'.format(cmd_name) + (' <{}> '*len(arg_names)).format(*arg_names) + 'idiote'
        if len(args) != len(arg_names):
            await ctx.send(break_msg)
            raise ValueError("Args don't work")
        try:
            args = [formatters[i](arg) for i,arg in enumerate(args)]
        except:
            await ctx.send(break_msg)
            raise ValueError("Args don't work")
    else:
        break_msg = 'Format is {} <{}1> <{}2> <{}3> ... idiote'.format(cmd_name, *[arg_names]*3)
        if len(args) == 0:
            await ctx.send(break_msg)
            raise ValueError("Args don't work")
        try:
            args = [formatters[0](arg) for arg in args]
        except:
            await ctx.send(break_msg)
            raise ValueError("Args don't work")

    return tuple(args)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def join(ctx):
    queue_name = await parse_args(ctx, '!sqjoin', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])
    queue_name = queue_name[0]
    if queue_name not in queue_dict.keys():
        s = 'Queue_name {}'.format(queue_name) + ' not found!\n'+'Currently active queues are: {}'.format(queue_dict.keys())+'\n'
        s += 'Starting a new queue for the game {}'.format(queue_name)+'\n'
        s += 'If this was a mistake or a typo please use !sqremove to clean up your mess'
        await ctx.send(s)
        new_q = Queue(queue_name)
        queue_dict.set(queue_name, new_q)

    queue = await queue_dict.get(queue_name, ctx)
    queue.add(ctx.author)
    await ctx.send(queue.showq())
        
@client.command()
async def leave(ctx):
    queue_name = await parse_args(ctx, '!sqleave', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])
    queue_name = queue_name[0]
    queue = await queue_dict.get(queue_name, ctx)
    queue.remove(ctx.author)
    await ctx.send(queue.showq())
    if len(queue) == 0:
        await queue_dict.delete(queue_name, ctx)

@client.command()
async def clear(ctx):
    queue_name = await parse_args(ctx, '!sqclear', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])
    queue_name = queue_name[0]
    await queue_dict.delete(queue_name, ctx)
    await ctx.send('Queue {} beleted\n'.format(queue_name))

@client.command()
async def pop(ctx):
    num, queue_name = await parse_args(ctx, '!sqpop', ['num', 'queue_name'], formatters=[lambda z: int(z), lambda z: str(z)], num_splits=2)
    queue = await queue_dict.get(queue_name, ctx)
    try:
        assert (1 <= num <= len(queue))
    except:
        await ctx.send('Format is !sqpop <queue_name> <num> idiote')
        raise ValueError

    s = ''
    for i in range(num):
        kicked = queue.pop(0)
        s = s + kicked.mention + ' '

    s = s +'please join the gameo {}\n'.format(queue) + queue.showq()
    if len(queue) == 0:
        await queue_dict.delete(queue_name, ctx)

    await ctx.send(s)


@client.command()
async def kick(ctx):
    num, queue_name = await parse_args(ctx, '!sqkick', ['num', 'queue_name'], formatters=[lambda z: int(z), lambda z: str(z)], num_splits=2)
    queue = await queue_dict.get(queue_name, ctx)
    try:
        num = int(num)
        num = num - 1
        assert (0 <= num < len(queue))
    except:
        await ctx.send('Format is !sqkick <num> idiote')
        raise ValueError

    kicked = queue.pop(num)
    string = 'Kicked {}'.format(kicked.name) + '\n'
    string = string + queue.showq()
    if len(queue) == 0:
        await queue_dict.delete(queue_name, ctx)

    await ctx.send(string)


@client.command()
async def show(ctx):
    show_str = ''
    for queue_name in queue_dict.keys():
        q = await queue_dict.get(queue_name, ctx)
        show_str += q.showq() +'\n'

    if len(queue_dict.keys()) == 0:
        await ctx.send('NO QUEUES FOOL')
    else:
        await ctx.send(show_str)

@client.command()
async def meme(ctx):
    await ctx.send(file=discord.File('jaydebot.jpg'))

@client.command()
async def remove(ctx):
    queue_name = await parse_args(ctx, '!sqremove', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])
    queue_name = queue_name[0]
    await queue_dict.delete(queue_name, ctx)
    await ctx.send('Queue {} beleted'.format(queue_name))
    
@client.command()
async def nuke(ctx):
    for q in queue_dict.keys():
        await queue_dict.delete(q, ctx)

client.run(TOKEN)

