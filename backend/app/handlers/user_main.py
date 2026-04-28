from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Union

from app.states import LearningStates
from app.database.repo.user import UserRepo
from app.handlers.general import update_history, load_histiory


from app.keyboards.for_main import (
    get_all_learnings
)

# from app.database.repo.user import UserRepo

def get_main_menu():
    """Главное меню (внизу экрана)"""
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔥 Обучение"), KeyboardButton(text="📚 Рассылка")],
        [KeyboardButton(text="📎 Анкетирование"), KeyboardButton(text="⚙️ Настройки")]
    ], resize_keyboard=True, one_time_keyboard=True)
    return kb

# Инициализируем роутер уровня модуля
router = Router(name="user_router")


@router.message(F.text == "🔥 Обучение") #* no state here
async def learning_main(event: Union[Message, CallbackQuery] , state: FSMContext, **kwargs):
    if isinstance(event, CallbackQuery):
        # history, history_data = await load_histiory(state)
        await state.set_state(LearningStates.learning)
        await event.message.edit_text(
            "Отличное решение!\nВыбери желаемую секцию и начинаем!",
            reply_markup=get_all_learnings()
        )
        return
        
    history, history_data = await update_history(state, event.text, "learning_main") #! callback_data may be provided from 'back' callback func
    await state.update_data(
        history=history,
        history_data=history_data
    )

    await state.set_state(LearningStates.learning)
    await event.answer(
        "Отличное решение!\nВыбери желаемую секцию и начинаем!",
        reply_markup=get_all_learnings()
    )

@router.message(CommandStart())
async def cmd_start(event: Message, state: FSMContext, **kwargs):
    await state.clear()
    user_repo = kwargs["user_repo"]
    # Проверяем, есть ли юзер в базе и добавляем
    user = await user_repo.get_or_create(event.from_user.id, event.from_user.username, event.from_user.full_name)
    print(user.level)
    
    if user.level != "None":
        await event.answer(f"Йо, {user.full_name}  👋 С возвращением!.", reply_markup=get_main_menu())
        return

    # Если новый - другой велком
    await event.answer(
        "Йо! Я Бот, который поможет тебе учить язык по-новому. Но для начала нужно настроться.\n\n"
        "Переходи в <b> Анкетирование </b> и начнем работу!",
        reply_markup=get_main_menu()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Я Bot. Я помогу тебе с изучением английского языка!.")