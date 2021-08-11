import logging
import random
import subprocess
import sys
from os import name
from typing import List

import discord
from discord import channel
from data import data
from discord import Spotify, TextChannel, Role
from discord.ext import commands
from discord.ext.commands import Context
from discord_eprompt import ReactPromptPreset, react_prompt_response
from discord_slash import SlashContext, cog_ext
from discord_slash.model import (SlashCommandOptionType,
                                 SlashCommandPermissionType)
from discord_slash.utils.manage_commands import (create_choice, create_option,
                                                 create_permission)
from fuzzywuzzy import fuzz
from utils import A_EMOJI, closest_user, emoji_list

SERVICES = [
    create_choice(
        name="Minecraft",
        value="minecraft-server.service"
    )
]


class simple(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @cog_ext.cog_slash(name="server",
                       description="Start a Chis Bot service",
                       options=[
                           create_option(
                               name="service",
                               description="Select a service",
                               option_type=SlashCommandOptionType.STRING,
                               required=True,
                               choices=SERVICES
                           ),
                           create_option(
                               name="state",
                               description="Stop a service",
                               option_type=SlashCommandOptionType.STRING,
                               required=True,
                               choices=[create_choice(
                                    name="start",
                                    value="start"
                               ),
                                   create_choice(
                                   name="stop",
                                   value="stop"
                               ), create_choice(
                                   name="status",
                                   value="status"
                               )]
                           )
                       ],
                       default_permission=False,
                       guild_ids=[315969566411063297],
                       permissions={315969566411063297: [create_permission(
                           722937537714192464, SlashCommandPermissionType.ROLE, True)]}
                       )
    async def server_command(self, ctx, service, state):
        # sys.stdout.buffer.write(command.stdout)
        # sys.stderr.buffer.write(command.stderr)
        # sys.exit(command.returncode)
        await ctx.defer()
        command = subprocess.run(
            ['systemctl', '--user', state, service], capture_output=True)
        embed = discord.Embed(
            title=f'Chis Server', description='', color=0xff00d4)
        embed.set_author(name="Chis Bot", url="https://chis.dev/chis-bot/",
                         icon_url="https://cdn.discordapp.com/app-icons/724657775652634795/22a8bc7ffce4587048cb74b41d2a7363.png?size=256")

        if state == 'status':
            if command.returncode == 3:
                embed.add_field(name=f'{state}',
                                value=f'{service} is stopped.', inline=False)
            if command.returncode == 0:
                embed.add_field(name=f'{state}',
                                value=f'{service} is running.', inline=False)

        if state == 'start':
            embed.add_field(name=f'{state}',
                            value=f'{service} is being started.', inline=False)

        if state == 'stop':
            embed.add_field(name=f'{state}',
                            value=f'{service} is stopped.', inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='kill', aliases=['k'], hidden=True)
    async def kill_command(self, ctx):
        """ kill the bot [owner-only]
        """
        if await self.bot.is_owner(ctx.message.author):
            sys.exit(0)
        logging.info(f'{ctx.author} tried to kill the bot and failed')
        await ctx.send('Weakling')

    @commands.command(name='inv', aliases=[])
    async def inv_command(self, ctx: Context, hidden=True):
        if ctx.author.id != 219152343588012033:
            return
        for guild in self.bot.guilds:
            invite = await guild.text_channels[0].create_invite(max_uses=1, unique=True)
            if ctx.author.id == 219152343588012033:
                await ctx.author.send(invite)

    @cog_ext.cog_slash(name="set",
                       description="Set message channels.",
                       options=[
                           create_option(
                               name="type",
                               description="Choose message type.",
                               option_type=SlashCommandOptionType.STRING,
                               required=True,
                               choices=[
                                   create_choice(
                                    name="Spam Channel",
                                    value="Spam"
                                   ),
                                   create_choice(
                                       name="Birthday Channel",
                                       value="Birthday"
                                   ),
                                   create_choice(
                                       name="IRL Birthday Channel",
                                       value="IRL Birthday"
                                   ),
                                   create_choice(
                                       name="IRL Birthday Role",
                                       value="IRL Role"
                                   )
                               ]
                           ),
                           create_option(
                               name="channel",
                               description="Choose output channel.",
                               option_type=SlashCommandOptionType.CHANNEL,
                               required=False,
                           ),
                           create_option(
                               name="role",
                               description="Choose output role.",
                               option_type=SlashCommandOptionType.ROLE,
                               required=False,
                           )
                       ]
                       )
    async def set_command(self, ctx: Context, type, channel: TextChannel = None, role: Role = None):
        simple = data(ctx.guild)

        if type == "IRL Role":
            if not isinstance(role, Role):
                await ctx.send("Invalid command usage.")
                return
            simple.set_command('irl_role', role.id)
            await ctx.send(f"{type} channel has been set to `{role}`.")
            return

        if not isinstance(channel, TextChannel):
            await ctx.send("Invalid command usage.")
            return

        if type != "IRL Role" and role != None:
            await ctx.send("Invalid command usage.")

        if type == 'Spam':
            simple.set_command('spam', channel.id)

        if type == 'Birthday' or type == 'bday':
            simple.set_command('birthday', channel.id)

        if type == 'IRL Birthday' or type == 'bday':
            simple.set_command('birthday_irl', channel.id)

        await ctx.send(f"{type} channel has been set to `{channel}`.")

    @commands.command(name='hello', aliases=['hi'])
    async def hi_command(self, ctx):
        """ will say hi back.
        """
        logging.info(f'Said hello to {ctx.author.display_name}')
        await ctx.send('What\'s up!')

    @commands.command(name='flip', aliases=['coin'])
    async def flip_command(self, ctx):
        """ flip a coin
        """
        coin = random.randint(0, 1)
        if coin:
            await ctx.send('Heads')
        else:
            await ctx.send('Tails')
        logging.info(f'{ctx.author} flipped a coin and got ' +
                     ('heads' if coin else f'tails'))

    @commands.command(name='roll', aliases=[])
    async def roll_command(self, ctx, number: int):
        """ roll 'n' sided die
        """
        roll = random.randint(0, number)
        await ctx.send(f'Rolled: {roll}')
        logging.info(
            f'{ctx.author.display_name} rolled a "{number}" sided die and got "{roll}"')

    @commands.command(name='user', aliases=[], hidden=True)
    async def user_command(self, ctx, *args):
        """ fuzzy matches a discord user
        """
        logging.info(f'{ctx.author} tried to fuzzy match')
        member_string = ' '.join(arg for arg in args[0:])
        # closest_user(member_string, ctx.guild.members)
        await ctx.send(f'The closest user is {closest_user(member_string, ctx.guild)}')

    @commands.Cog.listener()
    async def on_member_update(self, old_member: discord.Member, new_member: discord.Member):
        guild = new_member.guild
        info = data(guild)
        channel = self.bot.get_channel(info.get_command('spam'))

        if channel is None:
            # message is annoying
            logging.info(f'No channel to send "spam" command on {guild.name}')
            return

        if new_member.activity:
            user = new_member.display_name
            activity = new_member.activity

            if type(activity) is Spotify:
                logging.info(f'{new_member} is listening to Spotify')

                # if "Logic" in activity.artists:
                #     await channel.send(f"{user} is a real hiphop fan that listens to LOGIC! 🤢")

                # if "The Strokes" in activity.artists:
                #     await channel.send(f"{user} listens to The Strokes")

                # if "Chance the Rapper" in activity.artists:
                #     await channel.send(f"{user} loves their wife")

                # if "The National" in activity.artists:
                #     await channel.send(f"{user} might like https://www.youtube.com/watch?v=T8Xb_7YDroQ")

                # if "Kanye West" in activity.artists:
                #     await channel.send(f"{user} wants this hot new merch https://www.youtube.com/watch?v=nxIvg0y6vCY")

                # if "Drake" in activity.artists:
                #     await channel.send(f"{user} needs to read: https://aspe.hhs.gov/report/statutory-rape-guide-state-laws-and-reporting-requirements-summary-current-state-laws/sexual-intercourse-minors")

        # if new_member.display_name != old_member.display_name:
        #     await channel.send(f"{old_member.display_name} nickname was changed to {new_member.display_name}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id == 832460499773685790 and message.author.id == 607656626895454218:
            if message.content == "morning!" and random.randint(0, 7) == 0:
                await message.channel.send("evening.")
