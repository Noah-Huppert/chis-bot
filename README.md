# Chis Discord Bot

A Discord bot that provides users with a simple interface to plan pick up Valorant games.

*More information at [chis-bot](https://chis.dev/chis-bot).*

## Setup

1. Install Python dependencies
   ``` bash
   python3 -m pip install pipenv
   pipenv install
   ```
2. Setup a Discord API Application  
   2.1. Create a new application on the [Discord Developer Portal](https://discord.com/developers/applications)  
   2.2. Create a Bot for your application, make note of this value for the config file  
   2.3. Authenticate your bot with Discord servers you want it to operate within using the OAuth2 page  
      - Select the Scopes: `bot`, `applications.commands`  
	  - Select bot Bot Permissions:  
	     - General Permissions: `Manage Channels`, `View Channels`  
		 - Text Permissions: `Send Messages`, `Public Threads`, `Embed Links`, `Add Reactions`, `Use Slash Commands`  
		 - Voice Permissions: `Move Members`  
    2.4. Then click the "Copy" button to copy the Discord OAuth2 invite URL. Open this URL in a new tab and complete the dialog.  
2. Create a `config.json` from `config-example.json`  
   This will contain the bot token, prefix, and list of owners.  
3. Run the bot.  
   ```bash
   ./dev.sh
   ```


*Please give support to [zacharied](https://github.com/zacharied) for the wonderful [Discord React-Prompt library](https://github.com/zacharied/discord-eprompt).*

## Docker Development

A development environment can be run using Docker Compose.

Install Docker and Docker Compose. 

- To start the development container:
  ```bash
  docker-compose up -d --build
  ```
- View logs:
  ```bash
  docker-compose logs -f --tail=20 bot
  ```
- Open a debugging shell:
  ```bash
  docker-compose run --entrypoint bash bot
  ```
