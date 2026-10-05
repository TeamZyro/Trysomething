from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from DAXXMUSIC import collection as CHARACTERS, app
import re, math

RARITY = {
    1: "💫 Rare",
    2: "🌿 Medium",
    3: "🦄 Legendary",
    4: "💮 Special Edition",
    5: "🔮 Limited Edition",
    6: "🎉 Festival",
    7: "🍂 Seasonal",
    8: "🎐 Celestial",
    9: "❄️ Winter",
    10: "💝 Valentine",
    11: "🔞 Erotic",
    12: "🪽 AMV",
    13: "🐉 Ethereal",
    14: "🕌 Fast edition",
    15: "🎬 Hollywood",
    16: "🎃 Halloween",
    17: "🌈 Chroma edition",
    18: "⚙🛠️ Customized",
    19: "☔ Rain edition",
}

def _normalize(s: str) -> str:
    return re.sub(r'[^\w\s]', '', s).strip().lower()

@app.on_message(filters.command("nrarity"), group=953735272)
async def rarity_info(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "⚠️ Usage: `/nrarity <rarity>`\nExample: `/nrarity  💫 Rare , 🌿 Medium , 🦄 Legendary , 💮 Special Edition , 🔮 Limited Edition ,  🎉 Festival , 🍂 Seasonal , 🎐 Celestial , ❄️ Winter , 💝 Valentine , 🔞 Erotic , 🪽 AMV , 🐉 Ethereal, 🕌 Fast edition , 🎬 Hollywood, 🎃 Halloween , 🌈 Chroma edition , ⚙🛠️ Customized , ☔ Rain edition` or `/nrarity 1`",
            quote=True
        )

    arg = " ".join(message.command[1:]).strip()
    selected_label = None

    if arg.isdigit():
        selected_label = RARITY.get(int(arg))
    else:
        for v in RARITY.values():
            if arg.lower() == v.lower():
                selected_label = v
                break
        if not selected_label:
            arg_norm = _normalize(arg)
            for v in RARITY.values():
                if arg_norm in _normalize(v):
                    selected_label = v
                    break

    if not selected_label:
        return await message.reply("❌ Invalid rarity!", quote=True)

    docs = await CHARACTERS.find({"rarity": selected_label}, {"id": 1, "name": 1}).to_list(length=None)
    if not docs:
        return await message.reply(f"⚠️ No characters found for `{selected_label}`", quote=True)

    await send_rarity_page(message, selected_label, docs, page=1)


async def send_rarity_page(message, rarity, docs, page=1):
    per_page = 25
    total = len(docs)
    total_pages = math.ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    page_docs = docs[start:end]

    lines = []
    for d in page_docs:
        cid = d.get("id", "??")
        name = d.get("name", "Unknown")
        lines.append(f"`{cid}` — {name}")

    text = f"✨ Rarity: **{rarity}**\n📊 Total: {total}\n📖 Page {page}/{total_pages}\n\n" + "\n".join(lines)

    buttons = []
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ Back", callback_data=f"nrarity:{rarity}:{page-1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("➡️ Next", callback_data=f"nrarity:{rarity}:{page+1}"))
    if nav:
        buttons.append(nav)

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    if isinstance(message, CallbackQuery):
        await message.message.edit(text, reply_markup=reply_markup)
        await message.answer()
    else:
        await message.reply(text, reply_markup=reply_markup, quote=True)


@app.on_callback_query(filters.regex(r"^nrarity:"))  # ✅ unique prefix
async def rarity_page_callback(client, cq: CallbackQuery):
    _, rarity, page = cq.data.split(":")
    page = int(page)

    docs = await CHARACTERS.find({"rarity": rarity}, {"id": 1, "name": 1}).to_list(length=None)
    await send_rarity_page(cq, rarity, docs, page)
