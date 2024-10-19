import os
import uuid  # For generating unique IDs
import logging
import sqlite3
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://your-app-name.onrender.com")  # Update with your Render URL

# Verify token
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize SQLite database
def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS links (id TEXT PRIMARY KEY, url TEXT)")
    conn.commit()
    conn.close()

def store_link(slug, url):
    """Store link in SQLite."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("INSERT INTO links (id, url) VALUES (?, ?)", (slug, url))
    conn.commit()
    conn.close()

# Initialize DB
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await update.message.reply_text("Send me a video link to store.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user-sent links."""
    link = update.message.text

    if not link.startswith("http"):
        await update.message.reply_text("Please send a valid link.")
        return

    # Generate a unique slug
    slug = str(uuid.uuid4())
    store_link(slug, link)

    # Generate the streaming/download link
    output_link = f"{BASE_URL}/link/{slug}"

    # Send the link to the user
    await update.message.reply_text(
        f"Your video link has been stored!\n\n"
        f"📺 Stream & Download: {output_link}\n\n"
        f"Click the link above to stream or download your file."
    )

def main():
    """Start the Telegram bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    app.run_polling()

if __name__ == '__main__':
    main()
