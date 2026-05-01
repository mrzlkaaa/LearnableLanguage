from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.states import OnboardingStates
from app.keyboards.for_onboarding import get_placement_test_kb, get_goal_menu, get_active_time_menu
from app.handlers.user_main import get_main_menu
# Импортируем репозитории (предполагаем, что они прокинуты через Middleware из Блока 2)
# from app.database.repo ...

router = Router(name="onboarding")

# 1.sTART
@router.message(F.text == "📎 Анкетирование")
async def process_goal(message: Message, state: FSMContext):
