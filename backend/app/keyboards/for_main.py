from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.keyboards.for_base_navigation import back_inline


def get_all_learnings():
    builder = InlineKeyboardBuilder()
    
    words = types.InlineKeyboardButton(
        text="Учим слова",
        callback_data="vocabulary"
    )
    reading = types.InlineKeyboardButton(
        text="Чтение",
        callback_data="0"
    )
    speaking = types.InlineKeyboardButton(
        text="Говорение",
        callback_data="1"
    )
    audio = types.InlineKeyboardButton(
        text="Аудирование",
        callback_data="2"
    )
    writing = types.InlineKeyboardButton(
        text="Письмо",
        callback_data="3"
    )

    builder.add(
        words,
        reading,
        speaking,
        audio,
        writing,
        back_inline
    )
    builder.adjust(2)
    
    return builder.as_markup()