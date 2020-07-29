from discord.ext import commands
import discord
import logging
import sys
import random

class simple(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='kill', alias=['k'], hidden=True)
    async def kill_command(self,ctx):
        """ owner command to kill the bot
        """
        if await self.bot.is_owner(ctx.message.author):
            sys.exit(0)
        await ctx.send('Weakling')

    @commands.command(name='hello', aliases=['hi'])
    async def hi_command(self, ctx):
        """ Will send a friendly message back to you.
        """
        logging.info(f'Said hello to {ctx.author.display_name}')
        await ctx.send('Sup, chad ;)')

    @commands.command(name='flip', alias=['f', 'c', 'coin'])
    async def flip_command(self, ctx):
        """ flip a coin
        """
        if random.randint(0,1) == 0:
            await ctx.send('Heads')
        await ctx.send('Tails')

    @commands.command(name='roll', alias= ['r'])
    async def roll_command(self, ctx, num: int):
        """ roll 'n' sided die
        """
        await ctx.send(f'Rolled: {random.randint(0,num)}')
    
    @commands.command(name='trans', aliases=['queen', 'king'])
    async def trans_command(self, ctx):
        """ The rat assumes their true identity.
        """
        logging.info(f'I am {ctx.guild.me.display_name}')
        me = ctx.guild.me
        if "Queen" in ctx.guild.me.display_name:
            await ctx.guild.me.edit(nick='Rat King')
        else:
            await ctx.guild.me.edit(nick='Rat Queen')

def setup(bot):
    bot.add_cog(simple(bot))



