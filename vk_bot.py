import random
import os

from dotenv import load_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
import redis


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


def handle_new_question(event, vk_api, redis_conn):
    questions = load_questions("questions.txt")
    question, answer = random.choice(list(questions.items()))

    redis_conn.set(f"user:{event.user_id}:question", question)
    redis_conn.set(f"user:{event.user_id}:answer", answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=get_keyboard()
    )


def handle_give_up(event, vk_api, redis_conn):
    answer = redis_conn.get(f"user:{event.user_id}:answer")
    vk_api.messages.send(
            user_id=event.user_id,
            message=f"Правильный ответ: {answer}",
            random_id=random.randint(1, 1000),
            keyboard=get_keyboard()
        )


def handle_solution_attempt(event, vk_api, redis_conn):
    user_answer = event.text
    correct_answer = redis_conn.get(f"user:{event.user_id}:answer") or ""
    correct_answer = correct_answer.lower().replace('"', '')

    if user_answer.lower().strip() in correct_answer:
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»."
    else:
        message = "Неправильно… Попробуешь ещё раз?"

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000),
        keyboard=get_keyboard()
    )


def handle_my_score(event, vk_api):
    vk_api.messages.send(
            user_id=event.user_id,
            message="Вы нажали «Мой счёт»",
            random_id=random.randint(1, 1000),
            keyboard=get_keyboard()
        )


def get_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос")
    keyboard.add_button("Сдаться")
    keyboard.add_line()
    keyboard.add_button("Мой счёт")

    return keyboard.get_keyboard()


def handle_message(event, vk_api, redis_conn):
    if event.text == "Новый вопрос":
        handle_new_question(event, vk_api, redis_conn)
    elif event.text == "Сдаться":
        handle_give_up(event, vk_api, redis_conn)
    elif event.text == "Мой счёт":
        handle_my_score(event, vk_api)
    else:
        if redis_conn.get(f"user:{event.user_id}:question"):
            handle_solution_attempt(event, vk_api, redis_conn)
        else:
            vk_api.messages.send(
                user_id=event.user_id,
                message="Привет! Я бот для викторин. Выбери действие:",
                random_id=random.randint(1, 1000),
                keyboard=get_keyboard()
            )


def main():
    load_dotenv()

    redis_conn = redis.Redis(
        host=os.getenv('REDIS_ADDRESS'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        db=0,
        decode_responses=True
    )
    try:
        redis_conn.ping()
        print("Подключение к Redis работает!")
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")
        return

    VK_TOKEN = os.getenv('VK_TOKEN')
    vk_session = vk.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk_api, redis_conn)


if __name__ == "__main__":
    main()
