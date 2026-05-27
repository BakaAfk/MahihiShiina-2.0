import disnake
from disnake.ext import commands


class KickMemebr(commands.Cog):
    """Kick thành viên"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Kick mấy con gà")
    @commands.has_permissions(kick_members=True)
    async def kick(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User, *, reason: str):
        try:
            await user.send(f"Bạn đã bị sút khỏi {inter.guild.name} với lý do: {reason}")
        except:
            pass
        await inter.guild.kick(user, reason=reason)
        await inter.response.send_message(f"Đã sút {user.mention}. Siuuuuuu")
        # Tạo embed thông báo vào log
        embed = disnake.Embed(title="Kick", description=f"{user.mention} đã bị sút", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.add_field(name="Reason", value=reason)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        await inter.guild.get_channel(872721744861995008).send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)
        
    @kick.error
    async def kick_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")


def setup(bot: commands.Bot):
    bot.add_cog(KickMemebr(bot))