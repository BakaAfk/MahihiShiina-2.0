import disnake
from disnake.ext import commands
import config

class MuteCommands(commands.Cog):
    """Mute related commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Cấm chat")
    @commands.has_permissions(manage_server=True)
    async def mute(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User,  time: int, reason: str):
        # Add muted role to user
        muted_role = inter.guild.get_role(config.MUTED_ROLE_ID)
        if not muted_role:
            await inter.response.send_message("Chưa cấu hình role mute.")
            return
        await inter.guild.get_member(user.id).add_roles(muted_role, reason=reason)
        await inter.response.send_message(f"Đã cấm chat {user.mention}")
        # Send embed to log channel and current channel
        embed = disnake.Embed(title="Mute Member", description=f"{user.mention} đã bị cấm chat", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.add_field(name="Reason", value=reason)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        log_channel = inter.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)
        # Mute duration
        await asyncio.sleep(time)
        # Remove muted role
        await inter.guild.get_member(user.id).remove_roles(muted_role, reason="Hết thời gian cấm chat")
        # Send embed to log channel only
        embed = disnake.Embed(title="Unmute Member", description=f"{user.mention} đã được un-mute", color=0x00FF00)
        embed.add_field(name="Moderator", value=self.bot.user.mention)
        embed.add_field(name="Reason", value="Hết thời gian cấm chat")
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        log_channel = inter.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
        
    @mute.error
    async def mute_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")
        
    @commands.slash_command(description="Thả chat all")
    @commands.has_permissions(manage_server=True)
    async def unmute(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        # Remove muted role from user 
        muted_role = inter.guild.get_role(config.MUTED_ROLE_ID)
        if not muted_role:
            await inter.response.send_message("Chưa cấu hình role mute.")
            return
        await inter.guild.get_member(user.id).remove_roles(muted_role)
        await inter.response.send_message(f"Đã thả rọ mõm {user.mention}")
        # Send embed to log channel and current channel
        embed = disnake.Embed(title="Unmute Member", description=f"{user.mention} đã được thả rọ mõm", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        log_channel = inter.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)
    
    @unmute.error
    async def unmute_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")

def setup(bot: commands.Bot):
    bot.add_cog(MuteCommands(bot))