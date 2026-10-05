import os
import aiohttp
from pyrogram import filters
from DAXXMUSIC import app
from daxxhub import daxxhub as papadaxx
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ─────────────────────────────
# GITHUB COMMAND (TEXT ONLY)
# ─────────────────────────────
@app.on_message(filters.command(["github", "git"]))
async def github(_, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage:\n/git username")

    username = message.command[1]
    url = f"https://api.github.com/users/{username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as request:

            if request.status == 404:
                return await message.reply_text("User not found.")

            data = await request.json()

    name = data.get("name") or "N/A"
    bio = data.get("bio") or "N/A"
    company = data.get("company") or "N/A"
    blog = data.get("blog") or "N/A"
    location = data.get("location") or "N/A"
    created_at = data.get("created_at") or "N/A"
    repositories = data.get("public_repos") or 0
    followers = data.get("followers") or 0
    following = data.get("following") or 0
    profile_url = data.get("html_url") or "N/A"

    caption = f"""**GitHub Info**

**Username:** {username}
**Name:** {name}
**Bio:** {bio}
**Profile:** {profile_url}
**Company:** {company}
**Blog:** {blog}
**Location:** {location}
**Created On:** {created_at}
**Public Repos:** {repositories}
**Followers:** {followers}
**Following:** {following}
"""

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Close", callback_data="close")]]
    )

    await message.reply_text(
        caption,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
