import disnake
from disnake.ext import commands
import aiohttp
import io


class DeleteCheker(commands.Cog):
    """Log tin nhắn bị xóa"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        # Check tin nhắn của bot
        if message.author.bot:
            return
        
        # Check channel bị bỏ qua
        elif message.channel.id == 1012236568066531338:
            user = self.bot.get_user(1067718540221743134)
            if not user:
                return

            await user.send(
                f"Đã xóa tin nhắn của {message.author.mention} trong {message.channel.mention}: {message.content or '(Không có nội dung)'}"
            )

            if message.attachments:
                attachment = message.attachments[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            file = disnake.File(io.BytesIO(data), filename=attachment.filename)
                            await user.send("Ảnh đính kèm:", file=file)
                        else:
                            await user.send("Không thể tải ảnh đính kèm.")

        # Gửi log vào channel log 
        else:      
            channel = self.bot.get_channel(872721744861995008) # ID của channel log
            be4 = await message.channel.history(limit=10, before=message).flatten()
            found_message = be4[0] if be4 else None

            # Tạo embed
            embed = disnake.Embed(
                title="Delete ehe",
                color=disnake.Color.red()
            )

            if message.attachments:
                content = f"{message.content} \n{message.attachments[0].url}"
            else:
                content = message.content or "(Không có nội dung)"
                
            embed.add_field(name="Tin nhắn bị xóa", value=content, inline=False)
            embed.add_field(name="Người gửi", value=message.author.mention, inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)

            if found_message:
                embed.add_field(name="Link dị điểm", value=f"[Jump to message]({found_message.jump_url})")

            embed.set_footer(text=f"ID: {message.id}")
            await channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(DeleteCheker(bot))
    