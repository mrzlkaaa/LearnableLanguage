from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state  # <--- Ключевая вещь!
from aiogram.filters import StateFilter


from app.states import LearningStates
from app.keyboards.for_notifications import NotificationAction
from app.handlers.user.words_learning import words_learning_menu

router = Router()

@router.callback_query(
    StateFilter(any_state), #* Ловим В ЛЮБОМ стейте (даже если стейта нет)
    NotificationAction.filter(F.action.in_(["start_new_words", "start_review_words"])),
)
async def handle_notification_words(
    callback: CallbackQuery,
    state: FSMContext,
    **kwargs
):
    
    
    await callback.message.edit_text("🔄 Уже подготавливаем слова и карточки...")
    # 1. ОБЯЗАТЕЛЬНО: Сбрасываем текущий стейт юзера!
    # Если он в этот момент добавлял слово и не закончил — его процесс прервется.
    # Это нормальное поведение (User Interruption), так как он САМ нажал кнопку тренировки.
    await state.clear()

    # 2. Устанавливаем нужный стейт для изучения (если он требуется твоей логикой)
    await state.set_state(LearningStates.learning)
    await words_learning_menu(callback, state, **kwargs)
