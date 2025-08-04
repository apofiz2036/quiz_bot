import logging
import random
from pathlib import Path

logger = logging.getLogger(__name__)

QUESTIONS = {}


def load_questions(questions_path="questions.txt"):
    global QUESTIONS
    try:
        path = Path(questions_path)

        if not path.exists():
            logger.error(f"Файл с вопросами не найден: {path}")
            return False

        with open(path, "r", encoding="KOI8-R") as file:
            text = file.read().split('\n\n')

        current_question = None

        for block in text:
            if block.startswith('Вопрос '):
                current_question = block.split(':', 1)[1].strip()
            elif block.startswith('Ответ:') and current_question:
                answer = block.split(':', 1)[1].strip()
                QUESTIONS[current_question] = answer
                current_question = None
        return True
    except Exception as e:
        logger.error(f"Ошибка загрузки вопросов: {e}")
        return False


def get_random_question():
    return random.choice(list(QUESTIONS.items()))
