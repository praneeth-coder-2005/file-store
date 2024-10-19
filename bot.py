import os
import uuid  # For generating unique IDs
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://your-app-name.onrender.com")  # Update this URL

# Verify the token is loaded correctly
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize SQLite database
def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS links (id TEXT PRIMARY KEY, url TEXT)")
    conn.commit()
    conn.close()

def store_link(slug, link):
    """Store a link with a slug in the SQLite database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("INSERT INTO links (id, url) VALUES (?, ?)", (slug, link))
    conn.commit()
    conn.close()

# Initialize the database at startup
init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command to store a link."""
    await update.message.reply_text("Please send the link to store.")

async def store_and_generate_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store the link and generate a custom streaming/download link."""
    link = update.message.text

    if not link.startswith("http"):
        await update.message.reply_text("Please send a valid link.")
        return

    # Generate a unique slug
    slug = str(uuid.uuid4())
    store_link(slug, link)

    # Create the streaming/download URL
    output_link = f"{BASE_URL}/link/{slug}"
    logging.info(f"Generated link: {output_link}")  # Debugging

    # Send the generated link to the user
    await update.message.reply_text(
        f"Your link has been stored!\n\n"
        f"📺 Stream & Download: {output_link}\n\n"
        f"Click the link to stream or download your file."
    )

def main():
    """Start the Telegram bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, store_and_generate_link))
    
    app.run_polling()

if __name__ == '__main__':
    main()
