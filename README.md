## Chis Discord Bot

**Chis Bot** is a Discord bot that provides users with a simple interface to plan pick up Valorant games.

Once **Chis Bot** becomes verified on the [Riot Developer Portal](https://developer.riotgames.com/), the API's match statistics will aid in team selections.
  
### Setup

``` bash
python3.8 -m pip install pipenv
pipenv install
```

Create a [config.json](chis-bot/blob/master/config-example.json) file. 
This will contain the bot token, prefix, and list of owners.

[`./run.sh`](chis-bot/blob/master/run.sh)

### Usage

#### Create a plan

```bash
$plan [spots=5] [name=""]
#Only one plan can exist at a time
```

Takes in a number of players, creates a new game.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/aWKH89w.gif" alt="plan" height="350"/>
</details>

#### Add users to the plan

```bash
$add [users]
#Accepted types: @Name, Name, "Name With Spaces*
```

Add users by @tag or by typing the display name. If display name has spaces wrap in double quotes.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/0wkp11u.gif" alt="add" height="350"/>
</details>

#### Delete users from the plan

```bash
$delete [users]
#Accepted types: @Name, Name, "Name With Spaces*
```

Delete users by @tag or by typing the display name. If display name has spaces wrap in double quotes.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/ZDl7cuw.gif" alt="delete" height="350"/>
</details>

#### Start the team selection

```bash
$team [users]
#Accepted types: @Name, Name, "Name With Spaces"
```

Give a list of valid captains to start team selection.

Notes:

- More than two captains can be selected
- Captains **must** be part of the plan

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/3xAfZVe.gif" alt="team1" height="350"/>
</details>

##### Select team members

 When prompted, captains must click on the letter corresponding to the player they want added to their roster.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/3WUbvAT.gif" alt="team2" height="350"/>
</details>

*Please give support to [zacharied](https://github.com/zacharied) for the wonderful [Discord React-Prompt library](https://github.com/zacharied/discord-eprompt).*

#### Move teams to seperate voice channels

`$play`

When prompted, click on the letter corresponding to the correct voice channel to move each team.

<details>
    <summary>Example</summary>
    <img src="https://i.imgur.com/MATv1Io.gif" alt="play" height="350"/>
</details>

*Please give support to [zacharied](https://github.com/zacharied) for the wonderful [Discord React-Prompt library](https://github.com/zacharied/discord-eprompt).*
