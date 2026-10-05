import random
import asyncio
from DAXXMUSIC import *
from pyrogram import Client, filters
from pyrogram.types import Message
import time

games = {}
cooldowns = {}

anime_characters = [
    "Naruto", "Sasuke", "Goku", "Luffy", "Zoro", "Ichigo", "Tanjiro", "Nezuko", "Levi", "Eren",
    "Mikasa", "Gojo", "Itadori", "Kakashi", "Hinata", "Killua", "Gon", "Shinobu", "Asuka", "Edward",
    "Bakugo", "Deku", "Todoroki", "All Might", "Asta", "Yami", "Noelle", "Julius", "Escanor", "Meliodas",
    "Elizabeth", "Diane", "King", "Ban", "Merlin", "Hawk", "Saitama", "Genos", "Tatsumaki", "Boruto",
    "Sarada", "Mitsuki", "Madara", "Obito", "Minato", "Shikamaru", "Ino", "Kiba", "Rock Lee", "Gaara",
    "Temari", "Kankuro", "Orochimaru", "Jiraiya", "Tsunade", "Erza", "Natsu", "Lucy", "Gray", "Juvia",
    "Gajeel", "Makarov", "Laxus", "Mirajane", "Elfman", "Lisanna", "Haruhi", "Tamaki", "Kyoya", "Hikaru",
    "Kaoru", "Mori", "Honey", "Zero", "Kaname", "Yuki", "Sebastian", "Ciel", "Alois", "Claude", "Shoto",
    "Rukia", "Renji", "Uryu", "Byakuya", "Kenpachi", "Toshiro", "Mayuri", "Aizen", "Grimmjow", "Ulquiorra",
    "Vegeta", "Gohan", "Trunks", "Raditz", "Frieza", "Cell", "Broly", "Beerus", "Whis", "Jiren",
    "Yusuke", "Hiei", "Kurama", "Kuwabara", "Raizen", "Toguro", "Keiko", "Botan", "Mukuro", "Shizuru",
    "Shinichi", "Kaito", "Heiji", "Ran", "Ai Haibara", "Kogoro", "Eisuke", "Subaru", "Amuro", "Vermouth",
    "Armin", "Hange", "Connie", "Sasha", "Zeke", "Reiner", "Gabi", "Pieck", "Falco", "Jean",
    "Megumin", "Aqua", "Kazuma", "Darkness", "Emilia", "Subaru", "Rem", "Ram", "Beatrice", "Roswaal",
    "Ryuk", "Misa", "Near", "Mello", "Teru", "Soichiro", "Watari", "Naomi", "Lelouch", "Suzaku",
    "C.C.", "Kallen", "Shirley", "Rolo", "Milly", "Rangiku", "Gin", "Komamura", "Hitsugaya", "Urahara"
]


# Function to shuffle word
def shuffle_word(word):
    word = list(word)
    random.shuffle(word)
    return "".join(word)

@app.on_message(filters.command("scramble") & filters.group)
async def scramble_word(client: Client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    
    # Check if user is in cooldown
    current_time = time.time()
    if user_id in cooldowns and cooldowns[user_id] > current_time:
        remaining_time = int(cooldowns[user_id] - current_time)
        minutes, seconds = divmod(remaining_time, 60)
        await message.reply(f"⏳ You need to wait {minutes}m {seconds}s before playing again!")
        return
    
    original_word = random.choice(anime_characters)  # Pick a random anime character name
    scrambled_word = shuffle_word(original_word)
    
    games[user_id] = {
        "original": original_word,
        "attempts": 3
    }
    
    cooldowns[user_id] = current_time + 180  # Set cooldown for 180s
    
    response = (
        "🎲 Welcome to Word Resemble Game! 🎲\n\n"
        "🔠 Unshuffle this word:\n\n"
        f"✨ {scrambled_word} ✨\n\n"
        "⏳ You have *3 attempts* to guess the word.\n"
        "❌ Use /xshuffle to end the game."
    )
    
    await message.reply(response)

@app.on_message(filters.text & ~filters.command(["scramble", "xshuffle"]) & filters.group, group=1)
async def check_answer(client: Client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    if user_id in games:
        game = games[user_id]
        if message.text.lower() == game["original"].lower():
            # Grant 60 coins
            await user_collection.update_one({'id': user_id}, {'$inc': {'coins': 60}}, upsert=True)
            
            # Track Scramble Solved in WebApp Guild Event DB
            try:
                import datetime
                db_guild_event = ddw['Guild_Event_DB']
                user_event_data = db_guild_event['users']
                today_str = str(datetime.datetime.now(datetime.timezone.utc).date())
                
                existing_event = await user_event_data.find_one({"_id": user_id})
                
                upd = {"$inc": {"weekly_scrambles_solved": 1}}
                if existing_event and existing_event.get("last_scramble_date") == today_str:
                    upd["$inc"]["daily_scrambles_solved"] = 1
                else:
                    upd["$set"] = {"daily_scrambles_solved": 1, "last_scramble_date": today_str}
                    
                await user_event_data.update_one({"_id": user_id}, upd, upsert=True)
                
                # Check task completion after the update
                updated_event = await user_event_data.find_one({"_id": user_id})
                if updated_event:
                    daily_scrambles = updated_event.get("daily_scrambles_solved", 0)
                    weekly_scrambles = updated_event.get("weekly_scrambles_solved", 0)
                    
                    completed_tasks = []
                    if daily_scrambles == 1:
                        completed_tasks.append("🧩 <b>Word Scrambler</b> (Daily)")
                        completed_tasks.append("🧩 <b>Daily Scrambler</b> (Waifu Pass)")
                    if weekly_scrambles == 5:
                        completed_tasks.append("🧠 <b>Scramble Master</b> (Weekly)")
                        completed_tasks.append("🧠 <b>Scramble Specialist</b> (Waifu Pass)")
                        
                    if completed_tasks:
                        task_list_str = "\n".join(completed_tasks)
                        me = await client.get_me()
                        tc_image_url = "https://files.catbox.moe/8t2cui.png"
                        from html import escape
                        caption = (
                            f'<a href="{tc_image_url}">&#8203;</a>'
                            "🎉 <b>ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
                            f"👤 <b>ʜᴜɴᴛᴇʀ:</b> <a href='tg://user?id={user_id}'>{escape(message.from_user.first_name)}</a>\n"
                            f"{task_list_str}\n\n"
                            "✨ <i>Claim rewards in Mini App!</i> 💎"
                        )
                        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("Open Mini App", url=f"https://t.me/{me.username}?startapp=true")]
                        ])
                        
                        try:
                            from pyrogram import enums
                            await client.send_message(
                                chat_id=message.chat.id,
                                text=caption,
                                reply_markup=keyboard,
                                parse_mode=enums.ParseMode.HTML
                            )
                        except Exception as send_err:
                            print(f"Error sending task completed messages in word.py: {send_err}")
            except Exception as e:
                print(f"Error tracking scramble task: {e}")
                
            del games[user_id]
            await message.reply("✅ Correct! You earned 60 coins.")
        else:
            game["attempts"] -= 1
            if game["attempts"] == 0:
                del games[user_id]
                await message.reply(f"❌ Game Over! The correct word was: {game['original']}")
            else:
                await message.reply(f"❌ Wrong! You have {game['attempts']} attempts left.")

@app.on_message(filters.command("xshuffle") & filters.group)
async def end_game(client: Client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    if user_id in games:
        del games[user_id]
        await message.reply("🚫 Game cancelled.")
    else:
        await message.reply("You have no active game.")
