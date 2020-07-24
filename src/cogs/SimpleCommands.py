from discord.ext import commands
import discord
import logging

class SimpleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot= bot

    @commands.command(name='hello', aliases=['hi'])
    async def hi_command(self, ctx):
        """ Will send a friendly message back to you.
        """
        logging.info(f'Said hello to {ctx.author.display_name}')
        await ctx.send('Sup, chad ;)')

    @commands.command(name='pet', aliases=['woof'])
    async def pet_command(self, ctx):
        """ Bellies out.
        """
        logging.info(f'{ctx.author.display_name} tried to pet me')
        try:
            await ctx.author.edit(nick="dummy")
        except discord.Forbidden:
            logging.info(f'Cannot rename {ctx.author.display_name}')
        await ctx.send(f'I\'m not a dog, {ctx.author.display_name}.')
    
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

    @commands.command(name='user')
    async def user_command(self, ctx, user: discord.User):
        """ Is this you dawg?
        """
        logging.info(user)
        if user == ctx.author:
            await ctx.send(f'You are {user}')
        else:
            await ctx.send(f'Not you')

def setup(bot):
    bot.add_cog(SimpleCommands(bot))



