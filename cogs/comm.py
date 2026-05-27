import disnake
from disnake.ext import commands


class Communication(commands.Cog):
    """Dùng bot để nhắn tin với gái :blush:"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.slash_command(description="Chat sếch với gái")
    @commands.has_permissions(administrator=True)
    async def comm(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User, *, message: str, attachment: disnake.Attachment = None):
        await inter.response.defer()
        await user.send(message)
        if attachment:
            await user.send(file=await attachment.to_file())
        if attachment:
            await inter.edit_original_message(content=f"Đã gửi tin nhắn cho {user.mention} với file đính kèm: {attachment.url}")
        else:
            await inter.edit_original_message(content=f"Đã gửi tin nhắn cho {user.mention}")
    async def comm_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")

def setup(bot: commands.Bot):
    bot.add_cog(Communication(bot))