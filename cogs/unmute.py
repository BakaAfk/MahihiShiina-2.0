import disnake
from disnake.ext import commands


class UnmuteMembr(commands.Cog):
    """Unmute thành viên"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Thả chat all")
    @commands.has_permissions(administrator=True)
    async def unmute(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        # xóa role muted 
        muted_role = inter.guild.get_role(882254188183191633)
        await inter.guild.get_member(user.id).remove_roles(muted_role)
        await inter.response.send_message(f"Đã thả rọ mõm {user.mention}")
        # Tạo embed thông báo vào log
        embed = disnake.Embed(title="Unmute Member", description=f"{user.mention} đã được thả rọ mõm", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        await inter.guild.get_channel(872721744861995008).send(embed=embed)
    
    @unmute.error
    async def unmute_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")


def setup(bot: commands.Bot):
    bot.add_cog(UnmuteMembr(bot))