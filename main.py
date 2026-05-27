import disnake
from disnake.ext import commands
import importlib.util
import os
from pathlib import Path
from dotenv import load_dotenv

# Client setup
client = commands.Bot(command_prefix='?', intents=disnake.Intents.all(), sync_commands_debug=True)
load_dotenv()

# Load cogs and events
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # Set bot presence
    await client.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name="Amane-kun's heart", large_image_url="https://i.imgur.com/TMRW6LD.jpeg"))

def load_modules(folder_name: str):
    base_path = Path(__file__).resolve().parent / folder_name
    for file_path in base_path.rglob("*.py"):
        if "__pycache__" in file_path.parts:
            continue

        module_name = f"{folder_name}.{file_path.stem}.{abs(hash(file_path))}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            print(f"Không thể load module: {file_path}")
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "setup"):
            module.setup(client)


load_modules("cogs")
load_modules("events")

# Run the bot
client.run(os.getenv('DISCORD_TOKEN'))