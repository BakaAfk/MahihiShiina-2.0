import disnake
from disnake.ext import commands


class VoiceBotOut(commands.Cog):
    """Out TTS bot khi channel không còn ai"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _disconnect_if_channel_empty(self, guild: disnake.Guild, channel: disnake.VoiceChannel | None):
        if channel is None:
            return

        voice_client = guild.voice_client
        if not voice_client or voice_client.channel != channel:
            return

        non_bot_members = [member for member in channel.members if not member.bot]
        if non_bot_members:
            return

        await voice_client.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        if before.channel == after.channel:
            return

        if member.id == self.bot.user.id and after.channel is None:
            return

        if before.channel and not after.channel:
            await self._disconnect_if_channel_empty(member.guild, before.channel)
            return

        if before.channel and after.channel and before.channel != after.channel:
            await self._disconnect_if_channel_empty(member.guild, before.channel)
            return

        if after.channel:
            await self._disconnect_if_channel_empty(member.guild, after.channel)
    
def setup(bot: commands.Bot):
    bot.add_cog(VoiceBotOut(bot)) 
