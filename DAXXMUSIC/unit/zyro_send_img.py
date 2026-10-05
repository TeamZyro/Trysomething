from DAXXMUSIC import *
import random
import asyncio
from pyrogram import Client
from pyrogram.types import Message
from pyrogram import enums


log = "-1002635044798"

async def delete_message(client: Client, chat_id, message_id):
    await asyncio.sleep(300)
    try:
        await client.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

RARITY_WEIGHTS = {
    "💫 Rare": (40, True),
    "🌿 Medium": (20, True),
    "🦄 Legendary": (12, True),
    "☔ Rain edition": (8, False),
    "💮 Special Edition": (6, True),
    "🔮 Limited Edition": (4, True),
    "🎉 Festival": (2, True),
    "🎐 Celestial": (2, True),
    "💝 Valentine": (1.5, False),
    "🎃 Halloween": (1.2, False),
    "🎬 Hollywood": (0.5, True),
    "🔞 Erotic": (0.5, False)
}

async def send_image(client: Client, message: Message):
    chat_id = message.chat.id

    all_characters = list(await collection.find({"rarity": {"$in": [k for k, v in RARITY_WEIGHTS.items() if v[1]]}}).to_list(length=None))

    if not all_characters:
        await client.send_message(chat_id, "No characters found with allowed rarities in the database.")
        return

    available_characters = [
        c for c in all_characters 
        if 'id' in c and c.get('rarity') is not None and RARITY_WEIGHTS.get(c['rarity'], (0, False))[1]
    ]

    if not available_characters:
        await client.send_message(chat_id, "No available characters with the allowed rarities.")
        return

    cumulative_weights = []
    cumulative_weight = 0
    for character in available_characters:
        cumulative_weight += RARITY_WEIGHTS.get(character.get('rarity'), (1, False))[0]
        cumulative_weights.append(cumulative_weight)

    rand = random.uniform(0, cumulative_weight)
    selected_character = None
    for i, character in enumerate(available_characters):
        if rand <= cumulative_weights[i]:
            selected_character = character
            break

    if not selected_character:
        selected_character = random.choice(available_characters)

    last_characters[chat_id] = selected_character
    last_characters[chat_id]['timestamp'] = time.time()
    
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    has_rainy_token = random.random() < 0.05
    last_characters[chat_id]['rainy_token'] = has_rainy_token
    
    caption_text = f"""✨ A {selected_character['rarity']} Character Appears! ✨
🔍 Use /collect to claim this mysterious character!
💫 Hurry, before someone else snatches them!"""
    
    if has_rainy_token:
        caption_text += "\n\n🎁 Guess this character to receive 1 Rainy Token! ☔"

    if 'vid_url' in selected_character:
        sent_message = await client.send_video(
            chat_id=chat_id,
            video=selected_character['vid_url'],
            caption=caption_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        sent_message = await client.send_photo(
            chat_id=chat_id,
            photo=selected_character['img_url'],
            caption=caption_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )

    last_characters[chat_id]['message_id'] = sent_message.id
    asyncio.create_task(delete_message(client, chat_id, sent_message.id))
