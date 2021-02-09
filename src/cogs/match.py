from discord.ext import commands
import discord
import logging
import random
from data import data
from utils import A_EMOJI, MAPS, emoji_list, closest_user, update_message
from discord_eprompt import ReactPromptPreset, react_prompt_response


class match(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.match_messages = {}

    @commands.command(name='side', aliases=[])
    async def side_command(self, ctx):
        """ picks a side Attackers/Defenders
        """
        side = random.randint(0, 1)
        if side:
            await ctx.send('Attackers')
        else:
            await ctx.send('Defenders')
        logging.info(f'{ctx.author} got side ' +
                     ('Attackers' if side else f'Defenders'))

    @commands.command(name='map')
    async def map_command(self, ctx):
        """ picks a Valorant map
        """
        picked_map = random.choice(MAPS)
        logging.info(f'{ctx.author} got map {picked_map}')
        await ctx.send(picked_map)

    @commands.command(name='plan', aliases=['p'])
    async def plan_command(self, ctx, spots=5, *args):
        """ takes a # of players, makes a new match
        """
        await ctx.message.delete()

        title = ""
        if len(args) > 0:
            title = ' '.join(arg for arg in args[0:])

        match = data(ctx.guild)
        match.start(spots=spots, title=title)
        logging.info(
            f'{ctx.author} is planning a {spots} player match called "{title}"')
        await update_message(ctx, self.match_messages, self.match_message(match))

    @commands.command(name='add', aliases=['a', 'join'])
    async def add_command(self, ctx, *args):
        """ @users to add them to the match
        """
        await ctx.message.delete()
        match = data(ctx.guild)
        args = list(map(lambda user: closest_user(user, ctx.guild), args))
        if len(args) == 0:
            args = [ctx.author]

        logging.info(f'{ctx.author} tried to add {*args,} to the plan')

        for user in args:
            if match.people < match.spots:
                if not match.add_gamer(user):
                    await ctx.send(f'{user} is already a gamer.')
            else:
                await ctx.send(f'Cannot add {user}, too many gamers.')
        await update_message(ctx, self.match_messages, self.match_message(match))

    @commands.command(name='addall', aliases=['aa'])
    async def addall_command(self, ctx, *args):
        """ Add all users in the voice channel
        """
        await ctx.message.delete()
        voice_channels = ctx.guild.voice_channels
        match = data(ctx.guild)

        if ctx.author.voice is None:
            await ctx.send(f'{ctx.author} is not in a voice channel.')
            return


        for channel in voice_channels:
            if ctx.author.voice.channel != None and ctx.author.voice.channel is channel:
                for user in channel.members:
                    if match.people < match.spots:
                        if not match.add_gamer(user):
                            await ctx.send(f'{user} is already a gamer.')
                    else:
                        await ctx.send(f'Cannot add {user}, too many gamers.')
        await update_message(ctx, self.match_messages, self.match_message(match))


    @commands.command(name='del', aliases=['delete', 'd', 'remove', 'leave'])
    async def remove_command(self, ctx, *args):
        """ @users to remove them from the match
        """
        await ctx.message.delete()
        match = data(ctx.guild)
        args = list(map(lambda user: closest_user(user, ctx.guild), args))

        if len(args) == 0:
            args = [ctx.author]

        logging.info(f'{ctx.author} tried to remove {*args,} from the plan')

        for user in args:
            if not match.del_gamer(user):
                await ctx.send(f'{user} is not a gamer.')
        await update_message(ctx, self.match_messages, self.match_message(match))


    @commands.command(name='rename', aliases=["r"])
    async def rename_command(self, ctx, *args):
        """Renames the current match"""
        
        await ctx.message.delete()
        match = data(ctx.guild)
        match.title = ""
        if len(args) > 0:
            match.title = ' '.join(arg for arg in args[0:])

        logging.info(f'{ctx.author} renamed the match to {match.title}')

        await update_message(ctx, self.match_messages, self.match_message(match))

    # resize command?

    @commands.command(name='play', aliases=[])
    async def play_command(self, ctx):
        """ moves teams to respective voice channels
        """
        logging.info(f'{ctx.author} used the "play" command')

        await ctx.message.delete()
        match = data(ctx.guild)

        if match.turn == None:
            await ctx.send("Teams have not been picked")
            return

        voice_channels = ctx.guild.voice_channels

        if len(match.captains) > len(voice_channels):
            await ctx.send("Not enough voice channels to move players")
            return

        for i in range(len(match.captains)):
            captain = match.captains[i]

            message = '⠀\n'  # blank unicode character
            message += f'**Move {captain.display_name}\'s team**'
            message += '```\n'
            message += '\n'.join('{}. {}'.format(chr(k[0]), k[1])
                                 for k in enumerate(voice_channels, start=A_EMOJI))
            message += '```'
            message = await ctx.send(message)

            choice = await react_prompt_response(self.bot, ctx.author, message, reacts=emoji_list(len(voice_channels)))
            selected_channel = voice_channels[choice]
            # move captain
            if captain.voice != None:
                await captain.move_to(selected_channel)
            # move player
            for player in match.get_players(captain):
                if player.voice != None:
                    await player.move_to(selected_channel)

    @commands.command(name='move', aliases=[])
    async def move_command(self, ctx):
        """ move gamers to a voice channel
        """
        logging.info(f'{ctx.author} used the move command ')

        await ctx.message.delete()
        voice_channels = ctx.guild.voice_channels
        if len(voice_channels) == 0:
            await ctx.send("No voice channels to move players")

        match = data(ctx.guild)
        message = '```\n'
        message += '\n'.join('{}. {}'.format(chr(k[0]), k[1])
                             for k in enumerate(voice_channels, start=A_EMOJI))
        message += '```'
        message = await ctx.send(message)
        choice = await react_prompt_response(self.bot, ctx.author, message, reacts=emoji_list(len(voice_channels)))

        voice = voice_channels[choice]
        for gamer in match.gamers:
            # move gamers
            if gamer.voice != None:
                await gamer.move_to(voice)

    @commands.command(name='show', aliases=['s', 'list', 'print', 'display'])
    async def print_command(self, ctx):
        """ display current gamers
        """
        logging.info(f'{ctx.author} printed the match message')

        await ctx.message.delete()
        match = data(ctx.guild)
        await update_message(ctx, self.match_messages, self.match_message(match))

    @commands.command(name="team", aliases=["t"])
    async def team_command(self, ctx, *args):
        """ @captains to start team selection
        """
        logging.info(f'{ctx.author} used "team" command')

        await ctx.message.delete()
        match = data(ctx.guild)
        args = list(map(lambda user: closest_user(user, ctx.guild), args))

        if len(args) == 0:
            await ctx.send("Please enter team captains")
            return
        if len(args) == 1:
            await ctx.send("Please enter more than one captain")
            return
        if len(set(args)) != len(args):
            await ctx.send("Captains must be different")
            return

        for cap in args:
            if cap not in match.gamers:
                await ctx.send("Captains must be part of the match")
                return

        match.captains = args
        await self.select_teams(ctx, match)

    async def select_teams(self, ctx, match: data):
        # initial captain
        match.turn = match.captains[0 % len(match.captains)]
        await update_message(ctx, self.match_messages, self.team_message(match))

        for pick in range(match.picks):
            # get captain pick
            match.turn = match.captains[pick % len(match.captains)]

            if match.picks != 1:
                choice = await react_prompt_response(self.bot, match.turn, self.match_messages[ctx.guild.id], reacts=emoji_list(match.picks))
            else:
                choice = 0
            # add player to their team
            match.add_player(match.turn, choice)

            if match.picks != 0:
                match.turn = match.captains[(pick - 1) % len(match.captains)]
            await update_message(ctx, self.match_messages, self.team_message(match))

    def match_message(self, match: data):
        message = '⠀\n'  # blank unicode character
        if match.title != "":
            message += f'**{match.title} **\n'
        message += f'**Gamers**\n'
        message += '```\n'
        for spot in range(match.spots):
            message += f'{spot + 1}. '
            if spot < match.people:
                message += (f'{match.get_gamer(spot).display_name}')
            message += ('\n')
        message += '\n```'
        message += '**Basic Commands**: $add, $del, $team, $play, $help\n'
        message += '[For more info visit https://chis.dev/chis-bot]\n'

        return message

    def team_message(self, match: data):
        message = '⠀\n'  # blank unicode character
        if match.picks != 0:
            message += f'**Turn: {match.turn.display_name}**\n'
        else:
            message += f'**Teams have been selected**\n'

        # Free
        if match.picks != 0:
            message += '```\n'
            for spot in range(match.picks):
                message += (f'{chr(spot + A_EMOJI)}. ')
                if spot < match.picks:
                    message += (f'{match.get_agent(spot).display_name}')
                message += ('\n')
            message += '```\n'

        # Taken
        for cap in match.captains:
            message += '```\n'
            message += f'1. {cap.display_name} (captain)\n'
            for spot in range(int(match.spots/len(match.captains)) - 1):
                message += (f'{spot + 2}. ')
                if spot < match.team_size(cap):
                    message += (f'{match.get_player(cap, spot).display_name}')
                message += ('\n')
            message += '\n```'
        if match.picks == 0:
            message += f'**{match.turn.display_name} picked last**, they get priority picking sides.\n'
            message += f'Use `$play` to switch voice channels\n'

        return message
