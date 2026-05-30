import disnake
from disnake.ext import commands
import asyncio


class ServerInfo(commands.Cog):
    """Get information about the server"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Lấy thông tin của server")
    async def serverinfo(self, inter: disnake.ApplicationCommandInteraction):
        role_count = len(inter.guild.roles)
        list_of_bots = [bot.mention for bot in inter.guild.members if bot.bot]
        # Get all roles with administrator permissions and list their members
        staff_role = [role.id for role in inter.guild.roles]
        staff_role.reverse()
        staff_role = staff_role[:2]
        
                
        created_at = inter.guild.created_at.timestamp()
        text_channel_count = len(inter.guild.text_channels)
        voice_channel_count = len(inter.guild.voice_channels)
        member_count = inter.guild.member_count
        
        embed = disnake.Embed(title=f"Thông tin của server {inter.guild.name}", color=inter.user.color, timestamp=inter.created_at)
        embed.add_field(name="ID", value=inter.guild.id, inline=False)
        embed.add_field(name="Chủ server", value=inter.guild.owner.mention, inline=False)
        embed.add_field(name="Ngày tạo server", value=f"<t:{int(created_at)}:F>", inline=False)
        embed.add_field(name="Min mod", value="\u200b", inline=False)
        for r in staff_role:
            role = inter.guild.get_role(r)
            if role:
                staff = '\n'.join([member.name for member in role.members]) or "Không có"
                embed.add_field(name=role.name, value=staff, inline=True)
        embed.add_field(name="Role", value=str(role_count), inline=True)
        embed.add_field(name="Channel", value=f"Text: {text_channel_count}\nVoice: {voice_channel_count}", inline=True)
        embed.add_field(name="Mêm bờ", value=f"Tổng số: {member_count}\nHoomen: {member_count - len(list_of_bots)}", inline=True)
        embed.add_field(name=f"Bot: {len(list_of_bots)}", value=",".join(list_of_bots) or "Không có", inline=False)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.set_thumbnail(url=inter.guild.icon.url)
        embed.set_footer(text=f"Requested bởi {inter.author} | ID: {inter.author.id}", icon_url=inter.author.avatar.url)
        await inter.response.send_message(embed=embed)
            
        
        
        


def setup(bot: commands.Bot):
    bot.add_cog(ServerInfo(bot))