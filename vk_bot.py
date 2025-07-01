import random
import os

from dotenv import load_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard


def handle_new_question(event, vk_api):
    vk_api.messages.send(
            user_id=event.user_id,
            message="Вы нажали «Новый вопрос»",
            random_id=random.randint(1, 1000),
            keyboard=get_keyboard()
        )


def handle_give_up(event, vk_api):
    vk_api.messages.send(
            user_id=event.user_id,
            message="Вы нажали «Сдаться»",
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


def handle_message(event, vk_api):
    if event.text == "Новый вопрос":
        handle_new_question(event, vk_api)
    elif event.text == "Сдаться":
        handle_give_up(event, vk_api)
    elif event.text == "Мой счёт":
        handle_my_score(event, vk_api)
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message="Привет! Я бот для викторин. Выбери действие:",
            random_id=random.randint(1, 1000),
            keyboard=get_keyboard()
        )


def main():
    load_dotenv()
    VK_TOKEN = os.getenv('VK_TOKEN')
    vk_session = vk.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk_api)


if __name__ == "__main__":
    main()
