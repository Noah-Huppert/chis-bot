from discord.ext import tasks, commands
import discord
import os
import json
import logging
from data import data
import wallet_sdk
import requests


class wallet(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}
        self.wallet_client = wallet_sdk.WalletClient.LoadFromConfig(os.path.dirname(__file__) + '/../../rat-king.prod.client-config.json')
        self.check_wallet_service.start()


    @commands.command(name='wallet', aliases=[])
    async def wallet_command(self, ctx):
        """ gets all wallets
        """
        logging.info(self.wallet_client.get_wallets())

    @tasks.loop(minutes=5)
    async def check_wallet_service(self):
        try:
            self.wallet_client.check_service_health()
        except wallet_sdk.WalletAPIError as e:
            logging.error(f"wallet service not healthy: {e}")
            for owner in self.bot.owner_ids:
                await self.bot.get_user(owner).send("Wallet service is down")
    
    @check_wallet_service.before_loop
    async def before_check_wallet_service(self):
        await self.bot.wait_until_ready()
