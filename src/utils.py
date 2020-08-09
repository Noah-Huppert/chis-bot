A_EMOJI = 127462
MAPS = ['Haven', 'Split', 'Ascent', 'Bind']

def emoji_list(num):
    emojis = {}
    for index in range(num):
        emojis[chr(index + A_EMOJI)] = index
    return emojis