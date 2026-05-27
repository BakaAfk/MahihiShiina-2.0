import disnake
from disnake.ext import commands
import os

class Tops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Top yêu trường")
    async def top(self, inter: disnake.ApplicationCommandInteraction):
        try:
            with open('chuitruong.txt', 'r') as f:
                lines = f.readlines()
                count_dict = {}
                for line in lines:
                    user_id, count_value = line.split()
                    try:
                        count_dict[user_id] = int(count_value)
                    except ValueError:
                        # Nếu count_value không phải là số, bỏ qua dòng đó
                        continue

            if not count_dict:
                await inter.response.send_message("Không có dữ liệu hợp lệ trong danh sách.")
                return

            top = sorted(count_dict, key=lambda x: count_dict[x], reverse=True)
            top = top[:10]
            # fetch username from id
            top = [await self.bot.fetch_user(user_id) for user_id in top]
            top_list = "\n".join(f"{i+1}. {user.name} - {count_dict[str(user.id)]} lần" for i, user in enumerate(top))
            await inter.response.send_message(top_list)

        except Exception as e:
            await inter.response.send_message(f"Đã xảy ra lỗi khi đọc tệp: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(Tops(bot))
