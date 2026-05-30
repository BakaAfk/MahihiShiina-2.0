import asyncio
import disnake
from disnake.ext import commands

class VoicechatCommands(commands.Cog):
    
    async def _safe_disconnect(self, guild: disnake.Guild):
        """Safe disconnect and cleanup voice client"""
        vc = guild.voice_client
        if vc is None:
            return
        try:
            vc.stop()
        except Exception:
            pass
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass
        # Wait for connection fully closed
        await asyncio.sleep(0.5)

    @commands.slash_command(description="Tham gia kênh voice")
    async def voicejoin(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.VoiceChannel = commands.Param(default=None, description="Kênh voice để bot tham gia (tùy chọn)")):
        if not channel:
            if inter.author.voice:
                channel = inter.author.voice.channel
            else:
                await inter.response.send_message(
                    "Bạn cần ở trong một kênh voice hoặc chỉ định kênh để bot tham gia.",
                    ephemeral=True
                )
                return

        await inter.response.defer(ephemeral=True)

        vc = inter.guild.voice_client

        if vc is not None and vc.is_connected() and vc.channel.id == channel.id:
            await inter.edit_original_message(content=f"Bot đã ở trong kênh **{channel.name}** rồi.")
            return

        await self._safe_disconnect(inter.guild)
 
        try:
            await asyncio.wait_for(channel.connect(), timeout=15.0)
            await inter.edit_original_message(content=f"Đã tham gia kênh: **{channel.name}**")
        except asyncio.TimeoutError:
            await self._safe_disconnect(inter.guild)
            await inter.edit_original_message(content="Timeout khi kết nối voice. Discord server có thể đang lag.")
        except Exception as e:
            await self._safe_disconnect(inter.guild)
            await inter.edit_original_message(content=f" Đã xảy ra lỗi: {e}")

    @commands.slash_command(description="Rời kênh voice")
    async def voiceleave(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        vc = inter.guild.voice_client
        if vc is None:
            await inter.edit_original_message(content="Bot không ở trong kênh voice nào.")
            return
        channel_name = vc.channel.name
        await self._safe_disconnect(inter.guild)
        await inter.edit_original_message(content=f"Đã rời kênh: **{channel_name}**")

def setup(bot: commands.Bot):
    bot.add_cog(VoicechatCommands(bot))
