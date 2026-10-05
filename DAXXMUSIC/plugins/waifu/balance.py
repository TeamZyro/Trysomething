from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import OWNER_ID
from DAXXMUSIC import app, user_collection, require_power  # Ensure DB is imported from here
import html
import random

# ====================== BALANCE FETCH/INIT ====================== #
async def get_balance(user_id):
    user_data = await user_collection.find_one({'id': user_id})
    if not user_data:
        await user_collection.insert_one({
            'id': user_id,
            'coins': 5000,
            'crimson': 50,
            'username': None
        })
        return 5000, 50
    return user_data.get('coins', 0), user_data.get('crimson', 0)

# TEMPORARY PAYMENT APPROVAL TRACKER
payment_requests = {}

# ====================== /pay COMMAND ====================== #
@app.on_message(filters.command("pay"))
async def pay_handler(client: Client, message: Message):
    sender = message.from_user
    sender_id = sender.id
    args = message.command

    if len(args) < 2:
        return await message.reply("Usage: `/pay <amount> [@username/user_id or reply] [reason if >20k]`", quote=True)

    # Parse amount
    try:
        amount = int(args[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        return await message.reply("❌ Invalid amount. Must be a positive number.", quote=True)

    # Get recipient
    recipient = None
    if message.reply_to_message:
        recipient = message.reply_to_message.from_user
    elif len(args) > 2:
        try:
            recipient = await client.get_users(args[2])
        except:
            return await message.reply("❌ Invalid username or ID.", quote=True)
    else:
        return await message.reply("❌ You must reply to a user or provide @username/user_id.", quote=True)

    recipient_id = recipient.id
    reason = "No reason"

    if amount > 20000:
        if len(args) < 4:
            return await message.reply("❌ Reason is required for payments over 20,000 coins.", quote=True)
        reason = " ".join(args[3:])

    # OWNER bypass check
    is_owner = sender_id == OWNER_ID

    sender_balance, _ = await get_balance(sender_id)
    if not is_owner and sender_balance < amount:
        return await message.reply("❌ Insufficient balance.", quote=True)

    # Direct payment (under 20k or OWNER)
    if amount <= 20000 or is_owner:
        await user_collection.update_one({'id': sender_id}, {'$inc': {'coins': -amount}}, upsert=True)
        await user_collection.update_one({'id': recipient_id}, {'$inc': {'coins': amount}}, upsert=True)

        new_sender_balance, _ = await get_balance(sender_id)
        await message.reply(
            f"✅ You paid **{amount:,}** coins to [{recipient.first_name}](tg://user?id={recipient_id}).\n"
            f"💰 Your New Balance: `{new_sender_balance:,}`", quote=True
        )

        try:
            await client.send_message(
                recipient_id,
                f"🎉 You received **{amount:,}** coins from [{sender.first_name}](tg://user?id={sender_id})."
            )
        except:
            pass

        return

    # For >20k, send to owner for approval
    payment_id = str(random.randint(100000, 999999))
    payment_requests[payment_id] = {
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "amount": amount,
        "reason": reason
    }

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{payment_id}"),
            InlineKeyboardButton("❌ Decline", callback_data=f"decline_{payment_id}")
        ]
    ])

    await message.reply("🔄 Payment request sent to the owner for approval.", quote=True)

    await client.send_message(
        OWNER_ID,
        f"🔔 **New Payment Request**\n\n"
        f"👤 From: [{sender.first_name}](tg://user?id={sender_id})\n"
        f"👤 To: [{recipient.first_name}](tg://user?id={recipient_id})\n"
        f"💸 Amount: `{amount:,}` coins\n"
        f"📝 Reason: `{reason}`\n\n"
        f"Do you want to approve this request?",
        reply_markup=keyboard
    )

# ====================== CALLBACK HANDLER ====================== #
@app.on_callback_query(filters.regex("^(approve|decline)_(\\d+)$"))
async def handle_approval(client: Client, callback: CallbackQuery):
    action, payment_id = callback.data.split("_")
    data = payment_requests.get(payment_id)

    if not data:
        return await callback.answer("❌ Request not found or expired.", show_alert=True)

    sender_id = data["sender_id"]
    recipient_id = data["recipient_id"]
    amount = data["amount"]
    reason = data["reason"]

    sender_balance, _ = await get_balance(sender_id)

    if action == "approve":
        if sender_id != OWNER_ID and sender_balance < amount:
            await client.send_message(OWNER_ID, "❌ Payment failed. Sender no longer has enough balance.")
            await callback.message.edit("❌ Payment failed: sender has insufficient funds.")
            del payment_requests[payment_id]
            return

        await user_collection.update_one({'id': sender_id}, {'$inc': {'balance': -amount}}, upsert=True)
        await user_collection.update_one({'id': recipient_id}, {'$inc': {'balance': amount}}, upsert=True)

        await client.send_message(sender_id, f"✅ Your payment of `{amount:,}` coins to [user](tg://user?id={recipient_id}) was approved.")
        await client.send_message(recipient_id, f"🎉 You received `{amount:,}` coins from [user](tg://user?id={sender_id}).")

        await callback.message.edit("✅ Payment approved and completed.")
    else:
        await client.send_message(sender_id, f"❌ Your payment of `{amount:,}` coins was *declined* by the owner.\n📄 Reason: `{reason}`")
        await callback.message.edit("❌ Payment was declined.")

    del payment_requests[payment_id]

import random

@app.on_message(filters.command("toss"))
async def toss(client: Client, message: Message):
    user_id = message.from_user.id
    args = message.command

    # Check if correct number of arguments are provided
    if len(args) != 3:
        await message.reply_text("Usage: /toss <h/t> <amount> (e.g., /toss h 1000)")
        return

    # Validate choice (heads or tails)
    choice = args[1].lower()
    if choice not in ['h', 't']:
        await message.reply_text("Invalid choice. Use 'h' for heads or 't' for tails.")
        return

    # Validate amount
    try:
        amount = int(args[2])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.reply_text("Invalid amount. Please enter a positive number.")
        return

    # Check user's balance
    user_balance, _ = await get_balance(user_id)
    if user_balance < amount:
        await message.reply_text("Insufficient balance.")
        return

    # Simulate coin toss with 45% win probability
    win_probability = 0.45  # 45% chance to win
    is_win = random.random() < win_probability
    toss_result = 'h' if random.choice([True, False]) else 't'  # Randomly choose heads or tails

    # Determine outcome
    if (choice == 'h' and toss_result == 'h') or (choice == 't' and toss_result == 't'):
        # User wins: double the amount
        winnings = amount * 2
        await user_collection.update_one({'id': user_id}, {'$inc': {'coins': amount}})
        response = (
            f"🎉 The coin landed on {'heads' if toss_result == 'h' else 'tails'}!\n"
            f"You won {winnings} coins!\n"
            f"💰 Your new balance: {user_balance + amount} coins"
        )
    else:
        # User loses: deduct the amount
        await user_collection.update_one({'id': user_id}, {'$inc': {'coins': -amount}})
        response = (
            f"😢 The coin landed on {'heads' if toss_result == 'h' else 'tails'}.\n"
            f"You lost {amount} coins.\n"
            f"💰 Your new balance: {user_balance - amount} coins"
        )

    await message.reply_text(response)


from pyrogram import Client, filters
from pyrogram.types import Message

@app.on_message(filters.command(["balance", "account", "acc", "bal"], prefixes=["/", "!"]))
async def balance(client: Client, message: Message):
    user_id = message.from_user.id
    user_balance, user_tokens = await get_balance(user_id)

    user_name = message.from_user.first_name or "User"
    response = (
        f"**{user_name}**'s Profile\n"
        f"Crimson : 💷 {user_tokens:,}\n"
        f"Coin : 🪙 {user_balance:,}"
    )
    await message.reply_text(response)



@app.on_message(filters.command("kill"))
@require_power("Owner")
async def kill_handler(client, message):
    # Get the user_id from the reply message
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        await message.reply_text("Please reply to a user's message to use the /kill command.")
        return

    command_args = message.text.split()

    if len(command_args) < 2:
        await message.reply_text("Please specify an option: `c` to delete character, `f` to delete full data, or `b` to delete balance.")
        return

    option = command_args[1]

    try:
        if option == 'f':
            # Delete full user data
            await user_collection.delete_one({"id": user_id})
            await message.reply_text("The full data of the user has been deleted.")

        elif option == 'c':
            # Delete specific character from the user's collection
            if len(command_args) < 3:
                await message.reply_text("Please specify a character ID to remove.")
                return

            char_id = command_args[2]
            user = await user_collection.find_one({"id": user_id})

            if user and 'characters' in user:
                characters = user['characters']
                updated_characters = [c for c in characters if c.get('id') != char_id]

                if len(updated_characters) == len(characters):
                    await message.reply_text(f"No character with ID {char_id} found in the user's collection.")
                    return

                # Update user collection
                await user_collection.update_one({"id": user_id}, {"$set": {"characters": updated_characters}})
                await message.reply_text(f"Character with ID {char_id} has been removed from the user's collection.")
            else:
                await message.reply_text(f"No characters found in the user's collection.")

        elif option == 'b':
            # Check if amount is provided
            if len(command_args) < 3:
                await message.reply_text("Please specify an amount to deduct from balance.")
                return

            try:
                amount = int(command_args[2])
            except ValueError:
                await message.reply_text("Invalid amount. Please enter a valid number.")
                return

            # Fetch user balance
            user_data = await user_collection.find_one({"id": user_id}, {"coins": 1})
            if user_data and "coins" in user_data:
                current_balance = user_data["coins"]
                new_balance = max(0, current_balance - amount)  # Ensure balance doesn't go negative
                
                await user_collection.update_one({"id": user_id}, {"$set": {"coins": new_balance}})
                await message.reply_text(f"{amount} has been deducted from the user's balance. New balance: {new_balance}")
            else:
                await message.reply_text("The user has no balance to deduct from.")

        else:
            await message.reply_text("Invalid option. Use `c` for character, `f` for full data, or `b {amount}` to deduct balance.")

    except Exception as e:
        print(f"Error in /kill command: {e}")
        await message.reply_text("An error occurred while processing the request. Please try again later.")

