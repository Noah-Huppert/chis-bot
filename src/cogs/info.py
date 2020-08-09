from discord.ext import tasks, commands
import discord
from data import data
import datetime
from utils import days_left, BIRHDAY_RANGE_IN_DAYS
from datetime import datetime as dt
from dateutil import parser
import logging



class info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}
        self.notify_birthday.start()

    # TODO dynamically change BIRTHDAY_RANGE_IN_DAYS
    @commands.command(name='birthday', aliases=['bday'])
    async def birthday_command(self, ctx, user: discord.User, *args):
        """ get/set @users birthday
        """
        info = data(ctx.guild.id)
        
        if user == self.bot.user:
            curr = datetime.datetime.now()
            message = '⠀\n'  # blank unicode character
            message += f'**🎊All Birthdays in the next {BIRHDAY_RANGE_IN_DAYS} days🎊**\n'
            message += '```\n'

            members_with_no_bday = filter(lambda user: info.get_birthday(user.id) is not None, ctx.guild.members)
            sorted_members = sorted(members_with_no_bday, key=lambda user: days_left(info.get_birthday(user.id)))

            for member in sorted_members: #REPLACE ctx.guild.members with the sorted list
                    bday = info.get_birthday(member.id)
                    bday_days_left = days_left(bday)
                    if  bday_days_left <= BIRHDAY_RANGE_IN_DAYS:
                        if bday.replace(year= curr.year) > curr:
                            message += f'🔸 {member.display_name}:\n   turning {curr.year - bday.year} in {bday_days_left} days ({info.get_birthday(member.id).strftime("%B %d")}) \n\n'
                        else:
                            message += f'🔸 {member.display_name}:\n   turning {curr.year - bday.year + 1} in {bday_days_left} days ({info.get_birthday(member.id).strftime("%B %d")}) \n\n'
            message += '```'
            await ctx.send(message)
            return
        
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

    @tasks.loop(hours=24)
    async def notify_birthday(self):
        current = dt.now()

        for guild in self.bot.guilds:
            info = data(guild.id)
            try:
                channel = self.bot.get_channel(info.get_command('birthday'))
            except KeyError:
                logging.info(
                    f'No channel to send "bday" command on {guild.name}')
                return
            for user in info.info:
                birthday = info.get_birthday(user)

                # Notify channel that it is a users birthday
                if birthday.month == current.month and birthday.day == current.day:
                    logging.info(
                        f'It\'s {self.bot.get_user(user)}\'s birthday on {guild.name}!!')
                    await channel.send(f'⠀\n**🎉🎉🎉 Happy Birthday <@!{self.bot.get_user(user).id}> 🎉🎉🎉**')

    @notify_birthday.before_loop
    async def before_notify_birthday(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(info(bot))
