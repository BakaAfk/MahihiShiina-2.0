import disnake
from disnake.ext import commands

import config

class BanCommands(commands.Cog):
    """Ban related commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Ban mấy con gà")
    @commands.has_permissions(ban_members=True)
    async def ban(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User, *, reason: str):
        await user.send(f"Bạn đã bị ban khỏi {inter.guild.name} với lý do: {reason}")
        await inter.guild.ban(user, reason=reason)
        await inter.response.send_message(f"Đã ban {user.mention}")
        # Send embed to log channel and current channel
        embed = disnake.Embed(title="Ban", description=f"{user.mention} đã bị ban", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.add_field(name="Reason", value=reason)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        log_channel = inter.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)
        
    @ban.error
    async def ban_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này")
        else:
            await inter.response.send_message("Đã có lỗi xảy ra")

    @commands.slash_command(description="Ân xá cho mấy con gà")
    @commands.has_permissions(ban_members=True)
    async def unban(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        # Unban user
        await inter.guild.unban(user)
        await inter.response.send_message(f"Đã unban {user.mention}", ephemeral=True)
        # Send embed to log channel and current channel
        embed = disnake.Embed(title="Unban", description=f"{user.mention} đã được unban", color=0xFF0000)
        embed.add_field(name="Moderator", value=inter.author.mention)
        embed.set_author(name=user.mention, icon_url=user.avatar.url)
        log_channel = inter.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)

    @unban.error
    async def unban_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này", ephemeral=True)
        else:
            await inter.response.send_message("Đã có lỗi xảy ra", ephemeral=True)
    
    @commands.slash_command(description="Mấy con gà")
    async def banlist(self, inter: disnake.ApplicationCommandInteraction):
        # Extract the list of banned members
        bans = await inter.guild.bans().flatten()
        # Create embed
        embed = disnake.Embed(title="Danh sách member bị ban", color=0xFF0000)
        for ban_entry in bans:
            user = ban_entry.user
            reason = ban_entry.reason or "Không có lý do"
            embed.add_field(name=user.mention, value=f"Lý do: {reason}", inline=False)
        await inter.response.send_message(embed=embed)
        embed.set_author(name=inter.author, icon_url=inter.author.avatar.url)
        await inter.guild.get_channel(inter.channel_id).send(embed=embed)   

def setup(bot: commands.Bot):
    bot.add_cog(BanCommands(bot))
