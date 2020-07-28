import json
import os
import copy

DEFAULT_GAME_SIZE = 5

#TODO convert to python 2020 getters and setters
class data():
    def __init__(self, filename):
        self.filename = filename
        self.agents = []
        self.captains = {}
        self.data = {}
        self.picks = 0
        if os.path.exists(os.path.dirname(__file__) + f'/data/{self.filename}.json'):
            self.load()
        else:
            self.start()
            self.save()

    def load(self):
        with open(os.path.dirname(__file__) + f'/data/{self.filename}.json') as f:
            self.data = json.load(f)

    def save(self):
        with open(os.path.dirname(__file__) + f'/data/{self.filename}.json', 'w') as f:
            json.dump(self.data, f, indent=4)



    def start(self, *args, **kwargs):
        spots = kwargs.get('spots', DEFAULT_GAME_SIZE)
        game = kwargs.get('game', "")
        self.data = {"game": game, "spots": spots,
                     "people": 0, "gamers": []}
        self.save()
        
    def getGame(self):
        self.load()
        return self.data["game"]

    def getSpots(self):
        self.load()
        return self.data["spots"]

    def getPeople(self):
        self.load()
        return self.data["people"]

    def setPeople(self, num):
        self.load()
        self.data["people"] = num
        self.save()

    def getPicks(self):
        return self.picks
    
    def setPicks(self, num):
        self.picks = num

    def getGamer(self, num):
        self.load()
        return self.data["gamers"][num]["name"]
    
    def getAgent(self, num):
        self.load()
        return self.agents[num]["name"]

    def isAgent(self):
        self.load()
        return len(self.agents) != 0

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

    def addGamer(self, user):
        self.load()
        if {"name": user.name, "tag": user.discriminator} not in self.data["gamers"]:
            self.data["gamers"].append(
                {"name": user.name, "tag": user.discriminator})
            self.save()
            self.setPeople(self.getPeople() + 1)
            return True
        return False

    def delGamer(self, user):
        self.load()
        if {"name": user.name, "tag": user.discriminator} in self.data["gamers"]:
            self.data["gamers"].remove({"name": user.name, "tag": user.discriminator})
            self.save()
            self.setPeople(self.getPeople() - 1)
            return True
        return  False
    
    def setCaptians(self, captains):
        self.load()
        self.picks = self.data["people"]
        self.agents = copy.deepcopy(self.data["gamers"])
        self.captains = {}
        for cap in captains:
            self.captains[cap.display_name] = []
            # captains cannot pick themselves
            self.agents.remove({ "name": cap.name, "tag": cap.discriminator })
            self.setPicks(self.getPicks() - 1)

    def turn(self, captains, turn):
        return captains[turn % len(captains)]
