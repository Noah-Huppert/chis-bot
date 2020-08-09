import datetime as dt
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
