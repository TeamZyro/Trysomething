import urllib.request
import uuid
import requests
import random
import html
import logging
from pymongo import ReturnDocument
from typing import List
from bson import ObjectId
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    CallbackQuery,
    Message,
)
from datetime import datetime, timedelta
import asyncio

# Assuming these are defined elsewhere in your code
from DAXXMUSIC import db, UPDATE_CHAT, SUPPORT_CHAT, CHARA_CHANNEL_ID, collection, user_collection, sudo_users, require_power
from DAXXMUSIC import (app, PHOTO_URL, OWNER_ID,
                    user_collection, top_global_groups_collection, top_global_groups_collection, 
                    group_user_totals_collection)

shops_collection = db["shops"]

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
LOGGER = logging.getLogger(__name__)

# Rewards for consecutive days
daily_rewards = {
    1: 40,
    2: 60,
    3: 80,
    4: 100,
}

# BOT_JOIN_LINK (if needed)
BOT_JOIN_LINK = "https://t.me/oneforall_support"

# ==================== COIN SYSTEM ====================
async def add_coins(user_id: int, amount: int) -> None:
    try:
        if amount <= 0:
            LOGGER.warning("Attempted to add non-positive amount of coins.")
            return
        
        user = await user_collection.find_one({"id": user_id})

        if user:
            current_coins = user.get("coins", 0)
            await user_collection.update_one(
                {"id": user_id},
                {"$set": {"coins": current_coins + amount}},
            )
        else:
            await user_collection.insert_one({"id": user_id, "coins": amount})
    except Exception as e:
        LOGGER.error(f"Error adding coins: {e}")

# ==================== COMMAND HANDLERS ====================

# /balance - Check coin balance
@app.on_message(filters.command(["balance", "bal"]))
async def check_balance(client: Client, message: Message):
    try:
        # Check if the command is a reply
        if message.reply_to_message:
            target_user_id = message.reply_to_message.from_user.id
        # Check if there are mentions
        elif message.entities and message.entities[0].type == "mention":
            target_user_id = int(message.text[message.entities[0].offset: message.entities[0].length].strip('@'))
        else:
            target_user_id = message.from_user.id  # Default to the command sender

        user = await user_collection.find_one({"id": target_user_id})

        if user:
            coins = user.get("coins", 0)
            await message.reply_text(
                f"Bᴇʜᴏʟᴅ, Yᴏᴜʀ Cᴜʀʀᴇɴᴛ Bᴀʟᴀɴᴄᴇ Sʜɪɴᴇs ➻ 💸 {coins} Cᴏɪɴs."
            )
        else:
            await message.reply_text("Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴʏ Cᴏɪɴs Yᴇᴛ.")
    except Exception as e:
        await message.reply_text("An error occurred while checking the balance.")

# /daily - Claim daily reward
@app.on_message(filters.command("daily"))
async def daily_reward(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        user = await user_collection.find_one({"id": user_id})
        today = datetime.now()

        if user:
            last_claimed = user.get("last_daily_claimed")
            streak = user.get("daily_streak", 0)

            if last_claimed:
                last_claimed_date = last_claimed

                # Check if the user already claimed today
                if last_claimed_date.date() == today.date():
                    # Calculate the time remaining until the next claim
                    time_remaining = last_claimed_date + timedelta(days=1) - today
                    hours, remainder = divmod(time_remaining.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)

                    await message.reply_text(
                        f"Yᴏᴜ Hᴀᴠᴇ Aʟʀᴇᴀᴅʏ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Dᴀɪʟʏ Rᴇᴡᴀʀᴅ.\n"
                        f"Nᴇxᴛ Cʟᴀɪᴍ Aʀᴏᴜɴᴅ: {int(hours)}h {int(minutes)}m {int(seconds)}s"
                    )
                    return
                elif (today - last_claimed_date).days > 1:
                    streak = 1  # Reset streak if a day was skipped
                    await message.reply_text("Yᴏᴜʀ Dᴀɪʟʏ Sᴛʀᴇᴀᴋ Hᴀs Bᴇᴇɴ Rᴇsᴇᴛ.")
                else:
                    streak += 1

                # Cap the streak at 4
                streak = min(streak, 4)
            else:
                streak = 1  # First-time claim

            # Get the reward based on the streak
            coins_earned = daily_rewards[streak]
            await add_coins(user_id, coins_earned)

            # Update user's streak and last claimed time
            await user_collection.update_one(
                {"id": user_id},
                {"$set": {"daily_streak": streak, "last_daily_claimed": today}}
            )

            await message.reply_text(
                f"Yᴏᴜ Hᴀᴠᴇ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Dᴀɪʟʏ ʀᴇᴡᴀʀᴅ. Yᴏᴜ Eᴀʀɴᴇᴅ {coins_earned} Cᴏɪɴs. (Leval {streak}🆙)"
            )
        else:
            # First-time claim
            await user_collection.insert_one({"id": user_id, "coins": 40, "daily_streak": 1, "last_daily_claimed": today})
            await message.reply_text("Yᴏᴜ Hᴀᴠᴇ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Dᴀɪʟʏ ʀᴇᴡᴀʀᴅ. Yᴏᴜ Eᴀʀɴᴇᴅ 40 Cᴏɪɴs. (Leval 1)")
    except Exception as e:
        LOGGER.error(f"Error in daily_reward for user {user_id}: {e}")
        await message.reply_text("An error occurred while processing your daily reward.")

# /weekly - Claim weekly reward
@app.on_message(filters.command("weekly"))
async def weekly_reward(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        user = await user_collection.find_one({"id": user_id})

        current_time = datetime.utcnow()
        start_of_week = current_time.date() - timedelta(days=current_time.weekday())

        if user:
            last_claimed = user.get("last_weekly_claimed")
            if last_claimed and last_claimed.date() >= start_of_week:
                # Calculate the next claim time
                next_claim_time = last_claimed + timedelta(days=7)
                remaining_time = next_claim_time - current_time

                # Ensure remaining time is not negative
                if remaining_time.total_seconds() < 0:
                    remaining_time = timedelta(seconds=0)

                days = remaining_time.days
                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                await message.reply_text(
                    f"Yᴏᴜ Hᴀᴠᴇ Aʟʀᴇᴀᴅʏ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Wᴇᴇᴋʟʏ Rᴇᴡᴀʀᴅ.\n"
                    f"Nᴇxᴛ Cʟᴀɪᴍ Iɴ: {days} Dᴀʏs, {hours} Hᴏᴜʀs, {minutes} Mɪɴᴜᴛᴇs."
                )
                return

            # If the user can claim
            await add_coins(user_id, 250)
            await user_collection.update_one(
                {"id": user_id},
                {"$set": {"last_weekly_claimed": current_time}},
            )
            await message.reply_text("Yᴏᴜ Hᴀᴠᴇ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Wᴇᴇᴋʟʏ Rᴇᴡᴀʀᴅ. Yᴏᴜ Eᴀʀɴᴇᴅ 𝟸𝟻𝟶 Cᴏɪɴs.")
        else:
            await user_collection.insert_one({"id": user_id, "coins": 500, "last_weekly_claimed": current_time})
            await message.reply_text("Yᴏᴜ Hᴀᴠᴇ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Wᴇᴇᴋʟʏ Rᴇᴡᴀʀᴅ. Yᴏᴜ Eᴀʀɴᴇᴅ 500 Cᴏɪɴs.")
    except Exception as e:
        LOGGER.error(f"Error occurred: {e}")
        await message.reply_text("Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ, ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

# /paycoin - Transfer coins to another user
@app.on_message(filters.command("paycoin"))
async def pay_coins(client: Client, message: Message):
    try:
        # Parse the amount from the command arguments
        args = message.text.split()[1:]
        if len(args) != 1:
            await message.reply_text("Invalid format. Use: /paycoin <amount>")
            return

        try:
            amount = int(args[0])
            if amount <= 0:
                await message.reply_text("Amount must be a positive number.")
                return
        except ValueError:
            await message.reply_text("Invalid amount. Please provide a valid number.")
            return

        # Check if the command is a reply to a message
        if not message.reply_to_message:
            await message.reply_text("Please reply to the message of the user you want to pay.")
            return

        # Extract the recipient's user ID from the replied message
        recipient_id = message.reply_to_message.from_user.id

        # Get the sender's user ID
        sender_id = message.from_user.id

        # Check if sender is trying to pay themselves
        if sender_id == recipient_id:
            await message.reply_text("You cannot pay yourself.")
            return

        # Retrieve sender's wallet
        sender_wallet = await user_collection.find_one({"id": sender_id})
        if not sender_wallet:
            await message.reply_text("Sender's wallet not found.")
            return

        # Check sender's balance
        sender_balance = sender_wallet.get("coins", 0)
        if sender_balance < amount:
            await message.reply_text("Insufficient balance to make the payment.")
            return

        # Retrieve recipient's wallet
        recipient_wallet = await user_collection.find_one({"id": recipient_id})
        if not recipient_wallet:
            await message.reply_text("Recipient's wallet not found.")
            return

        # Update sender's balance
        new_sender_balance = sender_balance - amount
        await user_collection.update_one({"id": sender_id}, {"$set": {"coins": new_sender_balance}})

        # Update recipient's balance
        recipient_balance = recipient_wallet.get("coins", 0)
        new_recipient_balance = recipient_balance + amount
        await user_collection.update_one({"id": recipient_id}, {"$set": {"coins": new_recipient_balance}})

        await message.reply_text(f"Successfully transferred {amount} coins to user {recipient_id}.")

    except Exception as e:
        LOGGER.error(f"Error occurred: {e}")
        await message.reply_text("An error occurred while processing the payment.")

# ==================== OWNER COMMANDS ====================

# /removecoins - Owner command to remove coins
@app.on_message(filters.command("removecoins") & filters.user(OWNER_ID))
async def remove_coins(client: Client, message: Message):
    try:
        # Parse the amount and recipient ID
        args = message.text.split()[1:]
        if len(args) != 2:
            await message.reply_text("Invalid format. Use: /removecoins <user_id> <amount>")
            return

        try:
            recipient_id = int(args[0])
            amount = int(args[1])
            if amount <= 0:
                await message.reply_text("Amount must be a positive number.")
                return
        except ValueError:
            await message.reply_text("Invalid input. Please provide a valid user ID and amount.")
            return

        # Retrieve recipient's wallet
        recipient_wallet = await user_collection.find_one({"id": recipient_id})
        if not recipient_wallet:
            await message.reply_text("Recipient's wallet not found. Make sure the user is registered.")
            return

        # Check recipient's balance
        recipient_balance = recipient_wallet.get("coins", 0)
        if recipient_balance < amount:
            await message.reply_text(f"User {recipient_id} has insufficient coins. Current balance: {recipient_balance}.")
            return

        # Update recipient's balance
        new_recipient_balance = recipient_balance - amount
        await user_collection.update_one({"id": recipient_id}, {"$set": {"coins": new_recipient_balance}})

        # Notify the user of successful operation
        await message.reply_text(f"Successfully removed {amount} coins from user {recipient_id}.")

    except Exception as e:
        LOGGER.error(f"Error occurred while removing coins: {e}")
        await message.reply_text("An error occurred while processing the transaction.")


# ==================== BONUS SYSTEM ====================
TARGET_GROUP_ID = -1002562168076  # यह वह ग्रुप है जहाँ बोनस मिलेगा
BOT_JOIN_LINK = "https://t.me/oneforall_support"  # बॉट का जॉइन लिंक

# /bonus - Claim daily bonus (works in all groups but only gives bonus in target group)
@app.on_message(filters.command("bonus"))
async def bonus_command(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        
        # Check if command is used in the target group
        if message.chat.id != TARGET_GROUP_ID:
            keyboard = [[InlineKeyboardButton("Join Here To Claim Bonus", url=BOT_JOIN_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text(
                "⚠️ You can only claim your daily bonus in our official group!",
                reply_markup=reply_markup
            )
            return

        user = await user_collection.find_one({"id": user_id})
        now = datetime.now()
        
        if user:
            last_claimed = user.get("last_bonus_claimed")

            # Check if the user has claimed today
            if last_claimed and last_claimed.date() == now.date():
                await message.reply_text("Yᴏᴜ Hᴀᴠᴇ Aʟʀᴇᴀᴅʏ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Bᴏɴᴜs Tᴏᴅᴀʏ.")
                return

            # Add bonus and update claim date
            await add_coins(user_id, 500)
            await user_collection.update_one(
                {"id": user_id},
                {"$set": {"last_bonus_claimed": now}},
            )
            
            await message.reply_text(
                "🎊Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs🎉 Yᴏᴜ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Dᴀɪʟʏ Bᴏɴᴜs ᴏғ 500 Cᴏɪɴs! Eɴᴊᴏʏ"
            )
        else:
            await user_collection.insert_one({"id": user_id, "coins": 500, "last_bonus_claimed": now})
            await message.reply_text(
                "🎊Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs🎉 Yᴏᴜ Cʟᴀɪᴍᴇᴅ Yᴏᴜʀ Dᴀɪʟʏ Bᴏɴᴜs ᴏғ 500 Cᴏɪɴs! Eɴᴊᴏʏ"
            )

    except Exception as e:
        LOGGER.error(f"Error occurred: {e}")
        await message.reply_text(f"Error occurred: {e}")


# /givecoins - Owner/VIP command to give coins
@app.on_message(filters.command("givecoins"))
@require_power("Owner")  # या "VIP" या "OWNER" (जैसा आप चाहें)
async def give_coins(client: Client, message: Message):
    try:
        args = message.text.split()[1:]

        if message.reply_to_message:
            # Command used in reply: /givecoins <amount>
            if len(args) != 1:
                await message.reply_text("Invalid format. Use in reply: /givecoins <amount>")
                return

            try:
                amount = int(args[0])
                if amount <= 0:
                    await message.reply_text("Amount must be a positive number.")
                    return
            except ValueError:
                await message.reply_text("Invalid amount.")
                return

            recipient_id = message.reply_to_message.from_user.id

        else:
            # Command used normally: /givecoins <user_id> <amount>
            if len(args) != 2:
                await message.reply_text("Invalid format. Use: /givecoins <user_id> <amount>")
                return

            try:
                recipient_id = int(args[0])
                amount = int(args[1])
                if amount <= 0:
                    await message.reply_text("Amount must be a positive number.")
                    return
            except ValueError:
                await message.reply_text("Invalid input. Please provide a valid user ID and amount.")
                return

        # Retrieve recipient's wallet
        recipient_wallet = await user_collection.find_one({"id": recipient_id})
        if not recipient_wallet:
            await message.reply_text("Recipient's wallet not found. Make sure the user is registered.")
            return

        # Update recipient's balance
        recipient_balance = recipient_wallet.get("coins", 0)
        new_recipient_balance = recipient_balance + amount
        await user_collection.update_one({"id": recipient_id}, {"$set": {"coins": new_recipient_balance}})

        # Notify success
        await message.reply_text(f"Successfully added {amount} coins to user {recipient_id}.")

    except Exception as e:
        LOGGER.error(f"Error occurred while giving coins: {e}")
        await message.reply_text("An error occurred while processing the transaction.")
