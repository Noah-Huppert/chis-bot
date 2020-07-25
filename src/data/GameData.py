import json
import os

#TODO $s with no game should cause an error
#TODO convert to python 2020 getters and setters
class GameData():
    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        self.save()

    def load(self):
        with open(os.path.dirname(__file__) + f'/{self.filename}.json') as f:
            self.data = json.load(f)

    def save(self):
        with open(os.path.dirname(__file__) + f'/{self.filename}.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    #TODO only save if the file doesn't already exist
    def start(self, spots):
        self.data = {"match": "Game", "spots": spots,
                     "people": 0, "gamers": [], "agents": [], "captains": {}}
        self.save()
        
            #only save if the file doesn't already existself.save()

    def getSpots(self):
        self.load()
        return self.data["spots"]

    # def setSpots(self, num):
    #     self.load()
    #     self.data["spots"] = num
    #     self.save()

    def getPeople(self):
        self.load()
        return self.data["people"]

    def setPeople(self, num):
        self.load()
        self.data["people"] = num
        self.save()

    def getGamer(self, num):
        self.load()
        return self.data["gamers"][num]["name"]

    def isGamers(self):
        self.load()
        return len(self.data["gamers"]) != 0

    # maybe not add by just display name since it isn't unique
    def teamSize(self, captain):
        self.load()
        return len(self.data["captains"][captain.display_name])

    def getPlayer(self, captain, num):
        self.load()
        return self.data["captains"][captain.display_name][num]

    #TODO player should be added by name/discriminator
    def addPlayer(self, captains, pick, choice):
        self.load()
        self.data["captains"][ captains[pick % len(captains)].display_name ].append(self.data["gamers"][choice]["name"])
        del self.data["gamers"][choice]
        self.save()
        self.setPeople(self.getPeople() - 1)

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
        self.data["captains"] = {}
        for cap in captains:
            self.data["captains"][cap.display_name] = []
            # captains cannot pick themselves
            self.data["gamers"].remove({ "name": cap.name, "tag": cap.discriminator })
            self.save()
            self.setPeople(self.getPeople() - 1)

    def turn(self, captains, turn):
        return captains[turn % len(captains)]
