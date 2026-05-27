import disnake
from disnake.ext import commands


class Banlist(commands.Cog):
    """Lấy danh sách member bị ban"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Mấy con gà")
    async def banlist(self, inter: disnake.ApplicationCommandInteraction):
        # Lấy danh sách member bị ban
        bans = await inter.guild.bans().flatten()
        # Tạo embed
        embed = disnake.Embed(title="Danh sách member bị ban", color=0xFF0000)
        for ban in bans:
            embed.add_field(name=ban.user, value=f'{ban.user.id}\n{ban.reason}')
            embed.set_author(name=inter.author, icon_url=inter.author.avatar.url)
            embed.set_footer(text=f"Tổng cộng {len(bans)} member")
        await inter.response.send_message(embed=embed)
       


def setup(bot: commands.Bot):
    bot.add_cog(Banlist(bot))