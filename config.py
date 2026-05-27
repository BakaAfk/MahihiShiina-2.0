from copy import deepcopy
import json
from pathlib import Path


CONFIG_FILE = Path(__file__).resolve().parent / "server_config.json"

DEFAULT_SETTINGS = {
	"LOG_CHANNEL_ID": 872721744861995008,
	"DM_DUMP_CHANNEL_ID": 874521453268193301,
	"HEX_CHANNEL_ID": 881881931736842250,
	"POKETWO_CHANNEL_ID": 872718633539883028,
	"MUTED_ROLE_ID": 882254188183191633,
	"POKETWO_PING_ROLE_ID": 1508191540529467402,
	"GUILD_ID": 872692134845759508,
	"MEMBER_COUNTER_CHANNEL_IDS": {
		"online": 1367502522482294794,
		"offline": 1367502599384731668,
		"idle": 1367502406060871771,
		"dnd": 1367503242958737478,
	},
	"TRUONG_WORDS": [
		"truong loz", "truong lon", "em yeu truong em", "tron luong",
		"trường loz", "trường lon", "em yêu trường em", "trốn lường",
		"truờng lồn", "truờng lớn", "chồn lường",
		"dm truong", "đm truong", "đm trường", "dm trường",
		"l truong", "l trường", "truong l", "trường l",
	],
	"TRUONG_COUNTER_FILE": str(Path(__file__).resolve().parent / "cogs" / "Some fun tracking cmd" / "chuitruong.txt"),
}

RUNTIME_SETTINGS = deepcopy(DEFAULT_SETTINGS)

# Fixed IDs that are intentionally not part of the server config command.
OWNER_ID = 1067718540221743134
VENT_CHANNEL_ID = 1012236568066531338
IGNORE_LOG_USER_ID = 1067718540221743134


def _sync_globals() -> None:
	for key, value in RUNTIME_SETTINGS.items():
		globals()[key] = value


def load_settings() -> dict:
	global RUNTIME_SETTINGS
	stored_settings = {}
	if CONFIG_FILE.exists():
		try:
			with CONFIG_FILE.open("r", encoding="utf-8") as file:
				stored_settings = json.load(file)
		except Exception:
			stored_settings = {}

	merged_settings = deepcopy(DEFAULT_SETTINGS)
	for key, value in stored_settings.items():
		if key in merged_settings:
			merged_settings[key] = value

	RUNTIME_SETTINGS = merged_settings
	_sync_globals()
	return deepcopy(RUNTIME_SETTINGS)


def save_settings() -> None:
	with CONFIG_FILE.open("w", encoding="utf-8") as file:
		json.dump(RUNTIME_SETTINGS, file, indent=4, ensure_ascii=False)


def get_setting(key: str, default=None):
	return RUNTIME_SETTINGS.get(key, default)


def set_setting(key: str, value):
	RUNTIME_SETTINGS[key] = value
	_sync_globals()
	save_settings()


def reset_setting(key: str | None = None):
	global RUNTIME_SETTINGS
	if key is None:
		RUNTIME_SETTINGS = deepcopy(DEFAULT_SETTINGS)
	else:
		RUNTIME_SETTINGS[key] = deepcopy(DEFAULT_SETTINGS[key])
	_sync_globals()
	save_settings()


load_settings()