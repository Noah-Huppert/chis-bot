## Chis Discord Bot

A Discord bot that provides users with a simple interface to plan pick up Valorant games.

*More information at [chis-bot](https://chis.dev/chis-bot).*

### Setup

``` bash
python3.8 -m pip install pipenv
pipenv install
```

Create a [config.json](config-example.json) file. 
This will contain the bot token, prefix, and list of owners.

Then run:

```bash
pipenv shell
./src/bot.py
```


*Please give support to [zacharied](https://github.com/zacharied) for the wonderful [Discord React-Prompt library](https://github.com/zacharied/discord-eprompt).*

## Docker Development

If Python 3.8 is not installed on your system the Docker development environment can be used.

Install Docker and Docker Compose. 

Then run:

```bash
docker-compose up -d --build
```
