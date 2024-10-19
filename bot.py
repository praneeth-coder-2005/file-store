import os
import logging
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("8088260771:AAFzLrBqd51JkEIv4zP4Fww23PDDpo__onw")
BASE_URL = os.getenv("BASE_URL", "https://file-store.onrender.com")

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text("Welcome! Send me an MKV file, and I'll give you a link to access it.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded MKV files."""
    if update.message.document.mime_type == 'video/x-matroska':
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"files/{update.message.document.file_name}"
        
        os.makedirs("files", exist_ok=True)
        await file.download(file_path)

        # Create a shareable link
        file_link = f"{BASE_URL}/file/{update.message.document.file_name}"
        await update.message.reply_text(f"Here is your link: {file_link}")
    else:
        await update.message.reply_text("Please send an MKV file.")

def main() -> None:
    """Start the bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    app.run_polling()

if __name__ == '__main__':
    main()
