from discord.ext import tasks, commands
import discord
from data import data
import datetime
from utils import closest_user, guild_birthdays_message, update_message
from datetime import datetime as dt
from dateutil import parser
import logging
import asyncio
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.model import SlashCommandOptionType

""" The hour of day at which birthday notifications will be sent out.
"""
BIRTHDAY_NOTIFY_HOUR = 8

class info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}
        self.bday_messages = {}
        self.notify_birthday.start()

    @cog_ext.cog_slash(name="birthday",
                       description="Get/set a user's birthday.",
                       options=[
                           create_option(
                               name="user",
                               description="The user's birthday to view/change.",
                               option_type=SlashCommandOptionType.USER,
                               required=True
                           ),
                           create_option(
                               name="birthday",
                               description="The users birthday. (mm/dd/yyy)",
                               option_type=SlashCommandOptionType.STRING,
                               required=False,
                           )
                       ])
    async def birthday_command(self, ctx, user: discord.User = None, birthday=""):
        """ get/set users birthday
        """

        logging.info(f'{ctx.author} tried to use the "birthday" command')

        info = data(ctx.guild)

        if birthday == "":
            if info.get_birthday(user) is not None:
                await ctx.send(f'{user.display_name}\'s birthday is `{info.get_birthday(user).strftime("%m/%d/%Y")}`')
            else:
                await ctx.send(f'Please set {user.display_name}\'s birthday')
            return

        try:
            birthday = parser.parse(birthday)
        except parser.ParserError:
            await ctx.send("Incorrect birthday format, try `month-day-year`")
            return

        info.set_birthday(user, birthday)

        logging.info(f'{user} birthday is now {info.get_birthday(user)}')
        await ctx.send(f'Set {user.display_name}\'s birthday to `{info.get_birthday(user).strftime("%m/%d/%Y")}`')

    @tasks.loop(hours=1)
    async def notify_birthday(self):
        current = dt.now()

        for guild in self.bot.guilds:
            info = data(guild)
            birthday_channel = self.bot.get_channel(info.get_command('birthday'))
            irl_birthday_channel = self.bot.get_channel(info.get_command('birthday_irl'))

            if birthday_channel is None:
                logging.info(
                    f'No channel to send "bday" command on {guild.name}')
                return

            for user in info.info:
                birthday = info.get_birthday(user)

                # Notify channel that it is a users birthday
                if birthday.month == current.month and birthday.day == current.day and current.hour == BIRTHDAY_NOTIFY_HOUR:
                    logging.info(
                        f'It\'s {user}\'s birthday on {guild.name}!!')
                    irl = False
                    for role in user.roles:
                        if role.id == info.get_command('irl_role'):
                            irl = True
                    if irl:
                        await irl_birthday_channel.send(f'⠀\n**🎉🎉🎉 Happy Birthday <@!{user.id}> 🎉🎉🎉**')
                    else:
                        await birthday_channel.send(f'⠀\n**🎉🎉🎉 Happy Birthday <@!{user.id}> 🎉🎉🎉**')

    @notify_birthday.before_loop
    async def before_notify_birthday(self):
        await self.bot.wait_until_ready()
        now = dt.now()

        today_top_of_hour = now.replace(hour=BIRTHDAY_NOTIFY_HOUR,
            minute=0, second=0, microsecond=0)

        offset = today_top_of_hour - now

        if offset.total_seconds() < 0:
            next_day_top_of_hour = now.replace(hour=BIRTHDAY_NOTIFY_HOUR,
                minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
            
            offset = next_day_top_of_hour - now

        logging.debug(f"sleeping for {str(offset.total_seconds())} so birthday notification is sent at the top of the hour")
        await asyncio.sleep(offset.total_seconds())
