from discord.ext import commands
import discord
from data import data
from dateutil import parser
import logging

class info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}

    
    @commands.command(name='birthday', aliases = [])
    async def birthday_command(self, ctx, user: discord.User, *args):
        """ get/set @users birthday
        """
        # if user is None:
        #     user = ctx.author.id

        if len(args) > 0:
            birthday = ' '.join(arg for arg in args[0:])
            birthday = parser.parse(birthday)
            logging.info(birthday)
        info = data(ctx.guild.id)
        # await self.update_message(ctx, self.print_message(info))
    
    async def update_message(self, ctx, message):
        if  ctx.guild.id in self.info_msg:
            await self.game_msg[ctx.guild.id].delete()
        else:
            logging.info(f'No info message found on {ctx.guild.name}, printing new one')
        self.info_msg[ctx.guild.id] = await ctx.send(message)


def setup(bot):
    bot.add_cog(info(bot))