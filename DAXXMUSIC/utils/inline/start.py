from pyrogram.types import InlineKeyboardButton
from pyrogram import enums
import config
from DAXXMUSIC import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=enums.ButtonStyle.PRIMARY   # 🔵 Blue
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_GROUP,
                style=enums.ButtonStyle.SUCCESS   # 🟢 Green
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=enums.ButtonStyle.PRIMARY
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                user_id=config.OWNER_ID,
            ),
            InlineKeyboardButton(
                text=_["S_B_6"],
                url=config.SUPPORT_CHANNEL,
                style=enums.ButtonStyle.SUCCESS
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="settings_back_helper",
            ),
        ],
    ]

    return buttons