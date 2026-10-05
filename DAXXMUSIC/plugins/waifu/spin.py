import random
from pyrogram.enums import ParseMode
import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from DAXXMUSIC import app, collection, user_collection, bounty_values

class SpinEvent:
    def __init__(self):
        self.SPIN_REWARDS = [
            {"type": "coins", "value": 200, "weight": 20, "emoji": "💰"},
            {"type": "coins", "value": 500, "weight": 15, "emoji": "💰"},
            {"type": "coins", "value": 1000, "weight": 10, "emoji": "💰"},
            {"type": "coins", "value": 2000, "weight": 5, "emoji": "💰"},
            {"type": "nothing", "value": 0, "weight": 10, "emoji": "😢"},
            {"type": "nothing", "value": 0, "weight": 5, "emoji": "🥲"},
            {"type": "crimson", "value": 1, "weight": 15, "emoji": "💷"},
            {"type": "crimson", "value": 2, "weight": 10, "emoji": "💷"},
            {"type": "character", "rarity": "💫 Rare", "weight": 10, "emoji": "💫"},
            {"type": "character", "rarity": "🌿 Medium", "weight": 8, "emoji": "🌿"},
        ]

        self.SINGLE_SPIN_COST = 1000
        self.MULTI_SPIN_COST = 10000
        self.setup_handlers()

    def setup_handlers(self):
        @app.on_message(filters.command("spin"), group=9292929)
        async def spin_command(client, message):
            keyboard = [
                [
                    InlineKeyboardButton("🎰 Single Spin", callback_data="spin:single"),
                    InlineKeyboardButton("🎉 Multi Spin", callback_data="spin:multi")
                ],
                [
                    InlineKeyboardButton("🤓 Free Spin", callback_data="spin:free")
                ]
            ]
            await message.reply_photo(
                photo="https://files.catbox.moe/ynouve.jpg",
                caption=f"🌹 **Lucky Spin Event** 🌹\n\n"
                        f"💸 **Spin Cost:** Coins only (💰)\n\n"
                        f"🎁 **Possible rewards:**\n"
                        f"- Characters (💫/🌿/🦄)\n"
                        f"- Coins (💰)\n"
                        f"- Crimson (🔴)\n"
                        f"- Jackpot (🏆)\n\n"
                        f"Choose your spin option:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )

        # ✅ yaha filter laga diya
        @app.on_callback_query(filters.regex(r"^spin:"))
        async def callback_handler(client, callback: CallbackQuery):
            action = callback.data.split(":")[1]

            if action == "free":
                await self.handle_free_spin(callback)
            elif action == "single":
                await self.handle_paid_spin(callback, single=True)
            elif action == "multi":
                await self.handle_paid_spin(callback, single=False)
            elif action == "menu":  # ✅ ab safe hai
                # 🔄 Show spin menu again
                keyboard = [
                    [
                        InlineKeyboardButton("🎰 Single Spin", callback_data="spin:single"),
                        InlineKeyboardButton("🎉 Multi Spin", callback_data="spin:multi")
                    ],
                    [
                        InlineKeyboardButton("🤓 Free Spin", callback_data="spin:free")
                    ]
                ]
                await callback.edit_message_text(
                    "🌹 **Lucky Spin Event** 🌹\n\n"
                    "💸 **Spin Cost:** Coins only (💰)\n\n"
                    "🎁 **Possible rewards:**\n"
                    "- Characters (💫/🌿/🦄)\n"
                    "- Coins (💰)\n"
                    "- Crimson (🔴)\n"
                    "- Jackpot (🏆)\n\n"
                    "Choose your spin option:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
                
    async def handle_free_spin(self, callback):
        user_id = callback.from_user.id
        user = await user_collection.find_one({"id": user_id})

        if user and "last_free_spin" in user:
            last = user["last_free_spin"]
            if (datetime.datetime.now() - last).total_seconds() < 86400:
                remaining = 86400 - (datetime.datetime.now() - last).total_seconds()
                h, m = divmod(int(remaining // 60), 60)
                await callback.edit_message_text(f"⏳ Wait {h}h {m}m for next free spin.")
                return

        reward = await self.process_spin(user_id)
        await self.send_spin_result(callback, reward, "🎁 FREE SPIN RESULT")

        await user_collection.update_one(
            {"id": user_id},
            {"$set": {"last_free_spin": datetime.datetime.now()}},
            upsert=True
        )

    async def handle_paid_spin(self, callback, single):
        user_id = callback.from_user.id
        cost = self.SINGLE_SPIN_COST if single else self.MULTI_SPIN_COST
        spins = 1 if single else 11  # 10 + 1 bonus

        user = await user_collection.find_one({"id": user_id})
        if not user or user.get("coins", 0) < cost:
            await callback.answer("❌ Not enough coins!", show_alert=True)
            return

        await user_collection.update_one({"id": user_id}, {"$inc": {"coins": -cost}})

        if single:
            reward = await self.process_spin(user_id)
            await self.send_spin_result(callback, reward, f"🎰 SINGLE SPIN ({cost} coins)")
        else:
            rewards = [await self.process_spin(user_id) for _ in range(spins)]

            total_coins = sum(r['value'] for r in rewards if r['type'] == 'coins')
            total_crimson = sum(r['value'] for r in rewards if r['type'] == 'crimson')
            total_nothing = sum(1 for r in rewards if r['type'] == 'nothing')
            chars = [r for r in rewards if r['type'] in ['character', 'jackpot']]

            msg = f"\n🎉 **MULTI SPIN RESULT** 🎉\n\n"
            msg += f"💰 Coins: {total_coins}\n🔴 Crimson: {total_crimson}\n😢 Nothing: {total_nothing}\n👤 Characters: {len(chars)}\n\n"
            if chars:
                msg += "🎁 Character Rewards:\n"
                for ch in chars:
                    char = ch['character']
                    char_id = char.get('id', char.get('_id', 'N/A'))
                    msg += (
                        f"{ch['emoji']} {char['name']} ({ch['rarity']}) "
                        f"- 🆔 ID: {char_id} | 💰 {bounty_values.get(ch['rarity'], 'N/A')}\n"
                    )
            keyboard = [
            [InlineKeyboardButton("🔄 Spin Again", callback_data="spin:menu")]
        ]

        await callback.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        

    async def process_spin(self, user_id):
        total_weight = sum(r['weight'] for r in self.SPIN_REWARDS)
        pick = random.uniform(0, total_weight)
        curr = 0
        for reward in self.SPIN_REWARDS:
            curr += reward['weight']
            if pick <= curr:
                reward = reward.copy()

                if reward['type'] == 'coins':
                    await user_collection.update_one(
                        {"id": user_id},
                        {"$inc": {"coins": reward['value']}},
                        upsert=True
                    )

                elif reward['type'] == 'crimson':
                    await user_collection.update_one(
                        {"id": user_id},
                        {"$inc": {"crimson": reward['value']}},
                        upsert=True
                    )

                elif reward['type'] in ['character', 'jackpot']:
                    char = await self.get_random_character(reward['rarity'])
                    if char:
                        reward['character'] = char
                        await self.save_character(user_id, char)

                return reward

    async def get_random_character(self, rarity):
        result = await collection.aggregate([
            {"$match": {"rarity": rarity}},
            {"$sample": {"size": 1}}
        ]).to_list(1)
        return result[0] if result else None

    async def save_character(self, user_id, char):
        await user_collection.update_one(
            {"id": user_id},
            {
                "$push": {"characters": char},  # agar duplicates avoid karne hain to $addToSet use kar
                "$inc": {
                    "total_characters": 1,
                    f"rarity_counts.{char['rarity']}": 1,
                    "total_bounty": bounty_values.get(char['rarity'], 0)
                }
            },
            upsert=True
        )

    async def send_spin_result(self, callback, reward, title):
        msg = f"🎡 {title} 🎡\n\n🎁 You won: {self.format_reward(reward)}"
        if reward.get("character"):
            char = reward["character"]
            char_id = char.get("id", char.get("_id", "N/A"))
            msg += (
                f"\n\n👤 **Character Details:**\n"
                f"Name: {char['name']}\n"
                f"ID: {char_id}\n"
                f"Rarity: {char['rarity']}\n"
                f"Bounty: {bounty_values.get(char['rarity'], 'N/A')}"
            )

        # ✅ Inline button "Spin Again"
        keyboard = [
            [InlineKeyboardButton("🔄 Spin Again", callback_data="spin:menu")]
        ]

        await callback.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

        
    def format_reward(self, reward):
        if reward['type'] == 'coins':
            return f"{reward['emoji']} {reward['value']} coins"
        elif reward['type'] == 'crimson':
            return f"{reward['emoji']} {reward['value']} crimson"
        elif reward['type'] == 'character':
            return f"{reward['emoji']} 1 {reward['rarity']} Character"
        elif reward['type'] == 'jackpot':
            return f"{reward['emoji']} JACKPOT! {reward['rarity']} Character"
        else:
            return f"{reward['emoji']} Better luck next time!"

# Instantiate
spin_event = SpinEvent()
