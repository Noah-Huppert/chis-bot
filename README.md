# Chis Discord Bot

A simple, "chis-bot". 

This bot was created to help a small group friends plan Valorant 10-mans.
Hopefully one day chis-bot will become something bigger. :)


## Installation

### Setup a python virtual environment (optional)

``` bash
python3.8 -m pip install virtualenv
python3.8 -m virtualenv env
source env/scripts/activate
```

### Install Requirements

```
pip install -r requirements.txt
```

## Setup

Make your own config.json file, this will contain the bot token, prefix, and list of owners.

See [config file](config-example.json).


## Run

`./src/bot.py`

## Usage


### Creating a Plan

$[plan|p] [spots=5] [name=""]

Takes in a number of players, makes a new game.

![plan](https://i.imgur.com/aWKH89w.gif)

### Add/Delete users to the game

$[add|a|join] [users]

Type a users name to add them to the game.

![add](https://i.imgur.com/0wkp11u.gif)

### Delete users from the game

$[del|delete|d|remove|leave] [users]

Type a users name to delete them to the game.

![delete](https://i.imgur.com/ZDl7cuw.gif)

### Start the team selection

$[team|t] [users]

Type out a list of captains to start team selection.

![team1](https://i.imgur.com/3xAfZVe.gif)

### Selecting team members

https://github.com/zacharied/discord-eprompt

![team2](https://i.imgur.com/3WUbvAT.gif)

### Picking the Side

$side 

Randomly selects a side [Attackers/Defenders]

![side](https://i.imgur.com/PmmiRVZ.gif)

### Picking the Map

$map 

Randomly selects a Valorant map

![map](https://i.imgur.com/k7dalPJ.gif)


### Move teams to different voice channels

https://github.com/zacharied/discord-eprompt

![play](https://i.imgur.com/MATv1Io.gif)

## License

[MIT](https://choosealicense.com/licenses/mit/)
