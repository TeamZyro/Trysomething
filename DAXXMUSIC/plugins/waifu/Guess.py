from DAXXMUSIC import *
from html import escape
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import enums
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import random
import requests
import config 
import pytz
from bson import ObjectId


emojis = ["❤️", "👀", "💕", "🔥", "🎀", "🍓", "💘", "⚡", "🍀", "⚡️", "🏆", "🕊️", "🎉"]

async def react_to_message(chat_id, message_id):
    random_emoji = random.choice(emojis)
    url = f'https://api.telegram.org/bot{config.BOT_TOKEN}/setMessageReaction'
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reaction': [{
            "type": "emoji",
            "emoji": random_emoji
        }]
    }
    response = requests.post(url, json=params)
    if response.status_code == 200:
        print("Reaction set successfully!")
    else:
        print(f"Failed to set reaction. Status code: {response.status_code}")

@app.on_message(filters.command(["guess", "protecc", "collect", "grab", "hunt"]))
async def guess(client: Client, message: Message):
    if not message.from_user:
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    today = datetime.utcnow().date()

    if await check_cooldown(user_id):
        remaining_time = await get_remaining_cooldown(user_id)
        await message.reply_text(
            f"⚠️ You are still in cooldown. Please wait {remaining_time} seconds before using any commands."
        )
        return

    if 'name' not in last_characters.get(chat_id, {}):
        await message.reply_text("❌ character Guess not available")
        return
    
    if chat_id not in last_characters:
        await message.reply_text("❌ character Guess not available")
        return

    if chat_id in first_correct_guesses:
        await message.reply_text("❌ character Guess not available")
        return

    if last_characters[chat_id].get('ranaway', False):
        await message.reply_text("❌ THE CHARACTER HAS ALREADY RUN AWAY!")
        return 

    guess = ' '.join(message.command[1:]).lower() if len(message.command) > 1 else ''
    
    if "()" in guess or "&" in guess.lower():
        await message.reply_text("Nahh You Can't use This Types of words in your guess..❌️")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()
    
    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        for task in asyncio.all_tasks():
            if task.get_name() == f"expire_session_{chat_id}":
                task.cancel()
                break

        timestamp = last_characters[chat_id].get('timestamp')
        if timestamp:
            time_taken = time.time() - timestamp
            time_taken_str = f"{int(time_taken)} seconds"
        else:
            time_taken_str = "Unknown time"

        if user_id not in user_guess_progress or user_guess_progress[user_id]["date"] != today:
            user_guess_progress[user_id] = {"date": today, "count": 0}

        user_guess_progress[user_id]["count"] += 1
        
        # --- Build the character object to add to harem ---
        char_data = last_characters[chat_id]
        character_to_add = {
            "id": char_data.get("id"),
            "name": char_data.get("name"),
            "anime": char_data.get("anime"),
            "rarity": char_data.get("rarity"),
            "img_url": char_data.get("img_url"),
            "vid_url": char_data.get("vid_url"),
        }

        user = await user_collection.find_one({'id': user_id})
        if user:
            current_balance = user.get('coins', 0)
            new_balance = current_balance + 40
            # Update coins AND push character to harem
            await user_collection.update_one(
                {'id': user_id},
                {
                    '$set': {'coins': new_balance},
                    '$push': {'characters': character_to_add}
                }
            )
        else:
            # New user — create doc with coins and first character
            await user_collection.insert_one({
                'id': user_id,
                'coins': 40,
                'characters': [character_to_add]
            })
            new_balance = 40

        # --- GUILD & PROGRESSION UPDATE ---
        guild_msg = ""
        in_guild = False
        me = None
        try:
             # Re-using connection string
            guild_mongo_url = "mongodb+srv://nibbanmisal3302:Gokukhan3303@cluster0.0u22b.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            guild_client = AsyncIOMotorClient(guild_mongo_url)
            guild_db = guild_client["Guild_Event_DB"]
            guild_user_col = guild_db["users"]
            guild_col = guild_db["guilds"]

            me = await client.get_me()

            # Award Values
            earned_xp = 4
            earned_pts = 4
            earned_gp = 4

            # Update User
            g_user = await guild_user_col.find_one({"_id": user_id})
            
            # Save old XP and guess count to check milestones after update
            today_str = str(datetime.utcnow().date())
            old_xp = g_user.get("xp", 0) if g_user else 0
            old_guesses = g_user.get("guess_count", 0) if (g_user and g_user.get("last_guess_date") == today_str) else 0
            
            has_rainy = last_characters[chat_id].get('rainy_token', False)
            
            updates = {
                "$inc": {
                    "xp": earned_xp, 
                    "rank_points": earned_pts
                },
                "$set": {
                    "last_guess_date": today_str
                }
            }
            
            if has_rainy:
                updates["$inc"]["rainy_tokens"] = 1
            
            if g_user and g_user.get("last_guess_date") == today_str:
                updates["$inc"]["guess_count"] = 1
            else:
                updates["$set"]["guess_count"] = 1
            
            if g_user and g_user.get("guild_id"):
                in_guild = True
                updates["$inc"]["gp_contribution_weekly"] = earned_gp
                updates["$inc"]["gp_total"] = earned_gp 
                
                # Robustly handle Guild ID
                target_gid = g_user["guild_id"]
                
                # Ensure we have an ObjectId
                valid_oid = False
                try:
                    if isinstance(target_gid, str):
                        target_gid = ObjectId(target_gid)
                    valid_oid = True
                except:
                    print(f"Invalid Guild ObjectId: {target_gid}")

                if valid_oid:
                    # Update Guild Collection
                    result = await guild_col.update_one(
                        {"_id": target_gid},
                        {"$inc": {"gp_weekly": earned_gp, "gp_total": earned_gp, "weekly_guesses": 1}}
                    )
                    if result.modified_count == 0:
                        print(f"Warning: Guild GP update failed for ID {target_gid}. Doc not found?")

            await guild_user_col.update_one({"_id": user_id}, updates, upsert=True)
            
            # Post-update check for task completion and level up
            new_xp = old_xp + earned_xp
            new_guesses = old_guesses + 1
            
            import math
            def get_level(xp_val):
                if xp_val < 0: return 1
                lvl = int((-1.0 + math.sqrt(9.0 + xp_val / 62.5)) / 2.0)
                return max(1, lvl)
                
            old_level = get_level(old_xp)
            new_level = get_level(new_xp)
            
            tc_image_url = "https://files.catbox.moe/8t2cui.png"
            lu_image_url = "https://files.catbox.moe/s83wab.png"
            
            # 1. Level Up Notification
            if new_level > old_level:
                caption = (
                    f'<a href="{lu_image_url}">&#8203;</a>'
                    f"⚡ <b>ʟᴇᴠᴇʟ ᴜᴘ!</b> ⚡\n\n"
                    f"👤 <b>ʜᴜɴᴛᴇʀ:</b> <a href='tg://user?id={user_id}'>{escape(message.from_user.first_name)}</a>\n"
                    f"🌟 <b>ɴᴇᴡ ʟᴇᴠᴇʟ:</b> <code>Level {new_level}</code>"
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
                except Exception as lvl_err:
                    print(f"Error sending level up messages: {lvl_err}")

            # 2. Task Completion Notification
            if new_guesses == 10:
                caption = (
                    f'<a href="{tc_image_url}">&#8203;</a>'
                    "🎉 <b>ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
                    f"👤 <b>ʜᴜɴᴛᴇʀ:</b> <a href='tg://user?id={user_id}'>{escape(message.from_user.first_name)}</a>\n"
                    f"🎯 <b>ᴛᴀsᴋ:</b> 🏆 <b>Hunter Initiate</b> (10 Guesses)\n\n"
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
                except Exception as task_err:
                    print(f"Error sending task completed messages in Guess.py: {task_err}")

            guild_msg = f"\n\n<b>Progress:</b> +{earned_xp} XP | +{earned_pts} Rank Pts"
            if has_rainy:
                guild_msg += " | +1 Rainy Token ☔"
            if in_guild:
                guild_msg += f" | +{earned_gp} GP 🛡️"
            else:
                guild_msg += "\n\n⚠️ <i>You are not in a Guild! Create or Join a Guild in the Mini App to start earning Guild Points (GP) and unlock exclusive bonuses!</i> 🛡️"

        except Exception as e:
            print(f"Guild logic error: {e}")
        # ----------------------------------

        keyboard = [
            [InlineKeyboardButton("See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]
        ]
        if not in_guild and me:
            keyboard.append([InlineKeyboardButton("Join/Create Guild 🛡️", url=f"https://t.me/{me.username}?startapp=true")])

        await message.reply_text(
            f'🌟 <b><a href="tg://user?id={user_id}">{escape(message.from_user.first_name)}</a></b>, you\'ve captured a new character! 🎊\n\n'
            f'📛 𝗡𝗔𝗠Ｅ: <b>{last_characters[chat_id]["name"]}</b> \n'
            f'🌈 𝗔𝗡𝗜𝗠Ｅ: <b>{last_characters[chat_id]["anime"]}</b> \n'
            f'✨ 👑 <b>𝗥𝗔𝗥𝗜𝗧𝗬:</b> <b>{last_characters[chat_id]["rarity"]}</b>\n\n'
            f'⏱️ 𝗧𝗜𝗠Ｅ 𝗧𝗔𝗞𝗘𝗡: <b>{time_taken_str}</b>{guild_msg}\n'
            f'This Character has been added to Your Harem. Use /harem to see your harem.',
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        message_id = last_characters[chat_id].get('message_id')
        if message_id:
            keyboard = [
                [InlineKeyboardButton("See Media Again", url=f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")]
            ]
            await message.reply_text(
                '❌ Not quite right, brave guesser! Try again and unveil the mystery character! 🕵️‍♂️',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await message.reply_text('❌ Not quite right, brave guesser! Try again! 🕵️‍♂️')
