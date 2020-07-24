from discord.ext import commands
import discord
import logging
import json
import os
from discord_eprompt import ReactPromptPreset, react_prompt_response

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
    
    # TODO
    # print who's turn
    # captain should be at top of list (bolded)
    def print_team_message(self, captains):
        message = 'Currently in team selection\n'
        
        # Free
        if len(self.game_data["people"]) != 0:
            message += '```\n'
            for spot in range(self.game_data["gamers"]):
                message += (f'{chr(spot + 127462)}. ')
                if spot < len(self.game_data["people"]):
                    message += (f'{self.game_data["people"][spot]["name"]}')
                message += ('\n')
            message += '```\n'
        
        # Taken
        for cap in captains:
            message += '```\n'
            message += f'{cap.display_name}\n'
            for spot in range(int(self.game_data["spots"]/len(captains))):
                message += (f'{spot + 1}. ')
                if spot < len(self.game_data["captains"][cap.display_name]):
                     message += (f'{self.game_data["captains"][cap.display_name][spot]}')
                message += ('\n')
            message += '\n```'

        return message

    async def update_message(self, ctx, message):
        if self.game_msg is not None:
            logging.info('deleting game message')
            await self.game_msg.delete()
        self.game_msg = await ctx.send(message)
    
    def emoji_list(self):
        emojis = {}
        for index in range(self.game_data["gamers"]):
            emojis[chr(index + 127462)] = index
        return emojis

    # TODO
    # add support for multiple games
    @commands.command(name='game', aliases=['plan', 'p', "g"])
    async def game_command(self, ctx, spots: int):
        """ This command takes a number of players and established a new game.
        """
        self.load_games()
        self.game_data = {"match": "Valorant", "spots": spots, "gamers": 0, "people": [], "captains": {}}
        logging.info(f'{self.game_data}')
        logging.info(f'{ctx.author.display_name} tried to make a game')
        await self.update_message(ctx, self.print_message())
        self.save_games()

    # TODO implement set() to prevent duplicates
    @commands.command(name='add', aliases = ["a"])
    async def add_command(self, ctx, user: discord.User):
        """ This command requires @ing a discord user id to add them to the plan. If there are too many people in the party, you have to remove someone to add more
        """
        self.load_games()
        if len(self.game_data["people"]) < self.game_data["spots"]:
            self.game_data["people"].append({ "name": user.name, "tag": user.discriminator})
            self.game_data["gamers"] += 1
            logging.info(f'{ctx.author.display_name} added {user}.')
            await self.update_message(ctx, self.print_message())
        else:
            await ctx.send("too many!!")
            logging.info(f'{ctx.author.display_name} tried to add {user}.')
        self.save_games()
        
    @commands.command(name='del', aliases=["delete", "d", "remove"])
    async def remove_command(self, ctx, user: discord.User):
        """ This command takes a discord id and deletes them from the plan.
        """
        self.load_games()
        try:
            self.game_data["people"].remove({"name": user.name, "tag": user.discriminator })
            self.game_data["gamers"] -= 1
        except ValueError:
            self.game_data["gamers"] += 1
            await ctx.send(f'{user} ain\'t there')
        await self.update_message(ctx, self.print_message())
        self.save_games()
    
    @commands.command(name="show", aliases = ["s", "list", "print"])
    async def print_command(self, ctx):
        """ This command shows the list of players currently added to the match.
        """
        self.load_games()
        await self.update_message(ctx, self.print_message())

    @commands.command(name="team", aliases=["t", "pick"])
    async def team_command(self, ctx, *args: discord.User):
        """ This command will initiate the process of team selection. It takes two discord ids with the command as the two team captains. The first id has first pick in team selection.
        """
        logging.info(args)
        self.load_games()
        if len(args) == 0:
            await ctx.send("Please enter team captains")
            return
        self.create_captains(args)
        await self.select_teams(ctx, args)
        self.save_games()
        self.game_msg = None

    def create_captains(self, captains):
        self.game_data["captains"] = {}
        for cap in captains:
            self.game_data["captains"][cap.display_name] = []

    async def select_teams(self, ctx, captains):
        # captains cannot pick themselves
        self.game_data["gamers"] -= len(captains)
        for cap in captains:
            self.game_data["people"].remove({ "name": cap.name, "tag": cap.discriminator })
        
        await self.update_message(ctx, self.print_team_message(captains))
        for index in range(self.game_data["spots"] - 1):
            # get captain pick
            choice = await react_prompt_response(self.bot, captains[index % len(captains)], self.game_msg, reacts=self.emoji_list())
            # add player to their team
            logging.info(index % len(captains))
            logging.info(captains[index % len(captains)])
            self.game_data["captains"][ captains[index % len(captains)].display_name ].append(self.game_data["people"][choice]["name"])
            # player is no longer free
            del self.game_data["people"][choice]
            self.game_data["gamers"] -= 1
            self.game_msg = None
            await self.update_message(ctx, self.print_team_message(captains))





    
def setup(bot):
    bot.add_cog(GameCommands(bot))
