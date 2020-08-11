import discord
import datetime as dt
from fuzzywuzzy import fuzz
from dateutil.relativedelta import relativedelta
from data import data

DEFAULT_BIRHDAY_RANGE_IN_DAYS = 45
A_EMOJI = 127462
MAPS = ['Haven', 'Split', 'Ascent', 'Bind']


def emoji_list(num):
    emojis = {}
    for index in range(num):
        emojis[chr(index + A_EMOJI)] = index
    return emojis


def days_left(birthday: dt.datetime):
    current_date = dt.datetime.now()
    propagated_birthday = birthday.replace(year=current_date.year)

    if current_date > propagated_birthday:
        propagated_birthday += relativedelta(years=1)

    date_range = propagated_birthday - current_date

    return date_range.days


def closest_user(member_string, guild: discord.Guild):
    if member_string.startswith('<@!') and member_string.endswith('>'):
        return guild.get_member(int(member_string[3:-1]))

    return list(sorted(guild.members, key=lambda member:
                       fuzz.partial_token_sort_ratio(member_string.lower(),
                                                     member.display_name.lower())))[-1]


async def update_message(ctx, last_message: dict, message, mode='delete'):
    if ctx.guild.id in last_message:

        if mode == 'delete':
            try:
                await last_message[ctx.guild.id].delete()
            except discord.errors.NotFound:
                pass  # user must have deleted the message

        if mode == 'edit':
            try:
                await last_message[ctx.guild.id].edit(content=message)
                return
            except discord.errors.NotFound:
                pass  # user must have deleted the message

    last_message[ctx.guild.id] = await ctx.send(message)


def guild_birthdays_message(guild: discord.Guild, birthday_range: int):

    if birthday_range is None or birthday_range < 0:
        birthday_range = DEFAULT_BIRHDAY_RANGE_IN_DAYS

    if birthday_range > 365:
        birthday_range = 365

    info = data(guild)
    curr = dt.datetime.now()
    message = '⠀\n'  # blank unicode character
    message += f'**🎊All Birthdays '
    if birthday_range != 365:
        message += f'in the next {birthday_range} days🎊**\n'
    else:
        message += f'on the server🎊**\n'
    message += '```\n'

    members_with_no_bday = filter(lambda user: info.get_birthday(
        user) is not None, guild.members)
    sorted_members = sorted(
        members_with_no_bday, key=lambda user: days_left(info.get_birthday(user)))

    for member in sorted_members:
        bday = info.get_birthday(member)
        bday_days_left = days_left(bday)
        if bday_days_left <= birthday_range:

            message += f'🔸 {member.display_name}:\n   turning '

            # account for yearly wrap around
            if bday.replace(year=curr.year) > curr:
                message += f'{curr.year - bday.year}'
            else:
                message += f'{curr.year - bday.year + 1}'

            if bday_days_left == 0:
                message += f' tomorrow!! ({info.get_birthday(member).strftime("%B %d")}) \n\n'
            else:
                # +1 because in birthday terms, less than a day is still a day. (there are no '0' days)
                message += f' in {bday_days_left + 1} days ({info.get_birthday(member).strftime("%B %d")}) \n\n'

    message += '```'

    return message
