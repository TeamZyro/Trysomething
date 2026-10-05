from DAXXMUSIC import *
import os
import importlib.util
import random
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from DAXXMUSIC.unit.zyro_help import HELP_DATA  

SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/thezyroempire")
UPDATE_CHAT = os.getenv("UPDATE_CHAT", "https://t.me/thezyroempire")

# 🔹 Function to Calculate Uptime
START_TIME = time.time()

def get_uptime():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

# 🔹 Function to Generate Private Start Message & Buttons
async def generate_start_message(client, message):
    bot_user = await client.get_me()
    bot_name = bot_user.first_name
    ping = round(time.time() - message.date.timestamp(), 2)
    uptime = get_uptime()
    
    caption = f"""[‌](https://files.catbox.moe/fd9zfk.mp4)╔══════════════════╗
  ✦ **𝖶𝖠𝖨𝖥𝖴 𝖢𝖮𝖫𝖫𝖤𝖢𝖳𝖮𝖱** ✦
╚══════════════════╝

🍃 **ɢʀᴇᴇᴛɪɴɢs, ɪ'ᴍ {bot_name} 🫧, ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ!**

**➻ 𝖶𝗁𝖺𝗍 𝖨 𝖣𝗈:** ɪ sᴘᴀᴡɴ ᴡᴀɪғᴜs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ ғᴏʀ ᴜsᴇʀs ᴛᴏ ɢʀᴀʙ.
**➻ 𝖳𝗈 𝖴𝗌𝖾 𝖬𝖾:** ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛᴀᴘ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ғᴏʀ ᴅᴇᴛᴀɪʟs.

📊 **𝖲𝗒𝗌𝗍𝖾𝗆 𝖲𝗍𝖺𝗍𝗎𝗌:**
 ➺ 𝖯𝗂𝗇𝗀: `{ping} ms`
 ➺ 𝖴𝗉𝗍𝗂ᴍ𝖾: `{uptime}`"""

    buttons = [
        [InlineKeyboardButton("Aᴅᴅ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ", url=f"https://t.me/{bot_user.username}?startgroup=true")],
        [InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT), 
         InlineKeyboardButton("Cʜᴀɴɴᴇʟ", url=UPDATE_CHAT)],
        [InlineKeyboardButton("Hᴇʟᴘ", callback_data="open_help")],
        [InlineKeyboardButton("Gɪᴛʜᴜʙ", url="https://github.com/MrZyro/ZyroWaifu")]
    ]
    
    return caption, buttons

# 🔹 Function to Generate Group Start Message & Buttons
async def generate_group_start_message(client):
    bot_user = await client.get_me()
    caption = f"🍃 ɪ'ᴍ {bot_user.first_name} 🫧\nɪ sᴘᴀᴡɴ ᴡᴀɪғᴜs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ғᴏʀ ᴜsᴇʀs ᴛᴏ ɢʀᴀʙ.\nᴜsᴇ /help ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ."
    buttons = [
        [
            InlineKeyboardButton("Aᴅᴅ Mᴇ", url=f"https://t.me/{bot_user.username}?startgroup=true"),
            InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)
        ]
    ]
    return caption, buttons

# 🔹 Private Start Command Handler
@app.on_message(filters.command("start") & filters.private)
async def start_private_command(client, message):
    # Only handle start if it contains a referral link
    if len(message.command) <= 1 or not message.command[1].startswith("ref_"):
        return  # Do nothing and let the other repository handle the normal start command welcome

    user_id = message.from_user.id
    existing_user = await user_collection.find_one({"id": user_id})
    
    db_guild_event = ddw['Guild_Event_DB']
    user_event_data = db_guild_event['users']
    existing_event_user = await user_event_data.find_one({"_id": user_id})
    
    is_new = (existing_user is None) and (existing_event_user is None)
    
    referrer_id = None
    ref_user = None
    ref_event_user = None
    
    try:
        potential_ref_id = int(message.command[1].split("_")[1])
        if potential_ref_id != user_id:
            # Validate referrer exists
            ref_user = await user_collection.find_one({"id": potential_ref_id})
            ref_event_user = await user_event_data.find_one({"_id": potential_ref_id})
            if ref_user or ref_event_user:
                referrer_id = potential_ref_id
    except (ValueError, IndexError):
        pass

    if not referrer_id:
        return  # Invalid referrer, do nothing

    if is_new:
        import datetime
        # Save user data only if they don't exist in the collection
        user_data = {
            "id": user_id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "start_time": time.time(),
            "coins": 1000 # Welcome Coins
        }
        await user_collection.insert_one(user_data)
        
        # Save/Initialize user in user_event_data
        new_event_user = {
            "_id": user_id,
            "name": message.from_user.first_name or "Unknown Hunter",
            "photo_url": "",
            "xp": 0,
            "level": 1,
            "diamonds": 10, # Welcome Diamonds
            "rank_points": 0,
            "guild_id": None,
            "claims": [],
            "referred_by": referrer_id,
            "referrals": [],
            "joined_at": datetime.datetime.now()
        }
        await user_event_data.insert_one(new_event_user)
        
        await user_collection.update_one({"id": referrer_id}, {"$inc": {"coins": 2000}}, upsert=True)
        await user_event_data.update_one(
            {"_id": referrer_id}, 
            {
                "$inc": {"diamonds": 20, "crates.common": 1}, 
                "$push": {"referrals": user_id}
            }, 
            upsert=True
        )
        
        # Send private message notification to referrer
        try:
            new_user_name = message.from_user.first_name or "A new user"
            ref_notify_text = (
                f"🎉 <b>ɴᴇᴡ ʀᴇғᴇʀʀᴀʟ!</b>\n\n"
                f"<b>{new_user_name}</b> has joined the hunt using your referral link!\n\n"
                f"🎁 <b>ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ:</b>\n"
                f"• 💸 2,000 Coins\n"
                f"• 💎 20 Diamonds\n"
                f"• 📦 1 Common Crate"
            )
            await client.send_message(chat_id=referrer_id, text=ref_notify_text)
        except Exception as notify_err:
            print(f"Failed to notify referrer {referrer_id}: {notify_err}")

        # Send confirmation to the joining user
        try:
            welcome_reward_text = (
                f"🎁 <b>ᴡᴇʟᴄᴏᴍᴇ ʀᴇᴡᴀʀᴅ!</b>\n\n"
                f"You joined via referral and received:\n"
                f"• 💸 1,000 Coins\n"
                f"• 💎 10 Diamonds"
            )
            await message.reply_text(welcome_reward_text)
        except Exception as reply_err:
            print(f"Failed to reply to joining user: {reply_err}")

# @app.on_message(filters.command("start") & filters.group)
async def start_group_command(client, message):
    pass

def find_help_modules():
    buttons = []
    
    for module_name, module_data in HELP_DATA.items():
        button_name = module_data.get("HELP_NAME", "Unknown")
        buttons.append(InlineKeyboardButton(button_name, callback_data=f"marinhelp_{module_name}"))

    return [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

@app.on_callback_query(filters.regex("^open_help$"))
async def show_help_menu(client, query: CallbackQuery):
    time.sleep(1)
    buttons = find_help_modules()
    buttons.append([InlineKeyboardButton("⬅ Back", callback_data="help_home")])

    await query.message.edit(
        text="""[‌](https://files.catbox.moe/fd9zfk.mp4)*ᴄʜᴏᴏsᴇ ᴛʜᴇ ᴄᴀᴛᴇɢᴏʀʏ ғᴏʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴɴᴀ ɢᴇᴛ ʜᴇʟᴩ.

ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ : /""",
        reply_markup=InlineKeyboardMarkup(buttons),  
        parse_mode=ParseMode.MARKDOWN
    )

# 🔹 Individual Module Help Handler
@app.on_callback_query(filters.regex(r"^marinhelp_(.+)"))
async def show_help(client, query: CallbackQuery):
    time.sleep(1)
    module_name = query.data.split("_", 1)[1]
    
    try:
        module_data = HELP_DATA.get(module_name, {})
        help_text = module_data.get("HELP", "Is module ka koi help nahi hai.")
        buttons = [[InlineKeyboardButton("⬅ Back", callback_data="open_help")]]
        
        await query.message.edit(
            text=f"[‌](https://files.catbox.moe/fd9zfk.mp4)**{module_name} Help:**\n\n{help_text}",
            reply_markup=InlineKeyboardMarkup(buttons),  
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await query.answer("Help load karne me error aayi!")


@app.on_callback_query(filters.regex("^marinback_to_home$"))
async def back_to_home(client, query: CallbackQuery):
    time.sleep(1)
    caption, buttons = await generate_start_message(client, query.message)
    await query.message.edit(
        text=f"[‌](https://files.catbox.moe/fd9zfk.mp4){caption}",
        reply_markup=InlineKeyboardMarkup(buttons), 
        parse_mode=ParseMode.MARKDOWN
    )
