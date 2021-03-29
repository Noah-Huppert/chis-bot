from discord import activity, message
from discord.ext import commands
import discord
import logging
import random
import math
from data import data
from dateutil.relativedelta import relativedelta
from datetime import datetime
from utils import A_EMOJI, MAPS, SKIP_EMOJI, YES_NO_SHOW, YES_NO_SHOW, emoji_list, closest_user, emoji_list_team, update_message
from discord_eprompt import ReactPromptPreset, react_prompt_response


class match(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.match_messages = {}

    @commands.command(name='side', aliases=[])
    async def side_command(self, ctx):
        """ selects randomly between attackers & defenders

        `$side`

        Example: $side
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

        `$map`

        Example: $map
        """
        picked_map = random.choice(MAPS)
        logging.info(f'{ctx.author} got map {picked_map}')
        await ctx.send(picked_map)

    @commands.command(name='plan', aliases=['p'])
    async def plan_command(self, ctx, spots=None, *args):
        """ creates a plan, takes in # of gamers, and title (optional) 

        `$plan[p] <#> <title>`
        Example:
        $plan 5
        $plan 10 VALORANT Match
        $p 15 Garry's Mod
        """
        # Add plan check
        match = data(ctx.guild)
        prefix = await self.bot.get_prefix(ctx.message)

        if not len(args) and not spots:
            embed = discord.Embed(title=f'', description="", color=0xff00d4)
            embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                             icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")
            embed.add_field(
                name="Usage", value='$plan[p] <#> <title>', inline=False)
            embed.add_field(
                name="Examples", value='$plan 5\n$plan 10 VALORANT Match\n$p 15 Garry\'s Mod', inline=False)
            embed.set_footer(text=f'Type {prefix}help for more details.')

            await ctx.send(embed=embed)
            return

        try:
            interval = datetime.now() - match.time
            # 15 min for now
            if interval.seconds < 900:
                embed = discord.Embed(
                    title=f'Current Plan Recently Created', description="Would you like to start a new one?", color=0xff00d4)
                embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                                 icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")
                embed.set_footer(
                    text=f'🔎 to view current plan.')
                message = await ctx.send(embed=embed)
                choice = await react_prompt_response(self.bot, ctx.author, message, reacts=YES_NO_SHOW)
                if choice == 0:
                    return
                if choice == 2:
                    await self.print_command(ctx)
                    return
        except KeyError:
            pass

        await ctx.message.delete()

        title = ""
        if len(args) > 0:
            title = ' '.join(arg for arg in args[0:])

        match.start(spots=spots, title=title)
        logging.info(
            f'{ctx.author} is planning a {spots} player match called "{title}"')
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @commands.command(name='add', aliases=['a'])
    async def add_command(self, ctx, *args):
        """  add users to the plan

        `$add[a] <@Name, Name, “Name With Spaces”>'`

        Example: 
        $a
        $add "Chis Bot"
        $a chis unholydog106
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
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @commands.command(name='addall', aliases=['aa'])
    async def addall_command(self, ctx, *args):
        """ add all users currently in the voice channel

        `$addall[aa]`

        Example: 
        $aa
        """
        await ctx.message.delete()
        voice_channels = ctx.guild.voice_channels
        match = data(ctx.guild)

        if ctx.author.voice is None:
            await ctx.send(f'{ctx.author} is not in a voice channel.')
            return

        for channel in voice_channels:
            if ctx.author.voice.channel != None and ctx.author.voice.channel is channel:
                members = sorted(
                    channel.members, key=lambda user: self.activity_check(user), reverse=True)

                for user in members:
                    if match.people < match.spots:
                        if not match.add_gamer(user):
                            await ctx.send(f'{user} is already a gamer.')
                    else:
                        await ctx.send(f'Cannot add {user}, too many gamers.')
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    def activity_check(self, user):
        # logging.info(f'{user} activities are')
        for activity in user.activities:
            # logging.info(f'{activity}')
            if isinstance(activity, discord.activity.Activity):
                # Valorant application id
                return activity.application_id == 700136079562375258
        return False

    @commands.command(name='delete', aliases=['del', 'd'])
    async def remove_command(self, ctx, *args):
        """ delete users from the plan

        `$delete[del,d] <@Name, Name, “Name With Spaces”>'`

        Example:
        $del 
        $delete "Chis Bot"
        $d chis unholydog106
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
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @commands.command(name='rename', aliases=["r"])
    async def rename_command(self, ctx, *args):
        """renames the current plan

        `$rename[r] <title>`

        Example: 
        $r New Plan Title
        $rename 10 Man VALORANT
        """

        await ctx.message.delete()
        match = data(ctx.guild)
        match.title = ""
        if len(args) > 0:
            match.title = ' '.join(arg for arg in args[0:])

        logging.info(f'{ctx.author} renamed the match to {match.title}')

        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    # resize command?

    @commands.command(name='play', aliases=[])
    async def play_command(self, ctx):
        """ moves teams to respective voice channels

        `$play`

        Example: 
        $play
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

            embed = discord.Embed(title=f'**Move Team: {captain.display_name}**',
                                  description="[Click here to learn more.](https://chis.dev/chis-bot/#usage)", color=0xff00d4)
            embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                             icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

            channels = '\n'.join('{} - {}'.format(chr(k[0]), k[1])
                                 for k in enumerate(voice_channels, start=A_EMOJI))

            embed.add_field(name="Current Voice Channels",
                            value=channels, inline=False)

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
        """ move plan members to a voice channel

        `$move[m]`

        Example: 
        $m
        $move
        """
        logging.info(f'{ctx.author} used the move command ')

        await ctx.message.delete()
        voice_channels = ctx.guild.voice_channels
        if len(voice_channels) == 0:
            await ctx.send("No voice channels to move players")

        match = data(ctx.guild)

        embed = discord.Embed(title=f'**Move All Users**',
                              description="[Click here to learn more.](https://chis.dev/chis-bot/#usage)", color=0xff00d4)
        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                         icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

        channels = '\n'.join('{} - {}'.format(chr(k[0]), k[1])
                             for k in enumerate(voice_channels, start=A_EMOJI))

        embed.add_field(name="Current Voice Channels",
                        value=channels, inline=False)

        message = await ctx.send(embed=embed)
        choice = await react_prompt_response(self.bot, ctx.author, message, reacts=emoji_list(len(voice_channels)))

        voice = voice_channels[choice]
        for gamer in match.gamers:
            # move gamers
            if gamer.voice != None:
                await gamer.move_to(voice)

    @commands.command(name='show', aliases=['s'])
    async def print_command(self, ctx):
        """ display current plan in text channel

        `$show[s]`

        Example: 
        $s
        $show
        """
        logging.info(f'{ctx.author} printed the match message')

        await ctx.message.delete()
        match = data(ctx.guild)
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @commands.command(name="team", aliases=["t"])
    async def team_command(self, ctx, *args):
        """start team selection, supply captains (optional)

        `$team[t] <@Name, Name, “Name With Spaces”>`

        Example:
        $team 
        $team chis unholydog106
        """
        logging.info(f'{ctx.author} used "team" command')

        await ctx.message.delete()
        match = data(ctx.guild)
        args = list(map(lambda user: closest_user(user, ctx.guild), args))

        gamers = list(match.gamers)
        captains = []

        if len(args) == 0:
            while True:
                embed = discord.Embed(title=f'**Select Match Captains**',
                                      description="[Click here to learn more.](https://chis.dev/chis-bot/#usage)", color=0xff00d4)
                embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                                 icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")
                embed_gamers = '\n'.join('{} - {}'.format(chr(k[0]), k[1])
                                         for k in enumerate(map(lambda gamer: gamer.mention, gamers), start=A_EMOJI))
                if len(captains):
                    embed_gamers += f'\n{chr(SKIP_EMOJI)} - **Continue**'

                embed.add_field(
                    name="Gamers", value=embed_gamers, inline=False)

                if len(captains):
                    embed_captains = '\n'.join('{}. {}'.format(k[0], k[1])
                                               for k in enumerate(map(lambda cap: cap.mention, captains), start=1))
                    embed.add_field(name="Current Captains",
                                    value=embed_captains, inline=False)

                message = await ctx.send(embed=embed)
                choice = await react_prompt_response(self.bot, ctx.author, message, reacts=emoji_list_team(match.people + 1))

                if choice != match.people:
                    captains.append(gamers.pop(choice))
                else:
                    args = captains
                    break

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
        await update_message(ctx, self.match_messages, self.team_message(ctx, match))

        while match.picks:

            # get captain pick
            choice = await react_prompt_response(self.bot, match.turn, self.match_messages[ctx.guild.id], reacts=emoji_list_team(match.picks + 1))

            # add player to their team
            if choice != match.picks:
                match.add_player(match.turn, choice)

            if match.picks != 0:
                # find the index of the current captain and add 1

                match.turn = match.captains[(match.captains.index(
                    match.turn) - 1) % len(match.captains)]
            await update_message(ctx, self.match_messages, self.team_message(ctx, match))

    async def match_message(self, ctx, match: data):
        embed = discord.Embed(
            title=match.title, description="[Click here to learn more.](https://chis.dev/chis-bot/#usage)", color=0xff00d4)
        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                         icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

        if match.people:
            embed_gamers = '\n'.join('{}. {}'.format(k[0], k[1])
                                     for k in enumerate(map(lambda gamer: gamer.mention, list(match.gamers)), start=1))
        else:
            embed_gamers = '⠀'

        embed.add_field(
            name=f'Gamers ({match.people}/{match.spots})', value=embed_gamers, inline=False)
        prefix = await self.bot.get_prefix(ctx.message)

        embed.add_field(name="Basic Commands:",
                        value=f'{prefix}add, {prefix}delete, {prefix}move, {prefix}rename\n**`$team` to start captain selection**', inline=False)
        embed.set_footer(text=f'Type {prefix}help for more details.')

        return embed

    def team_message(self, ctx, match: data):
        if match.picks != 0:
            embed = discord.Embed(title=f'**Turn: {match.turn.display_name}**',
                                  description="[Click here to learn more.](https://chis.dev/chis-bot/#usage)", color=0xff00d4)
        else:
            embed = discord.Embed(title=f'**Teams have been selected**',
                                  description="[Click here to learn more.](https://chis.dev/chis-bot/#usage)", color=0xff00d4)

        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                         icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

        # Taken
        for cap in match.captains:
            embed_teammates = '1. ' + cap.mention + ' *(captain)*\n'
            embed_teammates += '\n'.join('{}. {}'.format(k[0], k[1])
                                         for k in enumerate(map(lambda player: player.mention, match.get_players(cap)), start=2))

            if len(list(match.get_players(cap))):
                embed.add_field(
                    name=f'Team: {cap.display_name}', value=embed_teammates, inline=False)

        # Free
        if match.picks != 0:
            # whoops...
            agents = list(
                map(lambda agent: ctx.guild.get_member(int(agent)), match.agents))

            embed_agents = '\n'.join('{} - {}'.format(chr(k[0]), k[1])
                                     for k in enumerate(map(lambda agent: agent.mention, agents), start=A_EMOJI))
            embed_agents += f'\n{chr(SKIP_EMOJI)} - **Skip**'

            embed.add_field(name="Not Selected",
                            value=embed_agents, inline=False)

        if match.picks == 0:
            end_selection = '**' + match.turn.mention + \
                f' picked last**, they get priority picking sides.\n'
            end_selection += f'Use `$play` to switch voice channels'
            embed.add_field(name='Get Ready',
                            value=end_selection, inline=False)

        return embed
