import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv

# khai báo client
client = commands.Bot(command_prefix='?', intents=disnake.Intents.all(), sync_commands_debug=True)
load_dotenv()

# Event khi bot sẵn sàng
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # thêm status cho bot
    await client.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name="Amane-kun's heart", large_image_url="https://i.imgur.com/TMRW6LD.jpeg"))
#load commands
def load_cogs():  
    for filename in os.listdir('./cogs'):  
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            
#load events           
def load_events():
    for filename in os.listdir('./events'):
        if filename.endswith('.py'):
            client.load_extension(f'events.{filename[:-3]}')
# Gọi 2 function load                
load_cogs()
load_events()

# Token chạy bot
client.run(os.getenv('DISCORD_TOKEN'))