import disnake
from disnake.ext import commands

import config


class MessageHex(commands.Cog):
    """Automatically decode hex messages in a specific channel and send the decoded text back to the channel"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or message.channel.id != config.HEX_CHANNEL_ID:
            return

        hex_channel = self.bot.get_channel(config.HEX_CHANNEL_ID)
        if not hex_channel:
            return

        try:
            text = bytes.fromhex(message.content).decode()
            await hex_channel.send(text)
        except ValueError:
            pass


def setup(bot: commands.Bot):
    bot.add_cog(MessageHex(bot))