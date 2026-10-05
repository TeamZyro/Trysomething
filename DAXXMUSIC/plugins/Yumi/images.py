from pyrogram import filters
from DAXXMUSIC import app

@app.on_message(filters.command(["img", "image"], prefixes=["/", "!"]))
async def google_img_search(_, message):
    await message.reply_text("❌ This command is temporarily unavailable.")
