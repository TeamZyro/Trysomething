from DAXXMUSIC import *
from pyrogram import Client, filters, enums
from pyrogram.types import Message

@app.on_message(filters.command("cgive"))
@require_power("Owner")
async def give_command(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("❌ Usage: /cgive {character_id}")
        return

    char_id_arg = message.command[1]

    # Int + String dono tarah match
    query_options = []
    try:
        query_options.append({'id': int(char_id_arg)})
    except ValueError:
        pass
    query_options.append({'id': char_id_arg})

    character = await collection.find_one({'$or': query_options})
    if not character:
        await message.reply_text(f"❌ Character with ID {char_id_arg} not found.")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ Please reply to a user's message to give them the character.")
        return

    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.first_name

    # User ko character dena
    user = await user_collection.find_one({'id': user_id})
    if user:
        await user_collection.update_one(
            {'id': user_id},
            {'$push': {'characters': character}}
        )
    else:
        await user_collection.insert_one({
            'id': user_id,
            'username': message.reply_to_message.from_user.username,
            'first_name': user_name,
            'characters': [character],
        })

    # Video/Image ka message decide karo
    video_message = "🎥 This character has a video! Check it out below." if 'vid_url' in character else "🖼️ This character has an image."

    # Confirmation to admin
    await message.reply_text(
        f"✅ Character {character['name']} (ID: {character['id']}) has been given to {user_name}.\n"
        f"{video_message}"
    )

    # Confirmation to user
    user_message = (
        f"🎉 You have received a new character!\n\n"
        f"📛 𝗡𝗔𝗠𝗘: <b>{character['name']}</b>\n"
        f"🌈 𝗔𝗡𝗜𝗠𝗘: <b>{character['anime']}</b>\n"
        f"✨ 𝗥𝗔𝗥𝗜𝗧𝗬: <b>{character['rarity']}</b>\n"
        f"🆔 𝗜𝗗: <b>{character['id']}</b>\n\n"
        f"{video_message}"
    )

    if 'vid_url' in character:
        await client.send_video(
            chat_id=user_id,
            video=character['vid_url'],
            caption=user_message,
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await client.send_photo(
            chat_id=user_id,
            photo=character['img_url'],
            caption=user_message,
            parse_mode=enums.ParseMode.HTML
        )
