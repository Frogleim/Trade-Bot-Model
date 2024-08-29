from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update

# Replace 'your_api_key_here' with your actual NewsAPI key
api_key = 'f5fe5390fbb64c64883b26acdcadc8dc'
base_url = 'https://newsapi.org/v2/everything'

# Replace 'your_telegram_token_here' with your actual Telegram bot token
telegram_token = '7247839345:AAF1YTg3ZTio4n3vQlzgKCn0FexkpneHppI'


def start_bot(update: Update, context: CallbackContext):
    update.message.reply_text(f"Hello")


def main():
    updater = Updater(telegram_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_bot))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
