from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.states import OnboardingStates
from app.keyboards.for_onboarding import (
    get_goal_menu, get_words_per_day_menu, get_reminder_frequency_menu,
    get_active_hours_menu, get_topics_menu, get_placement_test_kb
)
from app.keyboards.for_base_navigation import back_inline
from app.handlers.user_main import get_main_menu

router = Router(name="onboarding")

# 1. GOAL
@router.message(F.text == "📎 Анкетирование")
async def process_goal(message: Message, state: FSMContext):
    await state.set_state(OnboardingStates.waiting_for_goal)
    await message.answer(
        "Анкета содержит только необходимую для продуктивной работы информацию\n"
        "🏆 **Какая у тебя цель изучения языка?**\n",
        reply_markup=get_goal_menu()
    )

@router.message(OnboardingStates.waiting_for_goal)
async def process_goal_answer(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(OnboardingStates.waiting_for_words_per_day)
    await message.answer(
        "📚 **Сколько новых слов в день ты готов учить?**",
        reply_markup=get_words_per_day_menu()
    )

# 2. WORDS PER DAY
@router.message(OnboardingStates.waiting_for_words_per_day)
async def process_words_per_day(message: Message, state: FSMContext):
    await state.update_data(words_per_day=message.text)
    await state.set_state(OnboardingStates.waiting_for_reminder_frequency)
    await message.answer(
        "⏰ **Как часто тебе удобно повторять слова?**",
        reply_markup=get_reminder_frequency_menu()
    )

# 3. REMINDER FREQUENCY
@router.message(OnboardingStates.waiting_for_reminder_frequency)
async def process_reminder_frequency(message: Message, state: FSMContext):
    await state.update_data(reminder_frequency=message.text)
    await state.set_state(OnboardingStates.waiting_for_active_hours)
    await message.answer(
        "🌅 **В какое время суток тебе удобно заниматься?**",
        reply_markup=get_active_hours_menu()
    )

# 4. ACTIVE HOURS
@router.message(OnboardingStates.waiting_for_active_hours)
async def process_active_hours(message: Message, state: FSMContext):
    await state.update_data(active_hours=message.text)
    await state.set_state(OnboardingStates.waiting_for_topics)
    await message.answer(
        "🎯 **Какие темы тебе интересны?**\n"
        "(Выбери несколько или напиши свои)",
        reply_markup=get_topics_menu()
    )

# 5. TOPICS
@router.message(OnboardingStates.waiting_for_topics)
async def process_topics(message: Message, state: FSMContext):
    await state.update_data(topics=message.text)
    await state.set_state(OnboardingStates.placement_test)
    await message.answer(
        "Отлично! 🚀\n\n"
        "Теперь давай определим твой уровень. "
        "Ответь на пару вопросов — только честно, не гугли!"
    )
    # Загружаем вопросы из БД
    from app.database.repo.onboarding import OnboardingRepo
    from app.database.base import Database
    db = Database()
    async with db.session() as session:
        onboarding_repo = OnboardingRepo(session)
        questions = await onboarding_repo.get_placement_questions()
    if not questions:
        # Fallback если нет вопросов в БД
        questions = [
            {"q": "I ___ to school yesterday.", "opts": ["go", "went", "gone"], "correct": 1, "level": "A1"},
            {"q": "If I ___ rich, I would buy a car.", "opts": ["was", "were", "am"], "correct": 1, "level": "B1"},
        ]
    await state.update_data(test_data=questions, current_q=0, score=0)
    await send_question(message, questions[0])

async def send_question(message: Message, question_data: dict):
    kb = get_placement_test_kb(question_data['opts'])
    await message.answer(f"❓ **Level Check**\n\n{question_data['q']}", reply_markup=kb)

# 6. PLACEMENT TEST ANSWERS
@router.callback_query(OnboardingStates.placement_test, F.data.startswith("pt_ans:"))
async def process_test_answer(callback: CallbackQuery, state: FSMContext, user_repo):
    selected_index = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    questions = data['test_data']
    current_idx = data['current_q']
    current_score = data['score']
    
    correct_index = questions[current_idx]['correct']
    if selected_index == correct_index:
        current_score += 1
        await callback.answer("✅ Accepted!")
    else:
        await callback.answer("✅ Accepted!")

    next_idx = current_idx + 1
    
    if next_idx < len(questions):
        await state.update_data(current_q=next_idx, score=current_score)
        await callback.message.delete()
        await send_question(callback.message, questions[next_idx])
    else:
        final_level = calculate_level(current_score, len(questions))
        
        # Сохраняем все настройки в БД
        user_id = callback.from_user.id
        settings = {
            "goal": data.get("goal", ""),
            "words_per_day": data.get("words_per_day", ""),
            "reminder_frequency": data.get("reminder_frequency", ""),
            "active_hours": data.get("active_hours", ""),
            "topics": data.get("topics", ""),
            "cefr_level": final_level,
            "onboarding_completed": True
        }
        await user_repo.update_settings(user_id, settings)
        
        await callback.message.delete()
        await callback.message.answer(
            f"🎉 Тест завершен!\n\n"
            f"Твой примерный уровень: **{final_level}**\n"
            f"Я подстроил программу под тебя. Погнали!",
            reply_markup=get_main_menu()
        )
        await state.clear()

def calculate_level(score, total):
    percentage = score / total
    if percentage < 0.3: return "A1"
    if percentage < 0.6: return "A2"
    if percentage < 0.8: return "B1"
    return "B2"
