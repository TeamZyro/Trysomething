import replicate
import aiofiles
import aiohttp
import os
from PIL import Image
from pyrogram import filters
from DAXXMUSIC import app

REPLICATE_API_TOKEN = "r8_T75GJeqo6W8HjAyGWvZH8tKxFuYragG2rvZ0o"

replicate.Client(api_token=REPLICATE_API_TOKEN)

# Function to convert image to JPG (telegraph/replicate safe)
def convert_to_jpg(path):
    try:
        im = Image.open(path).convert("RGB")
        new_path = path.rsplit(".", 1)[0] + ".jpg"
        im.save(new_path, "JPEG")
        return new_path
    except Exception as e:
        print(f"Image conversion failed: {e}")
        return path

@app.on_message(filters.command("upscale") & filters.reply)
async def upscale_image(_, message):
    replied = message.reply_to_message
    if not replied.photo:
        return await message.reply_text("Reply to a photo only!")

    temp = await message.reply_text("Downloading image...")

    image_path = await replied.download()
    image_path = convert_to_jpg(image_path)

    # Upload image to an image host that gives a public URL (imgbb, telegra.ph doesn't work with replicate)
    async with aiohttp.ClientSession() as session:
        with open(image_path, "rb") as img:
            data = aiohttp.FormData()
            data.add_field("image", img, filename="image.jpg", content_type="image/jpeg")
            async with session.post("https://0x0.st", data=data) as resp:
                if resp.status != 200:
                    return await temp.edit("Image upload failed.")
                upload_url = (await resp.text()).strip()

    await temp.edit("Upscaling using Replicate...")

    try:
        output = replicate.run(
            "tencentarc/gfpgan:1.4",  # you can change this model
            input={"img": upload_url}
        )
        if not output or not isinstance(output, str):
            return await temp.edit("Upscaling failed: No output URL received.")

        # Download result
        async with session.get(output) as resp:
            if resp.status != 200:
                return await temp.edit("Failed to download upscaled image.")
            out_path = f"upscaled_{os.path.basename(image_path)}"
            async with aiofiles.open(out_path, "wb") as f:
                await f.write(await resp.read())

        await message.reply_document(out_path, caption="Here is your upscaled image.")
        await temp.delete()
        os.remove(out_path)
        os.remove(image_path)

    except Exception as e:
        await temp.edit(f"Upscaling failed: {e}")
