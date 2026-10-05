import random
from pyrogram import Client, filters
from pyrogram.types import Message
from DAXXMUSIC import user_collection, app


SLOG = -1002025076123

async def send_log_message(chat_id: int, message: str):
    """Send a log message to the specified chat."""
    await app.send_message(chat_id=chat_id, text=message)

@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    """Handle new chat members joining the chat."""
    bot_user = await client.get_me()
    
    # Check if the bot is one of the new members
    if bot_user.id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        chat_title = message.chat.title
        chat_id = message.chat.id
        chat_username = f"@{message.chat.username}" if message.chat.username else "ᴩʀɪᴠᴀᴛ"

        # Construct the log message
        log_message = (
            f"#newgoroup\n\n"
            f"chat name : {chat_title}\n"
            f"username : {chat_username}\n"
            f"added by : {added_by}"
        )
        
        # Send the log message
        await send_log_message(SLOG, log_message)


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    """Handle the bot leaving the chat."""
    bot_user = await app.get_me()
    
    # Check if the bot is the one that left
    if bot_user.id == message.left_chat_member.id:
        removed_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        chat_title = message.chat.title
        chat_id = message.chat.id
        chat_username = f"@{message.chat.username}" if message.chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"

        # Construct the log message
        log_message = (
            f"#leftgroup \n\n"
            f"chat name : {chat_title}\n"
            f"chat username : {chat_username}\n"
            f"remove by : {removed_by}\n"
        )
        
        await send_log_message(SLOG, log_message)
