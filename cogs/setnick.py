import disnake
from disnake.ext import commands


class SetNickname(commands.Cog):
    """Đổi nickname"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Đổi nickname") 
    @commands.has_permissions(manage_nicknames=True)
    async def setnick(self, inter: disnake.ApplicationCommandInteraction, nickname: str, user: disnake.Member = None):
        if user is None:
            user = inter.author
        await user.edit(nick=nickname)
        await inter.response.send_message(f"Đã set nickname cho {user.mention}")
    @setnick.error
    async def setnick_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")
       
        

def setup(bot: commands.Bot):
    bot.add_cog(SetNickname(bot))