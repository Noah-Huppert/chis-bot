# Chis Discord Bot

A simple, "chis-bot". 

This bot was created to help a small group friends plan Valorant 10-mans.
Hopefully one day chis-bot will become something bigger. :)

## Installation

``` bash
python3.8 -m pip install pipenv
pipenv install
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

<img src="https://i.imgur.com/aWKH89w.gif" alt="plan" height="350"/>

### Add users to the game

$[add|a|join] [users]

Type a users name to add them to the game.

<img src="https://i.imgur.com/0wkp11u.gif" alt="add" height="350"/>


### Delete users from the game

$[del|delete|d|remove|leave] [users]

Type a users name to delete them to the game.

<img src="https://i.imgur.com/ZDl7cuw.gif" alt="delete" height="350"/>

### Start the team selection

$[team|t] [users]

Type out a list of captains to start team selection.

<img src="https://i.imgur.com/3xAfZVe.gif" alt="team1" height="350"/>

### Selecting team members

https://github.com/zacharied/discord-eprompt

<img src="https://i.imgur.com/3WUbvAT.gif" alt="team2" height="350"/>

### Picking the Side

$side 

Randomly selects a side [Attackers/Defenders]

<img src="https://i.imgur.com/PmmiRVZ.gif" alt="side" height="350"/>

### Picking the Map

$map 

Randomly selects a Valorant map

<img src="https://i.imgur.com/k7dalPJ.gif" alt="map" height="350"/>

### Move teams to different voice channels

https://github.com/zacharied/discord-eprompt

<img src="https://i.imgur.com/MATv1Io.gif" alt="play" height="350"/>

## License

[MIT](https://choosealicense.com/licenses/mit/)
