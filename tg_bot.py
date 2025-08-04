import logging
from dotenv import load_dotenv
import os
import random
from typing import Dict
import redis

from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

logger = logging.getLogger(__name__)

QUIZ_KEYBOARD = [
    ["Новый вопрос", "Сдаться"],
    ["Мой счёт"]
]

NEW_QUESTION, WAITING_FOR_ANSWER = range(2)


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
    return NEW_QUESTION


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def handle_new_question_request(update: Update, context: CallbackContext):
    redis_conn = context.bot_data['redis']
    user_id = update.message.from_user.id
    question_answer = random.choice(list(load_questions("questions.txt").items()))
    question = question_answer[0]
    answer = question_answer[1]

    redis_conn.set(f"user:{user_id}:question", question)
    context.user_data['current_answer'] = answer
    update.message.reply_text(question)

    return WAITING_FOR_ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext):
    user_answer = update.message.text
    correct_answer = context.user_data.get('current_answer', '').lower().replace('"', '')
    user_answer_cleaned = user_answer.lower().strip()
    if user_answer_cleaned in correct_answer:
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос».")
        return NEW_QUESTION
    else:
        update.message.reply_text("Неправильно… Попробуешь ещё раз?")
        return WAITING_FOR_ANSWER


def handle_give_up(update: Update, context: CallbackContext):
    answer = context.user_data.get('current_answer')
    update.message.reply_text(f"Правильный ответ: '{answer}'")
    return NEW_QUESTION


def main():
    load_dotenv()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    telegram_token = os.environ('TELEGRAM_TOKEN')
    redis_conn = redis.Redis(
        host=os.environ('REDIS_ADDRESS'),
        port=os.environ('REDIS_PORT'),
        password=os.environ('REDIS_PASSWORD'),
        db=0,
        decode_responses=True
    )

    try:
        redis_conn.ping()
        print("Подключение к Redis работает!")
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")
        return

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['redis'] = redis_conn

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NEW_QUESTION: [
                MessageHandler(Filters.regex("^Новый вопрос$"), handle_new_question_request),
            ],
            WAITING_FOR_ANSWER: [
                MessageHandler(Filters.regex("^Сдаться$"), handle_give_up),
                MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt),
            ]
        },
        fallbacks=[CommandHandler("help", help_command)]
    ))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
