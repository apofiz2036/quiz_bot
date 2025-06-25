import logging
from dotenv import load_dotenv
import os

from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

QUIZ_KEYBOARD = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счёт"]
    ]

def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(QUIZ_KEYBOARD, resize_keyboard=True)
    update.message.reply_text(
        "Привет! Я бот для викторин. Выбери действие:",
        reply_markup=reply_markup
    )


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def handle_buttons(update: Update, context: CallbackContext):
    text = update.message.text
    if text in ["Новый вопрос", "Сдаться", "Мой счёт"]:
        update.message.reply_text('Привет. Я бот для викторин')
    else:
        update.message.reply_text(update.message.text)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_buttons))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
