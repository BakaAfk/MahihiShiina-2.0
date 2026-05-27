import disnake
from disnake.ext import commands
import os

class Counts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Xem số lần chửi trường")
    async def count(self, inter: disnake.ApplicationCommandInteraction):
        try:
            with open('chuitruong.txt', 'r') as f:
                lines = f.readlines()
                count_dict = {}
                for line in lines:
                    try:
                        user_id, count_value = line.split()
                        count_dict[user_id] = int(count_value)
                    except ValueError:
                        # Nếu dòng không có định dạng đúng (có thể bỏ qua)
                        continue

            # Kiểm tra xem người dùng có trong danh sách không
            user_id = str(inter.author.id)
            count_value = count_dict.get(user_id, 0)

            await inter.response.send_message(f"Bạn đã chửi trường {count_value} lần")

        except Exception as e:
            await inter.response.send_message(f"Đã xảy ra lỗi khi đọc dữ liệu: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(Counts(bot))
