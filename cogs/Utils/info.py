import disnake
from disnake.ext import commands

class OutsideUserInfo(commands.Cog):
    """Get information about any user by their ID, even if they are not in the server"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Lấy thông tin của user")
    async def info(self, inter: disnake.ApplicationCommandInteraction, id: str = None):  # Đổi id thành str
        try:
            if not id:
                user = inter.author
            else:
                user_id = int(id) 
                if user_id <= 0:
                    raise ValueError("ID phải là số dương.")
                user = await self.bot.fetch_user(user_id)  

            acc_created = user.created_at.timestamp()
            info = {"Id": user.id}
            embed = disnake.Embed(title=f"Thông tin của {user}", color=inter.user.color, timestamp=inter.created_at)
            embed.set_footer(text=f"Requested bởi {inter.author} | ID: {inter.author.id}", icon_url=inter.author.avatar.url)
            embed.set_author(name=user, icon_url=user.avatar.url)
            embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="User ID", value=info["Id"], inline=False)
            embed.add_field(name="Ngày tạo tài khoản", value=f"<t:{int(acc_created)}:F>", inline=False)
            await inter.response.send_message(embed=embed)

        except ValueError as ve:
            await inter.response.send_message(f"Lỗi: {ve}")
        except disnake.NotFound:
            await inter.response.send_message(f"Không tìm thấy user với ID {id}.")
        except Exception as e:
            await inter.response.send_message(f"Có lỗi xảy ra: {str(e)}")

def setup(bot: commands.Bot):
    bot.add_cog(OutsideUserInfo(bot))