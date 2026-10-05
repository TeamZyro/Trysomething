import asyncio
import math
import random
from itertools import groupby
from html import escape
import logging
from DAXXMUSIC import app, user_collection, collection, rarity_map2, ddw
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, Message, CallbackQuery, User, InputMediaVideo
)
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def fetch_user_characters(user_id: int):
    """
    Fetches and validates a user's character list from the database.
    """
    try:
        user = await user_collection.find_one({"id": user_id})
        if not user or 'characters' not in user:
            return None, 'You have not claimed any characters yet. Use /guess to start!'

        # Filter out any malformed character entries
        characters = [c for c in user['characters'] if isinstance(c, dict) and 'id' in c]

        if not characters:
            return None, 'Your collection is empty or contains no valid characters.'

        return characters, None
    except Exception as e:
        logging.error(f"Database error in fetch_user_characters for user {user_id}: {e}")
        return None, "A database error occurred while fetching your characters."

# --- Command Handlers ---
@app.on_message(filters.command(["harem", "collection"]))
async def harem_handler(client: Client, message: Message):
    """
    Handles the /harem command for the user who sent it.
    """
    try:
        # The user who triggered the command
        target_user = message.from_user
        page = 0

        user_data = await user_collection.find_one({"id": target_user.id})
        filter_rarity = user_data.get('filter_rarity') if user_data else None

        # Call the main display function
        msg = await display_harem(client, message, target_user, page, filter_rarity, is_initial=True)

        # Auto-delete the message after 3 minutes
        if msg:
            await asyncio.sleep(180)
            await msg.delete()

    except Exception as e:
        logging.error(f"Error in /harem command for user {message.from_user.id}: {e}", exc_info=True)
        await message.reply_text("An unexpected error occurred while opening your harem. If the problem persists, please contact support.")


@app.on_message(filters.command(["h", "viewharem"]))
async def view_harem_handler(client: Client, message: Message):
    """
    Handles the /h {user_id_or_username} command or reply to view another user's harem.
    """
    try:
        target_user: User = None
        target_input_str = None

        # Case 1: Command is a reply to another user's message
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
            target_input_str = str(target_user.id) # For logging/feedback
        # Case 2: User ID or username provided in the command arguments
        elif len(message.command) > 1:
            target_input_str = message.command[1]
            try:
                # Try to get user by ID (if numerical) or username
                target_user = await client.get_users(target_input_str)
            except (ValueError, PeerIdInvalid):
                # This means the provided string was not a valid ID or username
                await message.reply_text("<b>Invalid User ID or Username.</b>\nPlease provide a valid numerical user ID or mention a user (e.g., `@username` or by replying to their message).")
                return
            except Exception as e:
                logging.error(f"Could not get user {target_input_str} in /h command: {e}")
                await message.reply_text(f"Could not find a user with the ID/username: <code>{target_input_str}</code>. Please ensure the user exists and is accessible.")
                return
        else:
            await message.reply_text("<b>Please provide a user ID, mention a user, or reply to a user's message.</b>\n\n<b>Usage:</b> <code>/h {user_id_or_username}</code>")
            return

        if not target_user:
            await message.reply_text("Could not determine the target user. Please ensure you provide a valid ID, username, or reply to a message.")
            return

        # Now display the harem for the target user
        page = 0
        user_data = await user_collection.find_one({"id": target_user.id})
        filter_rarity = user_data.get('filter_rarity') if user_data else None
        msg = await display_harem(client, message, target_user, page, filter_rarity, is_initial=True)

        if msg:
            await asyncio.sleep(180)
            await msg.delete()
    except Exception as e:
        logging.error(f"Error in /h command: {e}", exc_info=True)
        await message.reply_text("An unexpected error occurred while trying to view the harem.")

# --- Core Display Logic ---
# --- /fav command ---
@app.on_message(filters.command("fav"))
async def fav_handler(client: Client, message: Message):
    user_id = message.from_user.id

    # Argument check
    if len(message.command) < 2:
        await message.reply_text("Please provide a character ID.\nExample: /fav 123")
        return

    char_id_input = message.command[1]

    # Try int conversion
    try:
        char_id = int(char_id_input)
    except ValueError:
        char_id = char_id_input  # keep as string

    # Find user
    user_data = await user_collection.find_one({"id": user_id})
    if not user_data or not user_data.get("characters"):
        await message.reply_text("You don't have any characters in your collection.")
        return

    # Check if character exists in user's collection
    character = next((c for c in user_data["characters"] if str(c["id"]) == str(char_id)), None)
    if not character:
        await message.reply_text("You don't have this character.")
        return

    # Replace old favourite with new one
    await user_collection.update_one({"id": user_id}, {"$set": {"favorites": [str(char_id)]}})

    await message.reply_text(f"✅ {character['name']} is now your favourite character!")


# --- display_harem function updated ---
async def display_harem(client: Client, original_message: Message, target_user: "User", page: int, filter_rarity: str, is_initial: bool = False, callback_query: CallbackQuery = None):
    sent_message = None
    try:
        user_id = target_user.id
        user_first_name = target_user.first_name
        characters, error = await fetch_user_characters(user_id)
        if error:
            reply_target = callback_query or original_message
            await reply_target.reply_text(error) if not callback_query else await callback_query.answer(error, show_alert=True)
            return None

        characters.sort(key=lambda x: (x.get('anime', 'Unknown Anime'), str(x.get('id', ''))))

        if filter_rarity:
            filtered_characters = [c for c in characters if c.get('rarity') == filter_rarity]
            if not filtered_characters:
                keyboard = [[InlineKeyboardButton("Remove Filter", callback_data=f"remove_filter:{user_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                no_char_msg = f"No characters found with rarity: <b>{filter_rarity}</b>. Click below to remove the filter."
                if callback_query:
                    await callback_query.message.edit_text(no_char_msg, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                else:
                    await original_message.reply_text(no_char_msg, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                return None
            characters = filtered_characters

        if not characters:
            error_msg = "The collection is empty after applying filters."
            if callback_query:
                await callback_query.answer(error_msg, show_alert=True)
            else:
                await original_message.reply_text(error_msg)
            return None

        # Optimizing count and unique identification to O(N) to prevent slowness for large collections
        character_counts = {}
        unique_characters = []
        seen_ids = set()
        for c in characters:
            cid = str(c['id'])
            character_counts[cid] = character_counts.get(cid, 0) + 1
            if cid not in seen_ids:
                seen_ids.add(cid)
                unique_characters.append(c)

        if not unique_characters:
            await original_message.reply_text("Something went wrong, no unique characters could be processed.")
            return None

        total_pages = math.ceil(len(unique_characters) / 15)
        page = max(0, min(page, total_pages - 1))

        # --- GUILD & RANK INFO FETCH ---
        try:
            # Re-using the global connection pool (ddw) to avoid establishing new TCP connections
            guild_db = ddw["Guild_Event_DB"]
            guild_user_col = guild_db["users"]
            guild_col = guild_db["guilds"]

            g_user = await guild_user_col.find_one({"_id": user_id})
            
            guild_text = ""
            rank_text = ""
            if g_user:
                xp = g_user.get("xp", 0)
                lvl = (xp // 1000) + 1
                rank = g_user.get("rank", "Bronze")
                
                # Fetch Guild Name if in guild
                if g_user.get("guild_id"):
                    g_info = await guild_col.find_one({"_id": g_user["guild_id"]})
                    g_name = g_info.get("name", "Unknown") if g_info else "No Guild"
                    guild_text = f"🛡️ <b>{g_name}</b>"
                else:
                    guild_text = "🛡️ <i>No Guild</i>"
                
                rank_text = f" | ⚔️ <b>Lvl {lvl}</b> | 🏆 <b>{rank}</b>"
        except Exception as e:
            logging.error(f"Failed to fetch Guild Data: {e}")
            guild_text = ""
            rank_text = ""
        # -------------------------------

        harem_message = f"<b>{escape(user_first_name)}'s Harem - Page {page + 1}/{total_pages}</b>\n"
        harem_message += f"{guild_text}{rank_text}\n"
        if filter_rarity:
            harem_message += f"<b>Filtered by: {filter_rarity}</b>\n"

        start_index = page * 15
        end_index = start_index + 15
        current_page_chars = unique_characters[start_index:end_index]

        grouped_by_anime = groupby(current_page_chars, key=lambda x: x.get('anime', 'Unknown Anime'))
        
        # N+1 query optimization: Batch count characters of all distinct anime on this page in a single query
        unique_anime_names = list(set(c.get('anime', 'Unknown Anime') for c in current_page_chars))
        anime_counts = {}
        if unique_anime_names:
            try:
                pipeline = [
                    {"$match": {"anime": {"$in": unique_anime_names}}},
                    {"$group": {"_id": "$anime", "count": {"$sum": 1}}}
                ]
                cursor = collection.aggregate(pipeline)
                anime_counts_list = await cursor.to_list(length=None)
                anime_counts = {item["_id"]: item["count"] for item in anime_counts_list}
            except Exception as db_err:
                logging.error(f"Error querying anime counts: {db_err}")

        for anime, chars in grouped_by_anime:
            char_list = list(chars)
            total_in_anime = anime_counts.get(anime, 0)
            harem_message += f'\n<b>{anime} {len(char_list)}/{total_in_anime}</b>\n'
            for character in char_list:
                count = character_counts.get(str(character['id']), 1)
                rarity_emoji = rarity_map2.get(character.get('rarity'), '')
                harem_message += f'◈⌠{rarity_emoji}⌡ {character["id"]} {character["name"]} ×{count}\n'

        user_db_data = await user_collection.find_one({"id": user_id})
        saved_rarity = user_db_data.get('filter_rarity') if user_db_data else None

        if filter_rarity:
            rarity_emoji = rarity_map2.get(filter_rarity, '')
            inline_suffix = f".{rarity_emoji}" if rarity_emoji else f".{filter_rarity}"
        elif saved_rarity:
            inline_suffix = ".All"
        else:
            inline_suffix = ""

        keyboard = [
            [
                InlineKeyboardButton("Collection", switch_inline_query_current_chat=f"collection.{user_id}{inline_suffix}"),
                InlineKeyboardButton("💌 AMV", switch_inline_query_current_chat=f"collection.{user_id}{inline_suffix}.AMV")
            ]
        ]

        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"harem:{page-1}:{user_id}:{filter_rarity or 'None'}"))
            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"harem:{page+1}:{user_id}:{filter_rarity or 'None'}"))
            if nav_buttons:
                keyboard.append(nav_buttons)
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Favourite priority logic
        image_character = None

        if user_db_data and user_db_data.get('favorites'):
            fav_id = str(user_db_data['favorites'][0])
            image_character = next((c for c in unique_characters if str(c['id']) == fav_id), None)

        if not image_character and unique_characters:
            image_character = random.choice(unique_characters)

        media = None
        if image_character:
            media_url = image_character.get('vid_url') or image_character.get('img_url')
            if media_url:
                if media_url.endswith(('.mp4', '.mov', '.mkv')):
                    media = InputMediaVideo(media_url, caption=harem_message, parse_mode=enums.ParseMode.HTML)
                else:
                    media = InputMediaPhoto(media_url, caption=harem_message, parse_mode=enums.ParseMode.HTML)

        if is_initial:
            if media and media.media:
                if isinstance(media, InputMediaPhoto):
                    sent_message = await original_message.reply_photo(photo=media.media, caption=harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                else:
                    sent_message = await original_message.reply_video(video=media.media, caption=harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            else:
                sent_message = await original_message.reply_text(harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
        elif callback_query:
            try:
                if media and media.media and (callback_query.message.photo or callback_query.message.video):
                    await callback_query.message.edit_media(media=media, reply_markup=reply_markup)
                elif media and media.media:
                    await callback_query.message.delete()
                    if isinstance(media, InputMediaPhoto):
                        sent_message = await client.send_photo(callback_query.message.chat.id, photo=media.media, caption=harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                    else:
                        sent_message = await client.send_video(callback_query.message.chat.id, video=media.media, caption=harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
                else:
                    await callback_query.message.edit_text(harem_message, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            except Exception as edit_error:
                logging.error(f"Could not edit message during harem callback: {edit_error}")
                await callback_query.answer("A small error occurred while updating the view.", show_alert=False)

        return sent_message or callback_query.message
 
    except Exception as e:
        logging.error(f"Generic error in display_harem for user {target_user.id}: {e}", exc_info=True)
        if callback_query:
            await callback_query.answer("An error occurred while displaying the harem.", show_alert=True)
        else:
            await original_message.reply_text("An error occurred while displaying the harem.")
        return None

        


# --- Callback Handlers ---
@app.on_callback_query(filters.regex(r"^harem"))
async def harem_callback(client: Client, callback_query: CallbackQuery):
    """
    Handles pagination for the harem view.
    """
    try:
        try:
            _, page_str, user_id_str, filter_rarity = callback_query.data.split(':')
            page = int(page_str)
            user_id = int(user_id_str)
        except (ValueError, IndexError) as e:
            logging.error(f"Invalid harem callback data: {callback_query.data}. Error: {e}")
            return await callback_query.answer("Error: Invalid callback data.", show_alert=True)

        filter_rarity = None if filter_rarity == 'None' else filter_rarity

        if callback_query.from_user.id != user_id:
            return await callback_query.answer("This is not your Harem to control!", show_alert=True)

        try:
            target_user = await client.get_users(user_id)
        except Exception as e:
            logging.error(f"Could not fetch user {user_id} in harem_callback: {e}")
            return await callback_query.answer(f"Could not find user with ID: {user_id}.", show_alert=True)

        await display_harem(client, callback_query.message, target_user, page, filter_rarity, is_initial=False, callback_query=callback_query)
    except Exception as e:
        logging.error(f"Error in harem_callback: {e}", exc_info=True)
        await callback_query.answer("An error occurred during pagination.", show_alert=True)


@app.on_message(filters.command("hmode"))
async def hmode_handler(client: Client, message: Message):
    """
    Allows a user to set a rarity filter for their harem.
    """
    user_id = message.from_user.id
    keyboard = []
    row = []
    # Assuming rarity_map2 is ordered as desired
    for i, (rarity, emoji) in enumerate(rarity_map2.items(), 1):
        row.append(InlineKeyboardButton(emoji, callback_data=f"set_rarity:{user_id}:{rarity}"))
        if i % 4 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("All Rarities", callback_data=f"set_rarity:{user_id}:None")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Select a rarity to filter your harem:", reply_markup=reply_markup)

@app.on_callback_query(filters.regex(r"^set_rarity"))
async def set_rarity_callback(client: Client, callback_query: CallbackQuery):
    """
    Sets the rarity filter in the database based on user selection.
    """
    try:
        try:
            _, user_id_str, filter_rarity = callback_query.data.split(':')
            user_id = int(user_id_str)
        except (ValueError, IndexError):
            return await callback_query.answer("Invalid callback data.", show_alert=True)

        if callback_query.from_user.id != user_id:
            return await callback_query.answer("This is not your Harem to modify!", show_alert=True)

        filter_rarity = None if filter_rarity == 'None' else filter_rarity
        await user_collection.update_one({"id": user_id}, {"$set": {"filter_rarity": filter_rarity}}, upsert=True)

        if filter_rarity:
            await callback_query.message.edit_text(f"✅ Rarity filter set to: <b>{filter_rarity}</b>\n\nYour <code>/harem</code> will now only show characters with this rarity.")
        else:
            await callback_query.message.edit_text("✅ Rarity filter cleared. Your <code>/harem</code> will now show all rarities.")
        await callback_query.answer(f"Filter set to {filter_rarity if filter_rarity else 'All'}", show_alert=True)
    except Exception as e:
        logging.error(f"Error in set_rarity_callback: {e}", exc_info=True)
        await callback_query.answer("An error occurred while setting the filter.", show_alert=True)

@app.on_callback_query(filters.regex(r"^remove_filter"))
async def remove_filter_callback(client: Client, callback_query: CallbackQuery):
    """
    Removes the rarity filter when a user clicks the button.
    """
    try:
        try:
            _, user_id_str = callback_query.data.split(':')
            user_id = int(user_id_str)
        except (ValueError, IndexError):
            return await callback_query.answer("Invalid callback data.", show_alert=True)

        if callback_query.from_user.id != user_id:
            return await callback_query.answer("This is not your Harem to modify!", show_alert=True)

        await user_collection.update_one({"id": user_id}, {"$set": {"filter_rarity": None}}, upsert=True)
        await callback_query.message.delete()
        await callback_query.answer("Filter removed. Your harem will now show all rarities.", show_alert=True)
    except Exception as e:
        logging.error(f"Error in remove_filter_callback: {e}", exc_info=True)
        await callback_query.answer("An error occurred while removing the filter.", show_alert=True)
