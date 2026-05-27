import disnake
from disnake.ext import commands



class UserInfo(commands.Cog):
    """Get information about a user"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Lấy thông tin của user")
    async def userinfo(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
        if not user:
            user = inter.author
        acc_created = user.created_at.timestamp()
        acc_join = user.joined_at.timestamp()
        info = {"Id": user.id, "Quyền": user.guild_permissions}
        if user.guild_permissions.administrator:
            perm = "Admin"
            rank = "Server Admin"
        else:
            perm_list = [perm[0] for perm in info["Quyền"] if perm[1]]
            perm_real = [
                "manage_server", "manage_roles", "manage_channels",
                "manage_messages", "manage_webhooks", "manage_nicknames",
                "manage_emojis", "kick_members", "ban_members", "mention_everyone"
                         
            ]
            perm = "\n".join([perm for perm in perm_list if perm in perm_real])
        role = "".join([role.mention for role in user.roles if role.name != "@everyone"])
        if role == "":
            role = "\u200b"
        if user.bot:
            rank = "Bot"
        elif user == inter.guild.owner:
            rank = "Server Owner"
        embed = disnake.Embed(title=f"Thông tin của {user}", color=inter.user.color, timestamp=inter.created_at)
        embed.set_footer(text=f"Requested bởi {inter.author} | ID: {inter.author.id}", icon_url=inter.author.avatar.url)
        embed.set_author(name=user, icon_url=user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="User ID", value=info["Id"], inline=False)
        embed.add_field(name="Ngày tạo tài khoản", value=f"<t:{int(acc_created)}:F>", inline=False)
        embed.add_field(name="Ngày tham gia server", value=f"<t:{int(acc_join)}:F>", inline=False)
        embed.add_field(name="Vai trò", value=role, inline=False)
        embed.add_field(name="Trạng thái", value=user.status, inline=True)
        embed.add_field(name="Quyền công dân", value=perm, inline=True)
        try:
            embed.add_field(name="Rank", value=rank, inline=False)
        except:
            pass
        await inter.response.send_message(embed=embed)

        
        
        


def setup(bot: commands.Bot):
    bot.add_cog(UserInfo(bot))