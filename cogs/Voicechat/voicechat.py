import disnake
from disnake.ext import commands

class VoicechatCommands(commands.Cog):
    """Voice channel join command"""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Tham gia kênh voice")
    async def voicejoin(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.VoiceChannel = commands.Param(default=None, description="Kênh voice để bot tham gia (tùy chọn)")):
        # If no channel specified, try to join the voice channel the user is currently in
        if not channel:
            if inter.author.voice:
                channel = inter.author.voice.channel
            else:
                await inter.response.send_message("Bạn cần ở trong một kênh voice hoặc chỉ định kênh để bot tham gia.", ephemeral=True)
                return

        # If bot is already in a voice channel, disconnect first
        if inter.guild.voice_client:
            await inter.guild.voice_client.disconnect()

        try:
            await channel.connect()
            await inter.response.send_message(f"Đã tham gia kênh voice: **{channel.name}**")
        except Exception as e:
            await inter.response.send_message(f"Đã xảy ra lỗi: {e}")

    @commands.slash_command(description="Rời kênh voice")
    async def voiceleave(self, inter: disnake.ApplicationCommandInteraction):
        # Check if bot is in a voice channel
        voice_client = inter.guild.voice_client

        if voice_client is None:
            await inter.response.send_message("Bot không ở trong bất kỳ kênh voice nào.")
            return

        try:
            await voice_client.disconnect()
            await inter.response.send_message("Đã rời kênh voice.")
        except Exception as e:
            await inter.response.send_message(f"Đã xảy ra lỗi khi rời kênh: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(VoicechatCommands(bot))
