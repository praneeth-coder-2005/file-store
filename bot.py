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

# Verify that the token is loaded correctly
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

def store_link(unique_id, link):
    """Store a link in the SQLite database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("INSERT INTO links (id, url) VALUES (?, ?)", (unique_id, link))
    conn.commit()
    conn.close()

# Initialize the database at startup
init_db()

# Define states for conversation handler
ASK_MODE, COLLECT_BATCH = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask user if they want to store a single link or a batch."""
    keyboard = [[KeyboardButton("Single Link"), KeyboardButton("Batch Mode")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Do you want to store a single link or batch mode?", reply_markup=reply_markup)
    return ASK_MODE

async def ask_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user mode selection."""
    if update.message.text == "Single Link":
        await update.message.reply_text("Please send the link.")
        return ConversationHandler.END

    elif update.message.text == "Batch Mode":
        context.user_data["links"] = []  # Initialize batch storage
        await update.message.reply_text("Batch mode activated. Send links one by one. Type 'done' when finished.")
        return COLLECT_BATCH

async def handle_single_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a single link."""
    link = update.message.text

    if not link.startswith("http"):
        await update.message.reply_text("Please send a valid link.")
        return

    unique_id = str(uuid.uuid4())
    store_link(unique_id, link)

    await update.message.reply_text(f"Your link is stored with ID: {unique_id}")

async def handle_batch_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle batch link submissions."""
    if update.message.text.lower() == 'done':
        unique_id = str(uuid.uuid4())

        # Store all links in the batch under the same ID
        for link in context.user_data["links"]:
            store_link(unique_id, link)

        await update.message.reply_text(f"Batch stored with ID: {unique_id}")
        return ConversationHandler.END

    elif update.message.text.startswith("http"):
        context.user_data["links"].append(update.message.text)
        await update.message.reply_text("Link added. Send more or type 'done' to finish.")

    else:
        await update.message.reply_text("Please send a valid link or type 'done'.")

def main():
    """Start the Telegram bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mode)],
            COLLECT_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_batch_link)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_single_link))
    app.run_polling()

if __name__ == '__main__':
    main()
