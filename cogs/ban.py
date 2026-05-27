import disnake
from disnake.ext import commands


class BanMemebr(commands.Cog):
    """Ban thành viên"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Ban mấy con gà")
    @commands.has_permissions(ban_members=True)
    async def ban(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User, *, reason: str):
        await user.send(f"Bạn đã bị ban khỏi {inter.guild.name} với lý do: {reason}")
        await inter.guild.ban(user, reason=reason)
        await inter.response.send_message(f"Đã ban {user.mention}")
        # Tạo embed thông báo vào log
        embed = disnake.Embed(title="Ban", description=f"{user.mention} đã bị ban", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.add_field(name="Reason", value=reason)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        await inter.guild.get_channel(872721744861995008).send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)
        
    @ban.error
    async def ban_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")


def setup(bot: commands.Bot):
    bot.add_cog(BanMemebr(bot))