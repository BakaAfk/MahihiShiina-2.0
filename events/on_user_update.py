import disnake
from disnake.ext import commands


class MemberUpdate(commands.Cog):
    """Log các thay đổi của member: biệt danh, role, avatar, ..."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        channel = self.bot.get_channel(872721744861995008) # ID của channel log
        
        # Kiểm tra thay đổi vai trò
        if before.roles != after.roles:
            roleUpdate = list(set(after.roles) - set(before.roles))
            if roleUpdate: # Thêm role
                roleChange = ", ".join([role.mention for role in roleUpdate])
                cat = "Role added"

                
            else: # Xóa role
                roleUpdate = list(set(before.roles) - set(after.roles))
                roleChange = ", ".join([role.mention for role in roleUpdate])
                cat = "Role removed"

        
        # Kiểm tra thay đổi biệt danh
        if before.nick != after.nick:
            cat = "Nickname"
            if before.nick is None:
                before.nick = ""
            if after.nick is None:
                after.nick = ""

        
        '''# Kiểm tra thay đổi avatar (đéo biết check)
        if before.avatar != after.avatar:
            cat = "Avatar"
            #embed cho avatar
            embed = disnake.Embed(
                title="Avatar changed",
                color=disnake.Color.green()
            )
            embed.set_author(name=after, icon_url=after.avatar.url)
            embed.add_field(name="Before", value=before.avatar.url, inline=False)
            embed.add_field(name="After", value=after.avatar.url, inline=False)
            embed.set_footer(text=f"User ID: {after.id}")
            await channel.send(embed=embed)'''
                
                
        # Tạo embed 
        if cat == "Role added": 
            descrip = f'Đã thêm role cho {after.mention}'
            f1n = ":white_check_mark: Role đã thêm"
            val1 = f"{roleChange}"
        elif cat == "Role removed":
            descrip = f'Đã xóa role cho {after.mention}'
            f1n = ":x: Role đã xóa"
            val1 = f"{roleChange}"
        elif cat == "Nickname":
            descrip = f'Nickname của {after.mention} đã thay đổi'
            f1n = ":pencil: Nickname"
            val1 = f"{before.nick} -> {after.nick}"
        embed = disnake.Embed(
            title="Member Update",
            color=disnake.Color.red(),
            description=descrip
        )
        embed.add_field(name=f1n, value=val1, inline=False)
        embed.set_footer(text=f"User ID: {after.id}")
        await channel.send(embed=embed)
    
        
def setup(bot: commands.Bot):
    bot.add_cog(MemberUpdate(bot))