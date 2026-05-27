import disnake
from disnake.ext import commands
import random

class RandomNumber(commands.Cog):
    """Random number command"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Ranđom số từ 0 đến value")
    async def random(self, inter: disnake.ApplicationCommandInteraction, value: int = 100):
        random_number = random.randint(0, value)
        await inter.response.send_message(f"Bạn roll được: {random_number}")

def setup(bot: commands.Bot):
    bot.add_cog(RandomNumber(bot))