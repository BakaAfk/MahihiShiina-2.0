import disnake
from disnake.ext import commands
from disnake import FFmpegPCMAudio
import yt_dlp
import asyncio
import os
from functools import partial

QUEUE_FILE = "queue.txt"
LOOP_FILE = "loop.txt"
LOOP_QUEUE_FILE = "loop_queue.txt"  # New file for loop queue feature

class MusicPlayer:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_playing = False
        # Thêm biến để theo dõi voice client đang hoạt động
        self.active_voice_clients = {}

    def load_queue(self):
        if not os.path.exists(QUEUE_FILE):
            return []
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def save_queue(self, queue):
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(queue))

    def load_loop(self):
        return os.path.exists(LOOP_FILE)

    def toggle_loop(self):
        if self.load_loop():
            os.remove(LOOP_FILE)
        else:
            with open(LOOP_FILE, "w") as f:
                f.write("on")
    
    # Thêm hàm cho chức năng loop queue
    def load_loop_queue(self):
        return os.path.exists(LOOP_QUEUE_FILE)
    
    def toggle_loop_queue(self):
        if self.load_loop_queue():
            os.remove(LOOP_QUEUE_FILE)
        else:
            with open(LOOP_QUEUE_FILE, "w") as f:
                f.write("on")

    async def search_youtube(self, query, max_results=5):
        ydl_opts = {
            'quiet': True,
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch',
            'skip_download': True,  # Tăng tốc độ bằng cách không tải xuống
            'extract_flat': True,   # Chỉ lấy thông tin cơ bản, không lấy thông tin chi tiết
            'force_generic_extractor': False,
            'ignoreerrors': True,
            'geo_bypass': True,     # Bỏ qua giới hạn địa lý
            'socket_timeout': 10,   # Giảm thời gian chờ
            'nocheckcertificate': True,  # Bỏ qua kiểm tra chứng chỉ
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
                if 'entries' in info:
                    return [(entry['url'], entry['title']) for entry in info['entries'][:max_results]]
                return []
            except Exception as e:
                print(f"Error searching YouTube: {e}")
                return []

    async def get_stream_url(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'socket_timeout': 10,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if 'url' in info:
                    return info['url'], info['title']
                return None, None
            except Exception as e:
                print(f"Error getting stream URL: {e}")
                return None, None

    async def play_next(self, ctx):
        # Kiểm tra trước nếu bot không còn trong voice channel
        voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice or not voice.is_connected():
            self.is_playing = False
            print("Bot không còn trong voice channel, dừng phát nhạc")
            return
            
        queue = self.load_queue()

        if queue:
            # Kiểm tra lại một lần nữa xem bot còn trong voice channel không
            if not voice or not voice.is_connected():
                self.is_playing = False
                return
                
            # Logic cho song loop và queue loop
            if self.load_loop():
                # Nếu loop song, giữ bài hát hiện tại
                url = queue[0]
            else:
                # Lấy và xóa bài hát đầu tiên
                url = queue.pop(0)
                
                # Nếu queue loop, thêm bài hát vào cuối queue
                if self.load_loop_queue() and url:
                    queue.append(url)
                    
                # Lưu queue sau khi đã xử lý
                self.save_queue(queue)
                
            stream_url, title = await self.get_stream_url(url)
            if not stream_url:
                await ctx.send(f"Không thể phát nội dung này. Đang chuyển sang bài tiếp theo.")
                await self.play_next(ctx)
                return
                
            self.is_playing = True
            
            # Sử dụng FFMPEG options để tránh lỗi đứt đoạn
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
            
            try:
                # Kiểm tra lại voice client một lần nữa trước khi phát
                if not voice or not voice.is_connected():
                    self.is_playing = False
                    return
                    
                source = FFmpegPCMAudio(stream_url, **ffmpeg_options)
                
                # Sử dụng partial để truyền tham số vào callback
                def after_playing(error, ctx=ctx):
                    if error:
                        print(f"Player error: {error}")
                    # Kiểm tra xem bot có còn trong voice channel không
                    vc = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
                    if not vc or not vc.is_connected():
                        self.is_playing = False
                        return
                    asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
                
                voice.play(source, after=after_playing)
                await ctx.send(f"Đang phát: **{title}**")
            except Exception as e:
                print(f"Error playing audio: {e}")
                await ctx.send("Có lỗi khi phát nhạc. Đang chuyển sang bài tiếp theo.")
                # Kiểm tra lại trước khi đệ quy
                if voice and voice.is_connected():
                    await self.play_next(ctx)
        else:
            self.is_playing = False
            # Không ngắt kết nối ngay lập tức, chỉ thông báo hết danh sách phát
            await ctx.send("Hết danh sách phát.")

class MusicCog(commands.Cog):
    '''Trình chơi nhạc từ YT'''
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.music = MusicPlayer(bot)
        
        # Thêm sự kiện lắng nghe voice state update
        self.bot.add_listener(self.on_voice_state_update, "on_voice_state_update")

    # Thêm phương thức xử lý voice state update
    async def on_voice_state_update(self, member, before, after):
        # Nếu bot rời voice channel do bị kick hoặc lý do khác
        if member.id == self.bot.user.id and before.channel and not after.channel:
            print(f"Bot đã rời voice channel {before.channel.name} trong guild {before.channel.guild.name}")
            self.music.is_playing = False
            guild_id = before.channel.guild.id
            if guild_id in self.music.active_voice_clients:
                del self.music.active_voice_clients[guild_id]

    @commands.command()
    async def join(self, ctx):
        """Tham gia kênh thoại"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            # Kiểm tra xem bot đã ở trong voice channel chưa
            voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()
                # Lưu thông tin voice client
                self.music.active_voice_clients[ctx.guild.id] = voice
            await ctx.send(f"Đã tham gia kênh {channel.name}")
        else:
            await ctx.send("Bạn phải vào voice channel trước đã!")

    @commands.command()
    async def play(self, ctx, *, keyword=None):
        if not keyword:
            return await ctx.send("Vui lòng cung cấp URL hoặc từ khóa tìm kiếm.")
            
        if not ctx.author.voice:
            return await ctx.send("Bạn phải vào voice channel trước đã!")
            
        # Hiển thị thông báo đang xử lý
        processing_msg = await ctx.send("⏳ Đang xử lý yêu cầu...")
            
        # Kết nối với voice channel nếu chưa kết nối
        voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice or not voice.is_connected():
            channel = ctx.author.voice.channel
            try:
                voice = await channel.connect()
                # Lưu thông tin voice client
                self.music.active_voice_clients[ctx.guild.id] = voice
                await processing_msg.edit(content=f"Đã tham gia kênh {channel.name}. Đang xử lý âm nhạc...")
            except Exception as e:
                await processing_msg.edit(content=f"❌ Không thể tham gia kênh thoại: {str(e)}")
                return
        
        # Kiểm tra xem bot có thực sự ở trong voice channel không
        if not voice.is_connected():
            self.music.is_playing = False  # Reset trạng thái
            try:
                voice = await ctx.author.voice.channel.connect()
                self.music.active_voice_clients[ctx.guild.id] = voice
                await processing_msg.edit(content=f"Đã kết nối lại với kênh thoại. Đang xử lý âm nhạc...")
            except Exception as e:
                await processing_msg.edit(content=f"❌ Không thể kết nối lại: {str(e)}")
                return

        # Kiểm tra xem keyword có phải là URL YouTube không
        if keyword.startswith(('https://', 'http://', 'www.')):
            queue = self.music.load_queue()
            queue.append(keyword)
            self.music.save_queue(queue)
            
            # Cập nhật tin nhắn
            await processing_msg.edit(content="⏳ Đang lấy thông tin bài hát...")
            
            # Lấy tiêu đề từ URL
            _, title = await self.music.get_stream_url(keyword)
            title = title or "Không lấy được tiêu đề"
            
            embed = disnake.Embed(title="Đã thêm vào hàng đợi", description=f"{title}", color=disnake.Color.blue())
            await processing_msg.delete()
            await ctx.send(embed=embed)
            
            if not self.music.is_playing:
                await self.music.play_next(ctx)
            return

        # Nếu không phải URL, tìm kiếm trên YouTube
        await processing_msg.edit(content="🔍 Đang tìm kiếm trên YouTube...")
        results = await self.music.search_youtube(keyword)
        if not results:
            await processing_msg.delete() 
            return await ctx.send("❌ Không tìm thấy kết quả nào.")

        # Tạo embed cho kết quả tìm kiếm
        embed = disnake.Embed(
            title=f"🔍 Kết quả tìm kiếm cho: {keyword}", 
            description="Chọn bài hát bằng cách nhập số tương ứng:",
            color=disnake.Color.blue()
        )
        
        for i, (_, title) in enumerate(results):
            embed.add_field(name=f"{i+1}. {title}", value="\u200b", inline=False)
            
        embed.set_footer(text="⏱️ Thời gian chọn: 20 giây")
        
        await processing_msg.delete()
        select_msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

        try:
            processing_msg = await ctx.send("⏳ Đang chờ lựa chọn của bạn...")
            msg = await self.bot.wait_for("message", check=check, timeout=20)
            choice = int(msg.content)
            
            if not (1 <= choice <= len(results)):
                await processing_msg.delete()
                return await ctx.send("❌ Lựa chọn không hợp lệ.")
                
            await processing_msg.edit(content="✅ Đã nhận lựa chọn, đang xử lý...")
        except asyncio.TimeoutError:
            await processing_msg.delete()
            return await ctx.send("⏱️ Hết thời gian chọn bài.")

        url, title = results[choice - 1]
        queue = self.music.load_queue()
        queue.append(url)
        self.music.save_queue(queue)

        embed = disnake.Embed(
            title="🎵 Đã thêm vào hàng đợi", 
            description=f"**{title}**", 
            color=disnake.Color.green()
        )
        
        # Kiểm tra vị trí trong hàng đợi
        position = len(queue)
        if position > 1:
            embed.set_footer(text=f"Vị trí trong hàng đợi: #{position}")
        else:
            embed.set_footer(text="Đang chuẩn bị phát")
        
        await processing_msg.delete()
        await ctx.send(embed=embed)

        if not self.music.is_playing:
            await self.music.play_next(ctx)

    @commands.command()
    async def pause(self, ctx):
        """Tạm dừng phát nhạc"""
        voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        # Kiểm tra kỹ hơn về trạng thái voice client
        if not voice or not voice.is_connected():
            self.music.is_playing = False  # Đảm bảo cập nhật trạng thái
            await ctx.send("Bot không ở trong kênh thoại.")
            return
            
        if voice.is_playing():
            voice.pause()
            await ctx.send("Đã tạm dừng.")
        else:
            # Nếu bot nghĩ nó đang phát nhưng không phải vậy, cập nhật trạng thái
            if self.music.is_playing:
                self.music.is_playing = False
            await ctx.send("Không có bài hát nào đang phát.")

    @commands.command()
    async def resume(self, ctx):
        """Tiếp tục phát nhạc"""
        voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        # Kiểm tra kỹ hơn về trạng thái voice client
        if not voice or not voice.is_connected():
            self.music.is_playing = False  # Đảm bảo cập nhật trạng thái
            await ctx.send("Bot không ở trong kênh thoại.")
            return
            
        if voice.is_paused():
            voice.resume()
            self.music.is_playing = True  # Cập nhật trạng thái
            await ctx.send("Đã tiếp tục.")
        else:
            if not voice.is_playing():
                # Nếu bot không đang phát, kiểm tra hàng đợi
                queue = self.music.load_queue()
                if queue:
                    await ctx.send("Bắt đầu phát hàng đợi...")
                    await self.music.play_next(ctx)
                else:
                    await ctx.send("Không có bài hát nào trong hàng đợi.")
            else:
                await ctx.send("Bot đang phát nhạc, không cần tiếp tục.")

    @commands.command()
    async def skip(self, ctx):
        """Bỏ qua bài hát hiện tại"""
        voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if not voice or not voice.is_connected():
            self.music.is_playing = False  # Cập nhật trạng thái
            await ctx.send("Bot không ở trong kênh thoại.")
            return
            
        if voice.is_playing() or voice.is_paused():
            voice.stop()  # Điều này sẽ kích hoạt callback after_playing và chơi bài tiếp theo
            await ctx.send("Đã bỏ qua bài hát.")
        else:
            # Thử phát bài kế tiếp nếu có
            queue = self.music.load_queue()
            if queue and not self.music.is_playing:
                await ctx.send("Đang phát bài tiếp theo...")
                await self.music.play_next(ctx)
            else:
                await ctx.send("Không có bài hát nào đang phát hoặc trong hàng đợi.")

    @commands.command()
    async def stop(self, ctx):
        """Dừng phát nhạc và xóa hàng đợi"""
        voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        # Kiểm tra xem bot có trong voice channel không
        if voice and voice.is_connected():
            # Xóa hàng đợi
            self.music.save_queue([])
            # Cập nhật trạng thái
            self.music.is_playing = False
            # Dừng phát nếu đang phát
            if voice.is_playing() or voice.is_paused():
                voice.stop()
            # Xóa khỏi danh sách voice clients đang hoạt động
            if ctx.guild.id in self.music.active_voice_clients:
                del self.music.active_voice_clients[ctx.guild.id]
            await ctx.send("Đã dừng phát nhạc và xóa hàng đợi.")
        else:
            # Reset trạng thái
            self.music.is_playing = False
            self.music.save_queue([])
            # Xóa khỏi danh sách voice clients đang hoạt động nếu có
            if ctx.guild.id in self.music.active_voice_clients:
                del self.music.active_voice_clients[ctx.guild.id]
            await ctx.send("Bot không ở trong kênh thoại. Đã xóa hàng đợi.")

    @commands.command()
    async def leave(self, ctx):
        """Rời khỏi kênh thoại"""
        voice = disnake.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            # Dừng phát nếu đang phát
            if voice.is_playing() or voice.is_paused():
                voice.stop()
            # Cập nhật trạng thái
            self.music.is_playing = False
            # Xóa khỏi danh sách voice clients đang hoạt động
            if ctx.guild.id in self.music.active_voice_clients:
                del self.music.active_voice_clients[ctx.guild.id]
            # Ngắt kết nối
            await voice.disconnect()
            await ctx.send("Đã rời khỏi kênh thoại.")
        else:
            # Reset trạng thái
            self.music.is_playing = False
            # Xóa khỏi danh sách voice clients đang hoạt động nếu có
            if ctx.guild.id in self.music.active_voice_clients:
                del self.music.active_voice_clients[ctx.guild.id]
            await ctx.send("Bot không ở trong kênh thoại.")

    @commands.command()
    async def loop(self, ctx):
        """Bật/tắt chế độ lặp bài hát hiện tại"""
        # Nếu đang bật loop queue, tắt nó trước
        if self.music.load_loop_queue():
            self.music.toggle_loop_queue()
            await ctx.send("Đã tắt chế độ lặp hàng đợi để bật chế độ lặp bài hát.")
            
        self.music.toggle_loop()
        state = "bật" if self.music.load_loop() else "tắt"
        await ctx.send(f"Chế độ lặp bài hát đã được {state}.")

    @commands.command(name="loopqueue")
    async def loop_queue(self, ctx):
        """Bật/tắt chế độ lặp toàn bộ hàng đợi"""
        # Nếu đang bật loop bài hát, tắt nó trước
        if self.music.load_loop():
            self.music.toggle_loop()
            await ctx.send("Đã tắt chế độ lặp bài hát để bật chế độ lặp hàng đợi.")
            
        self.music.toggle_loop_queue()
        state = "bật" if self.music.load_loop_queue() else "tắt"
        await ctx.send(f"Chế độ lặp hàng đợi đã được {state}.")

    @commands.command(name="queue")
    async def _queue(self, ctx):
        queue = self.music.load_queue()
        if not queue:
            return await ctx.send("Hàng đợi trống.")

        await ctx.send("Đang lấy thông tin hàng đợi...")
        titles = []
        
        # Cấu hình tối ưu cho YDL
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
            'socket_timeout': 5,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
        }
        
        # Sử dụng một phiên YDL duy nhất cho tất cả URL để tăng tốc
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, url in enumerate(queue):
                # Chỉ hiển thị 10 bài đầu tiên để tránh timeout
                if i >= 10:
                    titles.append("...")
                    break
                    
                try:
                    info = ydl.extract_info(url, download=False, process=False)  # process=False tăng tốc
                    # Nếu không lấy được tiêu đề từ quá trình trên
                    if not info or not info.get('title'):
                        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
                        titles.append(f"Video #{i+1} (ID: {video_id})")
                    else:
                        titles.append(info.get('title', url))
                except:
                    # Trích xuất ID video từ URL để hiển thị
                    try:
                        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
                        titles.append(f"Video #{i+1} (ID: {video_id})")
                    except:
                        titles.append(f"Bài hát #{i+1}")

        desc = "\n".join([f"{i+1}. {title}" for i, title in enumerate(titles)])
        if len(queue) > 10:
            desc += f"\n\nVà {len(queue) - 10} bài hát khác..."
            
        # Thêm thông tin về trạng thái loop
        loop_info = ""
        if self.music.load_loop():
            loop_info = "🔂 Đang lặp bài hát hiện tại"
        elif self.music.load_loop_queue():
            loop_info = "🔁 Đang lặp hàng đợi"
            
        if loop_info:
            desc = f"{loop_info}\n\n{desc}"
            
        embed = disnake.Embed(title="Hàng đợi hiện tại", description=desc, color=disnake.Color.green())
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, index: int):
        """Xóa một bài hát khỏi hàng đợi"""
        queue = self.music.load_queue()
        if not queue:
            return await ctx.send("Hàng đợi trống.")
            
        if not 1 <= index <= len(queue):
            return await ctx.send(f"Chỉ số không hợp lệ. Hãy nhập số từ 1 đến {len(queue)}.")
            
        # Lấy tiêu đề trước khi xóa - sử dụng phương pháp nhanh hơn
        try:
            # Sử dụng cấu hình tối ưu
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'socket_timeout': 5,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'process': False  # Không xử lý thông tin chi tiết
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(queue[index-1], download=False, process=False)
                if info and 'title' in info:
                    title = info.get('title')
                else:
                    # Trích xuất ID video từ URL để hiển thị
                    url = queue[index-1]
                    video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
                    title = f"Video (ID: {video_id})"
        except:
            title = "Bài hát #" + str(index)
            
        # Xóa bài hát khỏi hàng đợi
        queue.pop(index-1)
        self.music.save_queue(queue)
        
        await ctx.send(f"Đã xóa **{title}** khỏi hàng đợi.")

def setup(bot: commands.Bot):
    bot.add_cog(MusicCog(bot))