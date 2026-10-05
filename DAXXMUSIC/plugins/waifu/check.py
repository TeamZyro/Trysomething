# TEAMZYRO/commands/check.py
from DAXXMUSIC import app, collection as character_collection, user_collection, char_power
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import asyncio 

@app.on_message(filters.command("check"))
async def check_character(client, message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("Please provide a Character ID: `/check <character_id>`")
        return

    char_id_arg = args[1]

    # Try both int and string search
    query_options = []
    try:
        query_options.append({'id': int(char_id_arg)})
    except ValueError:
        pass
    query_options.append({'id': char_id_arg})

    character = await character_collection.find_one({'$or': query_options})

    if not character:
        await message.reply_text("Character not found.")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Who Have It", callback_data=f"whohaveit_{character['id']}")]
    ])

    text = (
        f"🌟 **Character Info**\n"
        f"🆔 ID: `{character['id']}`\n"
        f"📛 Name: {character['name']}\n"
        f"📺 Anime: {character['anime']}\n"
        f"💎 Rarity: {character['rarity']}\n"
    )

    if 'vid_url' in character:
        await message.reply_video(character['vid_url'], caption=text, reply_markup=keyboard)
    else:
        await message.reply_photo(character['img_url'], caption=text, reply_markup=keyboard)



@app.on_callback_query(filters.regex("^whohaveit_"))
async def who_have_it(client, callback_query):
    character_id = callback_query.data.split("_")[1]

    query_options = []
    try:
        int_char_id = int(character_id)
        query_options.append({'characters.id': int_char_id})
    except ValueError:
        int_char_id = None

    query_options.append({'characters.id': character_id})
    query_options.append({'characters': character_id})   # agar sirf string store ho
    if int_char_id is not None:
        query_options.append({'characters': int_char_id})  # agar sirf int store ho

    users = await user_collection.find({'$or': query_options}).to_list(length=10)

    if not users:
        await callback_query.answer("No one owns this character yet!", show_alert=True)
        return

    owner_text = "**🏆 Top 10 Users Who Own This Character:**\n\n"
    for i, user in enumerate(users, 1):
        user_name = user.get('first_name', 'Unknown')

        count = 0
        for char in user.get("characters", []):
            # Agar dict hai
            if isinstance(char, dict):
                char_id = char.get("id")
                if str(char_id) == str(character_id):
                    count += 1
                elif int_char_id is not None and isinstance(char_id, int) and char_id == int_char_id:
                    count += 1

            # Agar sirf str ya int hai
            else:
                if str(char) == str(character_id):
                    count += 1
                elif int_char_id is not None and isinstance(char, int) and char == int_char_id:
                    count += 1

        owner_text += f"{i}. [{user_name}](tg://user?id={user['id']}) — x{count}\n"

    await callback_query.message.edit_caption(
        caption=f"{callback_query.message.caption}\n\n{owner_text}",
        reply_markup=None
    )
    
