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

    @commands.command(name='plan', aliases=['p'])
    async def plan_command(self, ctx, spots=5, *args):
        """ takes a number of players and creates a new game.
        """
        title=""
        if len(args) > 0:
            title = ' '.join(arg for arg in args[0:])
        
        game = data(ctx.guild.id)
        game.start(spots=spots, title=title)
        logging.info(f'{ctx.author.display_name} tried to make a game')
        await self.update_message(ctx, self.print_message(game))

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
    
    @commands.command(name='rename', aliases=[])
    async def rename_command(self, ctx, *args):
        """Renames the current game"""
        game = data(ctx.guild.id)
        game.title = ""
        if len(args) > 0:
            game.title = ' '.join(arg for arg in args[0:])
        await self.update_message(ctx, self.print_message(game))

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

    @commands.command(name="team", aliases=["t"])
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
        del self.game_msg[ctx.guild.id] 

    async def select_teams(self, ctx, game: data):
        # initial captain
        game.turn = game.captains[0 % len(game.captains)]
        await self.update_message(ctx, self.print_team_message(game))

        for pick in range(game.picks):
            # get captain pick
            game.turn = game.captains[pick % len(game.captains)]

            if game.picks != 1:
                choice = await react_prompt_response(self.bot, self.bot.get_user(game.turn), self.game_msg[ctx.guild.id], reacts=self.emoji_list(game))
            else:
                choice = 0
            # add player to their team
            game.add_player(game.turn, choice)
            del self.game_msg[ctx.guild.id]

            if game.picks != 0:
                game.turn = game.captains[(pick - 1) % len(game.captains)]
            await self.update_message(ctx, self.print_team_message(game))

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
                message += (f'{self.bot.get_user(discord_id).name}')
            message += ('\n')
        message += '\n```'
        message += '**Basic Commands**: plan, add, del, show, team'
        message += '[`$help game` for more info]\n'

        return message
    
    def print_team_message(self, game: data):
        message = '⠀\n' #blank unicode character
        if game.picks != 0:
            message += f'**Turn: {self.bot.get_user(game.turn).name}**\n'
        else:
            message += f'**Teams have been selected**\n'
        
        # Free
        if game.picks != 0:
            message += '```\n'
            for spot in range(game.picks):
                message += (f'{chr(spot + 127462)}. ')
                if spot < game.picks:
                    discord_id = game.get_agent(spot)
                    message += (f'{self.bot.get_user(discord_id).name}')
                message += ('\n')
            message += '```\n'
        
        # Taken
        for cap in game.captains:
            message += '```\n'
            message += f'1. {self.bot.get_user(cap).name} (captain)\n'
            for spot in range(int(game.spots/len(game.captains)) - 1):
                message += (f'{spot + 2}. ')
                if spot < game.team_size(cap):
                    discord_id = game.get_player(cap, spot)
                    message += (f'{self.bot.get_user(discord_id).name}')
                message += ('\n')
            message += '\n```'
        if game.picks == 0:
            message += f'**{self.bot.get_user(game.turn).name} picked last, they get priority picking sides.**\n'

        return message

    async def update_message(self, ctx, message):
        if  ctx.guild.id in self.game_msg:
            await self.game_msg[ctx.guild.id].delete()
        else:
            logging.info(f'No game message found on {ctx.guild.name}, printing new one')
        self.game_msg[ctx.guild.id] = await ctx.send(message)
    
    def emoji_list(self, game: data):
        emojis = {}
        for index in range(game.picks):
            emojis[chr(index + A_EMOJI)] = index
        return emojis

def setup(bot):
    bot.add_cog(game(bot))
