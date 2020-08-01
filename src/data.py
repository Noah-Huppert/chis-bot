import json
import os
import copy
import random
import logging
from collections import OrderedDict

DEFAULT_GAME_SIZE = 5

#TODO convert to python 2020 getters and setters
class data():
    def __init__(self, server):
        self.server = server
        # self.agents = []
        self.data = {}
        # self.picks = 0
        if os.path.exists(os.path.dirname(__file__) + f'/data/{self.server}.json'):
            self.load()
        else:
            self.start()
            self.save()

    @property
    def title(self):
        self.load()
        return self.data["title"]

    @property
    def spots(self):
        self.load()
        return self.data["spots"]

    @property
    def people(self):
        self.load()
        return len(self.data["gamers"])

    @property
    def picks(self):
        self.load()
        return len(self.data["agents"])

    @property
    def captains(self):
        self.load()
        return list(self.data['captains'].keys())
    
    @captains.setter
    def captains(self, args):
        self.load()
        self.data['agents'] = copy.deepcopy(self.data['gamers'])
        self.data['captains'] = OrderedDict()
        for cap in args:
            # captains cannot pick themselves
            try:
                self.data['agents'].remove(cap.id)
            except ValueError:
                return False
            self.data['captains'][cap.id] = []
        self.save()
        return True


    def load(self):
        with open(os.path.dirname(__file__) + f'/data/{self.server}.json') as f:
            self.data = json.load(f)

    def save(self):
        with open(os.path.dirname(__file__) + f'/data/{self.server}.json', 'w') as f:
            json.dump(self.data, f, indent=4)



    def start(self, *args, **kwargs):
        self.data['title'] = kwargs.get('title', "")
        self.data['spots'] = kwargs.get('spots', DEFAULT_GAME_SIZE)
        self.data['gamers'] = []
        self.data['agents'] = []
        self.data['captains'] = OrderedDict()
        self.save()

    def get_gamer(self, num):
        self.load()
        return self.data['gamers'][num]
    
    def getAgent(self, num):
        self.load()
        return self.agents[num]["name"]

    def isAgent(self):
        self.load()
        return len(self.agents) != 0

    def getPicks(self):
        return self.picks
    
    def setPicks(self, num):
        self.picks = num


    # TODO add by just display name since it isn't unique
    def teamSize(self, captain):
        self.load()
        return len(self.captains[captain.display_name])

    def getPlayer(self, captain, num):
        self.load()
        return self.captains[captain.display_name][num]

    #TODO player should be added by name/discriminator
    def addPlayer(self, captains, pick, choice):
        self.load()
        self.captains[ captains[pick % len(captains)].display_name ].append(self.agents[choice]["name"])
        del self.agents[choice]
        self.save()
        self.setPicks(self.getPicks() -1)

    # use user tuple in dict
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
        return  False
    
    def turn(self):
        self.load()
        self.data["captains"][self.picks % len(self.captains)]

