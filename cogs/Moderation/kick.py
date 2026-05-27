import disnake
from disnake.ext import commands

import config

class KickCommands(commands.Cog):
    """Kick command"""
    
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
        # Send embed to log channel and current channel
        embed = disnake.Embed(title="Kick", description=f"{user.mention} đã bị sút", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.add_field(name="Reason", value=reason)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        log_channel = inter.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)
        
    @kick.error
    async def kick_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")

def setup(bot: commands.Bot):
    bot.add_cog(KickCommands(bot))