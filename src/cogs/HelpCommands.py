from discord.ext import commands
import discord
import logging

class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #These are dumb
    # @commands.group(name='helpcmd', invoke_without_command=True)
    # async def helpcommand(self, ctx):
    #     await ctx.send("Base help command. Subcommands: game, simple")
    
    # @helpcommand.command(name="game")
    # async def game_subcommand(self, ctx):
    #     await ctx.channel.send("This is the game subcommand, \
    #     all info about the game command should go here")

def setup(bot):
    bot.add_cog(HelpCommands(bot))
