import disnake
from disnake.ext import commands
import asyncio
import random
import time

# Global variables for game management
active_games = {}
game_tasks = {}


class TowerOfKarma(commands.Cog):
    """Tower of Karma gambling game"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="forceend",
        description="Force end Tower of Karma game"
    )
    async def forceend(self, inter: disnake.ApplicationCommandInteraction):
        if inter.channel.id in active_games:
            if inter.channel.id in game_tasks:
                game_tasks[inter.channel.id].cancel()
                del game_tasks[inter.channel.id]
            del active_games[inter.channel.id]
            await inter.response.send_message("Game đã được force end!")
        else:
            await inter.response.send_message("Không có game nào đang chạy trong channel này!")

    @commands.slash_command(
        name="tok",
        description="Tower of Karma gambling game (2 người)"
    )
    async def tok(
        self, 
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description="Người chơi thứ 2"),
        bet: int = commands.Param(default=100, description="Số tiền cược", min_value=1)
    ):
        if inter.channel.id in active_games:
            await inter.response.send_message("Đã có một game Tower of Karma đang chạy trong channel này! Dùng `/forceend` để kết thúc game hiện tại.")
            return
        
        if member is None or member == inter.author or member.bot:
            await inter.response.send_message("Bạn cần chọn một người chơi hợp lệ (không phải bot, không phải chính bạn)!")
            return
        
        active_games[inter.channel.id] = True
        task = asyncio.create_task(self.tower_of_karma(inter, inter.author, member, bet))
        game_tasks[inter.channel.id] = task
        await task
        if inter.channel.id in active_games:
            del active_games[inter.channel.id]
        if inter.channel.id in game_tasks:
            del game_tasks[inter.channel.id]

    async def tower_of_karma(self, inter: disnake.ApplicationCommandInteraction, p1, p2, bet):
        await inter.channel.send(f"**[Tower of Karma]**\n {p2.mention}, bạn có đồng ý tham gia Tower of Karma với {p1.mention} với cược {bet:,} không? (gõ `yes` để chấp nhận hoặc `no` để từ chối trong 30 giây)")
        def check_confirm(m):
            return m.author.id == p2.id and m.channel == inter.channel and m.content.lower() in ['đồng ý', 'yes', 'y', 'từ chối', 'decline', 'no', 'n']
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check_confirm)
            if msg.content.lower() in ['từ chối', 'decline', 'no', 'n']:
                await inter.channel.send(f"**[Tower of Karma]**\n {p2.mention} đã từ chối tham gia. Hủy game.")
                if inter.channel.id in active_games:
                    del active_games[inter.channel.id]
                if inter.channel.id in game_tasks:
                    del game_tasks[inter.channel.id]
                return
        except asyncio.TimeoutError:
            await inter.channel.send(f"**[Tower of Karma]**\n {p2.mention} không xác nhận tham gia. Hủy game.")
            if inter.channel.id in active_games:
                del active_games[inter.channel.id]
            if inter.channel.id in game_tasks:
                del game_tasks[inter.channel.id]
            return
        players = {
            p1.id: {'user': p1, 'beans': 0, 'guesses_left': 2, 'name': p1.display_name},
            p2.id: {'user': p2, 'beans': 0, 'guesses_left': 2, 'name': p2.display_name}
        }
        # Phase 1: Chọn đậu
        beans_chosen = {}
        for pid, pdata in players.items():
            user = pdata['user']
            try:
                dm = await user.create_dm()
                await dm.send("Chọn số hạt đậu từ 1-10:")
                def check_dm(m):
                    return m.author == user and isinstance(m.channel, disnake.DMChannel) and m.content.isdigit()
                msg = await self.bot.wait_for('message', timeout=60.0, check=check_dm)
                beans = int(msg.content)
                if 1 <= beans <= 10:
                    beans_chosen[pid] = beans
                    pdata['beans'] = beans
                    await dm.send(f"Bạn đã chọn {beans} hạt đậu!")
                else:
                    beans_chosen[pid] = random.randint(1, 10)
                    pdata['beans'] = beans_chosen[pid]
                    await dm.send(f"Số không hợp lệ! Chọn ngẫu nhiên {beans_chosen[pid]} hạt đậu.")
            except Exception as e:
                beans_chosen[pid] = random.randint(1, 10)
                pdata['beans'] = beans_chosen[pid]
                print(f"[Tower of Karma] Không thể gửi DM cho {user.display_name}! Chọn ngẫu nhiên {beans_chosen[pid]} hạt đậu. Lỗi: {e}")
        total_beans = sum(beans_chosen.values())
        round_num = 1
        try:
            while True:
                # Exchange Phase
                turn_order = [p1.id, p2.id]
                random.shuffle(turn_order)
                for current_turn in turn_order:
                    timeout_timestamp = int(time.time() + 180)  # 3 phút
                    await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Exchange Phase**\n**{players[current_turn]['name']}** đoán tổng số đậu:\nThời gian còn lại: <t:{timeout_timestamp}:R>")
                    def check_guess(m):
                        return m.author.id == current_turn and m.channel == inter.channel and m.content.isdigit()
                    try:
                        msg = await self.bot.wait_for('message', timeout=180.0, check=check_guess)
                        guess = int(msg.content)
                        player_beans = players[current_turn]['beans']
                        if guess < player_beans or guess > (player_beans + 10):
                            winner = p2.id if current_turn == p1.id else p1.id
                            await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Exchange Phase**\n**{players[current_turn]['name']}** đoán không hợp lệ (**{guess}**)! Bạn thua!\n**{players[winner]['name']}** thắng và nhận {int(bet*1.2):,} (cược + 20% bonus)")
                            return
                        if guess == total_beans:
                            await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Exchange Phase**\n**{players[current_turn]['name']}** đoán đúng (**{guess}**)! Thắng: {int(bet*1.2):,} (cược + 20% bonus)")
                            return
                        else:
                            await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Exchange Phase**\n**{players[current_turn]['name']}** đoán sai (**{guess}**).")
                    except asyncio.TimeoutError:
                        await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Exchange Phase**\n**{players[current_turn]['name']}** hết thời gian!")
                # Guessing Phase
                timeout_timestamp = int(time.time() + 180)  # 3 phút
                await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\nGõ `guess <số>` để đoán hoặc `skip` để bỏ lượt. Mỗi người chỉ được đoán 2 lần trong cả game.\nThời gian còn lại: <t:{timeout_timestamp}:R>")
                skip_count = 0
                guessing_phase = True
                while guessing_phase:
                    def check_guess_phase(m):
                        return m.author.id in players and m.channel == inter.channel
                    try:
                        msg = await self.bot.wait_for('message', timeout=180.0, check=check_guess_phase)
                        if msg.content.lower() == 'skip':
                            skip_count += 1
                            await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\n**{msg.author.display_name}** đã skip.")
                            if skip_count >= 2:
                                guessing_phase = False
                                await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\nCả hai người chơi đã skip. Chuyển sang round tiếp theo.")
                                break
                            continue
                        if msg.content.lower().startswith('guess '):
                            try:
                                guess = int(msg.content.split()[1])
                                pid = msg.author.id
                                if players[pid]['guesses_left'] <= 0:
                                    await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\n**{players[pid]['name']}** đã hết lượt đoán!")
                                    continue
                                player_beans = players[pid]['beans']
                                if guess < player_beans or guess > (player_beans + 10):
                                    winner = p2.id if pid == p1.id else p1.id
                                    await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\n**{players[pid]['name']}** đoán không hợp lệ (**{guess}**)! Bạn thua!\n**{players[winner]['name']}** thắng và nhận {int(bet*1.2):,} (cược + 20% bonus)")
                                    return
                                players[pid]['guesses_left'] -= 1
                                if guess == total_beans:
                                    await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\n**{players[pid]['name']}** đoán đúng (**{guess}**) trong guessing phase! Thắng: {bet:,}")
                                    return
                                else:
                                    await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\n**{players[pid]['name']}** đoán sai (**{guess}**)! Còn {players[pid]['guesses_left']} lượt đoán.")
                            except (ValueError, IndexError):
                                await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\nFormat: `guess <số>`")
                    except asyncio.TimeoutError:
                        guessing_phase = False
                if all(players[pid]['guesses_left'] == 0 for pid in players):
                    await inter.channel.send(f"**[Tower of Karma] Round {round_num} - Guessing Phase**\nCả hai đều hết lượt đoán! Hòa!")
                    break
                round_num += 1
                if round_num > 10:
                    await inter.channel.send(f"**[Tower of Karma] Round {round_num}**\nQuá nhiều round! Hòa!")
                    break
        except asyncio.CancelledError:
            await inter.channel.send(f"**[Tower of Karma]** Game đã bị force end!")
        except Exception as e:
            await inter.channel.send(f"**[Tower of Karma]** Lỗi: {str(e)}")


def setup(bot: commands.Bot):
    bot.add_cog(TowerOfKarma(bot)) 