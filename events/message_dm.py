import disnake
from disnake.ext import commands

import config


class MessageDM(commands.Cog):
    """Forward DM messages send to bot to a specific channel"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user:
            return

        if message.guild is not None or message.author.bot:
            return

        dump_channel = self.bot.get_channel(config.DM_DUMP_CHANNEL_ID)
        if not dump_channel:
            return

        embed = disnake.Embed(
            title="Tin nhắn DM",
            color=disnake.Color.green(),
            description=f"Tin nhắn từ {message.author.mention}",
        )

        if message.attachments:
            content = message.content + "\n" + "\n".join([attachment.url for attachment in message.attachments])
        else:
            content = message.content

        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        embed.add_field(name="Content", value=content, inline=False)
        embed.set_footer(text=f"User ID: {message.author.id}")

        await dump_channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(MessageDM(bot))