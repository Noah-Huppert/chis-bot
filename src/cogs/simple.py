from discord.ext import commands
import discord
import logging
import sys
import random
from data import data


class simple(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='kill', aliases=['k'], hidden=True)
    async def kill_command(self, ctx):
        """ owner command to kill the bot
        """
        if await self.bot.is_owner(ctx.message.author):
            sys.exit(0)
        logging.info(f'{ctx.author} tried to kill the bot and failed')
        await ctx.send('Weakling')

    @commands.command(name='hello', aliases=['hi'])
    async def hi_command(self, ctx):
        """ Will send a friendly message back to you.
        """
        logging.info(f'Said hello to {ctx.author.display_name}')
        await ctx.send('Sup, chad ;)')

    @commands.command(name='flip', aliases=['coin'])
    async def flip_command(self, ctx):
        """ flip a coin
        """
        coin = random.randint(0, 1)
        if coin:
            await ctx.send('Heads')
        else:
            await ctx.send('Tails')
        logging.info(f'{ctx.author} flipped a coin and got ' +
                     ('heads' if coin else f'tails'))

    @commands.command(name='roll', aliases=['dice'])
    async def roll_command(self, ctx, num: int):
        """ roll 'n' sided die
        """
        roll = random.randint(0, num)
        await ctx.send(f'Rolled: {roll}')
        logging.info(
            f'{ctx.author.display_name} rolled a "{num}" sided die and got "{roll}"')

    @commands.command(name='trans', aliases=['queen', 'king'])
    async def trans_command(self, ctx):
        """ The rat assumes their true identity.
        """
        if "Queen" in ctx.guild.me.display_name:
            await ctx.guild.me.edit(nick='Rat King')
        else:
            await ctx.guild.me.edit(nick='Rat Queen')
        logging.info(
            f'{ctx.author} changed the rats identity to "{ctx.guild.me.display_name}"')


def setup(bot):
    bot.add_cog(simple(bot))
