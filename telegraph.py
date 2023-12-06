from pyrogram import Client, filters
from pyrogram.types import Message
from bcnadds import TgGraph

token = "d3b25feccb89e508a9114afb82aa421fe2a9712b963b387cc5ad71e58722"
API_ID = "14688437"
API_HASH = "5310285db722d1dceb128b88772d53a6"
BOT_TOKEN = "6162291374:AAEJxgUYtTt0OYDE0G6V2ZhGW-WaLV-qzMQ"

app = Client("telegraph_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
tgraph = TgGraph(access_token=token)

@app.on_message(filters.private)
async def handle_messages(client, message):
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
            telegraph_response = await tgraph.create_page("Telegraph Page", html_content=f'<img src="{media_source_url}" alt="Telegraph Media">')
            telegraph_link = f'https://telegra.ph{telegraph_response[0]}'
            await message.reply(f"Telegraph link for the media: {telegraph_link}")
            
        elif message.text:
            # If the message contains text, create a Telegraph page with the text
            page_title = "Telegraph Page"
            page_content = message.text
            
            # Create a new Telegraph page
            telegraph_response = await tgraph.create_page(page_title, html_content=page_content, return_content=True, return_html=True)
            
            # Get the Telegraph link from the response
            telegraph_link = f'https://telegra.ph{telegraph_response[0]}'
            
            # Send the Telegraph link to the user
            await message.reply(f"Telegraph link for the text: {telegraph_link}")
        else:
            await message.reply("Unsupported message type. Please send text or media.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

app.run()
