import json
import os
import copy
import random
import logging
from datetime import datetime
from collections import OrderedDict

DEFAULT_GAME_SIZE = 5


class data():
    def __init__(self, server):
        self.server = server
        self.data = {}
        if os.path.exists(os.path.dirname(__file__) + f'/data/{self.server}.json'):
            self.load()
        else:
            self.init()
            self.save()

    def load(self):
        with open(os.path.dirname(__file__) + f'/data/{self.server}.json') as f:
            self.data = json.load(f)

    def save(self):
        with open(os.path.dirname(__file__) + f'/data/{self.server}.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def init(self):
        # game data
        self.data['title'] = ""
        self.data['spots'] = DEFAULT_GAME_SIZE
        self.data['gamers'] = []
        self.data['agents'] = []
        self.data['captains'] = OrderedDict()
        self.data['turn'] = None
        # other data
        self.data['info'] = {}  # dict of user_ids where value is dict
        self.data['set'] = {}
        self.save()

    def start(self, *args, **kwargs):
        self.load()
        self.data['title'] = kwargs.get('title', "")
        self.data['spots'] = kwargs.get('spots', DEFAULT_GAME_SIZE)
        self.data['gamers'] = []
        self.data['agents'] = []
        self.data['captains'] = OrderedDict()
        self.data['turn'] = None
        self.save()

    @property
    def title(self):
        self.load()
        return self.data['title']

    @title.setter
    def title(self, title):
        self.load()
        self.data['title'] = title
        self.save()

    @property
    def spots(self):
        self.load()
        return self.data['spots']

    @property
    def people(self):
        self.load()
        return len(self.data['gamers'])

    @property
    def picks(self):
        self.load()
        return len(self.data['agents'])

    @property
    def agents(self):
        self.load()
        return self.data['agents']

    @agents.setter
    def agents(self, people):
        self.load()
        self.data['agents'] = people
        self.save()

    @property
    def gamers(self):
        self.load()
        return self.data['gamers']

    @property
    def captains(self):
        self.load()
        cap_list = list(self.data['captains'].keys())
        return list(map(int, cap_list))

    @captains.setter
    def captains(self, args):
        self.load()
        self.data['agents'] = copy.deepcopy(self.data['gamers'])
        tmpdict = OrderedDict()
        self.data['captains'] = OrderedDict()
        for cap in args:
            # captains cannot pick themselves
            self.data['agents'].remove(int(cap.id))
            tmpdict[cap.id] = []
        # randomize order of captains
        keys = list(tmpdict.keys())
        random.shuffle(keys)
        for k in keys:
            self.data['captains'][k] = []
        self.save()

    @property
    def turn(self):
        self.load()
        return self.data['turn']

    @turn.setter
    def turn(self, captain):
        self.load()
        self.data['turn'] = captain
        self.save()

    @property
    def info(self):
        self.load()
        user_list = list(self.data['info'].keys())
        return list(map(int, user_list))

    def get_birthday(self, user):
        self.load()
        self.info_check(user, 'birthday')
        try:
            bday = self.data['info'][str(user)]['birthday']
        except KeyError:
            return None
        return datetime.fromisoformat(bday)

    def set_birthday(self, user, birthday: datetime):
        self.load()
        self.info_check(user, 'birthday')
        self.data['info'][user]['birthday'] = birthday.isoformat()
        self.save()

    def info_check(self, user, atr=None):
        self.load()
        if user not in self.data['info']:
            self.data['info'][user] = {}
        if atr != None and atr not in self.data['info'][user]:
            self.data['info'][user][atr] = None

    def set_command(self, command, value):
        self.load()
        self.data['set'][command] = value
        self.save()

    def get_command(self, command):
        self.load()
        try:
            value = self.data['set'][command]
        except KeyError:
            return None
        return value

    def get_gamer(self, num):
        self.load()
        return self.data['gamers'][num]

    def get_agent(self, num):
        self.load()
        return self.data['agents'][num]

    def team_size(self, captain):
        self.load()
        return len(self.data['captains'][str(captain)])

    def get_players(self, captain):
        self.load()
        return self.data['captains'][str(captain)]

    def get_player(self, captain, num):
        self.load()
        return self.data['captains'][str(captain)][num]

    def add_player(self, captain, choice):
        self.load()
        self.data['captains'][str(captain)].append(self.data['agents'][choice])
        del self.data['agents'][choice]
        self.save()

    def add_gamer(self, user):
        self.load()
        if user.id not in self.data['gamers']:
            self.data['gamers'].append(user.id)
            self.save()
            return True
        return False

    def del_gamer(self, user):
        self.load()
        if user.id in self.data['gamers']:
            self.data['gamers'].remove(user.id)
            self.save()
            return True
        return False
