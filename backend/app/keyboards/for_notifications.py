from aiogram.filters.callback_data import CallbackData
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NotificationAction(CallbackData, prefix="notif"):
    action: str  # Например: "start_new_words", "start_review"


def notify_new_words():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 К новым словам!",
        callback_data=NotificationAction(action="start_new_words")
    )
    return builder.as_markup() 

def notify_review_words():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 К повторению!",
        callback_data=NotificationAction(action="start_review_words")
    )
    return builder.as_markup()

