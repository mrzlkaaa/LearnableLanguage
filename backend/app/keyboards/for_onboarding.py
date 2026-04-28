from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_goal_menu():
    """Цель"""
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🥇 Подготовка к ЕГЭ / ОГЭ"), KeyboardButton(text="😎 Хочу получить языковой сертификат")],
        [KeyboardButton(text="📚 Саморазвитие"), KeyboardButton(text="В главное меню")]
    ], resize_keyboard=True)
    return kb

def get_active_time_menu():
    """Время активности"""
    kb = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="Утренние часы: с 08:00 до 12:00"), 
            KeyboardButton(text="Дневное время: с 12:00 до 18:00")
        ],
        [
            KeyboardButton(text="Вечерние часы: с 18:00 до 22:00"), 
            KeyboardButton(text="😎 Могу весь день: с 08:00 до 22:00")
        ]
    ], resize_keyboard=True)
    return kb

def get_placement_test_kb(options: list[str]):
    """Динамические кнопки для теста (варианты ответов)"""
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options):
        # callback_data="ans:0", "ans:1" ...
        builder.button(text=opt, callback_data=f"pt_ans:{i}")
    builder.adjust(2) # По 2 кнопки в ряд
    return builder.as_markup()