import disnake
from disnake.ext import commands


class MessageEdit(commands.Cog):
    """Log thay đổi tin nhắn"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        channel = self.bot.get_channel(872721744861995008) # ID của channel log
        
        # Check tin nhắn của bot
        if before.author.bot:
            return
        elif before.content == after.content:
            return
        # Check channel bị bỏ qua
        elif before.channel.id == 1012236568066531338:
            user = self.bot.get_user(1067718540221743134)
            await user.send(f"{before.author.mention} đã chỉnh sửa tin nhắn trong {after.channel.mention}: {before.content} -> {after.content}")
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