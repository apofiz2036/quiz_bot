import logging
from dotenv import load_dotenv
import os
import random
from typing import Dict
import redis

from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


QUIZ_KEYBOARD = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счёт"]
    ]


def load_questions(file_path):
    with open(file_path, "r", encoding="KOI8-R") as file:
        text = file.read().split('\n\n')

    question_answer = {}
    current_question = None

    for block in text:
        if block.startswith('Вопрос '):
            current_question = block.split(':', 1)[1].strip()
        elif block.startswith('Ответ:') and current_question:
            answer = block.split(':', 1)[1].strip()
            question_answer[current_question] = answer
            current_question = None

    return question_answer

def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(QUIZ_KEYBOARD, resize_keyboard=True)
    update.message.reply_text(
        "Привет! Я бот для викторин. Выбери действие:",
        reply_markup=reply_markup
    )


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def handle_buttons(update: Update, context: CallbackContext):
    r = context.bot_data['redis']
    user_id = update.message.from_user.id
    text = update.message.text
    if text == "Новый вопрос":
        question_answer = random.choice(list(load_questions("1vs1200.txt").items())) #  Это заглушка, пока что
        question = question_answer[0]
        answer = question_answer[1]

        r.set(f"user:{user_id}:question", question)

        context.user_data['current_question'] = question
        context.user_data['current_answer'] = answer
        update.message.reply_text(question)
    elif text == "Сдаться":
        if 'current_question' in context.user_data:
            answer = context.user_data['current_answer']
            update.message.reply_text(answer)
        else:
            update.message.reply_text("Сначала задайте вопрос!")
    elif text == "Мой счёт":
        update.message.reply_text("Ваш счёт: 0 очков")
    else:
        update.message.reply_text(update.message.text)


def main():
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    redis_conn = redis.Redis(
        host=os.getenv('REDIS_ADDRESS'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        db=0,
        decode_responses=True
    )

    try:
        redis_conn.ping()
        print("✅ Подключение к Redis работает!")
    except Exception as e:
        print(f"❌ Ошибка подключения к Redis: {e}")
        return

    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['redis'] = redis_conn

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_buttons))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
