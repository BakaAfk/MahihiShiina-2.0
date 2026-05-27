import disnake
from disnake.ext import commands


class UnbanMembr(commands.Cog):
    """Unban thành viên"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Ân xá cho mấy con gà")
    @commands.has_permissions(administrator=True)
    async def unban(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        # Unban user
        await inter.guild.unban(user)
        await inter.response.send_message(f"Đã unban {user.mention}", ephemeral=True)
        # Tạo embed thông báo vào log
        embed = disnake.Embed(title="Unban", description=f"{user.mention} đã được unban", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        await inter.guild.get_channel(872721744861995008).send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)
    @unban.error
    async def unban_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này", ephemeral=True)
        else:
            await inter.response.send_message("Đã có lỗi xảy ra", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(UnbanMembr(bot))