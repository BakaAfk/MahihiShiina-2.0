import disnake
from disnake.ext import commands


class PingCommand(commands.Cog):
    """Check độ trễ của bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Check độ trễ của bot")
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(f"Pong! trong {round(self.bot.latency * 1000)}ms")


def setup(bot: commands.Bot):
    bot.add_cog(PingCommand(bot))