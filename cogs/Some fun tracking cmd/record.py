import json
from pathlib import Path

import disnake
from disnake.ext import commands

import config


class Records(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.server_record_path = Path(config.SERVER_RECORD_FILE)
		self.user_record_path = Path(config.USER_RECORD_FILE)

	def _pretty_category(self, category: str) -> str:
		return {
			'fastest_grab': 'Fastest grab',
			'slowest_grab': 'Slowest grab',
			'burn_highest': 'Burn highest',
		}.get(category, category)

	def _load_json(self, path: Path, default):
		if not path.exists():
			return default

		try:
			with path.open('r', encoding='utf-8') as f:
				data = json.load(f)
		except Exception:
			return default

		return data if isinstance(data, type(default)) else default

	def _format_server_records(self, records: list[dict]) -> str:
		if not records:
			return "Không có dữ liệu record server."

		lines = []
		for record in records:
			if not isinstance(record, dict):
				continue

			category = record.get('category', 'unknown')
			userid = record.get('userid', 'unknown')
			value = record.get('value', 'unknown')
			cardcode = record.get('cardcode') or 'unknown'
			message_link = record.get('message_link', 'unknown')
			lines.append(
				f"- `{self._pretty_category(category)}` | User: `{userid}` | Time: `{value}` | Card: `{cardcode}` | Link: {message_link}"
			)

		return "\n".join(lines) if lines else "Không có dữ liệu record server hợp lệ."

	def _format_user_records(self, records: list[dict]) -> str:
		if not records:
			return "Không có dữ liệu record user."

		lines = []
		for user_entry in records:
			if not isinstance(user_entry, dict):
				continue

			userid = user_entry.get('userid', 'unknown')
			user_records = user_entry.get('record', [])
			if not isinstance(user_records, list):
				continue

			lines.append(f"**User `{userid}`**")
			for record in user_records:
				if not isinstance(record, dict):
					continue

				category = record.get('category', 'unknown')
				value = record.get('value', 'unknown')
				cardcode = record.get('cardcode') or 'unknown'
				message_link = record.get('message_link', 'unknown')
				lines.append(f"  - `{self._pretty_category(category)}` | Time: `{value}` | Card: `{cardcode}` | Link: {message_link}")

		return "\n".join(lines) if lines else "Không có dữ liệu record user hợp lệ."

	def _get_user_record_entry(self, records: list[dict], userid: int) -> dict | None:
		return next((item for item in records if isinstance(item, dict) and item.get('userid') == userid), None)

	@commands.slash_command(description="Xem record Karuta đã lưu")
	async def record(
		self,
		inter: disnake.ApplicationCommandInteraction,
		scope: str = commands.Param(choices=["server", "user"], description="Chọn loại record muốn xem"),
		target: disnake.User = commands.Param(default=None, description="Người dùng muốn xem record (tùy chọn)"),
	):
		try:
			if scope == "server":
				records = self._load_json(self.server_record_path, [])
				if not isinstance(records, list):
					records = []
				content = self._format_server_records(records)
				title = "Karuta Server Record"
			else:
				records = self._load_json(self.user_record_path, [])
				if not isinstance(records, list):
					records = []
				selected_user = target or inter.author
				user_entry = self._get_user_record_entry(records, selected_user.id)
				if user_entry is None:
					content = f"Không có record cho user `{selected_user}`."
				else:
					content = self._format_user_records([user_entry])
				title = f"Karuta User Record - {selected_user}"

			embed = disnake.Embed(title=title, description=content, color=0x00FF00)
			await inter.response.send_message(embed=embed)

		except Exception as e:
			await inter.response.send_message(f"Đã xảy ra lỗi khi đọc record: {e}")


def setup(bot: commands.Bot):
	bot.add_cog(Records(bot))
