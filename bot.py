import os
import uuid  # For generating unique IDs
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://your-app-name.onrender.com")  # Update with your Render URL

# In-memory storage for user-submitted links
stored_links = {}

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define states for conversation handler
ASK_MODE, COLLECT_BATCH = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot and ask if the user wants single or batch mode."""
    keyboard = [[KeyboardButton("Single Link"), KeyboardButton("Batch Mode")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Do you want to store a single link or use batch mode?", reply_markup=reply_markup)
    return ASK_MODE

async def ask_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's choice of mode."""
    chat_id = update.message.chat_id
    context.user_data["links"] = []  # Initialize list to store user links

    if update.message.text == "Single Link":
        await update.message.reply_text("Okay, please send the link.")
        return ConversationHandler.END  # End conversation for single link

    elif update.message.text == "Batch Mode":
        await update.message.reply_text("Batch mode activated. Send your links one by one. Type 'done' when finished.")
        return COLLECT_BATCH

async def handle_single_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle single link submission."""
    link = update.message.text

    # Validate the link
    if not link.startswith("http"):
        await update.message.reply_text("Please send a valid link.")
        return

    # Generate a unique ID and store the link
    unique_id = str(uuid.uuid4())
    stored_links[unique_id] = [link]

    # Provide the user with a unique output link
    output_link = f"{BASE_URL}/link/{unique_id}"
    await update.message.reply_text(f"Your link is stored! Access it here: {output_link}")

async def handle_batch_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect links in batch mode."""
    if update.message.text.lower() == 'done':
        # Generate a unique ID and store the batch of links
        unique_id = str(uuid.uuid4())
        stored_links[unique_id] = context.user_data["links"]

        # Provide the user with a unique output link
        output_link = f"{BASE_URL}/link/{unique_id}"
        await update.message.reply_text(f"Your batch links are stored! Access them here: {output_link}")

        return ConversationHandler.END

    elif update.message.text.startswith("http"):
        # Store the valid link in the user's session data
        context.user_data["links"].append(update.message.text)
        await update.message.reply_text("Link added. Send more or type 'done' when finished.")
    else:
        await update.message.reply_text("Please send a valid link or type 'done'.")

def main() -> None:
    """Run the bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation handler for mode selection and link collection
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
