from discord.ext import commands
import discord
import logging
import random
from data import data
from games import blackjack
from utils import emoji_list, closest_user, update_message
from discord_eprompt import ReactPromptPreset, react_prompt_response


class game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="blackjack")
    async def blackjack_command(self, ctx):
        blackjack.start()