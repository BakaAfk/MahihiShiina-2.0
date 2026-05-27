import disnake
from disnake.ext import commands
import aiohttp
import io

import config

class Clear(commands.Cog):
    """Clear messages command"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Xóa tin nhắn")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, inter: disnake.ApplicationCommandInteraction, amount: int, member: disnake.Member = None):
        await inter.response.defer(ephemeral=True)

        def _check(message):
            if member:
                if message.author != member:
                    return False
                _check.count += 1
                return _check.count <= amount + 1
            return True

        _check.count = 0

        # If member is specified, only delete messages from that member, otherwise delete all messages up to the specified amount
        if member:
            deleted_messages = await inter.channel.purge(limit=1000, check=_check)
        else:
            deleted_messages = await inter.channel.purge(limit=amount+1)

        try:
            await inter.edit_original_message(content=f"Đã xóa {len(deleted_messages)} tin nhắn.")
        except disnake.NotFound:
            await inter.followup.send(f"Đã xóa {len(deleted_messages)} tin nhắn.", ephemeral=True)

        # If the command is used in the "special" channel, send the deleted messages to the bot owner via DM
        if inter.channel.id == config.VENT_CHANNEL_ID:
            user = self.bot.get_user(config.OWNER_ID)
            if user:
                for msg in reversed(deleted_messages):  # Reverse to maintain original order
                    try:
                        content = msg.content or "(Không có nội dung)"
                        await user.send(
                            f"[VENT CLEAR] {msg.author.mention} trong {inter.channel.mention}:\n{content}"
                        )

                        # If the message has attachments, send them as well
                        if msg.attachments:
                            async with aiohttp.ClientSession() as session:
                                for attachment in msg.attachments:
                                    async with session.get(attachment.url) as resp:
                                        if resp.status == 200:
                                            data = await resp.read()
                                            file = disnake.File(io.BytesIO(data), filename=attachment.filename)
                                            await user.send(file=file)
                                        else:
                                            await user.send(f"Không thể tải file đính kèm: {attachment.filename}")
                    except disnake.Forbidden:
                        print(f"Không thể gửi tin nhắn đến {user.name}")

    @clear.error
    async def clear_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            if inter.response.is_done():
                await inter.followup.send("Bạn không đủ quyền hạn để sử dụng lệnh này", ephemeral=True)
            else:
                await inter.response.send_message("Bạn không đủ quyền hạn để sử dụng lệnh này", ephemeral=True)
        else:
            if inter.response.is_done():
                await inter.followup.send("Đã có lỗi xảy ra", ephemeral=True)
            else:
                await inter.response.send_message("Đã có lỗi xảy ra", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Clear(bot))
    