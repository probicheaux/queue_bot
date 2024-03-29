import redis
from queue_bot.classes import QueueList, Queue
from queue_bot.utils import SmusError, isint

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""

def parse_args(message, cmd_name, arg_names, num_splits=-1, formatters=[lambda z: z]):
    args = message.split(' ', num_splits)
    args = args[1:]
    if isinstance(arg_names, list):
        break_msg = 'Format is {}'.format(cmd_name) + (' <{}> '*len(arg_names)).format(*arg_names) + 'idiote\n'
        if len(args) != len(arg_names):
            raise SmusError("Error in parse_args", break_msg)
        try:
            args = [formatters[i](arg) for i,arg in enumerate(args)]
        except:
            raise SmusError("Error in parse_args", break_msg)
    else:
        break_msg = 'Format is {} <{}1> <{}2> <{}3> ... idiote\n'.format(cmd_name, *[arg_names]*3)
        if len(args) == 0:
            raise SmusError("Error in parse_args", break_msg)
        try:
            args = [formatters[0](arg) for arg in args]
        except:
            raise SmusError("Error in parse_args", break_msg)

    return tuple(args)

class DiscordBotApi:
    def __init__(self, bot):
        self.redis_connector = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
        self.queue_list = QueueList(self.redis_connector, bot)
        self.bot = bot

    def join(self, msg, author):
        queue_num = parse_args(msg, '!sqjoin', ['queue_index'], num_splits=1, formatters=[lambda z: z])[0]
        if isint(queue_num):
            queue = self.join_by_index(int(queue_num), str(author.id))
        else:
            queue = self.join_by_name(queue_num, str(author.id))

        index = self.queue_list.index(queue)+1
        response = queue.showq(index)
        return response

    def join_by_index(self, queue_num, author):
        if not (0 < queue_num <= len(self.queue_list)):
            err_msg = "Msg must be !sqjoin <int> <queue_name_or_number>"
            user_msg = "For you gotta pick a number between *1* and *{}* idiote".format(len(self.queue_list))
            raise SmusError(err_msg, user_msg)

        queue = self.queue_list[queue_num-1]
        queue.append(author)
        return queue

    def join_by_name(self, queue_name, author):
        queue = self.queue_list[queue_name]
        queue.append(author)
        return queue
            
    def start(self, msg, author):
        queue_name = parse_args(msg, '!sqstart', ['queue_name'], num_splits=1, formatters=[lambda z: str(z)])[0]
        new_queue = Queue(queue_name, self.redis_connector, self.bot)

        if new_queue in self.queue_list.keys():
            index = self.queue_list.index(new_queue)
            queue = self.queue_list[index]
            show_str = queue.showq(index+1)
            user_str = "Queue **{}** already started!\n".format(queue) + show_str
            raise SmusError("Attempted to add queue that already exists", user_str)

        new_queue.append(author.id)
        self.queue_list.append(new_queue)
        index = self.queue_list.index(new_queue)+1
        response = "Currently active queues are " + self.queue_list.show_queue_names() + new_queue.showq(index)
        return response

    def leave(self, msg, author):
        queue_name = parse_args(msg, '!sqleave', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])[0]
        if isint(queue_name):
            queue_name = int(queue_name)
            if not (0 < queue_name <= len(self.queue_list)):
                err_msg = "Msg must be !sqjoin <int> <queue_name_or_number>"
                user_msg = "For you gotta pick a number between *1* and *{}* idiote".format(len(self.queue_list))
                raise SmusError(err_msg, user_msg)
            queue = self.queue_list[queue_name- 1]
        else:
            queue = self.queue_list[queue_name]
        
        queue.remove(author.id)
        index = self.queue_list.index(queue)

        if isinstance(queue_name, int):
                assert index == queue_name - 1

        if len(queue) == 0:
            del(self.queue_list[index])

        response = queue.showq(index+1)
        return response

    def clear(self, msg):
        queue_name = parse_args(msg, '!sqclear', ['game_name'], num_splits=1, formatters=[lambda z: str(z)])[0]
        if isint(queue_name):
            queue_index = int(queue_name) - 1
            if not (0 <= queue_index < len(self.queue_list)):
                err_msg = "Msg must be !sqjoin <int> <queue_name_or_number>"
                user_msg = "For you gotta pick a number between *1* and *{}* idiote".format(len(self.queue_list))
                raise SmusError(err_msg, user_msg)
            queue_name = self.queue_list[queue_index]
            del(self.queue_list[int(queue_index)])
        else:
            index = self.queue_list.index(queue_name)
            del(self.queue_list[index])
        
        response = 'Queue **{}** beleted\n'.format(queue_name)
        return response

    def pop(self, msg):
        num, queue_name = parse_args(msg, '!sqpop', ['num', 'queue_name'], formatters=[lambda z: int(z), lambda z: str(z)], num_splits=2)
        if isint(queue_name):
            queue_name = int(queue_name)
            if not (0 < queue_name <= len(self.queue_list)):
                err_msg = "Msg must be !sqpop <int> <queue_name_or_number>"
                user_msg = "For you gotta pick a number between *1* and *{}* idiote".format(len(self.queue_list))
                raise SmusError(err_msg, user_msg)
            queue_name = int(queue_name) - 1
            queue = self.queue_list[queue_name]
        else:
           queue = self.queue_list[queue_name]

        try:
            assert (1 <= num <= len(queue))
        except:
            err_msg = "Msg must be !sqpop <int> <queue_name_or_number>"
            user_msg = "For queue **{}** you gotta pick a number between *1* and *{}* idiote".format(queue_name, len(queue))
            raise SmusError(err_msg, user_msg)

        response = ''
        for i in range(num):
            kicked = queue.pop(0)
            kicked = self.bot.get_user(int(kicked))
            response = response + kicked.mention + ' '

        index = self.queue_list.index(queue)
        response = response +'please join the gameo **{}**\n'.format(queue) + queue.showq(index+1)
        if len(queue) == 0:
            del(self.queue_list[index])

        return response

    def popall(self, msg):
        queue_name = parse_args(msg, '!sqpop', 'queue_index', num_splits=1)[0]
        if isint(queue_name):
            queue_name = int(queue_name)
            if not (0 < queue_name <= len(self.queue_list)):
                err_msg = "Msg must be !sqpop <int> <queue_name_or_number>"
                user_msg = "For you gotta pick a number between *1* and *{}* idiote".format(len(self.queue_list))
                raise SmusError(err_msg, user_msg)
            queue_name = int(queue_name) - 1
            queue = self.queue_list[queue_name]
        else:
           queue = self.queue_list[queue_name]

        num = len(queue)
        response = ''
        for i in range(num):
            kicked = queue.pop(0)
            kicked = self.bot.get_user(int(kicked))
            response = response + kicked.mention + ' '

        index = self.queue_list.index(queue)
        response = response +'please join the gameo **{}**\n'.format(queue) + queue.showq(index+1)
        if len(queue) == 0:
            del(self.queue_list[index])

        return response

    def kick(self, msg):
        num, queue_name = parse_args(msg, '!sqkick', ['num', 'queue_name'], formatters=[lambda z: int(z), lambda z: str(z)], num_splits=2)
        if isint(queue_name):
            queue_name = int(queue_name)
            if not (0 < queue_name <= len(self.queue_list)):
                err_msg = "Msg must be !sqpop <int> <queue_name_or_number>"
                user_msg = "For you gotta pick a number between *1* and *{}* idiote".format(len(self.queue_list))
                raise SmusError(err_msg, user_msg)
            queue_name = int(queue_name) - 1

        queue = self.queue_list[queue_name]
        try:
            num = num - 1
            assert (0 <= num < len(queue))
        except:
            err_msg = "Msg must be !sqkick <int> <queue_name_or_number>"
            user_msg = "For queue **{}** you gotta pick a number between *1* and *{}* idiote".format(queue_name, len(queue))
            raise SmusError(err_msg, user_msg)

        kicked = queue.pop(num)
        kicked = self.bot.get_user(int(kicked))
        response = 'Kicked {}'.format(kicked.mention) + '\n'
        index = self.queue_list.index(queue)
        response = response + queue.showq(index+1)
        if len(queue) == 0:
            del(self.queue_list[index])

        return response

    def show_all(self):
        return self.queue_list.show_all()

    def nuke(self):
        for q in self.queue_list.keys():
            del(self.queue_list[self.queue_list.index(q)])

        response = '**DELETED ALL QUEUES**\n'
        response += '*are you happy with the untold devastation you have wrought?*'
        return response
