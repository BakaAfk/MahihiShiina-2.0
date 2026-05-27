# MahihiShiina 2.0 Discord Bot

## Overview
MahihiShiina 2.0 is a Discord bot built with Python and `disnake`. It provides moderation tools, utility commands, voice features, and a few automated event handlers for server management.

## Main Modules
- `cogs/`: slash commands grouped by feature
- `events/`: automated listeners
- `config.py`: runtime settings used by the bot

## Features
- Moderation: `ban`, `kick`, `mute`, `unmute`, `clear`, `banlist`
- Utility: `help`, `ping`, `info`, `serverinfo`, `userinfo`, `load`, `convert`, `setnick`, `random`, `comm`
- Voice / Music: `voicejoin`, `voiceleave`, `tts`
- Tracking / Fun: AFK system, member count tracking, `tok_gamble`, `count`, `top`
- Events: message edit/delete logging, DM forwarding, Poketwo detection, hex decoding, member update logging, auto voice disconnect

## Configuration
The bot uses `config.py` to store runtime values such as channel IDs, role IDs, and member counter channels. Server configuration commands are available through the `config` cog.

## Project Structure
- `main.py`: bot entry point
- `config.py`: runtime settings
- `cogs/`: command modules
- `events/`: event modules
- `afks.json`: AFK data
- `queue.txt`, `chuitruong.txt`: lightweight data files

## Notes
- The bot currently serves a single server.
- Important IDs are centralized to reduce hardcoding.
- Some features still use simple text or JSON storage to keep the project lightweight.
