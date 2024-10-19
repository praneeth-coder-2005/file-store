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
BASE_URL = os.getenv("BASE_URL", "https://your-app-name.onrender.com")  # Update with your Render URL

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# SQLite database setup
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

# Initialize the database
init_db()

# Define states for the conversation handler
ASK_MODE, COLLECT_BATCH = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user if they want to store a single link or use batch mode."""
    keyboard = [[KeyboardButton("Single Link"), KeyboardButton("Batch Mode")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Do you want to store a single link or use batch mode?", reply_markup=reply_markup)
    return ASK_MODE

async def ask_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the user's choice."""
    if update.message.text == "Single Link":
        await update.message.reply_text("Okay, please send the link.")
        return ConversationHandler.END  # Normal link handling will proceed

    elif update.message.text == "Batch Mode":
        context.user_data["links"] = []  # Store batch links in the session
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

    output_link = f"{BASE_URL}/link/{unique_id}
    # Provide the user with the unique output link
    output_link = f"{BASE_URL}/link/{unique_id}"
    await update.message.reply_text(f"Your link is stored! Access it here: {output_link}")

async def handle_batch_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle links in batch mode."""
    if update.message.text.lower() == 'done':
        # Generate a unique ID for the batch of links
        unique_id = str(uuid.uuid4())

        # Store each link in the SQLite database
        for link in context.user_data["links"]:
            store_link(unique_id, link)

        # Provide the user with a unique output link for the batch
        output_link = f"{BASE_URL}/link/{unique_id}"
        await update.message.reply_text(f"Your batch links are stored! Access them here: {output_link}")

        return ConversationHandler.END

    elif update.message.text.startswith("http"):
        # Add the valid link to the user's session data
        context.user_data["links"].append(update.message.text)
        await update.message.reply_text("Link added. Send more or type 'done' when finished.")

    else:
        await update.message.reply_text("Please send a valid link or type 'done'.")

def main() -> None:
    """Run the Telegram bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Define the conversation handler for mode selection and link collection
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mode)],
            COLLECT_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_batch_link)],
        },
        fallbacks=[],
    )

    # Add handlers to the application
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_single_link))  # Handle single links

    app.run_polling()

if __name__ == '__main__':
    main()
