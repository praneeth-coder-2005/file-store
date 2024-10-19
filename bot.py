import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("8088260771:AAFzLrBqd51JkEIv4zP4Fww23PDDpo__onw")
BASE_URL = os.getenv("BASE_URL", "https://file-store.onrender.com")

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define states for the conversation handler
ASK_MODE, COLLECT_BATCH = range(2)

# To store batch files temporarily
user_files = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot and ask if single or batch mode is needed."""
    keyboard = [[KeyboardButton("Single File"), KeyboardButton("Batch Mode")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Do you want a single file link or batch mode?", reply_markup=reply_markup)
    return ASK_MODE

async def ask_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's choice of mode."""
    choice = update.message.text

    if choice == "Single File":
        await update.message.reply_text("Okay, please send the file.")
        return ConversationHandler.END  # Move to normal file handling

    elif choice == "Batch Mode":
        user_files[update.message.chat_id] = []  # Initialize batch for this user
        await update.message.reply_text("Batch mode activated. Send your files one by one. Type 'done' when finished.")
        return COLLECT_BATCH

async def handle_single_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle single file upload."""
    if update.message.document.mime_type == 'video/x-matroska':
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"files/{update.message.document.file_name}"

        os.makedirs("files", exist_ok=True)
        await file.download(file_path)

        # Generate the link
        file_link = f"{BASE_URL}/file/{update.message.document.file_name}"
        await update.message.reply_text(f"Here is your link: {file_link}")

    else:
        await update.message.reply_text("Please send an MKV file.")

async def handle_batch_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect files for batch mode."""
    if update.message.text and update.message.text.lower() == 'done':
        # Generate a batch link when user finishes
        chat_id = update.message.chat_id
        files = user_files.get(chat_id, [])

        if files:
            # Create a batch link containing all files
            file_links = [f"{BASE_URL}/file/{file_name}" for file_name in files]
            batch_link = "\n".join(file_links)
            await update.message.reply_text(f"Here are your batch files:\n{batch_link}")
        else:
            await update.message.reply_text("No files were uploaded.")

        # Clear user's batch files
        user_files.pop(chat_id, None)
        return ConversationHandler.END

    elif update.message.document and update.message.document.mime_type == 'video/x-matroska':
        chat_id = update.message.chat_id
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"files/{update.message.document.file_name}"

        os.makedirs("files", exist_ok=True)
        await file.download(file_path)

        # Store the file name in the user's batch
        user_files[chat_id].append(update.message.document.file_name)
        await update.message.reply_text("File added to batch. Send more or type 'done' when finished.")

    else:
        await update.message.reply_text("Please send only MKV files or type 'done'.")

def main() -> None:
    """Run the bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Setup conversation handler for choosing mode and batch collection
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mode)],
            COLLECT_BATCH: [MessageHandler(filters.ALL & ~filters.COMMAND, handle_batch_file)],
        },
        fallbacks=[],
    )

    # Add handlers to the app
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_single_file))  # For single file uploads

    app.run_polling()

if __name__ == '__main__':
    main()
