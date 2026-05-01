from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_goal_menu():
    """Цель изучения языка"""
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🥇 Подготовка к ЕГЭ / ОГЭ"), KeyboardButton(text="😎 Языковой сертификат")],
        [KeyboardButton(text="📚 Саморазвитие"), KeyboardButton(text="💼 Работа / Бизнес")],
        [KeyboardButton(text="✈️ Путешествия"), KeyboardButton(text="В главное меню")]
    ], resize_keyboard=True)
    return kb


def get_words_per_day_menu():
    """Сколько слов в день"""
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="3 слова")],
        [KeyboardButton(text="5 слов")],
        [KeyboardButton(text="10 слов")],
        [KeyboardButton(text="🔙 Назад")]
    ], resize_keyboard=True)
    return kb


def get_reminder_frequency_menu():
    """Как часто напоминать"""
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="1 раз в день")],
        [KeyboardButton(text="2 раза в день")],
        [KeyboardButton(text="3 раза в день")],
        [KeyboardButton(text="🔙 Назад")]
    ], resize_keyboard=True)
    return kb


def get_active_hours_menu():
    """Активные часы"""
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🌅 Утро: с 08:00 до 12:00")],
        [KeyboardButton(text="☀️ День: с 12:00 до 18:00")],
        [KeyboardButton(text="🌙 Вечер: с 18:00 до 22:00")],
        [KeyboardButton(text="😎 Весь день: с 08:00 до 22:00")],
        [KeyboardButton(text="🔙 Назад")]
    ], resize_keyboard=True)
    return kb


def get_topics_menu():
    """Интересы/темы"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☑️ Technology", callback_data="topic_tech")],
        [InlineKeyboardButton(text="☑️ Business", callback_data="topic_business")],
        [InlineKeyboardButton(text="☑️ Travel", callback_data="topic_travel")],
        [InlineKeyboardButton(text="☑️ Health", callback_data="topic_health")],
        [InlineKeyboardButton(text="☑️ Entertainment", callback_data="topic_entertainment")],
        [InlineKeyboardButton(text="✅ Готово", callback_data="topics_done")]
    ])
    return kb


def get_placement_test_kb(options: list[str]):
    """Динамические кнопки для теста (варианты ответов)"""
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        builder.button(text=opt, callback_data=f"pt_ans:{i}")
    builder.adjust(2)
    return builder.as_markup()
