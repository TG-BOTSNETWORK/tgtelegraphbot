from telegraph import Telegraph, upload_file
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

# Set your API_ID, API_HASH, and BOT_TOKEN here
API_ID = "14688437"
API_HASH = "5310285db722d1dceb128b88772d53a6"
BOT_TOKEN = "6162291374:AAEJxgUYtTt0OYDE0G6V2ZhGW-WaLV-qzMQ"

bot = Client("telegraph_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
telegraph = Telegraph()

@bot.on_message(filters.private)
async def upload_to_telegraph(client: Client, message: Message):
    try:
        if message.document:
            file_path = await message.download()
            file_url = upload_file(file_path)
        elif message.photo:
            file_path = await message.download()
            file_url = upload_file(file_path)
        else:
            return await message.reply_text("Unsupported file type. Please send a document or a photo.")

        # Generate a Telegraph link
        response = telegraph.create_page(
            title="Uploaded File",
            content=[{"tag": "p", "children": [file_url]}]
        )

        telegraph_link = response["url"]

        # Send the Telegraph link to the user
        buttons = [[InlineKeyboardButton("Open Telegraph Link", url=telegraph_link)]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(f"File uploaded to Telegraph. Here is the link: {telegraph_link}", reply_markup=reply_markup)

    except Exception as e:
        print(e)
        await message.reply_text("Something went wrong. Please try again.")

# Run the bot
bot.run()
