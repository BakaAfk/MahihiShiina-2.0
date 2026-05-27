import disnake
from disnake.ext import commands
import aiohttp
import io

class Clear(commands.Cog):
    """Xóa tin nhắn"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Xóa tin nhắn")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, inter: disnake.ApplicationCommandInteraction, amount: int, member: disnake.Member = None):
        await inter.response.defer(with_message=True)

        def _check(message):
            if member:
                if message.author != member:
                    return False
                _check.count += 1
                return _check.count <= amount + 1
            return True

        _check.count = 0

        # Xóa tin nhắn
        if member:
            deleted_messages = await inter.channel.purge(limit=1000, check=_check)
        else:
            deleted_messages = await inter.channel.purge(limit=amount+1)

        await inter.edit_original_message(content=f"Đã xóa {len(deleted_messages)} tin nhắn.")

        # Nếu là kênh đặc biệt, gửi toàn bộ log vào DM
        if inter.channel.id == 1012236568066531338:
            user = self.bot.get_user(1067718540221743134)
            if user:
                for msg in reversed(deleted_messages):  # đảo ngược để đúng thứ tự thời gian
                    try:
                        content = msg.content or "(Không có nội dung)"
                        await user.send(
                            f"Đã xóa tin nhắn của {msg.author.mention} trong {inter.channel.mention}:\n{content}"
                        )

                        # Gửi tất cả các tệp đính kèm
                        if msg.attachments:
                            async with aiohttp.ClientSession() as session:
                                for attachment in msg.attachments:
                                    async with session.get(attachment.url) as resp:
                                        if resp.status == 200:
                                            data = await resp.read()
                                            file = disnake.File(io.BytesIO(data), filename=attachment.filename)
                                            await user.send(file=file)
                                        else:
                                            await user.send("Không thể tải ảnh đính kèm.")
                    except disnake.Forbidden:
                        print(f"Không thể gửi tin nhắn đến {user.name}")

    @clear.error
    async def clear_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")

def setup(bot: commands.Bot):
    bot.add_cog(Clear(bot))
    