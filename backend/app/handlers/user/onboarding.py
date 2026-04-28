from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.states import OnboardingStates
from app.keyboards.for_onboarding import get_placement_test_kb, get_goal_menu, get_active_time_menu
# Импортируем репозитории (предполагаем, что они прокинуты через Middleware из Блока 2)
# from app.database.repo ...

router = Router(name="onboarding")

# 1.sTART
@router.message(F.text == "📎 Анкетирование")
async def process_goal(message: Message, state: FSMContext):
    await state.set_state(OnboardingStates.waiting_for_goal)
    
    await message.answer(
        "Анкета содержит только необходимую для продуктивной работы информацию\n"
        "🏆**Какая у тебя цель изучения языка?**\n",
        reply_markup=get_goal_menu()
    )

@router.message(OnboardingStates.waiting_for_goal)
async def process_goal(message: Message, state: FSMContext):
    
    await state.update_data(goal=message.text)
    
    await message.answer(
        "Принял. ⏰ **В какое время тебе удобно заниматься?**\n",
        reply_markup=get_active_time_menu()
    )
    await state.set_state(OnboardingStates.waiting_for_schedule)

# 3. СОХРАНЕНИЕ ВРЕМЕНИ -> ЗАПУСК ТЕСТА
@router.message(OnboardingStates.waiting_for_schedule)
async def start_placement_test(message: Message, state: FSMContext, user_repo):
    await state.update_data(active_time=message.text)
    # Сохраняем настройки в БД (создаем юзера с дефолтным уровнем A1 пока что)
    # data = await state.get_data()
    # await user_repo.create_user(..., settings={"goal": data['goal'], "time": message.text})
    
    await message.answer(
        "Окей, профиль создан! 🚀\n\n"
        "Теперь давай определим твой уровень. "
        "Ответь на пару вопросов, только честно, не гугли!."
    )
    
    # # Инициализируем тест (в реале берем вопросы из БД PlacementQuestion)
    # # Для примера хардкод:
    # test_questions = [
    #     {"q": "I ___ to school yesterday.", "opts": ["go", "went", "gone"], "correct": 1, "level": "A1"},
    #     {"q": "If I ___ rich, I would buy a car.", "opts": ["was", "were", "am"], "correct": 1, "level": "B1"},
    #     # ... еще вопросы
    # ]
    
    # # Сохраняем вопросы и текущий индекс в FSM
    # await state.update_data(test_data=test_questions, current_q=0, score=0)
    
    # # Показываем первый вопрос
    # await send_question(message, test_questions[0])
    # await state.set_state(OnboardingStates.placement_test)

# Вспомогательная функция отправки вопроса
async def send_question(message: Message, question_data: dict):
    kb = get_placement_test_kb(question_data['opts'])
    await message.answer(f"❓ **Level Check**\n\n{question_data['q']}", reply_markup=kb)

# 4. ОБРАБОТКА ОТВЕТОВ ТЕСТА
@router.callback_query(OnboardingStates.placement_test, F.data.startswith("pt_ans:"))
async def process_test_answer(callback: CallbackQuery, state: FSMContext, user_repo):
    # Парсим ответ
    selected_index = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    questions = data['test_data']
    current_idx = data['current_q']
    current_score = data['score']
    
    # Проверка ответа
    correct_index = questions[current_idx]['correct']
    if selected_index == correct_index:
        current_score += 1
        # Можно давать фидбек, но на тесте уровня лучше молчать или просто "Accepted"
        await callback.answer("Accepted!")
    else:
        await callback.answer("Accepted!")

    # Следующий вопрос или конец?
    next_idx = current_idx + 1
    
    if next_idx < len(questions):
        # Следующий вопрос
        await state.update_data(current_q=next_idx, score=current_score)
        # Удаляем старый (красота интерфейса)
        await callback.message.delete()
        await send_question(callback.message, questions[next_idx])
    else:
        # КОНЕЦ ТЕСТА
        final_level = calculate_level(current_score, len(questions))
        
        # Обновляем уровень в БД
        # await user_repo.update_level(callback.from_user.id, final_level)
        
        await callback.message.delete()
        await callback.message.answer(
            f"🎉 Тест завершен!\n\n"
            f"Твой примерный уровень: **{final_level}**\n"
            f"Я подстроил программу под тебя. Погнали!",
            reply_markup=get_main_menu()
        )
        await state.clear()

def calculate_level(score, total):
    """Простая логика расчета (можно усложнить)"""
    percentage = score / total
    if percentage < 0.3: return "A1"
    if percentage < 0.6: return "A2"
    if percentage < 0.8: return "B1"
    return "B2"