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
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option

from ..config import load_config

config = load_config()

class match(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.match_messages = {}

    @cog_ext.cog_slash(name="plan",
                       guild_ids=config.guilds,
                       description="Gather people to play video games.",
                       options=[
                           create_option(
                               name="spots",
                               description="Specify the number of gamers. (DEFAULT: 5)",
                               option_type=SlashCommandOptionType.STRING,
                               required=False,
                           ),
                           create_option(
                               name="title",
                               description="Name of the plan.",
                               option_type=SlashCommandOptionType.STRING,
                               required=False,
                           )
                       ])
    async def plan_command(self, ctx, spots="5", title=""):
        """ creates a plan, takes in # of gamers, and title (optional)
        """
        # Add plan check
        match = data(ctx.guild)
        prefix = await self.bot.get_prefix(ctx.message)

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

        match.start(spots=spots, title=title)
        logging.info(
            f'{ctx.author} is planning a {spots} player match called "{title}"')
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @cog_ext.cog_slash(name="add",
                       description="Add yourself to plan, or specify a gamer.",
                       options=[
                           create_option(
                               name="user",
                               description="Specify the gamer.",
                               option_type=SlashCommandOptionType.USER,
                               required=False,
                           ),
                       ])
    async def add_command(self, ctx, user: discord.User = None):
        """  add users to the plan
        """
        match = data(ctx.guild)
        if user == None:
            user = ctx.author

        logging.info(f'{ctx.author} tried to add {user} to the plan')

        if match.people < match.spots:
            if not match.add_gamer(user):
                await ctx.send(f'{user} is already a gamer.')
        else:
            await ctx.send(f'Cannot add {user}, too many gamers.')
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @cog_ext.cog_slash(name="addall",
                       description="Add all gamers in the current voice chat.")
    async def addall_command(self, ctx):
        """ add all users currently in the voice channel to the plan
        """
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

    @cog_ext.cog_slash(name="delete",
                       description="Delete yourself from plan, or specify a gamer.",
                       options=[
                           create_option(
                               name="user",
                               description="Specify the gamer.",
                               option_type=SlashCommandOptionType.USER,
                               required=False,
                           ),
                       ])
    async def remove_command(self, ctx, user: discord.User = None):
        """ delete users from the plan
        """
        match = data(ctx.guild)

        if user == None:
            user = ctx.author

        logging.info(f'{ctx.author} tried to remove {user} from the plan')

        if not match.del_gamer(user):
            await ctx.send(f'{user} is not a gamer.')
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @cog_ext.cog_slash(name="replace",
                       description="Replace a gamer on the plan.",
                       options=[
                           create_option(
                               name="current",
                               description="Specify the gamer to be replaced.",
                               option_type=SlashCommandOptionType.USER,
                               required=True,
                           ),
                           create_option(
                               name="new",
                               description="Specify the gamer who will be added to the plan",
                               option_type=SlashCommandOptionType.USER,
                               required=True,
                           )
                       ])
    async def replace_command(self, ctx, current: discord.User, new: discord.User):
        """ replace a user on the plan
        """
        match = data(ctx.guild)

        if not match.del_gamer(current):
            await ctx.send(f'{current} is not a gamer.')
            return

        if new in list(match.gamers):
            await ctx.send(f'{new} is already a gamer.')
            return

        match.add_gamer(new)

        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @cog_ext.cog_slash(name="rename",
                       description="Rename the current plan.",
                       options=[
                           create_option(
                               name="title",
                               description="Name of the plan.",
                               option_type=SlashCommandOptionType.STRING,
                               required=True,
                           )
                       ])
    async def rename_command(self, ctx, title):
        """renames the current plan
        """
        match = data(ctx.guild)
        match.title = title

        logging.info(f'{ctx.author} renamed the match to {match.title}')

        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @cog_ext.cog_slash(name="play",
                       description="Starts the match."
                       )
    async def play_command(self, ctx):
        """ moves teams to respective voice channels
        """
        logging.info(f'{ctx.author} used the "play" command')

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

    @cog_ext.cog_slash(name="move",
                       description="Move gamers to a voice channel."
                       )
    async def move_command(self, ctx):
        """ move plan members to a voice channel
        """
        logging.info(f'{ctx.author} used the move command ')

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

    @cog_ext.cog_slash(name="display",
                       description="Display current plan in text channel."
                       )
    async def print_command(self, ctx):
        """ display current plan in text channel
        """
        logging.info(f'{ctx.author} printed the match message')

        match = data(ctx.guild)
        await update_message(ctx, self.match_messages, await self.match_message(ctx, match))

    @cog_ext.cog_slash(name="team",
                       description="Start team selection.",
                       options=[
                           create_option(
                               name="captain1",
                               description="Name of the captain.",
                               option_type=SlashCommandOptionType.USER,
                               required=True,
                           ),
                           create_option(
                               name="captain2",
                               description="Name of the captain.",
                               option_type=SlashCommandOptionType.USER,
                               required=True,
                           )
                       ])
    async def team_command(self, ctx, captain1: discord.User, captain2: discord.User):
        """start team selection, supply captains (optional)
        """
        logging.info(f'{ctx.author} used "team" command')

        match = data(ctx.guild)

        gamers = list(match.gamers)
        captains = []

        if captain1 == captain2:
            await ctx.send("Captains must be different")
            return

        if captain1 not in match.gamers or captain2 not in match.gamers:
            await ctx.send("Captains must be part of the match")
            return

        match.captains = [captain1, captain2]
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

        embed.add_field(name="Basic Commands:",
                        value=f'/add, /delete, /replace, /rename\n**`/team` to start captain selection**', inline=False)

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
            end_selection += f'Use `/play` to switch voice channels'
            embed.add_field(name='Get Ready',
                            value=end_selection, inline=False)

        return embed
