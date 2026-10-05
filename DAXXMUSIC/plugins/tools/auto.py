import asyncio
from pyrogram import filters
from DAXXMUSIC.utils.database import get_assistant
from DAXXMUSIC import app
import config

MIN_MEMBERS = 20  # Minimum members required


@app.on_message(filters.command("autocheck") & filters.user(config.OWNER_ID))
async def auto_check_groups(client, message):
    msg = await message.reply("🔍 Assistant checking groups...")

    userbot = await get_assistant(config.LOGGER_ID)

    checked = 0
    left = 0

    async for dialog in userbot.get_dialogs():
        try:
            chat = dialog.chat

            if chat.type in ["group", "supergroup"]:
                checked += 1

                members_count = await userbot.get_chat_members_count(chat.id)

                if members_count < MIN_MEMBERS:
                    await userbot.leave_chat(chat.id)
                    left += 1
                    await asyncio.sleep(2)  # Flood protection

        except Exception as e:
            print(f"[ERROR] {e}")
            await asyncio.sleep(1)

    await msg.edit(
        f"✅ **Auto Check Completed**\n\n"
        f"📊 Total Groups Checked: {checked}\n"
        f"🚪 Groups Left: {left}\n"
        f"🛑 Minimum Required Members: {MIN_MEMBERS}"
    )
