import discord
import datetime as dt
from fuzzywuzzy import fuzz
from dateutil.relativedelta import relativedelta

BIRHDAY_RANGE_IN_DAYS = 45
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
