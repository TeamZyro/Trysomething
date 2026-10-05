from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from DAXXMUSIC import app, user_collection, ddw
import random
import uuid
import re


# 🔹 Game settings
GRID_SIZE = 4
NUM_MINES = 3
ENTRY_FEE = 1000         # coins required to start
MAX_MINE_HITS = 2

# 🔹 Rewards Table (sirf coins)
REWARD_COINS = {
    1: 600,
    2: 1200,
    3: 1800,
    4: 2000,
    5: 2300,
    6: 2500,
    7: 2700,
    8: 3000,
    9: 3200,
    10: 3400,
    11: 3700,
    12: 4000,
    13: 5000
}


# ✅ Create game grid
def create_game():
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    mines = random.sample([(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], NUM_MINES)
    return grid, mines


# ✅ Generate keyboard
def generate_keyboard(grid, game_id, player_id, safe_opened, mine_hits):
    keyboard = []
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            if grid[i][j] == 1:
                row.append(InlineKeyboardButton("💎", callback_data=f"mine_{game_id}_{player_id}_{i}_{j}_opened"))
            elif grid[i][j] == 2:
                row.append(InlineKeyboardButton("🧨", callback_data=f"mine_{game_id}_{player_id}_{i}_{j}_opened"))
            else:
                row.append(InlineKeyboardButton("🔳", callback_data=f"mine_{game_id}_{player_id}_{i}_{j}"))
        keyboard.append(row)

    game_over = mine_hits >= MAX_MINE_HITS
    if safe_opened > 0 and not game_over:
        keyboard.append([InlineKeyboardButton("Claim Reward", callback_data=f"claim_{game_id}_{player_id}_{safe_opened}")])
    return InlineKeyboardMarkup(keyboard)


# ✅ Award only coins
async def award_rewards(user_id, safe_opened):
    user_data = await user_collection.find_one({'id': user_id})
    if not user_data:
        user_data = {'id': user_id, 'coins': 0}

    if safe_opened in REWARD_COINS:
        user_data['coins'] += REWARD_COINS[safe_opened]

    try:
        await user_collection.update_one(
            {'id': user_id},
            {'$set': {'coins': user_data.get('coins', 0)}},
            upsert=True
        )
    except Exception as e:
        print(f"Error updating user_collection: {e}")
        return user_data

    return user_data


# 🔹 Game state
game_state = {}
processing_locks = set()

async def track_mines_game_end(client: Client, chat_id: int, user_id: int, first_name: str):
    try:
        import datetime
        from html import escape
        db_guild_event = ddw['Guild_Event_DB']
        user_event_data = db_guild_event['users']
        today_str = str(datetime.datetime.now(datetime.timezone.utc).date())
        
        existing_event = await user_event_data.find_one({"_id": user_id})
        
        upd = {"$inc": {"weekly_mines_games": 1}}
        if existing_event and existing_event.get("last_mines_game_date") == today_str:
            upd["$inc"]["daily_mines_games"] = 1
        else:
            upd["$set"] = {"daily_mines_games": 1, "last_mines_game_date": today_str}
            
        await user_event_data.update_one({"_id": user_id}, upd, upsert=True)
        
        # Check task completion after the update
        updated_event = await user_event_data.find_one({"_id": user_id})
        if updated_event:
            daily_mines = updated_event.get("daily_mines_games", 0)
            weekly_mines = updated_event.get("weekly_mines_games", 0)
            
            completed_tasks = []
            if daily_mines == 1:
                completed_tasks.append("🏆 <b>Mines Explorer</b> (Daily)")
            if daily_mines == 2:
                completed_tasks.append("🎫 <b>Daily Mine Runner</b> (Waifu Pass)")
            if weekly_mines == 5:
                completed_tasks.append("👑 <b>Underground Master</b> (Weekly)")
                completed_tasks.append("💎 <b>Mine Expert</b> (Waifu Pass)")
                
            if completed_tasks:
                task_list_str = "\n".join(completed_tasks)
                me = await client.get_me()
                tc_image_url = "https://files.catbox.moe/8t2cui.png"
                caption = (
                    f'<a href="{tc_image_url}">&#8203;</a>'
                    "🎉 <b>ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
                    f"👤 <b>ʜᴜɴᴛᴇʀ:</b> <a href='tg://user?id={user_id}'>{escape(first_name)}</a>\n"
                    f"{task_list_str}\n\n"
                    "✨ <i>Claim rewards in Mini App!</i> 💎"
                )
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Open Mini App", url=f"https://t.me/{me.username}?startapp=true")]
                ])
                
                try:
                    await client.send_message(
                        chat_id=chat_id,
                        text=caption,
                        reply_markup=keyboard,
                        parse_mode=enums.ParseMode.HTML
                    )
                except Exception as send_err:
                    print(f"Error sending task completed messages in mines.py: {send_err}")
    except Exception as e:
        print(f"Error tracking mines task: {e}")


@app.on_message(filters.command("mines"), group=9202829)
async def start_mines(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = await user_collection.find_one({'id': user_id}, {'coins': 1})
    
    if not user_data or user_data.get('coins', 0) < ENTRY_FEE:
        await message.reply_text(f"❌ You need at least {ENTRY_FEE} coins to play Minesweeper!")
        return

    try:
        await user_collection.update_one({'id': user_id}, {'$inc': {'coins': -ENTRY_FEE}})
    except Exception as e:
        print(f"Error deducting balance: {e}")
        await message.reply_text("❌ Error starting game. Try again later.")
        return
    game_id = str(uuid.uuid4())
    player_id = str(user_id)
    grid, mines = create_game()
    
    game_state[user_id] = {
        'grid': grid, 'mines': mines, 'game_id': game_id, 'player_id': player_id,
        'safe_opened': 0, 'mine_hits': 0, 'message_id': None
    }
    
    caption_text = (
        "🎮 <b>Minesweeper!</b>\n\n"
        f"🧨 {NUM_MINES} mines | 💰 Fee: {ENTRY_FEE}\n"
        f"🛡️ {MAX_MINE_HITS} mine hits = Game Over!\n\n"
        "💎 <b>Rewards:</b>\n"
        "• 1–13 safe = Coins\n"
    )
    
    await message.reply_photo(
        photo="https://files.catbox.moe/bdbnxv.jpg",
        caption=caption_text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=generate_keyboard(grid, game_id, player_id, 0, 0)
    )


# Handle clicks on the mine grid
@app.on_callback_query(filters.regex(r'mine_(\S+)_(\d+)_(\d+)_(\d+)(?:_opened)?'))
async def handle_mine_click(client: Client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split('_')
    game_id, player_id, x, y = data[1], data[2], int(data[3]), int(data[4])
    
    if str(user_id) != player_id:
        await callback_query.answer("This is not your game!", show_alert=True)
        return
    
    if user_id not in game_state or game_state[user_id]['game_id'] != game_id:
        await callback_query.answer("Game expired or invalid!", show_alert=True)
        return
    
    state = game_state[user_id]
    grid, mines, safe_opened, mine_hits = state['grid'], state['mines'], state['safe_opened'], state['mine_hits']
    
    if grid[x][y] in [1, 2]:
        await callback_query.answer("This cell has already been revealed!", show_alert=True)
        return
    
    if (x, y) in mines:
        state['mine_hits'] += 1
        grid[x][y] = 2
        
        if state['mine_hits'] >= MAX_MINE_HITS:
            for mine_x, mine_y in mines:
                grid[mine_x][mine_y] = 2
            await callback_query.message.edit_text(
                "🧨 Game Over! You hit too many mines. No rewards earned. Try /mines to play again.",
                reply_markup=generate_keyboard(grid, game_id, player_id, safe_opened, state['mine_hits'])
            )
            del game_state[user_id]
            await track_mines_game_end(client, callback_query.message.chat.id, user_id, callback_query.from_user.first_name)
            return
        else:
            await callback_query.message.edit_text(
                f"🧨 You hit a mine but survived! Hits: {state['mine_hits']} / {MAX_MINE_HITS}. "
                f"Safe cells opened: {safe_opened}. Keep going or claim your reward!",
                reply_markup=generate_keyboard(grid, game_id, player_id, safe_opened, state['mine_hits'])
            )
            return
    else:
        grid[x][y] = 1
        state['safe_opened'] += 1
        await callback_query.message.edit_text(
            f"Opened a safe cell! Safe cells opened: {state['safe_opened']}. Keep going or claim your reward!",
            reply_markup=generate_keyboard(grid, game_id, player_id, state['safe_opened'], state['mine_hits'])
        )


# ✅ Handle claim with lock
@app.on_callback_query(filters.regex(r'claim_(\S+)_(\d+)_(\d+)'))
async def handle_claim(client: Client, callback_query):
    user_id = callback_query.from_user.id

    if user_id in processing_locks:
        await callback_query.answer("⏳ Processing your claim, please wait...", show_alert=True)
        return

    processing_locks.add(user_id)
    try:
        data = callback_query.data.split('_')
        game_id, player_id, safe_opened = data[1], data[2], int(data[3])

        if str(user_id) != player_id:
            await callback_query.answer("❌ This is not your game!", show_alert=True)
            return

        if user_id not in game_state or game_state[user_id]['game_id'] != game_id:
            await callback_query.answer("⚠️ Game expired or invalid!", show_alert=True)
            return

        del game_state[user_id]

        user_data = await award_rewards(user_id, safe_opened)

        if safe_opened in REWARD_COINS:
            coins = REWARD_COINS[safe_opened]
            await callback_query.message.edit_text(
                f"✅ You claimed <b>{coins} coins</b> for opening {safe_opened} safe cell(s)!",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await callback_query.message.edit_text("⚠️ No rewards available. Try again later!")
        
        await track_mines_game_end(client, callback_query.message.chat.id, user_id, callback_query.from_user.first_name)

    finally:
        if user_id in processing_locks:
            processing_locks.remove(user_id)
