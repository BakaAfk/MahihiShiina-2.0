from pathlib import Path
import json
import re

import disnake
from disnake.ext import commands

import config


class KarutaFilter(commands.Cog):
    """Filter messages from Karuta for specific words and update record for server and users"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter_path = Path(config.TRUONG_COUNTER_FILE)
        self.karuta_id = 646937666251915264
        self.server_record_path = Path(config.SERVER_RECORD_FILE)
        self.user_record_path = Path(config.USER_RECORD_FILE)

    def _load_json(self, path: Path, default):
        if not path.exists():
            return default

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return default

        return data if isinstance(data, type(default)) else default

    def _save_json(self, path: Path, data) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _parse_time(self, time_text: str) -> float | None:
        match = re.search(r"\d+(?:\.\d+)?", time_text)
        if match is None:
            return None

        try:
            return float(match.group())
        except ValueError:
            return None

    def _update_record(self, records: list[dict], category: str, userid: int, cardcode: str | None, record_value: float, prefer: str, message_link: str) -> bool:
        record = next((item for item in records if isinstance(item, dict) and item.get("category") == category), None)
        if record is None:
            record_data = {
                "category": category,
                "userid": userid,
                "value": record_value,
                "message_link": message_link,
            }
            if cardcode:
                record_data["cardcode"] = cardcode
            records.append(record_data)
            return True

        current_value = record.get("value")
        if not isinstance(current_value, (int, float)):
            record_data = {
                "userid": userid,
                "value": record_value,
                "message_link": message_link,
            }
            if cardcode:
                record_data["cardcode"] = cardcode
            record.update(record_data)
            return True

        is_better = record_value < current_value if prefer == "min" else record_value > current_value
        if not is_better:
            return False

        record_data = {
            "userid": userid,
            "value": record_value,
            "message_link": message_link,
        }
        if cardcode:
            record_data["cardcode"] = cardcode
        record.update(record_data)
        return True

    def _get_or_create_user_record(self, user_records: list[dict], userid: int) -> dict:
        record = next((item for item in user_records if isinstance(item, dict) and item.get("userid") == userid), None)
        if record is None:
            record = {"userid": userid, "record": []}
            user_records.append(record)
        elif not isinstance(record.get("record"), list):
            record["record"] = []
        return record

    def _update_user_record(self, user_record: dict, category: str, cardcode: str | None, record_value: float, prefer: str, message_link: str) -> bool:
        records = user_record["record"]
        record = next((item for item in records if isinstance(item, dict) and item.get("category") == category), None)
        if record is None:
            record_data = {
                "category": category,
                "value": record_value,
                "message_link": message_link,
            }
            if cardcode:
                record_data["cardcode"] = cardcode
            records.append(record_data)
            return True

        current_value = record.get("value")
        if not isinstance(current_value, (int, float)):
            record_data = {
                "value": record_value,
                "message_link": message_link,
            }
            if cardcode:
                record_data["cardcode"] = cardcode
            record.update(record_data)
            return True

        is_better = record_value < current_value if prefer == "min" else record_value > current_value
        if not is_better:
            return False

        record_data = {
            "value": record_value,
            "message_link": message_link,
        }
        if cardcode:
            record_data["cardcode"] = cardcode
        record.update(record_data)
        return True

    def _extract_first_number(self, text: str) -> float | None:
        match = re.search(r"\d+(?:\.\d+)?", text)
        if match is None:
            return None

        try:
            return float(match.group())
        except ValueError:
            return None

    def _extract_cardcode(self, embed_texts: list[str]) -> str:
        for text in embed_texts:
            match = re.search(r"\b[a-z0-9]{6,8}\b", text, re.IGNORECASE)
            if match is not None:
                return match.group(0)
        return "unknown"


    async def kci_record(self, message: disnake.Message, embed_texts: list[str]):
        try:
            cardcode = embed_texts[1].split(" ")[0][3:-3]
            grabber_text = embed_texts[7]
            time_text = embed_texts[11]
        except IndexError:
            return

        grabber_match = re.search(r"\d+", grabber_text)
        record_value = self._parse_time(time_text)
        if grabber_match is None or record_value is None:
            return

        grabber = int(grabber_match.group())
        message_link = message.jump_url
        server_records = self._load_json(self.server_record_path, [])
        user_records = self._load_json(self.user_record_path, [])
        if not isinstance(server_records, list):
            server_records = []
        if not isinstance(user_records, list):
            user_records = []

        server_updated = False
        server_updated |= self._update_record(server_records, "fastest_grab", grabber, cardcode, record_value, "min", message_link)
        server_updated |= self._update_record(server_records, "slowest_grab", grabber, cardcode, record_value, "max", message_link)
        if server_updated:
            self._save_json(self.server_record_path, server_records)

        user_record = self._get_or_create_user_record(user_records, grabber)
        user_updated = False
        user_updated |= self._update_user_record(user_record, "fastest_grab", cardcode, record_value, "min", message_link)
        user_updated |= self._update_user_record(user_record, "slowest_grab", cardcode, record_value, "max", message_link)
        if user_updated:
            self._save_json(self.user_record_path, user_records)

        if server_updated or user_updated:
            await message.channel.send(
                "Đã ghi nhận:\n"
                f"Card code: {cardcode}\n"
                f"Grabber: {grabber}\n"
                f"Time: {record_value}\n"
            )
            if server_updated:
                await message.channel.send("Cập nhật kỷ lục server thành công!")
            if user_updated:
                await message.channel.send("Cập nhật kỷ lục người dùng thành công!")

    async def burn_record(self, message: disnake.Message, embed_texts: list[str]):
        try:
            burn_value = int(embed_texts[3].split(" ")[1][2:-2])
            burn_message = message.reference.resolved if message.reference else None

            if burn_value is None or not isinstance(burn_message, disnake.Message):
                return

            userid = burn_message.author.id
        except (AttributeError, IndexError):
            return

        message_link = message.jump_url
        server_records = self._load_json(self.server_record_path, [])
        user_records = self._load_json(self.user_record_path, [])
        if not isinstance(server_records, list):
            server_records = []
        if not isinstance(user_records, list):
            user_records = []

        server_updated = self._update_record(server_records, "burn_highest", userid, None, burn_value, "max", message_link)
        if server_updated:
            self._save_json(self.server_record_path, server_records)

        user_record = self._get_or_create_user_record(user_records, userid)
        user_updated = self._update_user_record(user_record, "burn_highest", None, burn_value, "max", message_link)
        if user_updated:
            self._save_json(self.user_record_path, user_records)

        if server_updated or user_updated:
            await message.channel.send(
                "Đã ghi nhận burn record:\n"
                f"User: {userid}\n"
                f"Burn value: {burn_value}"
            )
            if server_updated:
                await message.channel.send("Cập nhật kỷ lục burn server thành công!")
            if user_updated:
                await message.channel.send("Cập nhật kỷ lục burn người dùng thành công!")

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.id != self.karuta_id:
            return
        if message.embeds is None or len(message.embeds) == 0:
            return
        embed_texts = []
        # add title + content to embed_texts
        for embed in message.embeds:
            if embed.title:
                embed_texts.append(embed.title)
            if embed.description:
                descriptions = embed.description.split("\n")
                embed_texts.extend(descriptions)

        if embed_texts[0] == "Burn Card":
            await self.burn_record(message, embed_texts)
            
        if embed_texts[0] == "Card Details":
            await self.kci_record(message, embed_texts)
            
        


def setup(bot: commands.Bot):
    bot.add_cog(KarutaFilter(bot))