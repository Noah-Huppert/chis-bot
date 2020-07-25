from discord.ext import commands
import discord
import logging
import json
import os

# this made GameData work, now I don't need it?
# import os,sys,inspect
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0,parentdir) 

from data.GameData import GameData
from discord_eprompt import ReactPromptPreset, react_prompt_response

class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot= bot
        self.game = GameData(filename="game_data")
        self.game_msg = None

    def print_message(self):
        message = 'These are the current users in the party'
        message += '```\n'
        for spot in range(self.game.getSpots()):
            message += (f'{spot + 1}. ')
            if spot < self.game.getPeople():
                message += (f'{self.game.getGamer(spot)}')
            message += ('\n')
        message += '\n```'
        return message
    
    # TODO
    # print who's turn
    # once picks are up print end message
    # captain should be at top of list (bolded)
    def print_team_message(self, captains, turn):
        
        if self.game.getPicks() != 0:
            message = f'**Turn: {turn.display_name}**\n'
        else:
            message = f'**Teams have been selected**\n'
        
        # Free
        if self.game.isAgent():
            message += '```\n'
            for spot in range(self.game.getPicks()):
                message += (f'{chr(spot + 127462)}. ')
                if spot < self.game.getPicks():
                    message += (f'{self.game.getAgent(spot)}')
                message += ('\n')
            message += '```\n'
        
        # Taken
        for cap in captains:
            message += '```\n'
            message += f'1. {cap.display_name} (captain)\n'
            for spot in range(int(self.game.getSpots()/len(captains)) - 1):
                message += (f'{spot + 2}. ')
                if spot < self.game.teamSize(cap):
                     message += (f'{self.game.getPlayer(cap, spot)}')
                message += ('\n')
            message += '\n```'

        return message

    async def update_message(self, ctx, message):
        if self.game_msg is not None:
            logging.info('deleting game message')
            await self.game_msg.delete()
        self.game_msg = await ctx.send(message)
    
    # TODO remove hard coded number - zach day
    def emoji_list(self):
        emojis = {}
        for index in range(self.game.getPicks()):
            emojis[chr(index + 127462)] = index
        return emojis

    # TODO add support for multiple games (waaayy later on)
    @commands.command(name='game', aliases=['plan', 'p', "g"])
    async def game_command(self, ctx, spots=5):
        """ This command takes a number of players and establishes a new game.
        """
        self.game.start(spots)
        logging.info(f'{ctx.author.display_name} tried to make a game')
        await self.update_message(ctx, self.print_message())

    # TODO catch BadArgument Error when someone passes in a non user argument
    @commands.command(name='add', aliases = ["a"])
    async def add_command(self, ctx, *args: discord.User):
        """ This command requires @ing a discord user id to add them to the plan. If there are too many people in the party, you have to remove someone to add more
        """
        for user in args:
            if self.game.getPeople() < self.game.getSpots():
                if self.game.addGamer(user):
                    await self.update_message(ctx, self.print_message())
                else:
                    await ctx.send(f'{user} is already a gamer.')
            else:
                await ctx.send(f'Cannot add {user}, too many gamers.')
        
    @commands.command(name='del', aliases=["delete", "d", "remove"])
    async def remove_command(self, ctx, *args: discord.User):
        """ This command takes a discord id and deletes them from the plan.
        """
        for user in args:
            if self.game.delGamer(user):
                await self.update_message(ctx, self.print_message())
            else:
                await ctx.send(f'{user} is not a gamer.')
        
    @commands.command(name="show", aliases = ["s", "list", "print"])
    async def print_command(self, ctx):
        """ This command shows the list of players currently added to the match.
        """
        await self.update_message(ctx, self.print_message())

    @commands.command(name="team", aliases=["t", "pick"])
    async def team_command(self, ctx, *args: discord.User):
        """ This command will initiate the process of team selection. It takes two discord ids with the command as the two team captains. The first id has first pick in team selection.
        """
        if len(args) == 0:
            await ctx.send("Please enter team captains")
            return
        if len (set(args)) != len(args):
                await ctx.send("Captains must be different")

        self.game.setCaptians(args)
        await self.select_teams(ctx, args)
        self.game_msg = None

    #TODO enforce more than one captain
    async def select_teams(self, ctx, captains):
        await self.update_message(ctx, self.print_team_message(captains, captains[0]))
        for pick in range(self.game.getSpots()- 2):
            # get captain pick
            choice = await react_prompt_response(self.bot, captains[pick % len(captains)], self.game_msg, reacts=self.emoji_list())
            # add player to their team
            self.game.addPlayer(captains, pick, choice)
            self.game_msg = None
            await self.update_message(ctx, self.print_team_message(captains, captains[(pick + 1) % (len(captains))]))
   
def setup(bot):
    bot.add_cog(GameCommands(bot))
