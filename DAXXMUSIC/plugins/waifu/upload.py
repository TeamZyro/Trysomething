import os
import requests
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from DAXXMUSIC import CHARA_CHANNEL_ID, SUPPORT_CHAT, OWNER_ID, collection, user_collection, db, SUDO, rarity_map, app as ZYRO, require_power

# Define the wrong format message and rarity map
WRONG_FORMAT_TEXT = """Wrong ❌ format...  eg. /upload reply to photo muzan-kibutsuji Demon-slayer 3

format:- /upload reply character-name anime-name rarity-number

use rarity number accordingly rarity Map
rarity_map = {
    1: "💫 Rare",
    2: "🌿 Medium",
    3: "🦄 Legendary",
    4: "💮 Special Edition",
    5: "🔮 Limited Edition",
    6: "🎉 Festival",
    7: "🍂 Seasonal",
    8: "🎐 Celestial", 
    9: "❄️ Winter",
    10: "💝 Valentine",
    11: "🔞 Erotic",
    12: "🪽 AMV",
    13: "🐉 Ethereal",
    14: "🕌 Fast edition",
    15: "🎬 Hollywood",
    16: "🎃 Halloween",
    17: "🌈 Chroma edition",
    18: "⚙🛠️ Customized",
    19: "☔ Rain edition",
    20: "📽️ Webseries",
    21: "🧚‍♂️ komi",
    22: "🍭 Winter event",
    23: "✨ Kinetic Art",
    24: "👑 Royal Pass Edition"
}

"""

# --- ORIGINAL FIND FUNCTIONS ---
async def find():
    cursor = collection.find().sort('id', 1)
    ids = []

    async for doc in cursor:
        if 'id' in doc:
            ids.append(int(doc['id']))

    ids.sort()
    for i in range(1, len(ids) + 2):
        if i not in ids:
            return str(i).zfill(2)

    return str(len(ids) + 1).zfill(2)


async def find_available_id():
    cursor = collection.find().sort('id', 1)
    ids = []

    async for doc in cursor:
        if 'id' in doc:
            ids.append(int(doc['id']))

    ids.sort()
    for i in range(1, len(ids) + 2):
        if i not in ids:
            return str(i).zfill(2)

    return str(len(ids) + 1).zfill(2)


IMGBB_API_KEY = "7ff491f6f7076787ff4e5dab51b502a9"
upload_lock = asyncio.Lock()
user_upload_server = {}  # store each user's selected server

# --- SERVER SELECTION ---
# --- SERVER SELECTION (SUDO only) ---
@ZYRO.on_message(filters.command("server"))
@require_power("add_character")  # SUDO style permission
async def select_server(client, message):
    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("ImgBB", callback_data="set_server_imgbb"),
            InlineKeyboardButton("Catbox", callback_data="set_server_catbox")
        ]]
    )
    await message.reply("Select upload server:", reply_markup=buttons)
    
@ZYRO.on_callback_query()
async def server_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if callback_query.data == "set_server_imgbb":
        user_upload_server[user_id] = "imgbb"
        await callback_query.answer("Upload server set to ImgBB ✅", show_alert=True)
    elif callback_query.data == "set_server_catbox":
        user_upload_server[user_id] = "catbox"
        await callback_query.answer("Upload server set to Catbox ✅", show_alert=True)

# --- UPLOAD HELPERS ---
def upload_to_imgbb(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise Exception(f"Invalid file path: {file_path}")
    url = "https://api.imgbb.com/1/upload"
    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            data={"key": IMGBB_API_KEY},
            files={"image": f}
        )
    if response.status_code == 200:
        data = response.json()
        return data["data"]["url"]
    else:
        raise Exception(f"HTTP Error: {response.status_code} | {response.text}")

def upload_to_catbox(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise Exception(f"Invalid file path: {file_path}")
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as f:
        response = requests.post(url, data={"reqtype": "fileupload"}, files={"fileToUpload": f})
    if response.status_code == 200 and response.text.startswith("https"):
        return response.text
    else:
        raise Exception(f"Error uploading to Catbox: {response.text}")

# --- UPLOAD COMMAND ---
@ZYRO.on_message(filters.command(["gupload", "u", "upload"]))
@require_power("add_character")
async def ul(client, message):
    global upload_lock

    if upload_lock.locked():
        await message.reply_text("Another upload is in progress. Please wait until it is completed.")
        return

    async with upload_lock:
        reply = message.reply_to_message
        if reply and (reply.photo or reply.document or reply.video):
            args = message.text.split()
            if len(args) != 4:
                await client.send_message(chat_id=message.chat.id, text=WRONG_FORMAT_TEXT)
                return

            character_name = args[1].replace('-', ' ').title()
            anime = args[2].replace('-', ' ').title()
            rarity = int(args[3])

            if rarity not in rarity_map:
                await message.reply_text("Invalid rarity value. Please use a value between 1 and 18.")
                return

            rarity_text = rarity_map[rarity]
            available_id = await find_available_id()

            character = {
                'name': character_name,
                'anime': anime,
                'rarity': rarity_text,
                'id': available_id
            }

            processing_message = await message.reply("<ᴘʀᴏᴄᴇꜱꜱɪɴɢ>....")
            path = await reply.download()
            try:
                server = user_upload_server.get(message.from_user.id, "imgbb")
                if server == "imgbb":
                    file_url = upload_to_imgbb(path)
                else:
                    file_url = upload_to_catbox(path)

                if reply.photo or reply.document:
                    character['img_url'] = file_url
                    await client.send_photo(
                        chat_id=CHARA_CHANNEL_ID,
                        photo=file_url,
                        caption=(
                            f"Character Name: {character_name}\n"
                            f"Anime Name: {anime}\n"
                            f"Rarity: {rarity_text}\n"
                            f"ID: {available_id}\n"
                            f"Added by [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
                        ),
                    )
                elif reply.video:
                    character['vid_url'] = file_url
                    thumbnail_path = await client.download_media(reply.video.thumbs[0].file_id)
                    if server == "imgbb":
                        thumbnail_url = upload_to_imgbb(thumbnail_path)
                    else:
                        thumbnail_url = upload_to_catbox(thumbnail_path)
                    character['thum_url'] = thumbnail_url
                    os.remove(thumbnail_path)
                    await client.send_video(
                        chat_id=CHARA_CHANNEL_ID,
                        video=file_url,
                        caption=(
                            f"Character Name: {character_name}\n"
                            f"Anime Name: {anime}\n"
                            f"Rarity: {rarity_text}\n"
                            f"ID: {available_id}\n"
                            f"Added by [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n\n"
                        ),
                    )

                await collection.insert_one(character)
                await message.reply_text(
                    f"➲ ᴀᴅᴅᴇᴅ ʙʏ» [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n"
                    f"➥ Character ID: {available_id}\n"
                    f"➥ Rarity: {rarity_text}"
                )
            except Exception as e:
                await message.reply_text(f"Character Upload Unsuccessful. Error: {str(e)}")
            finally:
                os.remove(path)
        else:
            await message.reply_text("Please reply to a photo, document, or video.")
