# Chis Discord Bot

A simple chis bot.


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

See [config.json.example](config.json.example).


## Run

`./src/bot.py`

## Usage

```
game:
  add    @users to add them to the game.
  del    @users to remove them from the game
  move   Moves users from second team to a second voice channel
  plan   takes a number of players and creates a new game.
  rename Renames the current game
  show   display current gamers
  team   @captains to start team selection
simple:
  hello  Will send a friendly message back to you.
  pet    Bellies out.
  trans  The rat assumes their true identity.
  user   Is this you dawg?
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
