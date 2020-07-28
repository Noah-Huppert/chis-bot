#!/usr/bin/env python3.8

import discord
from discord.ext import commands

import json
import os, sys
import shutil
import random
from functools import reduce
import re
from enum import Enum
import argparse
import asyncio

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('root')
log_handler = RotatingFileHandler('bot.log', maxBytes=1024*1024*5, backupCount=2)
logging.basicConfig(level=logging.INFO, handlers=[log_handler, logging.StreamHandler()])

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

# redo the help command to get rid of NoCategory
#bot.remove_command('help')

extensions = ['cogs.simple', 'cogs.game']
for ext in extensions:
    bot.load_extension(ext)

if not os.path.exists(os.path.dirname(__file__) + '/../config.json'):
    print('Token file not found. Place your Discord token ID in a file called `config.json`.', file=sys.stderr)
    sys.exit(1)

with open(os.path.dirname(__file__) + '/../config.json', 'r') as f:
    config = json.load(f)
    bot.run(config["token"])
