class Queue(list):
    def __init__(self, game):
        if not self.is_valid_name(game):
            raise ValueError("Queue names can't start with a number\n")

        self.game = game
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

    def clear(self):
        for i in range(len(self)):
            self.pop(0)

    @staticmethod
    def is_valid_name(game):
        is_valid = True
        is_valid = is_valid and isinstance(game, str)
        is_valid = is_valid and game
        if is_valid:
            is_valid = is_valid and not game[0].isdigit()
        return is_valid


class QueueDict(dict):
    def __init__(self):
        super().__init__()
        self.keys_list = list()

    def __getitem__(self, item):
        queue_names = self.keys()
        if item not in queue_names:
            if len(queue_names) > 0:
                if len(queue_names) > 1:
                    qstr = (' {}, '*len(queue_names)).format(queue_names)
                else:
                    qstr = ' ' + str(queue_names[0])
                qstr += '\n*U gotta start queues before joining them now :(*\n'
                raise KeyError('Queue name {} not found, your options are:'.format(item) + qstr)
            else:
                qstr = 'No currently active queues, try starting one with !sqstart <game_name>'+ '\n'
                qstr += '*U gotta start queues before joining them now :(*\n'
                raise KeyError(qstr)
        else:
            return super().__getitem__(item)

    def __setitem__(self, index, value):
        super(QueueDict, self).__setitem__(index, value)
        if index not in self.keys():
            self.keys().append(value)

    def keys(self):
        return self.keys_list

    def __delitem__(self, item):
        super(QueueDict, self).__delitem__(item)
        self.keys().remove(item)

    def index(self, item):
        return self.keys().index(item)

    def get_by_ind(self, ind):
        if ind < 0 or ind >= len(self.keys()):
            err_msg = "Tried to select a queue that doesn't exist. Available queues are:\n" 
            err_msg += self.show_queue_names()
            raise ValueError(err_msg)

        return self.__getitem__(self.keys()[ind])

    def show_queue_names(self):
        show_str = 'Active queues are '
        for ind, queue_name in enumerate(self.keys()):
            last = ind == len(self.keys()) - 1
            if not last:
                list_str = '**{}) {}**, '.format(ind+1, queue_name)
            else:
                list_str = '**{}) {}**'.format(ind+1, queue_name)
            show_str += list_str

        if len(self.keys()) == 0:
            show_str = 'NO QUEUES FOOL'

        return show_str + '\n'

    def show_all(self):
        show_str = ''
        for ind, queue_name in enumerate(self.keys()):
            q = self[queue_name]
            show_str += q.showq(ind+1) +'\n'

        if len(self.keys()) == 0:
            show_str = 'NO QUEUES FOOL\n'

        return show_str
