from aiogram.fsm.state import State, StatesGroup

class OnboardingStates(StatesGroup):
    """Цепочка регистрации"""
    waiting_for_goal = State()       # Цель (ЕГЭ, Разговорный, Работа)
    waiting_for_words_per_day = State()      # Сколько слов в день
    waiting_for_reminder_frequency = State() # Как часто напоминать
    waiting_for_active_hours = State()       # Активные часы
    waiting_for_topics = State()             # Интересы/темы
    placement_test = State()         # Прохождение теста (цикл вопросов)

class LearningStates(StatesGroup):
    """Цикл обучения"""
    learning = State()
    vocabulary = State()    # Ждем ответ (войс/текст) на слово
    reading_quiz = State()           # Ждем ответ на тест по тексту