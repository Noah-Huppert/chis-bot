# Chis Discord Bot

A simple, "chis-bot".

This bot was created to help a small group friends plan Valorant 10-mans.
Hopefully one day chis-bot will become something bigger. :)

------

## Installation

``` bash
python3.8 -m pip install pipenv
pipenv install
```

------

## Setup

Make your own config.json file, 
this will contain the bot token, prefix, and list of owners.

See [config file](config-example.json).

------

## Run

`./run.sh`

------

## Usage

### Creating a Plan

`$plan [spots=5] [name=""]`

Takes in a number of players, makes a new game.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/aWKH89w.gif" alt="plan" height="350"/>
</details>

### Add users to the game

`$add [users]`

Type a users name to add them to the game.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/0wkp11u.gif" alt="add" height="350"/>
</details>

### Delete users from the game

`$delete [users]`

Type a users name to delete them to the game.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/ZDl7cuw.gif" alt="delete" height="350"/>
</details>

### Start the team selection

`$team [users]`

Give a list of valid captains to start team selection.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/3xAfZVe.gif" alt="team1" height="350"/>
</details>

#### Select team members

Click on the lettter corresponding to the player.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/3WUbvAT.gif" alt="team2" height="350"/>
</details>

[Credit: Zacharied](<https://github.com/zacharied/discord-eprompt>)

### Picking the Side

`$side`

Randomly selects a side [Attackers/Defenders].

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/PmmiRVZ.gif" alt="side" height="350"/>
</details>

### Picking the Map

`$map`

Randomly selects a Valorant map.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/k7dalPJ.gif" alt="map" height="350"/>
</details>

### Move teams to different voice channels

`$move`

Click on the voice channel to move all current player in the plan.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/MATv1Io.gif" alt="play" height="350"/>
</details>

[Credit: Zacharied](<https://github.com/zacharied/discord-eprompt>)

------

## License

[MIT](https://choosealicense.com/licenses/mit/)
