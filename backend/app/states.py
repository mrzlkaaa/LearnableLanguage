from aiogram.fsm.state import State, StatesGroup

class OnboardingStates(StatesGroup):
    """Цепочка регистрации"""
    waiting_for_goal = State()       # Цель (ЕГЭ, Разговорный, Работа)
    waiting_for_schedule = State()   # Когда удобно заниматься?
    placement_test = State()         # Прохождение теста (цикл вопросов)

class LearningStates(StatesGroup):
    """Цикл обучения"""
    learning = State()
    vocabulary = State()    # Ждем ответ (войс/текст) на слово
    reading_quiz = State()           # Ждем ответ на тест по тексту