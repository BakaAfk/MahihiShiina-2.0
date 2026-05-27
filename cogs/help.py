import disnake
from disnake.ext import commands


class HelpCommand(commands.Cog):
    """Các câu lệnh của bot"""
    @commands.slash_command(description="Hiển thị danh sách câu lệnh")
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        admin_cmd = {
        'ban': 'Ban người dùng',
        'banlist': 'Danh sách người bị ban',
        'clear': 'Xóa tin nhắn (theo người dùng hoặc số lượng) (cần perm Manage message)',
        'comm': 'Giao tiếp qua bot',
        'kick': 'Kick người (cần perm Moderate member)',
        'mute': 'Mute người (cần perm Manage roles)',
        'setnick': 'Đổi nickname người khác (cần perm Manage nicknames)',
        'unban': 'Unban người dùng',
        'unmute': 'Unmute người dùng',
    }
    
        nor_cmd = {
        "ping": "Kiểm tra độ trễ bot",
        'help': 'Hiển thị danh sách câu lệnh',
        'random': 'Như tên',
        'load': 'Kiểm tra load của server',
        'serverinfo': 'Lấy thông tin của server',
        'userinfo': 'Lấy thông tin của user', 
    }
    
        embed = disnake.Embed(title="Danh sách câu lệnh", description="Dưới đây là danh sách các câu lệnh của bot", color=0x00FF00)
        embed.add_field(name="Admin commands", value="\n".join([f"{key}: {value}" for key, value in admin_cmd.items()]))
        embed.add_field(name="Normal commands", value="\n".join([f"{key}: {value}" for key, value in nor_cmd.items()]))
        embed.set_footer(text="Đối với admin commands, perm yêu cầu mặc định là Administator")
        embed.set_author(name="Help command", icon_url="https://i.imgur.com/SgHKpzA.png")
        await inter.response.send_message(embed=embed)

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    


def setup(bot: commands.Bot):
    bot.add_cog(HelpCommand(bot))