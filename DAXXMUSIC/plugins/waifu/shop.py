import asyncio
import random
from pyrogram import Client, filters, enums, types as t
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from DAXXMUSIC import app as bot
from DAXXMUSIC import user_collection, collection, user_nguess_progress, user_guess_progress, RARITY_R, db, rarity_map3 as rarity_map2

redeem_collection = db['redeem']

HANDLER = ["/", "!", "Ofa ", "ofa "]
async def get_balance(user_id):
    user_data = await user_collection.find_one({'id': user_id}, {'coins': 1})
    return user_data.get('coins', 0) if user_data else 0

async def update_balance(user_id, amount):
    user_data = await user_collection.find_one({'id': user_id}, {'coins': 1})
    current_balance = user_data.get('coins', 0) if user_data else 0
    new_balance = current_balance + amount
    await user_collection.update_one(
        {'id': user_id},
        {'$set': {'coins': new_balance}},
        upsert=True
    )

def get_rarity_buttons():
    buttons = []
    row = []
    for rarity, emoji in rarity_map2.items():
        row.append(InlineKeyboardButton(f"{emoji}", callback_data=f"rarity_{rarity}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

@bot.on_message(filters.command(["shop", "calimchar"], HANDLER), group=99999)
async def shop(_, message: t.Message):
    await message.reply_text(
        "🌟 **Welcome to the Rarity Shop!** 🌟\n\n"
        "Here, you can spin for characters of different rarities. Each rarity has its own unique characters and spin cost.\n\n"
        "**Please choose the rarity you want to spin for:**",
        reply_markup=get_rarity_buttons()
    )

import secrets
async def generate_random_code():
    return secrets.token_hex(3).upper()  # More unique 6-digit hex code in uppercase


@bot.on_callback_query(filters.regex(r"^see_code_"))
async def see_code(_, query: CallbackQuery):
    try:
        user_id = query.from_user.id
        code = query.data.split("_")[2]

        # Verify the code belongs to this user
        code_data = await redeem_collection.find_one({
            'code': code,
            'user_id': user_id,
            'redeemed': False
        })

        if not code_data:
            return await query.answer("❌ This is not your active code!", show_alert=True)

        # Try sending to PM first
        try:
            await bot.send_message(
                user_id,
                f"🔑 **Your Redeem Code**\n\n"
                f"`{code}`\n\n"
                f"Use `/redeem {code}` to claim your {code_data['rarity']} character!\n\n"
                "⚠️ This code can only be used by you!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎰 Spin Again", callback_data=f"rarity_{code_data['rarity']}")]
                ])
            )
            await query.answer("✅ Code sent to your PM!", show_alert=False)

        except Exception:
            # If PM fails, show in alert
            await query.answer(
                f"🔑 Your Code: {code}\n\n"
                f"Rarity: {code_data['rarity']}\n"
                "⚠️ Start me in PM for faster redeems!",
                show_alert=True
            )

    except Exception as e:
        await query.answer("❌ Error fetching code", show_alert=True)

        # Try sending to PM first
@bot.on_callback_query(filters.regex(r"^spin_"))
async def handle_spin_click(_, query: CallbackQuery):
    user_id = query.from_user.id
    rarity = query.data.split("_")[1]

    # Get cost for this rarity
    cost = next((cost for r, cost in RARITY_R if r == rarity), 0)
    user_balance = await get_balance(user_id)

    # Block if not enough coins
    if user_balance < cost:
        return await query.answer("❌ You don't have enough coins to spin.", show_alert=True)

    # Deduct coins and show loading
    await update_balance(user_id, -cost)
    await query.edit_message_text("🎰 Spinning...")
    await asyncio.sleep(2)

    # Generate a random redeem code
    random_code = await generate_random_code()
    await redeem_collection.insert_one({
        'user_id': user_id,
        'code': random_code,
        'rarity': rarity,
        'redeemed': False,
        'created_at': datetime.now()
    })

    # Try sending code via DM
    try:
        await bot.send_message(
            user_id,
            f"🔐 **Your Redeem Code:** `{random_code}`\n\n"
            f"Use `/redeem {random_code}` to claim your {rarity} character.\n\n"
            "⚠️ This code can only be used by you!",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        code_sent_msg = "🎟 **You got a Redeem Code!**\n\nYour code has been sent to your DM!"
    except Exception:
        code_sent_msg = "🎟 **You got a Redeem Code!**\n\n❗ I couldn't send it to your DM. Please start the bot in PM and try again."

    # Send response with buttons
    await query.edit_message_text(
        code_sent_msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛩️ send Code", callback_data=f"see_code_{random_code}")],
            [InlineKeyboardButton("🎰 Spin Again", callback_data=f"rarity_{rarity}")]
        ])
    )   


@bot.on_message(filters.command(["redeem"], HANDLER), group=9999999)
async def redeem_code(_, message):
    user_id = message.from_user.id
    args = message.text.split(" ")

    if len(args) < 2:
        return await message.reply_text("❌ Please provide a code: `/redeem CODE`")

    code = args[1].upper().strip()

    code_data = await redeem_collection.find_one({
        'code': code,
        'user_id': user_id,
        'redeemed': False
    })

    if not code_data:
        return await message.reply_text(
            "❌ Invalid code! This is either:\n- Not your code\n- Already redeemed\n- Doesn't exist"
        )

    rarity = code_data["rarity"]

    character = await collection.aggregate([
        {
            '$match': {
                'rarity': rarity
            }
        },
        {'$sample': {'size': 1}}
    ]).to_list(length=1)

    if not character:
        return await message.reply_text("❌ No characters found for this rarity!")

    character = character[0]

# In your new code, replace this:
# char_id = character.get('id') or str(character.get('_id'))
# await user_collection.update_one(
#     {'id': user_id},
#     {'$addToSet': {'characters': char_id}},
#     upsert=True
# )

# WITH THIS — use entire character document
    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': character}},
        upsert=True
      )

    await redeem_collection.update_one(
        {'_id': code_data['_id']},
        {'$set': {'redeemed': True, 'redeemed_at': datetime.now()}}
    )

    # Text-only response
    text = f"""🎉 A {rarity} Character Redeemed! 🎉

🌸 Name: {character.get('name', 'Unknown')}
🌈 Rarity: {character.get('rarity', 'Unknown')}
⛩️ Anime: {character.get('anime', 'Unknown')}
🪪 ID No: {character.get('id', 'Unknown')}
🆔 Code: {code} (now redeemed)
"""

    await message.reply_text(text)

@bot.on_callback_query(filters.regex(r"^rarity_"))
async def handle_rarity_click(_, query: t.CallbackQuery):
    user_id = query.from_user.id
    rarity = query.data.split("_")[1]
    total_characters = await collection.count_documents({'rarity': rarity})
    spin_cost = next((cost for r, cost in RARITY_R if r == rarity), 0)
    user_balance = await get_balance(user_id)

    if user_balance >= spin_cost:
        buttons = [
            [InlineKeyboardButton("🎰 Spin", callback_data=f"spin_{rarity}")],
        ]
    else:
        buttons = [
            [InlineKeyboardButton("❌ Not Enough Coins", callback_data="no_spin")]
        ]

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_rarity")])

    await query.edit_message_text(
        f"**{rarity} Rarity**\n\n"
        f"Total characters: {total_characters}\n"
        f"Spin cost: {spin_cost} coins\n"
        f"Your balance: {user_balance} coins\n\n"
        "Do you want to spin?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query(filters.regex(r"^no_spin$"))
async def no_spin_alert(_, query: CallbackQuery):
    await query.answer("❌ You don’t have enough coins to spin this rarity.", show_alert=True)
    
@bot.on_callback_query(filters.regex(r"^back_to_rarity$"))
async def handle_back_click(_, query: t.CallbackQuery):
    await query.edit_message_text(
        "🌟 **Welcome to the Rarity Shop!** 🌟\n\n"
        "Here, you can spin for characters of different rarities. Each rarity has its own unique characters and spin cost.\n\n"
        "**Please choose the rarity you want to spin for:**",
        reply_markup=get_rarity_buttons()
    )

@bot.on_callback_query(filters.regex(r"^rarity_"))
async def handle_rarity_click(_, query: t.CallbackQuery):
    user_id = query.from_user.id
    rarity = query.data.split("_")[1]
    total_characters = await collection.count_documents({'rarity': rarity})
    spin_cost = next((cost for r, cost in RARITY_R if r == rarity), 0)
    user_balance = await get_balance(user_id)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 Spin", callback_data=f"spin_{rarity}"),
         InlineKeyboardButton("🔙 Back", callback_data="back_to_rarity")]
    ])

    await query.edit_message_text(
        f"**{rarity} Rarity**\n\n"
        f"Total characters: {total_characters}\n"
        f"Spin cost: {spin_cost} coins\n"
        f"Your balance: {user_balance} coins\n\n"
        "Do you want to spin?",
        reply_markup=buttons
    )

