import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define states for conversation handler
ASK_MODE, COLLECT_BATCH = range(2)

# Store batch links in memory (in a dictionary keyed by user chat ID)
user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot and ask if the user wants single or batch mode."""
    keyboard = [[KeyboardButton("Single Link"), KeyboardButton("Batch Mode")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Do you want to store a single link or use batch mode?", reply_markup=reply_markup)
    return ASK_MODE

async def ask_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's choice of mode."""
    choice = update.message.text

    if choice == "Single Link":
        await update.message.reply_text("Okay, please send the link.")
        return ConversationHandler.END  # Ends conversation, normal link handling will proceed

    elif choice == "Batch Mode":
        user_links[update.message.chat_id] = []  # Initialize a list for storing links
        await update.message.reply_text("Batch mode activated. Send your links one by one. Type 'done' when finished.")
        return COLLECT_BATCH

async def handle_single_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle single link submission."""
    link = update.message.text

    # Validate the link (basic validation, can be extended)
    if not link.startswith("http"):
        await update.message.reply_text("Please send a valid link.")
        return

    # Send confirmation to the user
    await update.message.reply_text(f"Your link is stored: {link}")

async def handle_batch_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect multiple links for batch mode."""
    if update.message.text and update.message.text.lower() == 'done':
        # Generate and send the batch of links when the user is finished
        chat_id = update.message.chat_id
        links = user_links.get(chat_id, [])

        if links:
            batch_links = "\n".join(links)
            await update.message.reply_text(f"Here are your batch links:\n{batch_links}")
        else:
            await update.message.reply_text("No links were added.")

        # Clear the stored links for the user
        user_links.pop(chat_id, None)
        return ConversationHandler.END

    elif update.message.text.startswith("http"):
        # Store the valid link in the user's batch
        chat_id = update.message.chat_id
        user_links[chat_id].append(update.message.text)
        await update.message.reply_text("Link added to batch. Send more or type 'done' when finished.")

    else:
        await update.message.reply_text("Please send a valid link or type 'done'.")

def main() -> None:
    """Run the bot."""
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Setup conversation handler for mode selection and link collection
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mode)],
            COLLECT_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_batch_link)],
        },
        fallbacks=[]
    )

    # Add handlers to the application
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_single_link))  # For single links

    app.run_polling()

if __name__ == '__main__':
    main()
