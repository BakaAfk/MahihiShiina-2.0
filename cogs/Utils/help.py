import disnake
from disnake.ext import commands


class HelpCommand(commands.Cog):
    """Các câu lệnh của bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _format_command_line(self, command: commands.InvokableSlashCommand) -> str:
        description = command.description or "Không có mô tả"
        return f"`/{command.qualified_name}` - {description}"

    def _chunk_lines(self, lines: list[str], limit: int = 1024) -> list[str]:
        chunks: list[str] = []
        current: list[str] = []
        current_length = 0

        for line in lines:
            line_length = len(line) + (1 if current else 0)
            if current and current_length + line_length > limit:
                chunks.append("\n".join(current))
                current = [line]
                current_length = len(line)
            else:
                current.append(line)
                current_length += line_length

        if current:
            chunks.append("\n".join(current))

        return chunks

    def _build_help_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title="Danh sách câu lệnh",
            description="Tự động lấy từ các cog đã load trong thư mục `cogs`.",
            color=0x00FF00,
        )
        embed.set_author(name="Help command", icon_url="https://i.imgur.com/SgHKpzA.png")

        fields_added = 0
        for cog_name, cog in sorted(self.bot.cogs.items(), key=lambda item: item[0].lower()):
            slash_commands = getattr(cog, "get_slash_commands", lambda: [])()
            if not slash_commands:
                continue

            command_lines = [
                self._format_command_line(command)
                for command in sorted(slash_commands, key=lambda command: command.qualified_name)
            ]
            for index, chunk in enumerate(self._chunk_lines(command_lines), start=1):
                field_name = cog_name if index == 1 else f"{cog_name} ({index})"
                embed.add_field(name=field_name, value=chunk, inline=False)
                fields_added += 1

        if fields_added == 0:
            embed.description = "Chưa có command nào được load từ các cog."

        embed.set_footer(text="Mỗi dòng là một slash command đã được load từ cog tương ứng.")
        return embed

    @commands.slash_command(description="Hiển thị danh sách câu lệnh")
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message(embed=self._build_help_embed())


def setup(bot: commands.Bot):
    bot.add_cog(HelpCommand(bot))