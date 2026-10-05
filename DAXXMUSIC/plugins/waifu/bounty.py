from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from DAXXMUSIC import user_collection, app as shivuu, rarity_map

import io
import os
import asyncio



DEFAULT_IMAGE_PATH = "strings/default_profile.png"

async def fetch_and_resize_profile_photo(client, user_id):
    photos = []
    async for photo in client.get_chat_photos(user_id):
        photos.append(photo)

    if not photos:
        with open(DEFAULT_IMAGE_PATH, "rb") as f:
            return io.BytesIO(f.read())

    try:
        temp_file_path = await client.download_media(photos[0].file_id)

        with open(temp_file_path, "rb") as file:
            file_content = file.read()

        with Image.open(io.BytesIO(file_content)) as img:
            img_byte_array = io.BytesIO()
            img.save(img_byte_array, format="PNG")
            img_byte_array.seek(0)

        os.remove(temp_file_path)
        return img_byte_array

    except Exception as e:
        print(f"Error fetching image for user {user_id}: {e}")
        with open(DEFAULT_IMAGE_PATH, "rb") as f:
            return io.BytesIO(f.read())


async def create_wanted_poster(name: str, total_bounty: int, total_chars: int, rarity_breakdown: str, profile_image=None):
    template = Image.open("strings/wanted_template2.jpg")
    draw = ImageDraw.Draw(template)

    try:
        playfair_font_path = "PlayfairDisplay-Bold.ttf"
        noto_sans_font_path = "NotoSans-Regular.ttf"
        name_font_size = 250
        bounty_font_size = 200
        name_font = ImageFont.truetype(noto_sans_font_path, name_font_size)
        bounty_font = ImageFont.truetype(playfair_font_path, bounty_font_size)
    except:
        name_font = ImageFont.load_default()
        bounty_font = ImageFont.load_default()

    if profile_image:
        profile_image = profile_image.resize((720, 510), Image.Resampling.LANCZOS)
        border_size = 4
        bordered_image = Image.new("RGBA", (profile_image.width + 2 * border_size, profile_image.height + 2 * border_size), "black")
        bordered_image.paste(profile_image, (border_size, border_size))
        template.paste(bordered_image, (40, 280))

    text_color = "#4A2511"

    name_area = (90, 900, 740, 1040)
    name_width = draw.textlength(name, font=name_font)
    name_height = name_font.size
    while name_width > (name_area[2] - name_area[0]) or name_height > (name_area[3] - name_area[1]):
        name_font_size -= 5
        name_font = ImageFont.truetype(noto_sans_font_path, name_font_size)
        name_width = draw.textlength(name, font=name_font)
        name_height = name_font.size

    name_x = (name_area[2] + name_area[0] - name_width) // 2
    name_y = (name_area[3] + name_area[1] - name_height) // 2 - 20
    draw.text((name_x, name_y), name, fill=text_color, font=name_font)

    bounty_text = f"{total_bounty:,}"
    bounty_area = (160, 1060, 760, 1120)
    bounty_width = draw.textlength(bounty_text, font=bounty_font)
    bounty_height = bounty_font.size
    while bounty_width > (bounty_area[2] - bounty_area[0]) or bounty_height > (bounty_area[3] - bounty_area[1]):
        bounty_font_size -= 5
        bounty_font = ImageFont.truetype(playfair_font_path, bounty_font_size)
        bounty_width = draw.textlength(bounty_text, font=bounty_font)
        bounty_height = bounty_font.size

    bounty_x = 160
    bounty_y = (bounty_area[3] + bounty_area[1] - bounty_height) // 2 - 20
    draw.text((bounty_x, bounty_y), bounty_text, fill=text_color, font=bounty_font)

    img_byte_array = io.BytesIO()
    template.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)

    return img_byte_array


async def mybounty(client, message):
    user_id = message.from_user.id

    loading_msg = await message.reply_text("⏳ Generating your bounty poster...")

    user = await user_collection.find_one({'id': user_id})
    if not user:
        await loading_msg.delete()
        await message.reply_text("You have no characters, so no bounty for now. Start collecting!")
        return

    total_bounty = user.get('coins', 0)
    total_chars = len(user['characters'])

    rarity_counts = {key: 0 for key in rarity_map.keys()}
    rarity_name_to_id = {v: k for k, v in rarity_map.items()}

    for character in user['characters']:
        rarity_name = character.get('rarity')
        rarity_id = rarity_name_to_id.get(rarity_name)
        if rarity_id:
            rarity_counts[rarity_id] += 1

    top_rarity_id = max(rarity_counts.items(), key=lambda x: x[1])[0]
    top_rarity_name = rarity_map[top_rarity_id]

    rarity_breakdown = "\n".join(
        f"{rarity_map[rarity]}: {count}" 
        for rarity, count in rarity_counts.items() 
        if count > 0
    )

    profile_image = await fetch_and_resize_profile_photo(client, user_id)

    poster_image = await create_wanted_poster(
        name=message.from_user.first_name,
        total_bounty=total_bounty,
        total_chars=total_chars,
        rarity_breakdown=rarity_breakdown,
        profile_image=Image.open(profile_image)
    )

    await loading_msg.delete()

    caption = (
        f"🏴‍☠️ <b>{message.from_user.first_name}'s Bounty Report</b>\n\n"
        f"{rarity_breakdown}\n\n"
        f"⭐ <b>Top Rarity:</b> {top_rarity_name}\n"
        f"🎯 <b>Total Characters:</b> {total_chars}\n"
        f"💰 <b>Balance:</b> {total_bounty:,} coins"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Join Support Group", url="https://t.me/oneforall_support")]
    ])

    sent_msg = await message.reply_photo(
        photo=poster_image,
        caption=caption,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )

    await asyncio.sleep(20)
    try:
        await sent_msg.delete()
    except:
        pass


@shivuu.on_message(filters.command("bounty"), group=929292929)
async def mybounty_handler(client: Client, message: Message):
    await mybounty(client, message)
