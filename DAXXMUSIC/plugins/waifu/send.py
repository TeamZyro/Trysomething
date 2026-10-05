from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from DAXXMUSIC import user_collection
from DAXXMUSIC import app as shivuu

pending_gifts = {}
locked_users = set()
locked_characters = set()
cooldowns = {}
active_buttons = {}
processing_locks = set()

GIFT_TIMEOUT = 60  # seconds


# ------------------- GIFT COMMAND -------------------
@shivuu.on_message(filters.command("gift"))
async def gift(client, message):
    sender_id = message.from_user.id

    # Cooldown
    if sender_id in cooldowns:
        diff = time.time() - cooldowns[sender_id]
        if diff < 15:
            await message.reply_text(
                f"⏳ Please wait **{int(15 - diff)} seconds** before gifting again!"
            )
            return

    # Lock check
    if sender_id in locked_users:
        await message.reply_text(
            "⚠️ You already have a pending process! Complete it first."
        )
        return

    # Must reply
    if not message.reply_to_message:
        await message.reply_text("❗ Reply to a real user's message to gift.")
        return

    reply = message.reply_to_message

    # 🔴 HARD VALIDATION STARTS HERE

    # Must be real user
    if not reply.from_user:
        await message.reply_text("❗ You must reply to a real user's message!")
        return

    # No bots
    if reply.from_user.is_bot:
        await message.reply_text("🤖 You can't gift characters to bots!")
        return

    # No forwarded messages
    if reply.forward_from or reply.forward_sender_name:
        await message.reply_text("❗ You cannot gift using forwarded messages!")
        return

    # No anonymous/channel messages
    if reply.sender_chat:
        await message.reply_text("❗ You cannot gift to anonymous/channel messages!")
        return

    receiver_id = reply.from_user.id
    receiver_username = reply.from_user.username
    receiver_first_name = reply.from_user.first_name

    if sender_id == receiver_id:
        await message.reply_text("❗ You can't gift to yourself!")
        return

    if len(message.command) != 2:
        await message.reply_text("🆔 Provide a valid character ID!")
        return

    character_id = str(message.command[1])

    sender = await user_collection.find_one({'id': sender_id})
    if not sender:
        await message.reply_text("🛑 You don't have any saved data!")
        return

    # Find character safely
    character = None
    for char in sender.get("characters", []):
        if isinstance(char, dict) and str(char.get("id")) == character_id:
            character = char
            break
        elif str(char) == character_id:
            character = {"id": character_id}
            break

    if not character:
        await message.reply_text("🛑 You don't own this character!")
        return

    if character_id in locked_characters:
        await message.reply_text("🔒 This character is already in another transaction!")
        return

    # Lock user & character
    locked_users.add(sender_id)
    locked_characters.add(character_id)

    process_id = str(time.time())

    pending_gifts[(sender_id, receiver_id)] = {
        "character": character,
        "receiver_username": receiver_username,
        "receiver_first_name": receiver_first_name,
        "process_id": process_id,
        "created_at": time.time()
    }

    active_buttons[(sender_id, process_id)] = True

    await message.reply_text(
        f"🎁 {message.from_user.mention}, confirm gifting this character?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_gift:{process_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_gift:{process_id}")]
        ])
    )


# ------------------- CALLBACK -------------------
@shivuu.on_callback_query(filters.regex(r"^(confirm_gift|cancel_gift):"))
async def gift_callback(client, callback_query):

    sender_id = callback_query.from_user.id
    action, process_id = callback_query.data.split(":")

    if process_id in processing_locks:
        await callback_query.answer("❗ Already processing!", show_alert=True)
        return

    processing_locks.add(process_id)

    # Find gift
    gift_key = None
    for key, value in pending_gifts.items():
        if key[0] == sender_id and value["process_id"] == process_id:
            gift_key = key
            break

    if not gift_key:
        await callback_query.answer("❗ Invalid or expired process!", show_alert=True)
        processing_locks.discard(process_id)
        return

    gift = pending_gifts[gift_key]
    receiver_id = gift_key[1]
    character_id = str(gift["character"]["id"])

    # Expiry check
    if time.time() - gift["created_at"] > GIFT_TIMEOUT:
        await callback_query.answer("⌛ Gift request expired!", show_alert=True)
        del pending_gifts[gift_key]
        locked_users.discard(sender_id)
        locked_characters.discard(character_id)
        processing_locks.discard(process_id)
        return

    if action == "cancel_gift":
        await callback_query.message.edit_text("❌ Gift cancelled.")
    else:
        # Confirm gift
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        # Remove only one instance
        removed = False
        new_chars = []
        for c in sender.get("characters", []):
            if not removed and str(c if not isinstance(c, dict) else c.get("id")) == character_id:
                removed = True
                continue
            new_chars.append(c)

        await user_collection.update_one(
            {'id': sender_id},
            {'$set': {'characters': new_chars}}
        )

        if receiver:
            await user_collection.update_one(
                {'id': receiver_id},
                {'$push': {'characters': gift["character"]}}
            )
        else:
            await user_collection.insert_one({
                "id": receiver_id,
                "username": gift["receiver_username"],
                "first_name": gift["receiver_first_name"],
                "characters": [gift["character"]],
            })

        cooldowns[sender_id] = time.time()

        await callback_query.message.edit_text(
            f"🎉 Successfully gifted to [{gift['receiver_first_name']}](tg://user?id={receiver_id})!"
        )

    # Cleanup
    pending_gifts.pop(gift_key, None)
    locked_users.discard(sender_id)
    locked_characters.discard(character_id)
    active_buttons.pop((sender_id, process_id), None)
    processing_locks.discard(process_id)
