from pyrogram import Client, filters
from pyrogram.types import Message
from DAXXMUSIC import app

@app.on_message(filters.command("zyro") & filters.group)
async def mention_zyro_users(client: Client, message: Message):
    chat_id = message.chat.id
    zyro_users = []

    # Extract the optional reason text
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else None

    try:
        async for member in client.get_chat_members(chat_id):
            user = member.user
            if user.first_name and "【ＺＹＲＯ】".lower() in user.first_name.lower():
                zyro_users.append(f"[{user.first_name}](tg://user?id={user.id})")

        if zyro_users:
            mention_text = "\n".join(zyro_users)  # Har user ka name new line pe aayega
            reply_message = f"ZYRO Users in this group:\n{mention_text}"

            # Add reason if provided
            if reason:
                reply_message += f"\n\nReason: {reason}"

            await message.reply(reply_message)
        else:
            await message.reply("No users found with 【ＺＹＲＯ】 in their name.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
