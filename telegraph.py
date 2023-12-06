from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from bcnadds import TgGraph
import io

API_ID = "14688437"
API_HASH = "5310285db722d1dceb128b88772d53a6"
BOT_TOKEN = "6162291374:AAEJxgUYtTt0OYDE0G6V2ZhGW-WaLV-qzMQ"

bot = Client("telegraph_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
tgraph = TgGraph()

@app.on_message(filters.command("telegraph", prefixes="/") & filters.private)
async def telegraph_link(client, message):
    try:
        # Check if the message contains any media (photo, video, document)
        if message.media:
            # Download the media file
            file_path = await message.download()
            
            # Upload the media file to Telegraph
            uploaded_files = await tgraph.file_upload(file_path)
            
            # Get the source URL of the uploaded media
            media_source_url = uploaded_files[0].get('src')
            
            # Send the Telegraph link to the user
            await message.reply(f"Telegraph link for the media: {media_source_url}")
        elif message.text:
            # If the message contains text, create a Telegraph page with the text
            page_title = "Telegraph Page"
            page_content = message.text
            
            # Create a new Telegraph page
            response = await tgraph.create_page(page_title, html_content=page_content, return_content=True, return_html=True)
            
            # Get the Telegraph link from the response
            telegraph_link = response.get('url')
            
            # Send the Telegraph link to the user
            await message.reply(f"Telegraph link for the text: {telegraph_link}")
        else:
            await message.reply("Unsupported message type. Please send text or media.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

app.run()
