import disnake
from disnake.ext import commands

import config


class MessagePoketwo(commands.Cog):
    """Automatically detect poketwo spawn messages and ping a specific role in the channel"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user:
            return

        if not message.embeds or message.channel.id != config.POKETWO_CHANNEL_ID:
            return

        for embed in message.embeds:
            embed_text = f"{embed.title} {embed.description}".lower()
            if "wild pokémon has appeared" in embed_text:
                await message.channel.send(f"<@&{config.POKETWO_PING_ROLE_ID}> A wild pokemon has appeared!!!")
                break


def setup(bot: commands.Bot):
    bot.add_cog(MessagePoketwo(bot))