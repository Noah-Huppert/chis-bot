#!/usr/bin/env python3

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
        super().__init__(command_prefix='$', *args, **kwargs)

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)

    async def on_ready(self):
        logging.info(f'Logged in as "{self.user}".')


bot = ChisBot()

@bot.command()
async def hi(message):
    logging.info(f'said hello to {message.author.display_name}')
    await message.send('Sup, chad ;)')

if not os.path.exists('token.txt'):
    print('Token file not found. Place your Discord token ID in a file called `token.txt`.', file=sys.stderr)
    sys.exit(1)

with open('token.txt', 'r') as token_file:
    bot.run(token_file.read())