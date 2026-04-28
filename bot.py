import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# =========================
# CONFIG
# =========================
TOKEN = "8767368647:AAF-88w1X1z0mVPjjm2kvHkBP6jkN3eoAvQ"

# 👑 OWNER (YOU) — put your Telegram ID here
OWNER_ID = 6461680478

# 👥 Extra admins
ADMINS = [OWNER_ID]

MAINTENANCE_MODE = False

# =========================
# ADMIN CHECK
# =========================
def is_admin(user_id):
    return user_id in ADMINS

# =========================
# MENU
# =========================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎥 Download Video", callback_data="video")],
        [InlineKeyboardButton("🎵 Download Audio", callback_data="audio")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Mayor Downloader Bot\nCreated by Mayor Tech Inc 🚀",
        reply_markup=main_menu()
    )

# =========================
# DOWNLOAD ENGINE
# =========================
def download(url, mode):
    if mode == "audio":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "media.%(ext)s",
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    else:
        ydl_opts = {
            "format": "best",
            "outtmpl": "media.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # ADMIN PANEL
    if query.data == "admin":
        if not is_admin(user_id):
            await query.message.reply_text("❌ You are not an admin.")
            return

        await query.message.reply_text(
            f"🛠 ADMIN PANEL\n\n"
            f"Maintenance: {'ON' if MAINTENANCE_MODE else 'OFF'}\n\n"
            "Commands:\n"
            "/on - Enable maintenance\n"
            "/off - Disable maintenance\n"
            "/addadmin <id> - Add admin"
        )
        return

    if query.data == "about":
        await query.message.reply_text(
            "🏷 Mayor Downloader Bot\n"
            "Created by Mayor Tech Inc 🚀\n"
            "Supports TikTok, YouTube, Instagram"
        )
        return

    context.user_data["mode"] = query.data
    await query.message.reply_text("📎 Send your link now")

# =========================
# MESSAGE HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE

    user_id = update.message.from_user.id

    if MAINTENANCE_MODE and not is_admin(user_id):
        await update.message.reply_text("🛠 Bot under maintenance by Mayor Tech Inc")
        return

    url = update.message.text
    mode = context.user_data.get("mode", "video")

    if "http" not in url:
        await update.message.reply_text("❌ Send a valid link")
        return

    await update.message.reply_text("⏳ Downloading...")

    try:
        download(url, mode)

        file = None
        for f in os.listdir():
            if f.startswith("media"):
                file = f

        if not file:
            await update.message.reply_text("❌ Failed")
            return

        await update.message.reply_text("📤 Uploading...")

        if mode == "audio":
            with open(file, "rb") as a:
                await update.message.reply_audio(a)
        else:
            with open(file, "rb") as v:
                await update.message.reply_video(v)

        os.remove(file)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# =========================
# ADMIN COMMANDS
# =========================
async def maintenance_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE
    if not is_admin(update.message.from_user.id):
        return
    MAINTENANCE_MODE = True
    await update.message.reply_text("🛠 Maintenance ENABLED")

async def maintenance_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE
    if not is_admin(update.message.from_user.id):
        return
    MAINTENANCE_MODE = False
    await update.message.reply_text("✅ Maintenance DISABLED")

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return

    try:
        new_id = int(context.args[0])
        ADMINS.append(new_id)
        await update.message.reply_text(f"👑 Added admin: {new_id}")
    except:
        await update.message.reply_text("Usage: /addadmin <user_id>")

# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", maintenance_on))
    app.add_handler(CommandHandler("off", maintenance_off))
    app.add_handler(CommandHandler("addadmin", add_admin))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Mayor Tech PRO Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
