from discord.ext import commands
import discord
import logging
import json
import os

from data import data
from discord_eprompt import ReactPromptPreset, react_prompt_response

A_EMOJI = 127462

class game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot= bot
        self.game = data(filename="game_data")
        self.game_msg = None

    def print_message(self):
        message = '⠀\n' #blank unicode character
        if self.game.getGame() != "":
            message += f'**{self.game.getGame()} **\n'
        message += f'**Gamers**\n'
        message += '```\n'
        for spot in range(self.game.getSpots()):
            message += (f'{spot + 1}. ')
            if spot < self.game.getPeople():
                message += (f'{self.game.getGamer(spot)}')
            message += ('\n')
        message += '\n```'
        message += '**Basic Commands**: plan, add, del, show, team '
        message += '[`$help game` for more info]\n'

        return message
    
    def print_team_message(self, captains, turn):
        message = '⠀\n' #blank unicode character
        if self.game.getPicks() != 0:
            message += f'**Turn: {turn.display_name}**\n'
        else:
            message += f'**Teams have been selected**\n'
        
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
    
    def emoji_list(self):
        emojis = {}
        for index in range(self.game.getPicks()):
            emojis[chr(index + A_EMOJI)] = index
        return emojis

    # TODO add support for multiple games (waaayy later on)
    @commands.command(name='plan', aliases=['p'])
    async def plan_command(self, ctx, spots=5, *args):
        """ takes a number of players and creates a new game.
        """
        game=""
        if len(args) > 0:
            game = ' '.join(arg for arg in args[0:])

        self.game.start(spots=spots, game=game)
        logging.info(f'{ctx.author.display_name} tried to make a game')
        await self.update_message(ctx, self.print_message())

    @commands.command(name='add', aliases = ['a', 'join'])
    async def add_command(self, ctx, *args: discord.User):
        """ @users to add them to the game.
        """
        if len(args) == 0:
            args = [ctx.author]

        for user in args:
            if self.game.getPeople() < self.game.getSpots():
                if self.game.addGamer(user):
                    await self.update_message(ctx, self.print_message())
                else:
                    await ctx.send(f'{user} is already a gamer.')
            else:
                await ctx.send(f'Cannot add {user}, too many gamers.')
        
    @commands.command(name='del', aliases=['delete', 'd', 'remove', 'leave'])
    async def remove_command(self, ctx, *args: discord.User):
        """ @users to remove them from the game
        """
        if len(args) == 0:
            args = [ctx.author]

        for user in args:
            if self.game.delGamer(user):
                await self.update_message(ctx, self.print_message())
            else:
                await ctx.send(f'{user} is not a gamer.')
    
    @commands.command(name='rename', aliases=['r'])
    async def rename_command(self, ctx):
        """Renames the current game"""
        pass


    # TODO for user in team if user in voice channel move to correct voice chat
    # TODO implement a normie check (if all users are mormies, add to private voice channel)
    @commands.command(name='move', aliases=["transfer", "teamspeak", "m"])
    async def move_command(self, ctx):
        """ Moves users from second team to a second voice channel
        """
        pass

    @commands.command(name='show', aliases = ['s', 'list', 'print', 'display'])
    async def print_command(self, ctx):
        """ display current gamers
        """
        await self.update_message(ctx, self.print_message())

    # TODO initial pick should be random
    @commands.command(name="team", aliases=["t", "pick"])
    async def team_command(self, ctx, *args: discord.User):
        """ @captains to start team selection
        """
        if len(args) == 0:
            await ctx.send("Please enter team captains")
            return
        if len(args) == 1:
            await ctx.send("Please enter more than one captain")
            return
        if len (set(args)) != len(args):
                await ctx.send("Captains must be different")
                return

        self.game.setCaptians(args)
        await self.select_teams(ctx, args)
        self.game_msg = None

    async def select_teams(self, ctx, captains):
        await self.update_message(ctx, self.print_team_message(captains, captains[0]))
        for pick in range(self.game.getSpots() - 2):
            # get captain pick
            if pick != (self.game.getSpots() - 3):
                choice = await react_prompt_response(self.bot, captains[pick % len(captains)], self.game_msg, reacts=self.emoji_list())
            else:
                choice = 0
            # add player to their team
            self.game.addPlayer(captains, pick, choice)
            self.game_msg = None
            await self.update_message(ctx, self.print_team_message(captains, captains[(pick + 1) % (len(captains))]))
   
def setup(bot):
    bot.add_cog(game(bot))
