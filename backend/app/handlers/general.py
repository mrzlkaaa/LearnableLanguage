
from aiogram.fsm.context import FSMContext
from typing import Any, Union
from aiogram.types import  CallbackQuery


async def handle_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    if callback.data == "back":
        history, history_data = await load_histiory(state)
        # callback_data = history_data[-1]
    else:
        callback_data = callback.data
        history, history_data = await update_history(state, callback_data)
        await state.update_data(
            history=history,
            history_data=history_data
        )

    return history, history_data

async def load_histiory(state: FSMContext):
    data = await state.get_data()
    history = data.get("history", [])
    history_data = data.get("history_data", [])
    
    return history, history_data

async def update_history(state: FSMContext, data: Any, method_str: Union[str, None]=None):
    current_state = await state.get_state()
    print("Current state is ", current_state)
    state_data = await state.get_data()
    
    history = state_data.get("history", [])
    history_data = state_data.get("history_data", [])
    
    if current_state:
        if len(history) > 0 and history[-1] == current_state:
            return history, history_data
        history.append(current_state)
        history_data.append(data)
    
    elif method_str:
        history.append(method_str)
        history_data.append(data)

    return history, history_data