import disnake
from disnake.ext import commands
import asyncio


class MuteMember(commands.Cog):
    """Mute thành viên"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Cấm chat")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User,  time: int, reason: str):
        # Add muted role to user
        muted_role = inter.guild.get_role(882254188183191633)
        await inter.guild.get_member(user.id).add_roles(muted_role, reason=reason)
        await inter.response.send_message(f"Đã cấm chat {user.mention}")
        # Tạo embed thông báo vào log
        embed = disnake.Embed(title="Mute Member", description=f"{user.mention} đã bị cấm chat", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.add_field(name="Reason", value=reason)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        await inter.guild.get_channel(872721744861995008).send(embed=embed)
        # Delay thời gian mute
        await asyncio.sleep(time)
        # Gỡ role cấm chat
        await inter.guild.get_member(user.id).remove_roles(muted_role, reason="Hết thời gian cấm chat")
        # Gửi embed thông báo vào log
        embed = disnake.Embed(title="Unmute Member", description=f"{user.mention} đã được un-mute", color=0x00FF00)
        embed.add_field(name="Moderator", value=self.bot.user.mention)
        embed.add_field(name="Reason", value="Hết thời gian cấm chat")
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        await inter.guild.get_channel(872721744861995008).send(embed=embed)
        
        


def setup(bot: commands.Bot):
    bot.add_cog(MuteMember(bot))