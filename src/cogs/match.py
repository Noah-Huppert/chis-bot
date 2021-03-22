from discord import activity, message
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
                members= sorted(channel.members, key=lambda user: self.activity_check(user), reverse=True)
                
                for user in members:
                    if match.people < match.spots:
                        if not match.add_gamer(user):
                            await ctx.send(f'{user} is already a gamer.')
                    else:
                        await ctx.send(f'Cannot add {user}, too many gamers.')
        await update_message(ctx, self.match_messages, self.match_message(match))

    def activity_check(self, user):
        # logging.info(f'{user} activities are')
        for activity in user.activities:
            # logging.info(f'{activity}')
            if isinstance(activity, discord.activity.Activity):
                # Valorant application id
                return activity.application_id == 700136079562375258
        return False

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
            
            embed = discord.Embed(title=f'**Move Team: {captain.display_name}**', description="", color=0xff00d4)
            embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/", icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

            
            channels = '\n'.join('{}. {}'.format(chr(k[0]), k[1])
                                 for k in enumerate(voice_channels, start=A_EMOJI))

            embed.add_field(name="Current Voice Channels", value=channels, inline=False)        

            message = await ctx.send(embed=embed)

            choice = await react_prompt_response(self.bot, ctx.author, message, reacts=emoji_list(len(voice_channels)))
            selected_channel = voice_channels[choice]
            # move captain
            if captain.voice != None:
                await captain.move_to(selected_channel)
            # move player
            for player in match.get_players(captain):
                if player.voice != None:
                    await player.move_to(selected_channel)

    @commands.command(name='move', aliases=["m"])
    async def move_command(self, ctx):
        """ move gamers to a voice channel
        """
        logging.info(f'{ctx.author} used the move command ')

        await ctx.message.delete()
        voice_channels = ctx.guild.voice_channels
        if len(voice_channels) == 0:
            await ctx.send("No voice channels to move players")

        match = data(ctx.guild)

        embed = discord.Embed(title=f'**Move All Users**', description="", color=0xff00d4)
        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/", icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")
    
        channels = '\n'.join('{}. {}'.format(chr(k[0]), k[1])
                             for k in enumerate(voice_channels, start=A_EMOJI))

        embed.add_field(name="Current Voice Channels", value=channels, inline=False)        

        message = await ctx.send(embed=embed)
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
        embed = discord.Embed(title=match.title, description="", color=0xff00d4)
        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/", icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

        gamers = ""
        for spot in range(match.spots):
            gamers += f'{spot + 1}. '
            if spot < match.people:
                gamers += match.get_gamer(spot).mention
            gamers += '\n'

        embed.add_field(name="Gamers", value=gamers, inline=False)        

        embed.set_footer(text="Basic Commands: $add, $addall, $del, $team, $play, $move")

        return embed

    def team_message(self, match: data):
        if match.picks != 0:
            embed = discord.Embed(title=f'**Turn: {match.turn.display_name}**', description="", color=0xff00d4)
        else:
            embed = discord.Embed(title=f'**Teams have been selected**', description="", color=0xff00d4)

        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/", icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

        # Taken
        for cap in match.captains:
            teammates = ''
            teammates += '1. ' + cap.mention + ' (captain)\n'
            for spot in range(int(match.spots/len(match.captains)) - 1):
                teammates += (f'{spot + 2}. ')
                if spot < match.team_size(cap):
                    teammates += match.get_player(cap, spot).mention
                teammates += ('\n')

            embed.add_field(name= f'Team: {cap.display_name}', value=teammates, inline=False)

        # Free
        if match.picks != 0:
            not_selected =""
            for spot in range(match.picks):
                not_selected += f'{chr(spot + A_EMOJI)} - '
                if spot < match.picks:
                    not_selected += match.get_agent(spot).mention
                not_selected += '\n'
        
            embed.add_field(name="Not Selected", value=not_selected, inline=False)

        if match.picks == 0:
            end_selection = '**' + match.turn.mention + f' picked last**, they get priority picking sides.\n'
            end_selection += f'Use `$play` to switch voice channels'
            embed.add_field(name= 'Get Ready', value=end_selection, inline=False)

        return embed
