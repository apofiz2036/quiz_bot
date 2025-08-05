import logging
import random
from pathlib import Path

logger = logging.getLogger(__name__)


def load_questions(questions_path="questions.txt"):
    questions = {}
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
                questions[current_question] = answer
                current_question = None
        return questions
    except Exception as e:
        logger.error(f"Ошибка загрузки вопросов: {e}")
        return None


def get_random_question(questions):
    if not questions:
        return None, None
    return random.choice(list(questions.items()))