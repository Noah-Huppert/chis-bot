from discord.ext import tasks, commands
import discord
from data import data
import datetime
from utils import closest_user, guild_birthdays_message, update_message
from datetime import datetime as dt
from dateutil import parser
import logging


class info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}
        self.bday_messages = {}
        self.notify_birthday.start()

    @commands.command(name='embed', aliases=[])
    async def embed_command(self, ctx):
        embed=discord.Embed(title="TTT2 Tonight", description="", color=0xff00d4)
        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/", icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

        embed.add_field(name="Gamers", value="1. <@219152343588012033> \n2. <@!106973822896320512> \n3. <@410992680873623552> \n4. <@!262798724428726282>", inline=False)
        embed.add_field(name="Gamers", value=":regional_indicator_a: - <@219152343588012033> \n:regional_indicator_b: - <@!106973822896320512> \n:regional_indicator_c: - <@410992680873623552> \n:regional_indicator_d: - <@!262798724428726282>", inline=False)
        
        embed.add_field(name="<@219152343588012033> Team", value="1. <@219152343588012033> \n2. <@!106973822896320512> \n3. <@410992680873623552> \n4. <@!262798724428726282>", inline=False)

        embed.set_footer(text="Basic Commands: $add, $addall, $del, $team, $play, $move")
        await ctx.send(embed=embed)

    @commands.command(name='birthday', aliases=['bday'])
    async def birthday_command(self, ctx, user, *args):
        """ get/set @users birthday
        """

        logging.info(f'{ctx.author} tried to use the "birthday" command')

        info = data(ctx.guild)
        user = closest_user(user, ctx.guild)

        if user is None:
            await ctx.send('User not found')
            return

        if user == self.bot.user:
            try:
                await update_message(ctx, self.bday_messages, guild_birthdays_message(ctx.guild, next(iter(map(int, args)), None)))
            except ValueError:
                await ctx.send('Please give a valid day range (0 - 365)')
            return

        if len(args) == 0:
            if info.get_birthday(user) is not None:
                await ctx.send(f'{user.display_name}\'s birthday is `{info.get_birthday(user).strftime("%m/%d/%Y")}`')
            else:
                await ctx.send(f'Please set {user.display_name}\'s birthday')
            return

        birthday = ' '.join(arg for arg in args[0:])

        try:
            birthday = parser.parse(birthday)
        except parser.ParserError:
            await ctx.send("Incorrect birthday format, try `month-day-year`")
            return

        info.set_birthday(user, birthday)

        logging.info(f'{user} birthday is now {info.get_birthday(user)}')
        await ctx.send(f'Set {user.display_name}\'s birthday to `{info.get_birthday(user).strftime("%m/%d/%Y")}`')

    @tasks.loop(hours=24)
    async def notify_birthday(self):
        current = dt.now()

        for guild in self.bot.guilds:
            info = data(guild)
            channel = self.bot.get_channel(info.get_command('birthday'))

            if channel is None:
                logging.info(
                    f'No channel to send "bday" command on {guild.name}')
                return

            for user in info.info:
                birthday = info.get_birthday(user)

                # Notify channel that it is a users birthday
                if birthday.month == current.month and birthday.day == current.day:
                    logging.info(
                        f'It\'s {user}\'s birthday on {guild.name}!!')
                    await channel.send(f'⠀\n**🎉🎉🎉 Happy Birthday <@!{user.id}> 🎉🎉🎉**')

    @notify_birthday.before_loop
    async def before_notify_birthday(self):
        await self.bot.wait_until_ready()
