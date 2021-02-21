from queue_bot.utils import SmusError

class Queue:
    def __init__(self, game, redis_connector):
        if not self.is_valid_name(game):
            err = "Initialize the queue with a valid name"
            usr =  "Queue names can't start with a number\n"
            raise SmusError(err, usr)

        self.game = game
        self.name = game
        self.redis_connector = redis_connector

    def showq(self, index):
        if self.names():
            string = '**{}) {}:**\n'.format(index, self)
            for ind, s in enumerate(self.names()):
                string += str(ind+1)+': '+ s + '\n'
        else:
            string = "**{}** queue currently empty idiote".format(self.game)
        return string

    def __eq__(self, x):
        return self.game == x

    def __hash__(self):
        return hash(self.game)

    def __str__(self):
        return self.game

    def names(self):
        return self.redis_connector.lrange(self.name, 0, -1)

    def __len__(self):
        return len(self.names())

    def append(self, person):
        if person not in self.names():
            self.redis_connector.lpush(self.name, person)

    def remove(self, item):
        removed = self.redis_connector.lrem(self.name, 0, item)
        if not removed:
            user_str = "*You're not in* **{}** *silly*".format(self)
            raise SmusError(f"Person not found in {self.name}", user_str)

    def pop(self, item):
        person = self.redis_connector.lindex(self.name, item)
        removed = self.redis_connector.lrem(self.name, 0, person)
        if person and removed:
            return person
        else:
            user_str = "*You can't pop {} for queue* **{}** *silly*".format(item, self)
            raise SmusError(f"Person not found in {self.name}", user_str)

    def __getitem__(self, item):
        person = self.redis_connector.lindex(self.name, item)
        if person:
            return person
        else:
            user_str = "*You can't get {} for queue* **{}** *silly*".format(item, self)
            raise SmusError(f"Person not found in {self.name}", user_str)

    @staticmethod
    def is_valid_name(game):
        if not isinstance(game, str):
            return False
        if not game:
            return False
        if game[0].isdigit():
            return False

        return True


class QueueList(list):
    def __init__(self, redis_connector):
        self.name = "among smus queue list"
        self.redis_connect = redis_connector

    def __getitem__(self, item):
        length = len(self)
        if isinstance(item, str):
            item = self.index(item)
        if not (0 <= item < length):
            usr_msg = "Tried to get a queue that doesn't exist. Available queues are:\n" 
            usr_msg += self.show_queue_names()
            err_msg = f"{item} is out of bounds for {length}"
            raise SmusError(err_msg, usr_msg)

        return Queue(self.redis_connect.lindex(self.name, item), self.redis_connect)

    def games(self):
        return self.redis_connect.lrange(self.name, 0, -1)

    def __len__(self):
        return len(self.games())

    def get_by_name(self, item):
        names = self.games()
        if item not in names:
            if len(names) > 0:
                if len(names) > 1:
                    qstr = (' {}, '*len(names)).format(names)
                else:
                    qstr = ' ' + str(names[0])
                qstr += '\n*U gotta start queues before joining them now :(*\n'
                usr_msg = 'Queue name {} not found, your options are:'.format(item) + qstr
                err_msg = 'Queue_name {} not found'.format(item)
                raise SmusError(err_msg, usr_msg)
            else:
                usr_msg = 'No currently active queues, try starting one with !sqstart <game_name>'+ '\n'
                usr_msg += '*U gotta start queues before joining them now :(*\n'
                raise SmusError("Tried to get queue from empty list", usr_msg)
        else:
            return self[self.index(item)]

    def get_index(self, item):
        if isinstance(item, str):
            return self.games().index(item)

        elif isinstance(item, Queue):
            return self.games().index(str(item))

        else:
            raise IndexError("Input to index must be a queue or queue name")

    def index(self, item):
        try:
            return self.get_index(item)
        except IndexError as E:
            usr_message = "Couldn't find {}".format(item)
            raise SmusError(str(E), usr_message)

    def append(self, item):
        exists_error = SmusError("Can't append extant queue", 'Queue **{}** already started!'.format(item))
        if item.name in self.games():
            raise exists_error

        assert isinstance(item, Queue)
        self.redis_connect.lpush(self.name, item.name)


    def keys(self):
        return self.games()

    def __delitem__(self, item):
        try:
            games = self.games()
            length = len(games)
            if not (0 <= item < length):
                raise IndexError(f"{item} is out of bounds for {length}")
            item = games[item]
            response = self.redis_connect.lrem(self.name, 0, item)
            response and self.redis_connect.delete(item)
            if not response:
                raise IndexError(f"{item} is out of bounds for {length}")
 

        except IndexError as E:
            err_msg = "Tried to delete a queue that doesn't exist. Available queues are:\n" 
            err_msg += self.show_queue_names()
            raise SmusError(str(E), err_msg)

    def get_by_ind(self, ind):
        try:
            item = super(QueueList, self).__getitem__(ind)
        except IndexError as E:
            err_msg = "Tried to select a queue that doesn't exist. Available queues are:\n" 
            err_msg += self.show_queue_names()
            raise SmusError(str(E), err_msg)

        return item

    def show_queue_names(self):
        show_str = ''
        for ind, queue_name in enumerate(self.games()):
            last = ind == len(self) - 1
            if not last:
                list_str = '**{}) {}**, '.format(ind+1, queue_name)
            else:
                list_str = '**{}) {}**'.format(ind+1, queue_name)
            show_str += list_str

        if len(self) == 0:
            show_str = 'NO QUEUES FOOL'

        return show_str + '\n'

    def show_all(self):
        show_str = ''
        for ind in range(len(self.games())):
            q = self[ind]
            show_str += q.showq(ind+1) +'\n'

        if len(self.games()) == 0:
            show_str = 'NO QUEUES FOOL\n'

        return show_str
