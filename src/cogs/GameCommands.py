from discord.ext import commands
import discord
import logging
import json
import os

class GameCommands(commands.Cog):
    def __init__(self, bot):
        self.bot= bot
        self.game_data = {}
        self.game_msg = None

    def load_games(self):
        with open(os.path.dirname(__file__) + '/../data/games.json') as f:
            self.game_data = json.load(f)

    def save_games(self):
        with open(os.path.dirname(__file__) + '/../data/games.json', 'w') as f:
            json.dump(self.game_data, f, indent=2)

    def print_message(self):
        message = 'These are the current users in the party'
        message += '```\n'
        for spot in range(self.game_data["spots"]):
            message += (f'{spot +1}. ')
            if spot < len(self.game_data["people"]):
                message += (f'{self.game_data["people"][spot]["name"]}')
            message += ('\n')
        message += '\n```'
        return message

    async def update_message(self, ctx, text):
        if self.game_msg is not None:
            logging.info('editing game message')
            await self.game_msg.edit(content= text)
        else:
            self.game_msg = await ctx.send(self.print_message())


    #TODO
    # add support for multiple games
    @commands.command(name='game', aliases=['plan', 'w', 'p', 'bool', 'scrim', "slap", "dwarf", "valy", "valorant"])
    async def game_command(self, ctx, spots: int):
        self.load_games()
        self.game_data = {"match": "Valorant", "spots": spots, "people": []}
        logging.info(f'{self.game_data}')
        logging.info(f'{ctx.author.display_name} tried to make a game')
        await self.update_message(ctx, self.print_message())
        self.save_games()

    @commands.command(name='add', aliases = ["a"])
    async def add_command(self, ctx, user: discord.User):
        self.load_games()
        if len(self.game_data["people"]) < self.game_data["spots"]:
            self.game_data["people"].append({ "name": user.name, "tag": user.discriminator})
            logging.info(f'{ctx.author.display_name} added {user}.')
            await self.update_message(ctx, self.print_message())
        else:
            await ctx.send("too many!!")
            logging.info(f'{ctx.author.display_name} tried to add {user}.')
        self.save_games()
        
    @commands.command(name='del', aliases=["delete", "d", "remove", "yeet", "kick"])
    async def remove_command(self, ctx, user: discord.User):
        self.load_games()
        try:
            self.game_data["people"].remove({"name": user.name, "tag": user.discriminator })
        except ValueError:
            await ctx.send(f'{user} ain\'t there')
        await self.update_message(ctx, self.print_message())
        self.save_games()
    
    @commands.command(name="show", aliases = ["s", "list", "print", "homie_radar"])
    async def print_command(self, ctx):
        self.load_games()
        if self.game_msg is not None:
            await self.update_message(ctx, 'A new message has been printed')
        self.game_msg = await ctx.send(self.print_message())

    #TODO add reaction based team selection
    #@commands.Cog.listener()
    
def setup(bot):
    bot.add_cog(GameCommands(bot))
