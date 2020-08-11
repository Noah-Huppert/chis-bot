from discord.ext import tasks, commands
import discord
from data import data
import wallet_sdk


class wallet(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.info_msg = {}
        self.check_wallet_service.start()

        # self.wallet_client = wallet_sdk.WalletClient(
        #     api_url='http://127.0.0.1:8000', 
        #     authority_id='<your authority id>', 
        #     private_key=b'<your authority private key>')


    # @tasks.loop(minutes=5)
    # async def check_wallet_service(self):
    #     try:
    #         self.wallet_client.check_service_health()
    #     except wallet_sdk.WalletAPIError as e:
    #         print("Failed to ensure wallet service is running:", e)
    #         for owner in self.bot.owner_ids:
    #             self.bot.get_user(owner).send("Wallet service is down")


def setup(bot):
    bot.add_cog(wallet(bot))
