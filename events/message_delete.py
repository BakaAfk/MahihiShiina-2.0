import aiohttp
import io

import disnake
from disnake.ext import commands

import config


class DeleteChecker(commands.Cog):
    """Logging deleted messages"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot:
            return

        if message.channel.id == config.VENT_CHANNEL_ID:
            user = self.bot.get_user(config.OWNER_ID)
            if not user:
                return
            content = message.content or "(Không có nội dung)"
            await user.send(
                f"[VENT DELETE] {message.author.mention} trong {message.channel.mention}: {content}"
            )

            if message.attachments:
                async with aiohttp.ClientSession() as session:
                    for attachment in message.attachments:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                file = disnake.File(io.BytesIO(data), filename=attachment.filename)
                                await user.send(file=file)
                            else:
                                await user.send(f"Không thể tải file đính kèm: {attachment.filename}")
            return

        channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if not channel:
            return

        be4 = await message.channel.history(limit=10, before=message).flatten()
        found_message = be4[0] if be4 else None

        embed = disnake.Embed(
            title="Delete ehe",
            color=disnake.Color.red(),
        )

        if message.attachments:
            content = f"{message.content} \n{message.attachments[0].url}"
        else:
            content = message.content or "(Không có nội dung)"

        embed.add_field(name="Tin nhắn bị xóa", value=content, inline=False)
        embed.add_field(name="Người gửi", value=message.author.mention, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)

        if found_message:
            embed.add_field(name="Link dị điểm", value=f"[Jump to message]({found_message.jump_url})")

        embed.set_footer(text=f"ID: {message.id}")
        await channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(DeleteChecker(bot))