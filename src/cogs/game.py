from discord.ext import commands
import discord
import logging
import json
import os
import random

from data import data
from discord_eprompt import ReactPromptPreset, react_prompt_response

A_EMOJI = 127462
MAPS = ['Haven', 'Split', 'Ascent', 'Bind']

class game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot= bot
        self.game_msg = {}

    @commands.command(name='plan', aliases=['p'])
    async def plan_command(self, ctx, spots=5, *args):
        """ takes a number of players and creates a new game.
        """
        title=""
        game = data(ctx.guild.id)
        if len(args) > 0:
            title = ' '.join(arg for arg in args[0:])

        game.start(spots=spots, title=title)
        logging.info(f'{ctx.author.display_name} tried to make a game')
        await self.update_message(ctx, self.print_message(game))

    def print_message(self, game: data):
        message = '⠀\n' #blank unicode character
        if game.title != "":
            message += f'**{game.title} **\n'
        message += f'**Gamers**\n'
        message += '```\n'
        for spot in range(game.spots):
            message += f'{spot + 1}. '
            if spot < game.people:
                # correctly print user, even if name changes
                discord_id = game.get_gamer(spot)
                user = self.bot.get_user(discord_id)
                message += (f'{user.display_name}')
            message += ('\n')
        message += '\n```'
        message += '**Basic Commands**: plan, add, del, show, team'
        message += '[`$help game` for more info]\n'

        return message
    
    def print_team_message(self, data):
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
        if self.game.getPicks() == 0:
            message += f'**{turn.display_name} picked last, they get priority picking sides.**\n'

        return message

    async def update_message(self, ctx, message):
        try:
            del self.game_msg[ctx.guild.id]
        except KeyError:
            logging.info("No game message found on server, printing new one")
        self.game_msg[ctx.guild.id] = await ctx.send(message)
    
    def emoji_list(self):
        emojis = {}
        for index in range(self.game.getPicks()):
            emojis[chr(index + A_EMOJI)] = index
        return emojis

    @commands.command(name='add', aliases = ['a', 'join'])
    async def add_command(self, ctx, *args: discord.User):
        """ @users to add them to the game.
        """
        game = data(ctx.guild.id)
        if len(args) == 0:
            args = [ctx.author]

        for user in args:
            if game.people < game.spots:
                if game.add_gamer(user):
                    await self.update_message(ctx, self.print_message(game))
                else:
                    await ctx.send(f'{user} is already a gamer.')
            else:
                await ctx.send(f'Cannot add {user}, too many gamers.')
        
    @commands.command(name='del', aliases=['delete', 'd', 'remove', 'leave'])
    async def remove_command(self, ctx, *args: discord.User):
        """ @users to remove them from the game
        """
        game = data(ctx.guild.id)
        if len(args) == 0:
            args = [ctx.author]

        for user in args:
            if game.del_gamer(user):
                await self.update_message(ctx, self.print_message(game))
            else:
                await ctx.send(f'{user} is not a gamer.')
    
    @commands.command(name='rename', aliases=['r'])
    async def rename_command(self, ctx):
        """Renames the current game"""
        pass


    # TODO for user in team if user in voice channel move to correct voice chat
    # TODO implement a normie check (if all users are normies, add to private voice channel)
    @commands.command(name='move', aliases=["transfer", "teamspeak", "m"])
    async def move_command(self, ctx):
        """ Moves users from second team to a second voice channel
        """
        pass

    @commands.command(name='show', aliases = ['s', 'list', 'print', 'display'])
    async def print_command(self, ctx):
        """ display current gamers
        """
        game = data(ctx.guild.id)
        await self.update_message(ctx, self.print_message(game))

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
        game = data(ctx.guild.id)
        game.captains = args
        await self.select_teams(ctx, game)
        self.game_msg = None

    async def select_teams(self, ctx, game: data):
        # offset = random.randint(0,300)
        await self.update_message(ctx, self.print_team_message(game))
        for pick in range(game.picks):
            # get captain pick
            if pick != (game.spots - (len(game.captains) + 1)):
                choice = await react_prompt_response(self.bot, game.turn, self.game_msg, reacts=self.emoji_list())
            else:
                choice = 0
            # add player to their team
            self.game.addPlayer(captains, (offset + pick), choice)
            self.game_msg = None

            if pick == self.game.getSpots() - (len(captains) + 1):
                await self.update_message(ctx, self.print_team_message(captains, captains[(offset + pick) % (len(captains))]))
            else:
                await self.update_message(ctx, self.print_team_message(captains, captains[(offset + pick + 1) % (len(captains))]))

    @commands.command(name='side')
    async def side_command(self, ctx):
        """ picks a side Attackers/Defenders
        """
        if random.randint(0,1) == 0:
            await ctx.send('Attackers')
            return
        await ctx.send('Defenders')
    
    @commands.command(name='map')
    async def map_command(self, ctx):
        """ picks a Valorant map
        """
        await ctx.send(random.choice(MAPS))

def setup(bot):
    bot.add_cog(game(bot))
