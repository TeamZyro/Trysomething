import random
import string
from pymongo import ReturnDocument
from pyrogram import Client, filters
from pyrogram import enums
from DAXXMUSIC import app
from DAXXMUSIC import collection, user_collection, db, require_power

redeem_collection = db["redeem_codes"]  # Collection for redeem codes
lock = {}  # Dictionary to prevent multiple redemptions at once


# Helper function: find character by id (string or int)
async def find_character_by_id(character_id):
    try:
        character_id_int = int(character_id)
    except ValueError:
        character_id_int = None

    query = {"$or": [{"id": character_id}]}
    if character_id_int is not None:
        query["$or"].append({"id": character_id_int})

    return await collection.find_one(query)


# Command to generate a redeem code
@app.on_message(filters.command("cgen"), group=929292929)
@require_power("fuckoffbc")
async def generate_redeem_code(client, message):
    args = message.command
    if len(args) < 3:
        await message.reply_text(
            "Usage: `/gen <character_id> <redeem_limit>`",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return

    character_id = args[1]

    try:
        redeem_limit = int(args[2])
    except ValueError:
        await message.reply_text(
            "Invalid redeem limit. It must be a number.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return

    # Find character (string + int id both handled)
    character = await find_character_by_id(character_id)
    if not character:
        await message.reply_text("❌ Character not found.", parse_mode=enums.ParseMode.MARKDOWN)
        return

    # Generate a unique redeem code
    while True:
        redeem_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        exists = await redeem_collection.find_one({"code": redeem_code})
        if not exists:
            break

    # Always store character_id as string in redeem_collection
    char_id_str = str(character["id"])

    # Save redeem code in the database
    await redeem_collection.insert_one({
        "code": redeem_code,
        "character_id": char_id_str,  # store as string
        "character_name": character["name"],
        "redeem_limit": redeem_limit,
        "redeemed_by": []
    })

    # Formatting message properly
    char_info = (
        f"🎭 *Character:* `{character['name']}`\n"
        f"📺 *Anime:* `{character.get('anime', 'Unknown')}`\n"
        f"🌟 *Rarity:* `{character.get('rarity', 'Unknown')}`\n"
        f"🖼 *Image:* [Click Here]({character.get('img_url', '#' )})\n\n"
        f"🔢 *Redeem Limit:* `{redeem_limit}`\n"
        f"🎟 *Redeem Code:* `{redeem_code}`"
    )

    await message.reply_text(
        f"✅ *Redeem code generated!*\n\n{char_info}",
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )


# Command to redeem a code
@app.on_message(filters.command("credeem"), group=929292929)
async def redeem_character(client, message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("Usage: `/redeem <code>`", parse_mode=enums.ParseMode.MARKDOWN)
        return

    redeem_code = args[1]
    user_id = message.from_user.id

    # Check if user is already redeeming
    if user_id in lock:
        await message.reply_text("⚠️ Please wait! You are already redeeming a code.", parse_mode=enums.ParseMode.MARKDOWN)
        return

    # Lock user to prevent multiple redemptions
    lock[user_id] = True

    try:
        # Atomically find and update (avoid race condition)
        redeem_data = await redeem_collection.find_one_and_update(
            {
                "code": redeem_code,
                "redeemed_by": {"$ne": user_id},
                "$expr": {"$lt": [{"$size": "$redeemed_by"}, "$redeem_limit"]}
            },
            {"$push": {"redeemed_by": user_id}},
            return_document=ReturnDocument.AFTER
        )

        if not redeem_data:
            await message.reply_text(
                "❌ Invalid, already redeemed, or limit reached.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return

        # Find character (string + int id both handled)
        character = await find_character_by_id(redeem_data["character_id"])
        if not character:
            await message.reply_text("❌ Character not found.", parse_mode=enums.ParseMode.MARKDOWN)
            return

        # Normalize to int for user collection
        try:
            char_id_int = int(character["id"])
        except ValueError:
            char_id_int = character["id"]

        # Add character object with int id to user collection
        await user_collection.update_one(
            {"id": user_id},
            {"$push": {"characters": {"id": char_id_int}}},
            upsert=True
        )

        char_info = (
            f"🎭 *Character:* `{character['name']}`\n"
            f"📺 *Anime:* `{character.get('anime', 'Unknown')}`\n"
            f"🌟 *Rarity:* `{character.get('rarity', 'Unknown')}`\n"
            f"🖼 *Image:* [Click Here]({character.get('img_url', '#' )})\n\n"
            f"🎉 *You have successfully redeemed this character!*"
        )

        await message.reply_text(
            char_info,
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

    finally:
        # Remove lock after redemption process
        lock.pop(user_id, None)
