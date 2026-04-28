from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.handlers.user_main import (
    learning_main,
    cmd_start
)
from app.handlers.user.words_learning import words_learning_menu


router = Router(name="general")

@router.callback_query(F.data == "back")
async def back_inline(callback: CallbackQuery, state: FSMContext, **kwargs):
        
    data = await state.get_data()
    history = data.get("history", [])
    history_data = data.get("history_data", [])
    print(history, history_data)
    try:
        history.pop()
        history_data.pop()
        last_hanlder_name = history[-1]
        last_hanlder_data = history_data[-1]
        print(last_hanlder_name, last_hanlder_data)
    except IndexError:
        await cmd_start(callback.message, state, **kwargs)
        return 
    
    # callback.data = last_hanlder_data

    last_hanlder = SCREENS.get(last_hanlder_name, None)
    await last_hanlder(callback, state, **kwargs)
    

@router.callback_query(F.data == "menu")
async def main_menu(callback: CallbackQuery, state: FSMContext, **kwargs):
    await cmd_start(callback.message, state, **kwargs)


SCREENS = {
    "learning_main": learning_main,
    "LearningStates:learning": words_learning_menu
    # "LearningStates:learning": words_learning_menu
}