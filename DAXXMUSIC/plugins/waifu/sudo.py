from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pymongo import MongoClient

from DAXXMUSIC import OWNER_ID

from DAXXMUSIC import app, db, require_power
from functools import wraps

sudo_users = db['sudo_users']

# Predefined powers
ALL_POWERS = [
    "add_character",  # Adds a new character
    "delete_character",  # Deletes a character
    "update_character",  # Updates an existing character
    "approve_request",  # Approves a request
    "approve_inventory_request",  # Approves an inventory request
    "VIP",
    "Owner"
]

# Command: /addsudo
@app.on_message(filters.command("uaddsudo") & filters.reply)
@require_power("Owner")
async def add_sudo(client, message):
    
    replied_user_id = message.reply_to_message.from_user.id

    # Check if the user is already a sudo
    existing_user = await sudo_users.find_one({"_id": replied_user_id})
    if existing_user:
        await message.reply_text(f"User `{replied_user_id}` is already a sudo.")
        return

    # Add the user as a sudo
    sudo_users.update_one(
        {"_id": replied_user_id},
        {"$set": {"powers": {"add_character": True}}},  # Only giving the 'add_character' power
        upsert=True
    )
    await message.reply_text(f"User `{replied_user_id}` has been added as a sudo with 'add_character' power.")

@app.on_message(filters.command("urmsudo"))
@require_power("Owner")
async def remove_sudo(client, message):
    # Get user ID from reply or command argument
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1 and message.command[1].isdigit():
        user_id = int(message.command[1])
    else:
        await message.reply_text("❌ Please reply to a user or provide a valid user ID.")
        return

    # Check if the user is a sudo
    existing_user = await sudo_users.find_one({"_id": user_id})
    if not existing_user:
        await message.reply_text(f"⚠️ User `{user_id}` is not a sudo.")
        return

    # Remove the user from sudo
    await sudo_users.delete_one({"_id": user_id})
    await message.reply_text(f"✅ User [{user_id}](tg://user?id={user_id}) has been removed from sudo.", disable_web_page_preview=True)



# /ueditsudo command
@app.on_message(filters.command("ueditsudo") & filters.reply)
@require_power("Owner")
async def edit_sudo(client, message):
    replied_user_id = message.reply_to_message.from_user.id
    user_data = await sudo_users.find_one({"_id": replied_user_id})

    if not user_data:
        await message.reply_text("This user is not a sudo.")
        return

    powers = user_data.get("powers", {})
    buttons = []
    for p in ALL_POWERS:
        status = "Yes" if powers.get(p, False) else "No"
        buttons.append([
            InlineKeyboardButton(p, callback_data="noop"),
            InlineKeyboardButton(status, callback_data=f"toggle_{replied_user_id}_{p}")
        ])

    buttons.append([InlineKeyboardButton("Closed", callback_data="close_keyboard")])
    keyboard = InlineKeyboardMarkup(buttons)

    await message.reply_text(
        f"Edit powers for `{replied_user_id}`:",
        reply_markup=keyboard
    )


# Toggle powers (VIP required)
@app.on_callback_query(filters.regex(r"^toggle_(\d+)_(.+)$"))
@require_power("Owner")
async def toggle_power(client, callback_query):
    user_id = int(callback_query.matches[0].group(1))
    power = callback_query.matches[0].group(2)

    # Check if target user exists in sudo list
    user_data = await sudo_users.find_one({"_id": user_id})
    if not user_data:
        await callback_query.answer("User not found.", show_alert=True)
        return

    # Toggle power
    current_status = user_data.get("powers", {}).get(power, False)
    new_status = not current_status
    await sudo_users.update_one(
        {"_id": user_id},
        {"$set": {f"powers.{power}": new_status}}
    )

    await callback_query.answer(
        f"Power '{power}' updated to {'Yes' if new_status else 'No'}.",
        show_alert=True
    )

    # Refresh keyboard after toggle
    updated_data = await sudo_users.find_one({"_id": user_id})
    powers = updated_data.get("powers", {})
    buttons = []
    for p in ALL_POWERS:
        status = "Yes" if powers.get(p, False) else "No"
        buttons.append([
            InlineKeyboardButton(p, callback_data="noop"),
            InlineKeyboardButton(status, callback_data=f"toggle_{user_id}_{p}")
        ])
    buttons.append([InlineKeyboardButton("Closed", callback_data="close_keyboard")])

    await callback_query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))


# No-op handler for labels
@app.on_callback_query(filters.regex("^noop$"))
async def noop_callback(_, cq):
    await cq.answer()


# Close button handler (VIP required)
@app.on_callback_query(filters.regex("^close_keyboard$"))
@require_power("Owner")
async def close_keyboard(_, cq):
    await cq.message.edit_reply_markup(None)
    await cq.answer("Closed.")

# Callback handler for closing the keyboard
@app.on_callback_query(filters.regex(r"^close_keyboard$"))
@require_power("VIP")
async def close_keyboard(client, callback_query):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.answer("Keyboard closed.", show_alert=True)

def require_power(required_power):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            # Check if the message is a callback query or a regular message
            if isinstance(message, CallbackQuery):
                # This is a callback query, not a regular message
                user_id = message.from_user.id
                # If the user is the owner, bypass the power check
                if user_id == OWNER_ID:
                    return await func(client, message, *args, **kwargs)

                # Otherwise, check if the user has the required power
                user_data = await sudo_users.find_one({"_id": user_id})
                if not user_data or not user_data.get("powers", {}).get(required_power, False):
                    # Use callback_query.answer for callback queries
                    await message.answer(f"You do not have the `{required_power}` power required to use this button.", show_alert=True)
                    return
                return await func(client, message, *args, **kwargs)

            # Regular message handling
            user_id = message.from_user.id
            # If the user is the owner, bypass the power check
            if user_id == OWNER_ID:
                return await func(client, message, *args, **kwargs)

            # Otherwise, check if the user has the required power
            user_data = await sudo_users.find_one({"_id": user_id})
            if not user_data or not user_data.get("powers", {}).get(required_power, False):
                # Use message.reply_text for regular messages
                await message.reply_text(f"You do not have the `{required_power}` power required to use this command.")
                return
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator


# Command: /sudolist
@app.on_message(filters.command("uploaders"))
async def sudo_list(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("You do not have permission to use this command.")
        return

    # Fetch all sudo users from the database
    users = await sudo_users.find().to_list(length=None)

    if not users:
        await message.reply_text("There are no sudo users.")
        return

    sudo_list_text = "🔰 **Sudo Users List:**\n\n"
    for user in users:
        user_id = user.get("_id")
        
        # Fetch user details from Telegram
        try:
            user_info = await client.get_users(user_id)
            first_name = user_info.first_name
        except:
            first_name = "Unknown"

        # Show user first name and mention link
        sudo_list_text += f"➤ [{first_name}](tg://user?id={user_id}) (`{user_id}`)\n"

    await message.reply_text(sudo_list_text, disable_web_page_preview=True)
