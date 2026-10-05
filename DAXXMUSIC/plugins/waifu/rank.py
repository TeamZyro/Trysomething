import html
import random
from pyrogram import Client, filters, enums  
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from DAXXMUSIC import app as Client
from DAXXMUSIC import user_collection, top_global_groups_collection

PHOTO_URL = ["https://files.catbox.moe/aek9xx.jpg"]  

async def get_top_leaderboard():
    cursor = user_collection.aggregate([
        {
            "$project": {
                "id": 1,
                "first_name": 1,
                "character_count": {
                    "$cond": {
                        "if": {"$isArray": "$characters"},
                        "then": {"$size": "$characters"},
                        "else": 0
                    }
                }
            }
        },
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    return await cursor.to_list(length=10)

@Client.on_message(filters.command("rank"))
async def rank(client, message):
    leaderboard_data = await get_top_leaderboard()

    leaderboard_message = "<b>TOP 10 USERS WITH MOST CHARACTERS</b>\n\n"
    for i, user in enumerate(leaderboard_data, start=1):
        user_id = user.get('id', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))[:15] + '...'
        character_count = user.get('character_count', 0)
        leaderboard_message += f'{i}. <a href="tg://user?id={user_id}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'

    buttons = [
        [
            InlineKeyboardButton("✅ Top", callback_data="top"),
            InlineKeyboardButton("Top Group", callback_data="top_group"),
        ],
        [
            InlineKeyboardButton("MTOP", callback_data="mtop"),
            InlineKeyboardButton("crimson", callback_data="crimson"),
        ],
    ]

    await message.reply_photo(
        photo=random.choice(PHOTO_URL),
        caption=leaderboard_message,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def update_caption(callback_query, caption, active_button):
    buttons = [
        [
            InlineKeyboardButton("✅ Top" if active_button == "top" else "Top", callback_data="top"),
            InlineKeyboardButton("✅ Top Group" if active_button == "top_group" else "Top Group", callback_data="top_group"),
        ],
        [
            InlineKeyboardButton("✅ MTOP" if active_button == "mtop" else "MTOP", callback_data="mtop"),
            InlineKeyboardButton("✅ crimson" if active_button == "crimson" else "crimson", callback_data="crimson"),
        ],
    ]

    await callback_query.edit_message_caption(
        caption=caption,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^top$"))
async def top_callback(client, callback_query):
    leaderboard_data = await get_top_leaderboard()

    caption = "<b>TOP 10 USERS WITH MOST CHARACTERS</b>\n\n"
    for i, user in enumerate(leaderboard_data, start=1):
        user_id = user.get('id', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))[:15] + '...'
        character_count = user.get('character_count', 0)
        caption += f'{i}. <a href="tg://user?id={user_id}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'

    await update_caption(callback_query, caption, "top")

@Client.on_callback_query(filters.regex("^top_group$"))
async def top_group_callback(client, callback_query):
    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)
    
    caption = "<b>TOP 10 GROUPS WHO GUESSED MOST CHARACTERS</b>\n\n"
    for i, group in enumerate(leaderboard_data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))[:15] + '...'
        count = group['count']
        caption += f'{i}. <b>{group_name}</b> ➾ <b>{count}</b>\n'

    await update_caption(callback_query, caption, "top_group")

@Client.on_callback_query(filters.regex("^mtop$"))
async def mtop_callback(client, callback_query):
    top_users = await user_collection.find().sort("coins", -1).limit(10).to_list(length=10)

    caption = "<b>MTOP LEADERBOARD</b>\n\n🏆 Tᴏᴘ 10 Uꜱᴇʀs ʙʏ Cᴏɪɴs:\n\n"
    for rank, user in enumerate(top_users, start=1):
        user_id = user.get("id", "Unknown")
        first_name = user.get("first_name", "Unknown")
        coins = user.get("coins", 0)
        caption += f"{rank}. <a href='tg://user?id={user_id}'><b>{first_name}</b></a>: 💸 {coins} Coins\n"

    await update_caption(callback_query, caption, "mtop")

@Client.on_callback_query(filters.regex("^crimson$"))
async def tokens_callback(client, callback_query):
    top_users = await user_collection.find().sort("crimson", -1).limit(10).to_list(length=10)

    caption = "<b>Tokens LEADERBOARD</b>\n\n🏆 Tᴏᴘ 10 Uꜱᴇʀs ʙʏ crimson:\n\n"
    for rank, user in enumerate(top_users, start=1):
        user_id = user.get("id", "Unknown")
        first_name = user.get("first_name", "Unknown")
        crimson = user.get("crimson", 0)
        caption += f"{rank}. <a href='tg://user?id={user_id}'><b>{first_name}</b></a>: 🪙 {crimson} crimson\n"

    await update_caption(callback_query, caption, "crimson")
