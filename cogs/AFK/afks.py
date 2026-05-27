import disnake
from disnake.ext import commands
import json
import os
from datetime import datetime

class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.afk_file = "afks.json"
        self.afk_users = self.load_afk_users()
    
    def load_afk_users(self):
        """Load AFK users from JSON file"""
        if os.path.exists(self.afk_file):
            try:
                with open(self.afk_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_afk_users(self):
        """Save AFK users to JSON file"""
        try:
            with open(self.afk_file, 'w') as f:
                json.dump(self.afk_users, f, indent=4)
        except Exception as e:
            print(f"Error saving AFK users: {e}")
    
    @commands.slash_command(name="afk", description="Đặt trạng thái AFK")
    async def afk(self, inter: disnake.ApplicationCommandInteraction, reason: str = "AFK"):
        """Set AFK status for the user"""
        user_id = str(inter.author.id)
        
        # Store AFK data
        self.afk_users[user_id] = {
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "guild_id": str(inter.guild.id),
            "channel_id": str(inter.channel.id)
        }
        
        # Save to JSON file
        self.save_afk_users()
        
        # Create embed
        embed = disnake.Embed(
            title="Đã Đặt Trạng Thái AFK",
            description=f"Bạn hiện đang AFK: **{reason}**",
            color=disnake.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Đặt bởi {inter.author.display_name}")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle AFK removal and mentions"""
        if message.author.bot:
            return
        
        user_id = str(message.author.id)
        
        # Check if user is AFK and remove AFK status
        if user_id in self.afk_users:
            afk_data = self.afk_users[user_id]
            del self.afk_users[user_id]
            self.save_afk_users()
            
            # Calculate AFK duration
            afk_time = datetime.fromisoformat(afk_data["timestamp"])
            duration = datetime.now() - afk_time
            
            # Create welcome back embed
            await message.channel.send(f"{message.author.mention} đã trở lại!")
        
        # Check for mentions of AFK users
        for mention in message.mentions:
            mentioned_user_id = str(mention.id)
            if mentioned_user_id in self.afk_users:
                afk_data = self.afk_users[mentioned_user_id]
                afk_time = datetime.fromisoformat(afk_data["timestamp"])
                duration = datetime.now() - afk_time
                
                # Create mention notification embed
                await message.channel.send(f"{mention.mention} đang AFK: **{afk_data['reason']}**\nHọ đã AFK trong **{self.format_duration(duration)}**")   
    
    def format_duration(self, duration):
        """Format duration in a readable way"""
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} giây"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} phút"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours} giờ"
        else:
            days = total_seconds // 86400
            return f"{days} ngày"
    
    @commands.slash_command(name="afklist", description="Hiển thị tất cả người dùng đang AFK")
    async def afklist(self, inter: disnake.ApplicationCommandInteraction):
        """Show list of all AFK users"""
        if not self.afk_users:
            embed = disnake.Embed(
                title="Người Dùng AFK",
                description="Không có người dùng nào đang AFK",
                color=disnake.Color.blue()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = disnake.Embed(
            title="Người Dùng Đang AFK",
            color=disnake.Color.blue(),
            timestamp=datetime.now()
        )
        
        for user_id, afk_data in self.afk_users.items():
            try:
                user = await self.bot.fetch_user(int(user_id))
                afk_time = datetime.fromisoformat(afk_data["timestamp"])
                duration = datetime.now() - afk_time
                
                embed.add_field(
                    name=user.display_name,
                    value=f"Lý do: {afk_data['reason']}\nThời gian: {self.format_duration(duration)}",
                    inline=False
                )
            except:
                continue
        
        await inter.response.send_message(embed=embed, ephemeral=True)
    
    @commands.slash_command(name="removeafk", description="Gỡ bỏ trạng thái AFK cho bản thân hoặc người dùng khác")
    async def removeafk(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
        """Remove AFK status for the user"""
        target_user = user or inter.author
        user_id = str(target_user.id)
        
        if user_id not in self.afk_users:
            await inter.response.send_message(f"{target_user.mention} hiện không đang AFK")
        
        # Remove AFK status
        del self.afk_users[user_id]
        self.save_afk_users()
        await inter.response.send_message(f"Trạng thái AFK đã được gỡ bỏ cho {target_user.mention}")

def setup(bot: commands.Bot):
    bot.add_cog(AFK(bot))