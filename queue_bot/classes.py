from queue_bot.utils import SmusError


class Queue(list):
    def __init__(self, game):
        if not self.is_valid_name(game):
            err = "Initialize the queue with a valid name"
            usr =  "Queue names can't start with a number\n"
            raise SmusError(err, usr)

        self.game = game
        self.name = game
        super(list, self).__init__()

    def showq(self, index):
        if self:
            string = '**{}) {}:**\n'.format(index, self)
            for ind, s in enumerate(self):
                string += str(ind+1)+': '+ s.name + '\n'
        else:
            string = "**{}** queue currently empty idiote".format(self.game)
        return string

    def __eq__(self, x):
        return self.game == x

    def __hash__(self):
        return hash(self.game)

    def __str__(self):
        return self.game

    def append(self, person):
        if person not in self:
            super().append(person)

    def remove(self, item):
        try:
            super(Queue, self).remove(item)
        except ValueError as E:
            user_str = "*You're not in* **{}** *silly*".format(self)
            raise SmusError(str(E), user_str)

    def pop(self, item):
        try:
            return super(Queue, self).pop(item)
        except IndexError as E:
            user_str = "*You can't pop {} for queue* **{}** *silly*".format(item, self)
            raise SmusError(str(E), user_str)

    def __getitem__(self, item):
        try:
            super(Queue, self).__getitem__(item)
        except IndexError as E:
            user_str = "*You can't get {} for queue* **{}** *silly*".format(item, self)
            raise SmusError(str(E), user_str)

    @staticmethod
    def is_valid_name(game):
        is_valid = True
        is_valid = is_valid and isinstance(game, str)
        is_valid = is_valid and game
        if is_valid:
            is_valid = is_valid and not game[0].isdigit()
        return is_valid


class QueueList(list):
    def __init__(self):
        super().__init__()

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.get_by_ind(item)
        
        if isinstance(item, str):
            return self.get_by_name(item)

        if isinstance(item, Queue):
            return self.get_by_name(item.name)

    def get_by_name(self, item):
        names = [game.name for game in self]
        if item not in names:
            if len(names) > 0:
                if len(self) > 1:
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
            names = [game.name for game in self]
            return names.index(item)

        elif isinstance(item, Queue):
            return super(QueueList, self).index(item)

        elif isinstance(item, int):
            return item

    def index(self, item):
        try:
            return self.get_index(item)
        except IndexError as E:
            usr_message = "Couldn't find {}".format(item)
            raise SmusError(str(E), usr_message)

    def append(self, item):
        exists_error = SmusError("Can't append extant queue", 'Queue **{}** already started!'.format(item))
        if item in self:
            raise exists_error

        if item.name in [game.name for game in self]:
            raise exists_error

        assert isinstance(item, Queue)
        super(QueueList, self).append(item)

    def keys(self):
        return [game.name for game in self]

    def __delitem__(self, item):
        try:
            super(QueueList, self).__delitem__(self.index(item))
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
        for ind, queue_name in enumerate(self):
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
        for ind, queue_name in enumerate(self):
            q = self[queue_name]
            show_str += q.showq(ind+1) +'\n'

        if len(self) == 0:
            show_str = 'NO QUEUES FOOL\n'

        return show_str
