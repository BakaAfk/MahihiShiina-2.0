import disnake
from disnake.ext import commands



class ConvertHex(commands.Cog):
    """Convert hex to text command"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Convert hex to text")
    async def hex2text(self, inter: disnake.ApplicationCommandInteraction, hex_string: str):
        """Convert hex to text"""
        try:
            text = bytes.fromhex(hex_string).decode()
            await inter.response.send_message(text)
        except ValueError:
            await inter.response.send_message("Hex không hợp lệ!", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(ConvertHex(bot))