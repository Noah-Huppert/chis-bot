from discord.ext import tasks, commands 
import discord
from data import data
import datetime
from datetime import datetime as dt
from dateutil import parser
import logging

class info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}
        self.notify_birthday.start()

    @commands.command(name='birthday', aliases=['bday'])
    async def birthday_command(self, ctx, user: discord.User, *args):
        """ get/set @users birthday
        """
        info = data(ctx.guild.id)

        if len(args) == 0:
            try:
                await ctx.send(f'{user.display_name}\'s birthday is `{info.get_birthday(user.id).strftime("%m/%d/%Y")}`')
            except KeyError:
                await ctx.send(f'Please set {user.display_name}\'s birthday')
            return

        birthday = ' '.join(arg for arg in args[0:])

        try:
            birthday = parser.parse(birthday)
        except parser.ParserError:
            await ctx.send("Incorrect birthday format, try `month-day-year`")
            return

        info.set_birthday(user.id, birthday)

        logging.info(f'{user} birthday is now {info.get_birthday(user.id)}')
        await ctx.send(f'Set {user.display_name}\'s birthday to `{info.get_birthday(user.id).strftime("%m/%d/%Y")}`')

    #86400 seconds in a day
    @tasks.loop(seconds=15)
    async def notify_birthday(self):
        # TODO fix datetime syntax
        current = dt.now()
        offset = dt.now() + datetime.timedelta(days = 3)
        time_range = offset.timestamp() - current.timestamp() 
        
        # TODO replace with data file (set command)
        channel = self.bot.get_channel(724656035373121558)
        
        
        #TODO Notify 3 days before bday and on bday
        for guild in self.bot.guilds:
            info = data(guild.id)
            for user in info.info:
                birthday = info.get_birthday(user)
                propagated_birthday = birthday.replace(year=current.year)
                if  propagated_birthday > current and propagated_birthday.timestamp() - current.timestamp() < time_range:
                    logging.info('It\'s someones birthday!!')
                    await channel.send(f'{self.bot.get_user(user).display_name}\'s birthday is in less than 3 days!!!')

    @notify_birthday.before_loop
    async def before_notify_birthday(self):
        await self.bot.wait_until_ready()
    
def setup(bot):
    bot.add_cog(info(bot))

