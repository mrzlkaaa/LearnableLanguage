from enum import Enum

class NotificationType(str, Enum):
    HELLO_WORDS = "hello_words"
    GENTLE_REMINDER = "gentle_reminder"
    WEEKLY_REPORT = "weekly_report"

TEMPLATES = {
    NotificationType.HELLO_WORDS: (
        "☀️ <b>Привет! Твои новые слова на сегодня:</b>\n\n"
        "{words_list}\n\n"
        "Скоро тут будет клавиатурная навигация..."
        # "<i>Нажми на кнопку ниже, чтобы начать тренировку!</i> 👇"
    ),
    
    NotificationType.GENTLE_REMINDER: (
        "🌙 <b>Не забудь про повторение!</b>\n"
        "У тебя накопилось <b>{count}</b> слов для проверки.\n"
        "Потрать всего 2 минуты, чтобы не забыть их."
        "Скоро тут будет клавиатурная навигация..."
    ),
    
    NotificationType.WEEKLY_REPORT: (
        "📊 <b>Твой прогресс за неделю:</b>\n"
        "✅ Выучено слов: {learned}\n"
        "🔥 Лучшая серия: {streak} дней"
    )
}