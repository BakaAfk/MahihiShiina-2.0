import disnake
from disnake.ext import commands


class OnMessage(commands.Cog):
    """Log các thay đổi của member: biệt danh, role, avatar, ..."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # Lấy các channel log
        channel = self.bot.get_channel(872721744861995008)  # ID của channel log
        dump_channel = self.bot.get_channel(874521453268193301)  # ID của channel gửi tin nhắn DM
        hex_channel = self.bot.get_channel(881881931736842250) # ID của channel sếch
        poke_role = 1508191540529467402
        if message.author == self.bot.user:
            return
        #Kiểm tra tin nhắn Poketwo
        if message.embeds and message.channel.id == 872718633539883028:
            for embed in message.embeds:
                embed_text = f"{embed.title} {embed.description}".lower()
                # Quét chuỗi nhận diện đặc trưng
                if "a wild pokémon has appeared" in embed_text:
                    await message.channel.send(f"<@&{poke_role}> A wild pokemon has appeared!!!")
                    
                    # Thoát vòng lặp embed sau khi đã ping để tránh gửi nhiều tin nhắn
                    break
        # Kiểm tra tin nhắn DM
        if message.guild is None and not message.author.bot:
            embed = disnake.Embed(
                title="Tin nhắn DM",
                color=disnake.Color.green(),
                description=f"Tin nhắn từ {message.author.mention}"
            )

            # Kiểm tra xem tin nhắn có đính kèm file không
            if message.attachments:
                content = message.content + "\n" + "\n".join([attachment.url for attachment in message.attachments])
            else:
                content = message.content

            # Thêm thông tin vào embed
            embed.set_author(name=message.author, icon_url=message.author.avatar.url)
            embed.add_field(name="Content", value=content, inline=False)
            embed.set_footer(text=f"User ID: {message.author.id}")
            
            # Gửi tin nhắn vào dump channel
            await dump_channel.send(embed=embed)

        # Danh sách các từ ngữ cần kiểm tra
        words = [
            'truong loz', 'truong lon', 'em yeu truong em', 'tron luong',
            'trường loz', 'trường lon', 'em yêu trường em', 'trốn lường',
            'truờng lồn', 'truờng lớn', 'chồn lường',
            'dm truong', 'đm truong', 'đm trường', 'dm trường',
            'l truong', 'l trường', 'truong l', 'trường l'
        ]

        # Kiểm tra từ ngữ trong tin nhắn
        for word in words:
            if word in message.content.lower():
                with open('chuitruong.txt', 'r') as f:
                    lines = f.readlines()
                    count_dict = {}

                    # Đọc và lưu trữ số lần chửi của mỗi người
                    for line in lines:
                        user_id, count_value = line.split()
                        count_dict[user_id] = int(count_value)

                user_id = str(message.author.id)
                # Cập nhật số lần chửi của người dùng
                if user_id in count_dict:
                    count_dict[user_id] += 1
                else:
                    count_dict[user_id] = 1

                # Ghi lại số lần chửi vào file
                with open('chuitruong.txt', 'w') as f:
                    for user_id in count_dict:
                        f.write(f'{user_id} {count_dict[user_id]}\n')
                break
        
        if message.channel == hex_channel:
            try:
                text = bytes.fromhex(message.content).decode()
                await hex_channel.send(text)
            except ValueError:
                pass


def setup(bot: commands.Bot):
    bot.add_cog(OnMessage(bot))
