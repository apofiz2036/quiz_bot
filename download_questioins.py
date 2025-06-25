with open("1vs1200.txt", "r", encoding="KOI8-R") as file:
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

print(question_answer)