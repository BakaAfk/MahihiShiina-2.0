import disnake
from disnake.ext import commands, tasks

import config


class MemberCounter(commands.Cog):
    """Monitor member count and update channel names accordingly"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @tasks.loop(minutes=1)
    async def count_members(self):
        guild = self.bot.get_guild(config.GUILD_ID)
        if not guild:
            return
        online_count = 0
        offline_count = 0
        idle_count = 0
        dnd_count = 0
        total_count = 0

        for member in guild.members:
            if member.bot:
                continue
            total_count += 1
            if member.status == disnake.Status.online:
                online_count += 1
            elif member.status == disnake.Status.offline:
                offline_count += 1
            elif member.status == disnake.Status.idle:
                idle_count += 1
            elif member.status == disnake.Status.dnd:
                dnd_count += 1

        onl_channel = self.bot.get_channel(config.MEMBER_COUNTER_CHANNEL_IDS["online"])
        offl_channel = self.bot.get_channel(config.MEMBER_COUNTER_CHANNEL_IDS["offline"])
        idle_channel = self.bot.get_channel(config.MEMBER_COUNTER_CHANNEL_IDS["idle"])
        dnd_channel = self.bot.get_channel(config.MEMBER_COUNTER_CHANNEL_IDS["dnd"])

        await onl_channel.edit(name=f"🟢・Online: {online_count} / {total_count}")
        await offl_channel.edit(name=f"⚫・Offline: {offline_count} / {total_count}")
        await idle_channel.edit(name=f"🌙・Idle: {idle_count} / {total_count}")
        await dnd_channel.edit(name=f"🔴・DND: {dnd_count} / {total_count}")

    def cog_unload(self):
        self.count_members.cancel()
    
def setup(bot: commands.Bot):
    cog = MemberCounter(bot)
    bot.add_cog(cog)
    # cog.count_members.start()