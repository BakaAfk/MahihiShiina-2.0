import disnake
from disnake.ext import commands, tasks


class MemberCounter(commands.Cog):
    """Đếm số thành viên onl / off"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.onl_channel_id = 1367502522482294794
        self.offl_channel_id = 1367502599384731668
        self.idle_channel_id = 1367502406060871771
        self.dnd_channel_id = 1367503242958737478

    @tasks.loop(minutes=1)
    async def count_members(self):
        guild = self.bot.get_guild(872692134845759508)  
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

        onl_channel = self.bot.get_channel(self.onl_channel_id)
        offl_channel = self.bot.get_channel(self.offl_channel_id)
        idle_channel = self.bot.get_channel(self.idle_channel_id)
        dnd_channel = self.bot.get_channel(self.dnd_channel_id)

        await onl_channel.edit(name=f"🟢・Online: {online_count} / {total_count}")
        await offl_channel.edit(name=f"⚫・Offline: {offline_count} / {total_count}")
        await idle_channel.edit(name=f"🌙・Idle: {idle_count} / {total_count}")
        await dnd_channel.edit(name=f"🔴・DND: {dnd_count} / {total_count}")
    
def setup(bot: commands.Bot):
    bot.add_cog(MemberCounter(bot))