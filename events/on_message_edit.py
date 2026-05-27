import disnake
from disnake.ext import commands

import config


class MessageEdit(commands.Cog):
    """Logging edited messages"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        channel = self.bot.get_channel(config.LOG_CHANNEL_ID) # ID của channel log
        if not channel:
            return
        
        # Skip bot messages, unchanged messages, and messages in the ignored channel
        if before.author.bot:
            return
        elif before.content == after.content:
            return
        elif before.channel.id == config.VENT_CHANNEL_ID:
            user = self.bot.get_user(config.OWNER_ID)
            if not user:
                return
            await user.send(
                f"[VENT EDIT] {before.author.mention} trong {after.channel.mention}: {before.content or '(Không có nội dung)'} -> {after.content or '(Không có nội dung)'}"
            )
        # Gửi log vào channel log
        else:
            embed = disnake.Embed(
                title="Edit ehe",
                color=disnake.Color.orange()
            )
            embed.add_field(name="Tin nhắn trước", value=before.content, inline=False)
            embed.add_field(name="Tin nhắn sau", value=after.content, inline=False)
            embed.add_field(name="Người gửi", value=before.author.mention, inline=False)
            embed.add_field(name="Channel", value=before.channel.mention, inline=False)
            embed.add_field(name="Link dị điểm", value=f"[Jump to message]({after.jump_url})")
            embed.set_footer(text=f"ID tin nhắn: {before.id}")
            await channel.send(embed=embed)
        
def setup(bot: commands.Bot):
    bot.add_cog(MessageEdit(bot))