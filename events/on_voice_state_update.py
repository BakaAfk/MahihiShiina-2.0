import disnake
from disnake.ext import commands
import asyncio


class VoiceBotOut(commands.Cog):
    """Out TTS bot khi channel không còn ai"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, 
                                 before: disnake.VoiceState, 
                                 after: disnake.VoiceState):
        # Bỏ qua nếu không phải là sự kiện rời channel
        if before.channel == after.channel:
            return

        # Xử lý khi bot rời channel
        if member.id == self.bot.user.id and after.channel is None:
            await self.safe_disconnect(member.guild)
            return

        # Xử lý khi thành viên rời channel
        if before.channel and not after.channel:
            voice_client = member.guild.voice_client
            
            # Chỉ xử lý nếu bot đang trong voice channel
            if voice_client and voice_client.channel == before.channel:
                if await self.is_alone(before.channel):
                    # Đợi timeout trước khi rời
                    await asyncio.sleep(self.timeout)
                    if await self.is_alone(before.channel):
                        await self.safe_disconnect(member.guild)
    
def setup(bot: commands.Bot):
    bot.add_cog(VoiceBotOut(bot)) 
