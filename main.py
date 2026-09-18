import os
import requests
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
ALLOWED_IDS_RAW = os.getenv("ALLOWED_USER_IDS", "")

ALLOWED_USER_IDS = []
if ALLOWED_IDS_RAW:
    try:
        ALLOWED_USER_IDS = [int(x.strip()) for x in ALLOWED_IDS_RAW.split(",") if x.strip()]
    except:
        ALLOWED_USER_IDS = []

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

async def forward_to_discord(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    if ALLOWED_USER_IDS and message.from_user.id not in ALLOWED_USER_IDS:
        await message.reply_text("⛔ Lu gak ada akses.")
        return

    # CUMA AMBIL ISI PESANNYA AJA - CLEAN VERSION
    text_content = message.text or message.caption or ""

    files = None
    file_to_forward = None
    filename = "file"

    if message.photo:
        file_to_forward = message.photo[-1]
        filename = "photo.jpg"
    elif message.document:
        file_to_forward = message.document
        filename = file_to_forward.file_name
    elif message.video:
        file_to_forward = message.video
        filename = "video.mp4"
    elif message.animation:
        file_to_forward = message.animation
        filename = "animation.mp4"
    elif message.voice:
        file_to_forward = message.voice
        filename = "voice.ogg"
    elif message.audio:
        file_to_forward = message.audio
        filename = file_to_forward.file_name or "audio.mp3"
    elif message.sticker:
        file_to_forward = message.sticker
        filename = "sticker.webp"

    try:
        if file_to_forward:
            tg_file = await context.bot.get_file(file_to_forward.file_id)
            resp = requests.get(tg_file.file_path, timeout=30)
            resp.raise_for_status()
            file_bytes = resp.content
            if len(file_bytes) <= 24 * 1024 * 1024:
                files = {'file': (filename, file_bytes)}

        # Potong kalo kepanjangan (limit Discord 2000 char)
        content = text_content
        if len(content) > 1900:
            content = content[:1900] + "..."

        # Kalo cuma ngirim file tanpa caption, biarin kosong aja (Discord tetep kirim file nya)
        # Jangan kasih template rame

        payload = {
            "content": content
        }

        r = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files, timeout=20)
        r.raise_for_status()

        # Kalo gamau ada balasan "udah ke-forward" di Telegram, hapus / komen line di bawah ini
        # await message.reply_text("✅")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.reply_text(f"❌ Gagal: {e}")


if __name__ == '__main__':
    if not BOT_TOKEN or not DISCORD_WEBHOOK_URL:
        print("ERROR: Set BOT_TOKEN dan DISCORD_WEBHOOK dulu!")
        exit(1)

    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot jalan - clean mode...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, forward_to_discord))
    app.run_polling()
