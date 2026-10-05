import re
import asyncio
import random
from datetime import datetime, timedelta
from pyrogram.enums import ParseMode
from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from DAXXMUSIC import app, collection, user_collection, rarity_map

RARITY_WEIGHTS = {
    1: 30, 2: 25, 3: 15, 4: 10, 5: 8,
    6: 5, 7: 3, 8: 2, 9: 1, 10: 1
}

@app.on_message(filters.command("luckcard"), group=929292929)
async def luckcard_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user = await user_collection.find_one({"id": user_id})

    if not user:
        await message.reply("❌ You are not registered.")
        return

    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)

    await user_collection.update_one(
        {"id": user_id},
        {"$pull": {"luckcard_uses": {"$lt": day_ago}}}
    )

    user = await user_collection.find_one({"id": user_id})
    uses = user.get("luckcard_uses", [])
    remaining = max(0, 4 - len(uses))

    if remaining == 0:
        await message.reply("⏳ You’ve already used /luckcard 4 times in the last 24 hours. Try again later!")
        return

    coins = user.get("coins", 0)
    if coins < 500:
        await message.reply("❌ You need at least 500 coins to play.")
        return

    await user_collection.update_one(
        {"id": user_id},
        {"$inc": {"coins": -500}, "$push": {"luckcard_uses": now}}
    )

    outcome = random.choices(["coins", "character", "nothing"], weights=[60, 30, 10])[0]
    if outcome == "coins":
        reward = random.randint(300, 10000)
        prize_text = f"coins:{reward}"

    elif outcome == "character":
        chosen_rarity = random.choices(list(RARITY_WEIGHTS.keys()), weights=RARITY_WEIGHTS.values())[0]
        characters = await collection.aggregate([
            {"$match": {"rarity": chosen_rarity}},
            {"$sample": {"size": 1}}
        ]).to_list(length=1)

        if not characters:
            prize_text = "nothing:None"
        else:
            char = characters[0]
            character_name = char.get("name", "Unknown")
            anime = char.get("anime", "Unknown")
            rarity_text = rarity_map.get(str(char.get("rarity")), "Unknown")
            available_id = char.get("id", "N/A")
            catbox_url = char.get("img", None)

            await user_collection.update_one(
                {"id": user_id},
                {"$addToSet": {"character": available_id}}
            )

            prize_text = f"character:{character_name}|{anime}|{rarity_text}|{available_id}|{catbox_url}"
    else:
        prize_text = "nothing:Better luck next time!"

    await user_collection.update_one(
        {"id": user_id},
        {"$set": {"current_prize": prize_text}}
    )

    buttons = [[
        InlineKeyboardButton("🔲 Box 1", callback_data="open_0"),
        InlineKeyboardButton("🔲 Box 2", callback_data="open_1"),
        InlineKeyboardButton("🔲 Box 3", callback_data="open_2")
    ]]

    await message.reply_photo(
    photo="https://files.catbox.moe/ww9221.png",
    caption=(
        "<b>🎴 LuckCard</b>\n\n"
        "🧿 is your luck strong?\n"
        "👇 Choose the box below and see what you find!\n\n"
        f"🎯 <b>Tries Left:</b> {remaining - 1}/4"
    ),
    reply_markup=InlineKeyboardMarkup(buttons),
    parse_mode=ParseMode.HTML
    )
    


@app.on_callback_query(filters.regex("^open_\d+$"))
async def open_box(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user = await user_collection.find_one({"id": user_id})

    prize_text = user.get("current_prize")
    if not prize_text:
        await callback_query.answer("❌ No active prize!", show_alert=True)
        return

    # Step 1: Show suspense card emoji 🃏
    await callback_query.edit_message_text("🃏")
    await asyncio.sleep(2)  # suspense delay

    # Step 2: Process reward
    if prize_text.startswith("coins:"):
        amount = int(prize_text.split(":")[1])
        await user_collection.update_one({"id": user_id}, {"$inc": {"coins": amount}})
        await callback_query.edit_message_text(
            f"🎉 <b>Congratulations!</b>\n\n💰 You won <b>{amount} coins!</b>",
            parse_mode=ParseMode.HTML
        )

    elif prize_text.startswith("character:"):
        data = prize_text.split(":")[1].split("|")
        if len(data) == 5:
            character_name, anime, rarity_text, available_id, catbox_url = data
            caption = (
                f"<b>🎉 New Character Added!</b>\n\n"
                f"🌸 <b>Name:</b> {character_name}\n"
                f"⚡ <b>Anime:</b> {anime}\n"
                f"🎖️ <b>Rarity:</b> {rarity_text}\n"
                f"🆔 <b>ID:</b> {available_id}"
            )
            try:
                if catbox_url.endswith(".mp4"):
                    await callback_query.message.reply_video(catbox_url, caption=caption, parse_mode=ParseMode.HTML)
                else:
                    await callback_query.message.reply_photo(catbox_url, caption=caption, parse_mode=ParseMode.HTML)
            except Exception as e:
                await callback_query.message.reply(f"❌ Failed to send media.\nError: {e}")
            await callback_query.message.delete()
        else:
            await callback_query.edit_message_text("🎉 You won a character, but some info is missing.")

    else:
        await callback_query.edit_message_text(
            "😢 <b>Empty box!</b>\nBetter luck next time.",
            parse_mode=ParseMode.HTML
        )

    await user_collection.update_one({"id": user_id}, {"$unset": {"current_prize": ""}})
