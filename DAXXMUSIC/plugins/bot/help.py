from typing import Union
from pyrogram import filters, types, enums
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from DAXXMUSIC import app
from DAXXMUSIC.utils import help_pannel
from DAXXMUSIC.utils.database import get_lang
from DAXXMUSIC.utils.decorators.language import LanguageStart, languageCB
from DAXXMUSIC.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers
from DAXXMUSIC.utils.stuffs.buttons import BUTTONS
from DAXXMUSIC.utils.stuffs.helper import Helper

@app.on_message(filters.command(["musichelp"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)
        await update.message.edit(
            text=f'<a href="{START_IMG_URL}">\u200b</a>' + _["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        if START_IMG_URL.endswith(".mp4") or "catbox.moe" in START_IMG_URL:
            await update.reply_video(
                video=START_IMG_URL,
                caption=_["help_1"].format(SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        else:
            await update.reply_photo(
                photo=START_IMG_URL,
                caption=_["help_1"].format(SUPPORT_CHAT),
                reply_markup=keyboard,
            )


@app.on_message(filters.command(["musichelp"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_back_markup(_)
    if cb == "hb1":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_1, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb2":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_2, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb3":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_3, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb4":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_4, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb5":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_5, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb6":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_6, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb7":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_7, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb8":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_8, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb9":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_9, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb10":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_10, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb11":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_11, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb12":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_12, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb13":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_13, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb14":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_14, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    elif cb == "hb15":
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + helpers.HELP_15, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
        
        
@app.on_callback_query(filters.regex("mbot_cb") & ~BANNED_USERS)
async def helper_cb(client, CallbackQuery):
    await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + Helper.HELP_M, reply_markup=InlineKeyboardMarkup(BUTTONS.MBUTTON), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex('managebot123'))
async def on_back_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_pannel(_, True)
    if cb == "settings_back_helper":
        await CallbackQuery.message.edit(
            text=f'<a href="{START_IMG_URL}">\u200b</a>' + _["help_1"].format(SUPPORT_CHAT), reply_markup=keyboard, parse_mode=enums.ParseMode.HTML
        )

@app.on_callback_query(filters.regex('mplus'))      
async def mb_plugin_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"mbot_cb")]])
    if cb == "Okieeeeee":
        await CallbackQuery.message.edit(text=f"`something errors`",reply_markup=keyboard,parse_mode=enums.ParseMode.HTML)
    else:
        await CallbackQuery.message.edit(text=f'<a href="{START_IMG_URL}">\u200b</a>' + getattr(Helper, cb), reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
