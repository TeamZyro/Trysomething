from DAXXMUSIC import *
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import time

normal_message_counts = {}

@app.on_message(filters.text & ~filters.command([]), group=929292929)
async def message_counter(client: Client, message: Message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    user_id = message.from_user.id
    current_time = time.time()

    existing_group = await group_user_totals_collection.find_one({"group_id": chat_id})
    if not existing_group:
        await group_user_totals_collection.update_one(
            {"group_id": chat_id}, 
            {"$set": {"group_id": chat_id, "ctime": 80}},
            upsert=True
        )
        ctime = 80
    else:
        ctime = existing_group.get("ctime", 80)

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        if user_id in user_cooldowns:
            cooldown_end = user_cooldowns[user_id]
            if current_time < cooldown_end:
                return
            else:
                del user_cooldowns[user_id]

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id not in warned_users or current_time - warned_users[user_id] >= 600:
                    cooldown_end = current_time + 600
                    user_cooldowns[user_id] = cooldown_end
                    warned_users[user_id] = current_time
                    await message.reply_text(
                        f"⚠️ Don't Spam {message.from_user.first_name}...\n"
                        "Your Messages Will be ignored for 10 Minutes..."
                    )
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        if chat_id in normal_message_counts:
            normal_message_counts[chat_id] += 1
        else:
            normal_message_counts[chat_id] = 1

        if normal_message_counts[chat_id] % ctime == 0:
            await send_image(client, message)
            normal_message_counts[chat_id] = 0


# /just command handler
@app.on_message(filters.command("just") & filters.private, group=929292929)
async def just_command(client: Client, message: Message):
    await send_image(client, message)

