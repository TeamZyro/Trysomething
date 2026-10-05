from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from DAXXMUSIC import app, user_collection, collection as character_collection
from DAXXMUSIC import collection 
# Constants
COINS_PER_CRIMSON = 1000
CRIMSON_TO_COIN_RATE = 900

TARGET_RARITIES = {
    "🐉 Ethereal": {"emoji": "🐉", "price": 90},
    "🔞 Erotic":  {"emoji": "🔞", "price": 100}
}

@app.on_message(filters.command("exchange"))
async def exchange_coins(client: Client, message: Message):
    args = message.text.split()
    user_id = message.from_user.id

    if len(args) < 2 or not args[1].isdigit():
        await message.reply("Please specify how many coins to exchange. For example:\n/exchange 2000")
        return

    amount = int(args[1])
    if amount < COINS_PER_CRIMSON:
        await message.reply(f"Minimum {COINS_PER_CRIMSON} coins required for 1 💷 crimson.")
        return

    user = await user_collection.find_one({"id": user_id})
    if not user:
        await message.reply("User account not found.")
        return

    current_coins = user.get("coins", 0)
    current_crimson = user.get("crimson", 0)

    if current_coins < amount:
        await message.reply("You don't have enough coins.")
        return

    crimson_to_add = amount // COINS_PER_CRIMSON
    coins_to_deduct = crimson_to_add * COINS_PER_CRIMSON

    await user_collection.update_one(
        {"id": user_id},
        {"$inc": {"coins": -coins_to_deduct, "crimson": crimson_to_add}}
    )

    await message.reply(
        f"✅ You exchanged {coins_to_deduct} coins and received {crimson_to_add} 💷 crimson!\n"
        f"New balance:\n💸 Coins: {current_coins - coins_to_deduct}\n💷 Crimson: {current_crimson + crimson_to_add}"
    )

@app.on_message(filters.command("excoins"))
async def excoins(client: Client, message: Message):
    args = message.text.split()
    user_id = message.from_user.id

    try:
        amount = int(args[1])
    except (IndexError, ValueError):
        await message.reply("Please specify how many crimson to exchange. For example:\n/excoins 2")
        return

    if amount < 1:
        await message.reply("At least 1 💷 crimson required for exchange.")
        return

    user = await user_collection.find_one({"id": user_id})
    if not user:
        await message.reply("User account not found.")
        return

    current_crimson = user.get("crimson", 0)
    current_coins = user.get("coins", 0)

    if current_crimson < amount:
        await message.reply("You don't have enough 💷 crimson.")
        return

    coins_to_add = amount * CRIMSON_TO_COIN_RATE

    await user_collection.update_one(
        {"id": user_id},
        {"$inc": {"crimson": -amount, "coins": coins_to_add}}
    )

    await message.reply(
        f"✅ You exchanged {amount} 💷 crimson and received {coins_to_add} 💸 coins!\n"
        f"New balance:\n💸 Coins: {current_coins + coins_to_add}\n💷 Crimson: {current_crimson - amount}"
    )


@app.on_message(filters.command("buyc"), group=9393837373)
async def buyc_command(client, message: Message):
    user_id = message.from_user.id
    user_data = await user_collection.find_one({'id': user_id})

    if not user_data:
        await message.reply_text("❌ You are not registered in the database.")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /buyc {character_id}")
        return

    character_id_str = message.command[1]
    try:
        character_id_int = int(character_id_str)
    except ValueError:
        character_id_int = None

    # ✅ Query both string and int id
    query = {"$or": [{"id": character_id_str}]}
    if character_id_int is not None:
        query["$or"].append({"id": character_id_int})

    character = await collection.find_one(query)

    if not character:
        await message.reply_text("❌ Character not found.")
        return

    rarity = character.get("rarity")
    if rarity not in TARGET_RARITIES:
        allowed = ', '.join([f"{v['emoji']} {k}" for k, v in TARGET_RARITIES.items()])
        await message.reply_text(
            f"❌ This character is not purchasable with Crimson.\n"
            f"Only {allowed} are allowed."
        )
        return

    price = TARGET_RARITIES[rarity]["price"]
    emoji = TARGET_RARITIES[rarity]["emoji"]
    user_crimson = user_data.get("crimson", 0)

    if user_crimson < price:
        await message.reply_text(
            f"❌ You need {price} Crimson to buy this character. You have {user_crimson}."
        )
        return

    # ✅ Check if character already exists in user's collection
    existing_char = None
    for c in user_data.get("characters", []):
        cid = str(c.get("id")) if isinstance(c, dict) else str(c)
        if cid == str(character.get("id")):
            existing_char = c
            break

    if existing_char:
        # Increase count
        await user_collection.update_one(
            {'id': user_id, 'characters.id': character['id']},
            {
                '$inc': {'crimson': -price, 'characters.$.count': 1}
            }
        )
    else:
        # Add new with count = 1
        new_char = {
            "id": character["id"],
            "name": character["name"],
            "rarity": character["rarity"],
            "img_url": character.get("img_url"),
            "vid_url": character.get("vid_url"),
            "count": 1
        }
        await user_collection.update_one(
            {'id': user_id},
            {
                '$inc': {'crimson': -price},
                '$push': {'characters': new_char}
            }
        )

    msg = (
        f"{emoji} <b>{character['name']}</b> purchased successfully!\n"
        f"Rarity: <b>{rarity}</b>\n"
        f"Price: <b>{price} Crimson</b>\n"
        f"ID: <b>{character['id']}</b>"
    )

    if 'vid_url' in character:
        await client.send_video(
            chat_id=user_id,
            video=character['vid_url'],
            caption=msg,
            parse_mode=ParseMode.HTML
        )
    else:
        await client.send_photo(
            chat_id=user_id,
            photo=character['img_url'],
            caption=msg,
            parse_mode=ParseMode.HTML
        )

    await message.reply_text("✅ Character bought successfully!")
