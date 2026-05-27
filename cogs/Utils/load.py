import disnake
from disnake.ext import commands
import psutil


class Stat(commands.Cog):
    """Statistics command to check server load"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Kiểm tra load của server")
    async def load(self, inter: disnake.ApplicationCommandInteraction):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        ram_used = psutil.virtual_memory().used / 1048576
        ram_total = psutil.virtual_memory().total / 1048576
        
        await inter.response.send_message(f"CPU: {cpu}%\nRAM: {ram}% ({ram_used:.2f}/{ram_total:.2f} MB)")
        

def setup(bot: commands.Bot):
    bot.add_cog(Stat(bot))