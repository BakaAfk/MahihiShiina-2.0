from pathlib import Path

import disnake
from disnake.ext import commands

import config


class MessageFilter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter_path = Path(config.TRUONG_COUNTER_FILE)

    def load_counter(self) -> dict[str, int]:
        if not self.counter_path.exists():
            return {}

        count_dict: dict[str, int] = {}
        with self.counter_path.open("r", encoding="utf-8") as file:
            for line in file:
                parts = line.split()
                if len(parts) != 2:
                    continue
                user_id, count_value = parts
                try:
                    count_dict[user_id] = int(count_value)
                except ValueError:
                    continue
        return count_dict

    def save_counter(self, count_dict: dict[str, int]) -> None:
        with self.counter_path.open("w", encoding="utf-8") as file:
            for user_id, count_value in count_dict.items():
                file.write(f"{user_id} {count_value}\n")

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or not message.content:
            return

        content_lower = message.content.lower()
        if not any(word in content_lower for word in config.TRUONG_WORDS):
            return

        count_dict = self.load_counter()
        user_id = str(message.author.id)
        count_dict[user_id] = count_dict.get(user_id, 0) + 1
        self.save_counter(count_dict)


def setup(bot: commands.Bot):
    bot.add_cog(MessageFilter(bot))