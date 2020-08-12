from discord.ext import tasks, commands
import discord
import os
import json
from data import data
import wallet_sdk
import requests


class wallet(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}
        # self.check_wallet_service.start()
        
        # with open(os.path.dirname(__file__) + '/../../config.json', 'r') as f:
        #     config = json.load(f)
        #     self.wallet_client = wallet_sdk.WalletClient.LoadFromConfig(os.path.dirname(__file__) + '/../../noah.client-config.json')


    # @tasks.loop(minutes=5)
    # async def check_wallet_service(self):
    #     try:
    #         self.wallet_client.check_service_health()
    #     # Noah will fix
    #     except requests.exceptions.ConnectionError as e:
    #         print("Failed to ensure wallet service is running:", e)
    #         for owner in self.bot.owner_ids:
    #             await self.bot.get_user(owner).send("Wallet service is down")
    
    # @check_wallet_service.before_loop
    # async def before_check_wallet_service(self):
    #     await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(wallet(bot))
