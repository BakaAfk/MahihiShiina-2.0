import disnake
from disnake.ext import commands

class VoiceLeaves(commands.Cog):
    """Rời voice channel"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Rời kênh voice")
    async def voiceleave(self, inter: disnake.ApplicationCommandInteraction):
        # Kiểm tra xem bot có đang ở trong kênh voice không
        voice_client = inter.guild.voice_client

        if voice_client is None:
            await inter.response.send_message("Bot không ở trong bất kỳ kênh voice nào.")
            return

        try:
            # Rời khỏi kênh voice
            await voice_client.disconnect()
            await inter.response.send_message("Đã rời kênh voice.")
        except Exception as e:
            await inter.response.send_message(f"Đã xảy ra lỗi khi rời kênh: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(VoiceLeaves(bot))
