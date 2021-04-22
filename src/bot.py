#!/usr/bin/env python3.8
import discord
from discord.ext import commands
from discord_slash import SlashCommand # Importing the newly installed library.


import json
import os
import sys
import argparse
import asyncio

from cogs import simple, info, match, wallet, game, slash_match

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('root')

logging.basicConfig(level=logging.INFO,
                    handlers=[logging.StreamHandler()],
                    format="%(asctime)s %(levelname)s: [%(funcName)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")


class ChisBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)

    async def on_ready(self):
        logging.info(f'Logged in as "{self.user}".')
        # Setting `Playing ` status
        #await bot.change_presence(activity=discord.Game(name="$plan"))

        # Setting `Streaming ` status
        #await bot.change_presence(activity=discord.Streaming(name="$plan", url="my_twitch_url"))

        # Setting `Listening ` status
        #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a song"))

        # Setting `Watching ` status
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=" for /plan"))


        



with open(os.path.dirname(__file__) + '/../config.json', 'r') as f:
    config = json.load(f)
    # intents make everything
    bot = ChisBot(command_prefix=config["prefix"], owner_ids=config["owners"], intents=discord.Intents.all(), help_command=None)
    slash = SlashCommand(bot, sync_commands=True)


bot.add_cog(simple.simple(bot))
bot.add_cog(info.info(bot))
#bot.add_cog(match.match(bot))
bot.add_cog(game.game(bot))

# Testing
bot.add_cog(slash_match.match(bot))


if os.path.exists(os.path.dirname(__file__) + '/../rat-king.prod.client-config.json'):
    bot.add_cog(wallet.wallet(bot))
else:
    logging.warning("Not wallet config found, wallet service not loaded")

if not os.path.exists(os.path.dirname(__file__) + '/../config.json'):
    print('Token file not found. Place your Discord token ID in a file called `config.json`.', file=sys.stderr)
    sys.exit(1)

with open(os.path.dirname(__file__) + '/../config.json', 'r') as f:
    config = json.load(f)
    bot.run(config["token"])
