from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bcnadds import TgGraph
from datetime import datetime
import psycopg2

token = "d3b25feccb89e508a9114afb82aa421fe2a9712b963b387cc5ad71e58722"  # from https://telegra.ph/api
API_ID = "14688437"
API_HASH = "5310285db722d1dceb128b88772d53a6"
BOT_TOKEN = "6162291374:AAEJxgUYtTt0OYDE0G6V2ZhGW-WaLV-qzMQ"
DATABASE_URL = "postgres://rvnxvley:rOGv1m1OYE1IhsLmgzjj7Iv7EHdGS1l6@berry.db.elephantsql.com/rvnxvley"  # Replace with your PostgreSQL database URL

app = Client("telegraph_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
tgraph = TgGraph(access_token=token)

def Connect(query, values=None, fetch=False):
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = connection.cursor()

    try:
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        connection.commit()

        if fetch:
            return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()
        
create_users = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL
);
"""
Connect(create_users)

def get_users_count():
    query = "SELECT COUNT(user_id) FROM users;"
    result = Connect(query, fetch=True)
    return result[0][0] if result else 0

def add_stats(user_id):
    query = "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING RETURNING id;"
    result = Connect(query, (user_id,), fetch=True)
    return result[0][0] if result else None


@app.on_message(filters.command("stats"))
async def stats_callback(client, message):
    unique_users = get_users_count()
    msg = await message.reply_text("Getting your stats...")
    await msg.edit_text(
        f"📊 <b><u>Statistics</u></b>\n\n"
        f"<b>Users:</b> <code>{unique_users}</code>"
    )


@app.on_message(filters.photo | filters.video | filters.animation)
async def handle_messages(client, message):
    try:
        telegraph_link = None

        if message.photo or message.video or message.animation:
            # For photos, videos, or GIFs, generate a Telegraph link with text if available
            file_path = await message.download()
            uploaded_files = await tgraph.file_upload(file_path)
            media_source_url = uploaded_files[0].get('src')

            # Check if the message contains text
            if message.caption:
                msg = await message.reply_text("Uploading file...")
                await msg.edit_text("Generating your link...")
                page_title = "TgGraph"
                page_content = message.caption
                telegraph_response = await tgraph.create_page(
                    page_title,
                    html_content=f'<img src="{media_source_url}" alt="Telegraph Media">{page_content}',
                    return_content=True,
                    return_html=True
                )
                telegraph_link = f'https://telegra.ph/file/{telegraph_response.get("path")}'

                await msg.edit_text(f"🔗 Here is your link: {telegraph_link}")

            else:
                telegraph_link = f'https://graph.org/file/{media_source_url.split("/")[-1]}'
                msg = await message.reply_text("Uploading your link...")
                await msg.edit_text(f"🔗 Here is your link: {telegraph_link}")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")


@app.on_message(filters.text & ~filters.command("start") & ~filters.command("help") & ~filters.command("stats"))
async def handle_text_messages(client, message):
    try:
        if message.text:
            msg = await message.reply_text("Creating Telegraph page...")

            # If the message contains text, create a Telegraph page with the text
            page_title = "TgGraph"
            page_content = message.text
            telegraph_response = await tgraph.create_page(
                page_title,
                html_content=page_content,
                return_content=True,
                return_html=True
            )
            telegraph_link = f'https://graph.org/{telegraph_response.get("path")}'
            await msg.edit_text(f"Here is your link: {telegraph_link}")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")


@app.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="start"),
            ]
        ]
    )
    await callback_query.edit_message_text(
        "ℹ️ **Help**\n\n"
        "This bot can create Telegraph pages for your text, photos, videos, and GIFs.\n\n"
        "To create a Telegraph page, send a photo, video, GIF, or text to the bot with optional text.",
        reply_markup=keyboard
    )


@app.on_message(filters.command("help"))
async def help_(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="start"),
            ]
        ]
    )
    await message.reply_text(
        "ℹ️ **Help**\n\n"
        "This bot can create Telegraph pages for your text, photos, videos, and GIFs.\n\n"
        "To create a Telegraph page, send a photo, video, GIF, or text to the bot with optional text.",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("start"))
async def start_callback(client, callback_query):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Support", url="t.me/TgBotsNetwork"),
                InlineKeyboardButton("Updates", url="t.me/TgBotsNetwork")
            ],
            [
                InlineKeyboardButton("Help", callback_data="help"),
            ]
        ]
    )
    await callback_query.edit_message_text(
        "Hello! I am a Telegraph bot. I can help you create Telegraph pages for your content.\n\n"
        "Use /help to see more information.",
        reply_markup=keyboard
    )


@app.on_message(filters.command("start"))
async def start(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Support", url="t.me/TgBotsNetwork"),
                InlineKeyboardButton("Updates", url="t.me/TgBotsNetwork")
            ],
            [
                InlineKeyboardButton("Help", callback_data="help"),
            ]
        ]
    )
    add_stats(message.from_user.id)
    await message.reply(
        "Hello! I am a Telegraph bot. I can help you create Telegraph pages for your content.\n\n"
        "Use /help to see more information.",
        reply_markup=keyboard
    )

app.run()
