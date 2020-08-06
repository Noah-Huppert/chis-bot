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

```
# bot commands
game:
  add    @users to add them to the game.
  del    @users to remove them from the game
  map    picks a Valorant map
  move   move gamers to a voice channel
  plan   takes a number of players and creates a new game.
  play   moves teams to respective voice channels
  rename Renames the current game
  show   display current gamers
  side   picks a side Attackers/Defenders
  team   @captains to start team selection
simple:
  flip   flip a coin
  hello  Will send a friendly message back to you.
  roll   roll 'n' sided die
  trans  The rat assumes their true identity.
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
