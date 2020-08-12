#!/usr/bin/env python3.8
import discord
from discord.ext import commands

import json
import os
import sys
import argparse
import asyncio

from cogs import simple, info, game, wallet

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('root')

file_handler = RotatingFileHandler(
    'bot.log', maxBytes=1024*1024*5, backupCount=2)

logging.basicConfig(level=logging.INFO,
                    handlers=[file_handler, logging.StreamHandler()],
                    format="%(asctime)s %(levelname)s: [%(funcName)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")

class ChisBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)

    async def on_ready(self):
        logging.info(f'Logged in as "{self.user}".')


with open(os.path.dirname(__file__) + '/../config.json', 'r') as f:
    config = json.load(f)
    bot = ChisBot(command_prefix=config["prefix"], owner_ids=config["owners"])


bot.add_cog(simple.simple(bot))
bot.add_cog(info.info(bot))
bot.add_cog(game.game(bot))

if os.path.exists(os.path.dirname(__file__) + '/../rat-king.prod.client-config.json'):
    bot.add_cog(wallet.wallet(bot))
else:
    logging.warn("Not wallet config found, wallet service not loaded")

if not os.path.exists(os.path.dirname(__file__) + '/../config.json'):
    print('Token file not found. Place your Discord token ID in a file called `config.json`.', file=sys.stderr)
    sys.exit(1)

with open(os.path.dirname(__file__) + '/../config.json', 'r') as f:
    config = json.load(f)
    bot.run(config["token"])
