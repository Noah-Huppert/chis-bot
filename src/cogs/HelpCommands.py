from discord.ext import commands
import discord
import logging

class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
def setup(bot):
    bot.add_cog(HelpCommands(bot))