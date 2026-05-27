import disnake
from disnake.ext import commands

class VoiceJoins(commands.Cog):
    """Vào voice channel"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Tham gia kênh voice")
    async def voicejoin(
        self,  # Đảm bảo rằng 'self' có mặt trong hàm của class
        inter: disnake.ApplicationCommandInteraction, 
        channel: disnake.VoiceChannel = commands.Param(default=None, description="Kênh voice để bot tham gia (tùy chọn)")
    ):
        # Nếu không chỉ định kênh, bot sẽ tham gia kênh mà người dùng đang ở
        if not channel:
            if inter.author.voice:
                channel = inter.author.voice.channel
            else:
                await inter.response.send_message("Bạn cần ở trong một kênh voice hoặc chỉ định kênh để bot tham gia.", ephemeral=True)
                return

        # Kiểm tra xem bot đã tham gia kênh nào chưa
        if inter.guild.voice_client:
            await inter.guild.voice_client.disconnect()

        try:
            # Bot tham gia kênh voice
            await channel.connect()
            await inter.response.send_message(f"Đã tham gia kênh voice: **{channel.name}**")
        except Exception as e:
            await inter.response.send_message(f"Đã xảy ra lỗi: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(VoiceJoins(bot))
