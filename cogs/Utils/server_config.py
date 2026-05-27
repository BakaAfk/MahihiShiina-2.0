import disnake
from disnake.ext import commands

import config


CHANNEL_SETTINGS = {
    "log_channel": "LOG_CHANNEL_ID",
    "dm_dump_channel": "DM_DUMP_CHANNEL_ID",
    "hex_channel": "HEX_CHANNEL_ID",
    "poketwo_channel": "POKETWO_CHANNEL_ID",
    "online_channel": "MEMBER_COUNTER_CHANNEL_IDS.online",
    "offline_channel": "MEMBER_COUNTER_CHANNEL_IDS.offline",
    "idle_channel": "MEMBER_COUNTER_CHANNEL_IDS.idle",
    "dnd_channel": "MEMBER_COUNTER_CHANNEL_IDS.dnd",
}

ROLE_SETTINGS = {
    "muted_role": "MUTED_ROLE_ID",
    "poketwo_ping_role": "POKETWO_PING_ROLE_ID",
}


class ServerConfig(commands.Cog):
    """Server config commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _current_config_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title="Server Config",
            color=disnake.Color.blurple(),
            description="Cấu hình hiện tại của bot trong server này.",
        )
        embed.add_field(name="Log channel", value=f"<#{config.LOG_CHANNEL_ID}>", inline=False)
        embed.add_field(name="DM dump channel", value=f"<#{config.DM_DUMP_CHANNEL_ID}>", inline=False)
        embed.add_field(name="Hex channel", value=f"<#{config.HEX_CHANNEL_ID}>", inline=False)
        embed.add_field(name="Poketwo channel", value=f"<#{config.POKETWO_CHANNEL_ID}>", inline=False)
        embed.add_field(name="Muted role", value=f"<@&{config.MUTED_ROLE_ID}>", inline=False)
        embed.add_field(name="Poketwo ping role", value=f"<@&{config.POKETWO_PING_ROLE_ID}>", inline=False)
        embed.add_field(
            name="Member counters",
            value=(
                f"Online: <#{config.MEMBER_COUNTER_CHANNEL_IDS['online']}>\n"
                f"Offline: <#{config.MEMBER_COUNTER_CHANNEL_IDS['offline']}>\n"
                f"Idle: <#{config.MEMBER_COUNTER_CHANNEL_IDS['idle']}>\n"
                f"DND: <#{config.MEMBER_COUNTER_CHANNEL_IDS['dnd']}>"
            ),
            inline=False,
        )
        return embed

    def _set_channel_setting(self, setting: str, channel: disnake.TextChannel):
        if setting == "log_channel":
            config.set_setting("LOG_CHANNEL_ID", channel.id)
        elif setting == "dm_dump_channel":
            config.set_setting("DM_DUMP_CHANNEL_ID", channel.id)
        elif setting == "hex_channel":
            config.set_setting("HEX_CHANNEL_ID", channel.id)
        elif setting == "poketwo_channel":
            config.set_setting("POKETWO_CHANNEL_ID", channel.id)
        elif setting == "online_channel":
            config.MEMBER_COUNTER_CHANNEL_IDS["online"] = channel.id
            config.set_setting("MEMBER_COUNTER_CHANNEL_IDS", config.MEMBER_COUNTER_CHANNEL_IDS)
        elif setting == "offline_channel":
            config.MEMBER_COUNTER_CHANNEL_IDS["offline"] = channel.id
            config.set_setting("MEMBER_COUNTER_CHANNEL_IDS", config.MEMBER_COUNTER_CHANNEL_IDS)
        elif setting == "idle_channel":
            config.MEMBER_COUNTER_CHANNEL_IDS["idle"] = channel.id
            config.set_setting("MEMBER_COUNTER_CHANNEL_IDS", config.MEMBER_COUNTER_CHANNEL_IDS)
        elif setting == "dnd_channel":
            config.MEMBER_COUNTER_CHANNEL_IDS["dnd"] = channel.id
            config.set_setting("MEMBER_COUNTER_CHANNEL_IDS", config.MEMBER_COUNTER_CHANNEL_IDS)

    def _set_role_setting(self, setting: str, role: disnake.Role):
        if setting == "muted_role":
            config.set_setting("MUTED_ROLE_ID", role.id)
        elif setting == "poketwo_ping_role":
            config.set_setting("POKETWO_PING_ROLE_ID", role.id)

    @commands.slash_command(name="config", description="Cấu hình bot cho server")
    @commands.has_permissions(administrator=True)
    async def config_command(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(embed=self._current_config_embed(), ephemeral=True)

    @config_command.sub_command(name="show", description="Xem cấu hình hiện tại")
    @commands.has_permissions(administrator=True)
    async def config_show(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(embed=self._current_config_embed(), ephemeral=True)

    @config_command.sub_command(name="channel", description="Đặt channel cho setting")
    @commands.has_permissions(administrator=True)
    async def config_channel(
        self,
        inter: disnake.ApplicationCommandInteraction,
        setting: str = commands.Param(choices=list(CHANNEL_SETTINGS.keys())),
        channel: disnake.TextChannel = commands.Param(),
    ):
        self._set_channel_setting(setting, channel)
        await inter.response.send_message(f"Đã set {setting} = {channel.mention}", ephemeral=True)

    @config_command.sub_command(name="role", description="Đặt role cho setting")
    @commands.has_permissions(administrator=True)
    async def config_role(
        self,
        inter: disnake.ApplicationCommandInteraction,
        setting: str = commands.Param(choices=list(ROLE_SETTINGS.keys())),
        role: disnake.Role = commands.Param(),
    ):
        self._set_role_setting(setting, role)
        await inter.response.send_message(f"Đã set {setting} = {role.mention}", ephemeral=True)

    @config_command.sub_command(name="reset", description="Reset toàn bộ config về mặc định")
    @commands.has_permissions(administrator=True)
    async def config_reset(self, inter: disnake.ApplicationCommandInteraction):
        config.reset_setting()
        await inter.response.send_message("Đã reset toàn bộ config về mặc định.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(ServerConfig(bot))
