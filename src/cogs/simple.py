from discord.ext import commands
import discord
import logging
import sys
import random
from utils import A_EMOJI, emoji_list, closest_user
from data import data
from fuzzywuzzy import fuzz
from discord import Spotify
from discord_eprompt import ReactPromptPreset, react_prompt_response


class simple(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='kill', aliases=['k'], hidden=True)
    async def kill_command(self, ctx):
        """ kill the bot [owner-only]
        """
        if await self.bot.is_owner(ctx.message.author):
            sys.exit(0)
        logging.info(f'{ctx.author} tried to kill the bot and failed')
        await ctx.send('Weakling')

    @commands.command(name='set', aliases=[], hidden=True)
    async def set_command(self, ctx, type='spam', channel=None):
        """ set channel message spam [owner-only]
        """
        if not await self.bot.is_owner(ctx.message.author):
            return

        simple = data(ctx.guild.id)
        channels = ctx.guild.text_channels
        message = '```\n'
        message += '\n'.join('{}. {}'.format(chr(k[0]), k[1])
                             for k in enumerate(channels, start=A_EMOJI))
        message += '```'
        message = await ctx.send(message)
        choice = await react_prompt_response(self.bot, ctx.author, message, reacts=emoji_list(len(channels)))

        if type == 'spam':
            simple.set_command('spam', channels[choice].id)
        if type == 'birthday' or type == 'bday':
            simple.set_command('birthday', channels[choice].id)

    @commands.command(name='hello', aliases=['hi'])
    async def hi_command(self, ctx):
        """ will say hi back.
        """
        logging.info(f'Said hello to {ctx.author.display_name}')
        await ctx.send('Sup, chad ;)')

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
        info = data(guild.id)
        channel = self.bot.get_channel(info.get_command('spam'))

        if channel is None:
            # message is annoying
            # logging.info(f'No channel to send "spam" command on {guild.name}')
            return

        # if new_member.activity:
        #     user = new_member.display_name
        #     activity = new_member.activity

        #     if type(activity) is Spotify:
        #         logging.info(f'{new_member} is listening to Spotify')

        #         if "Logic" in activity.artists:
        #             await channel.send(f"{user} is a real hiphop fan that listens to LOGIC! 🤢")

        #         if "The Strokes" in activity.artists:
        #             await channel.send(f"{user} listens to The Strokes")

        #         if "Chance the Rapper" in activity.artists:
        #             await channel.send(f"{user} loves their wife")

        #         if "The National" in activity.artists:
        #             await channel.send(f"{user} might like https://www.youtube.com/watch?v=T8Xb_7YDroQ")

        #         if "Kanye West" in activity.artists:
        #             await channel.send(f"{user} wants this hot new merch https://www.youtube.com/watch?v=nxIvg0y6vCY")

        #         if "Drake" in activity.artists:
        #             await channel.send(f"{user} needs to read: https://aspe.hhs.gov/report/statutory-rape-guide-state-laws-and-reporting-requirements-summary-current-state-laws/sexual-intercourse-minors")

        if new_member.display_name != old_member.display_name:
            await channel.send(f"{old_member.display_name} changed their nickname to {new_member.display_name}")


def setup(bot):
    bot.add_cog(simple(bot))
