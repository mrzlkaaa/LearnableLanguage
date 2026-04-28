from app.handlers.user_main import router
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.states import LearningStates
from aiogram.filters import CommandStart, Command, StateFilter


from app.handlers.general import update_history, load_histiory, handle_callback
from app.keyboards.learning.for_words import (
    get_word_learnings, get_card_navigation, TranslateQuizCallback, WordCardQuizCallback,
    get_translation_card, get_word_card
)
from app.keyboards.for_base_navigation import get_back_inline
from app.core.services.words_learning import WordsLearningService
import random
from asyncio import sleep

router = Router(name="vocabulary")

@router.callback_query(StateFilter(LearningStates.vocabulary), F.data == "vocab_menu") #* no state here
async def to_words_learning_menu(callback: CallbackQuery, state: FSMContext, **kwargs):
    await words_learning_menu(callback, state, **kwargs)

#! revision is required. Must be made via kb/for_words.py
@router.callback_query(StateFilter(LearningStates.learning), F.data == "vocabulary") #* no state here
async def words_learning_menu(callback: CallbackQuery, state: FSMContext, **kwargs):
    #* drop previous state datas
    await state.update_data(
        card_counter=None
    )

    history, history_data = await handle_callback(callback, state)
    
    user_id = callback.from_user.id
    wls = kwargs["words_service"]
    #* set 35 words as a limit for learning and review
    review_words = await wls.get_words_for_review(user_id)
    #* check if new words in list
    new_words = await wls.get_new_user_words(user_id)
    
    words = review_words + new_words
    random.shuffle(words)

    await state.update_data(
        words=words,
        user_id=user_id
    )

    display_words = f"🔄 Слов на повтор: <b>{len(review_words)}</b>\n📚Новых слов: <b>{len(new_words)}</b>\n"

    await state.set_state(LearningStates.vocabulary)
    await callback.message.edit_text(
        "Каким образом сегодня учим / повторяем слова?\n" + display_words,
        reply_markup=get_word_learnings(words[0].word_id if len(words) > 0 else None)
    )


@router.callback_query(StateFilter(LearningStates.vocabulary), F.data == "new_words") #* no state here
async def get_new_words(callback: CallbackQuery, state: FSMContext, **kwargs):
    history, history_data = await handle_callback(callback, state)

    user_id = callback.from_user.id
    wls = kwargs["words_service"]
    new_words = await wls.get_new_global_words(user_id)

    # if not new_words:
    #     await callback.message.edit_text(
    #         "Предлагаю пока что новые слова не брать... С текущими бы разобраться",
    #         reply_markup=get_back_inline()
    #     )
    #     return

    await callback.message.edit_text(
        "Запрашиваю новые слова...",
        reply_markup=get_back_inline()
    )
    
    if not new_words:
        await callback.message.edit_text(
            "Лимит новых слов на сегодня закончился",
            reply_markup=get_back_inline()
        )
        return

    print(f"New {len(new_words)} global words added for user {user_id}")

    await words_learning_menu(callback, state, **kwargs)


async def get_next_card(state: FSMContext, direction: int = 1):
    data = await state.get_data()
    card_counter = data.get("card_counter", None)

    if card_counter is not None:
        if card_counter == len(data["words"]) - 1:
            return None
        
        if direction and card_counter < len(data["words"]) - 1:
            card_counter += 1
        elif not direction and card_counter > 0:
            card_counter -= 1
    else:
        card_counter = 0
    print("counter: ", card_counter)
    await state.update_data(
        card_counter=card_counter
    )

    word_card = data["words"][card_counter]
    return word_card

@router.callback_query(StateFilter(LearningStates.vocabulary), WordCardQuizCallback.filter()) #* no state here
async def word_cards(callback: CallbackQuery, callback_data: WordCardQuizCallback, state: FSMContext):
    #* init of pages
    history, history_data = await handle_callback(callback, state)

    if not callback_data.word_id:
        text, kb = get_word_card()
        return await callback.message.edit_text(
            text=text,
            reply_markup=kb
        )

    word = await get_next_card(state, callback_data.direction)
    text, kb = get_word_card(word)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=kb
    )


@router.callback_query(StateFilter(LearningStates.vocabulary), TranslateQuizCallback.filter()) #* no state here
async def translation_cards(callback: CallbackQuery, callback_data: TranslateQuizCallback, state: FSMContext, **kwargs):
    history, history_data = await handle_callback(callback, state)

    if not callback_data.word_id:
        text, kb = get_translation_card()
        await callback.message.edit_text(
            text=text,
            reply_markup=kb
        )
        return

    wls = kwargs["words_service"]
    data = await state.get_data()
    user_id = data["user_id"]
    

    if callback_data.is_correct:
         await callback.answer("✅ Верно!", show_alert=True)
    elif callback_data.is_correct == False:
        await callback.answer(f"❌ Увы! Правильный ответ: **{callback_data.translation}**", show_alert=True)
        #* adding failed word back to words list to display it again
        await state.update_data(
            words=data["words"] + [word for word in data["words"] if word.word_id == callback_data.word_id]
        )

    user_word = await wls.update_user_word_progress(user_id, callback_data.word_id, callback_data.is_correct)
    print("box level:", user_word.box, "next_review: ", user_word.next_review)

    #* init of pages
    word = await get_next_card(state)
    text, kb = get_translation_card(word)

    await callback.message.edit_text(
        text=text,
        reply_markup=kb
    )








