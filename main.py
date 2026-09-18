
import os
import requests
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
ALLOWED_IDS_RAW = os.getenv("ALLOWED_USER_IDS", "") # contoh: 123,456,789

ALLOWED_USER_IDS = []
if ALLOWED_IDS_RAW:
    try:
        ALLOWED_USER_IDS = [int(x.strip()) for x in ALLOWED_IDS_RAW.split(",") if x.strip()]
    except:
        ALLOWED_USER_IDS = []

# --- Mini web server biar Render/Koyeb gak ngira bot mati ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Bot Telegram -> Discord Bridge is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# --- Fungsi forward ---
async def forward_to_discord(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # Filter user kalo di-set
    if ALLOWED_USER_IDS and message.from_user.id not in ALLOWED_USER_IDS:
        await message.reply_text("⛔ Lu gak ada akses buat pake bot ini.")
        return

    user = message.from_user
    sender_name = f"{user.full_name} (@{user.username})" if user.username else user.full_name

    text_content = message.text or message.caption or ""
    content = f"**Dari {sender_name} (ID: {user.id}):**\n{text_content}"

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
        content = f"**🎤 Voice note dari {sender_name}**"
    elif message.audio:
        file_to_forward = message.audio
        filename = file_to_forward.file_name or "audio.mp3"
    elif message.sticker:
        file_to_forward = message.sticker
        filename = "sticker.webp"
        content = f"**Sticker dari {sender_name}**"
        if message.sticker.emoji:
            content += f" {message.sticker.emoji}"

    try:
        if file_to_forward:
            tg_file = await context.bot.get_file(file_to_forward.file_id)
            # download file telegram
            resp = requests.get(tg_file.file_path, timeout=30)
            resp.raise_for_status()
            file_bytes = resp.content

            # Discord limit 8MB (25MB kalo server boost)
            if len(file_bytes) > 24 * 1024 * 1024:
                content += "\n\n⚠️ File kegedean (>24MB), gak bisa di-forward ke Discord."
            else:
                files = {'file': (filename, file_bytes)}

        # Discord max 2000 char
        if len(content) > 1900:
            content = content[:1900] + "\n...(kepotong)"

        if not content.strip():
            content = f"**Pesan kosong dari {sender_name}**"

        payload = {
            "content": content,
            "username": "Telegram Bridge",
            "avatar_url": "https://telegram.org/img/t_logo.png"
        }

        r = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files, timeout=20)
        r.raise_for_status()

        await message.reply_text("✅ Udah ke-forward ke Discord!")

    except Exception as e:
        logging.error(f"Error forward: {e}")
        await message.reply_text(f"❌ Gagal forward: {e}")


if __name__ == '__main__':
    if not BOT_TOKEN or not DISCORD_WEBHOOK_URL:
        print("ERROR: Set dulu BOT_TOKEN dan DISCORD_WEBHOOK di Environment Variables!")
        exit(1)

    # Jalanin flask di thread terpisah
    threading.Thread(target=run_flask, daemon=True).start()

    print("Bot jalan...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, forward_to_discord))
    app.run_polling()
