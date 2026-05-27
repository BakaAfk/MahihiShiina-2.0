import disnake
from disnake.ext import commands
from gtts import gTTS
import nacl
from disnake import FFmpegPCMAudio
import asyncio
import os

class TTSs(commands.Cog):
    """Chuyển văn bản thành giọng nói"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Chuyển văn bản thành giọng nói")
    async def tts(
        self, 
        inter: disnake.ApplicationCommandInteraction,
        text: str = commands.Param(description="Nội dung để phát TTS"),
        channel: disnake.VoiceChannel = commands.Param(default=None, description="Kênh voice để bot tham gia (tùy chọn)"),
        language: str = commands.Param(default="vi", description="Ngôn ngữ (optional, mặc định là tiếng Việt)")
    ):
        # Nếu không chỉ định kênh, kiểm tra kênh voice của người dùng
        if not channel:
            if inter.author.voice:
                channel = inter.author.voice.channel
            else:
                await inter.response.send_message("Bạn cần ở trong một kênh voice hoặc chỉ định kênh để bot tham gia.", ephemeral=True)
                return

        # Tạo file TTS
        tts = gTTS(text=text, lang=language)
        tts.save("tts.mp3")

        try:
            # Kiểm tra nếu bot đã ở trong một kênh voice
            voice_client = inter.guild.voice_client

            if voice_client is None:  # Nếu bot chưa kết nối kênh
                voice_client = await channel.connect()
            elif voice_client.channel.id != channel.id:  # Nếu bot đang ở kênh khác
                await voice_client.move_to(channel)

            # Phát file âm thanh
            await inter.response.send_message(f"Đang phát trong kênh voice: **{channel.name}**, nội dung: {text}")
            voice_client.play(disnake.FFmpegPCMAudio("tts.mp3"))

            # Đợi cho đến khi phát xong
            while voice_client.is_playing():
                await asyncio.sleep(1)

        except Exception as e:
            await inter.response.send_message(f"Đã xảy ra lỗi: {e}")

        finally:
            # Xóa file tạm
            if os.path.exists("tts.mp3"):
                os.remove("tts.mp3")

def setup(bot: commands.Bot):
    bot.add_cog(TTSs(bot))
