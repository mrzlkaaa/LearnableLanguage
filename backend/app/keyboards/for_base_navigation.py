from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


back_inline = types.InlineKeyboardButton(
    text="Назад",
    callback_data="back"
)

main_menu_inline = types.InlineKeyboardButton(
    text="Главное меню",
    callback_data="menu"
)

def get_back_inline():
    builder = InlineKeyboardBuilder()
    
    builder.add(
        back_inline
    )
    
    return builder.as_markup()

def get_main_menu_inline():
    builder = InlineKeyboardBuilder()
    
    builder.add(
        main_menu_inline
    )
    
    return builder.as_markup()