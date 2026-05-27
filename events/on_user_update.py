import disnake
from disnake.ext import commands

import config


class MemberUpdate(commands.Cog):
    """Log member updates such as role changes, nickname changes, and avatar changes to a specific channel"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _build_update_embed(
        self,
        *,
        title: str,
        color: disnake.Color,
        description: str,
        field_name: str,
        field_value: str,
        member: disnake.Member,
    ) -> disnake.Embed:
        embed = disnake.Embed(title=title, color=color, description=description)
        embed.add_field(name=field_name, value=field_value, inline=False)
        embed.set_footer(text=f"User ID: {member.id}")
        return embed

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if not channel:
            return

        embeds: list[disnake.Embed] = []

        added_roles = [role for role in after.roles if role not in before.roles and not role.is_default()]
        removed_roles = [role for role in before.roles if role not in after.roles and not role.is_default()]

        if added_roles:
            embeds.append(
                self._build_update_embed(
                    title="Member Update",
                    color=disnake.Color.red(),
                    description=f"Đã thêm role cho {after.mention}",
                    field_name=":white_check_mark: Role đã thêm",
                    field_value=", ".join(role.mention for role in added_roles),
                    member=after,
                )
            )

        if removed_roles:
            embeds.append(
                self._build_update_embed(
                    title="Member Update",
                    color=disnake.Color.red(),
                    description=f"Đã xóa role cho {after.mention}",
                    field_name=":x: Role đã xóa",
                    field_value=", ".join(role.mention for role in removed_roles),
                    member=after,
                )
            )

        if before.nick != after.nick:
            old_nick = before.nick or ""
            new_nick = after.nick or ""
            embeds.append(
                self._build_update_embed(
                    title="Member Update",
                    color=disnake.Color.red(),
                    description=f"Nickname của {after.mention} đã thay đổi",
                    field_name=":pencil: Nickname",
                    field_value=f"{old_nick} -> {new_nick}",
                    member=after,
                )
            )

        if before.display_avatar.url != after.display_avatar.url:
            embed = disnake.Embed(
                title="Member Update",
                color=disnake.Color.green(),
                description=f"Avatar của {after.mention} đã thay đổi",
            )
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            embed.add_field(name="Before", value=before.display_avatar.url, inline=False)
            embed.add_field(name="After", value=after.display_avatar.url, inline=False)
            embed.set_footer(text=f"User ID: {after.id}")
            embeds.append(embed)

        for embed in embeds:
            await channel.send(embed=embed)
