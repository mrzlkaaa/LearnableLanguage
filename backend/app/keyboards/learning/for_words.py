from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from app.keyboards.for_base_navigation import back_inline, main_menu_inline
from app.core.dtos import WordCardDTO

import random

class TranslateQuizCallback(CallbackData, prefix="tq"):
    
    word_id: int | None
    is_correct: int | None = None
    translation: str | None = None
    

class WordCardQuizCallback(CallbackData, prefix="wc"):
    
    word_id: int | None
    direction: int = 1


vocab_menu_inline = types.InlineKeyboardButton(
    text="В меню изучения слов",
    callback_data="vocab_menu"
)


def get_word_learnings(word_id: int | None = None):
    builder = InlineKeyboardBuilder()
    
    new_words = types.InlineKeyboardButton(
        text="Получить новые слова",
        callback_data="new_words"
    )
    builder.button(
        text="Через карточки",
        callback_data=WordCardQuizCallback(
            word_id=word_id
        )
    )
    builder.button(
        text="Через переводы",
        callback_data=TranslateQuizCallback(
            word_id=word_id 
        )
    )

    use_cases = types.InlineKeyboardButton(
        text="Через Use Cases",
        callback_data="use_cases"
    )
    pronounce = types.InlineKeyboardButton(
        text="Через произношение",
        callback_data="pronounce"
    )

    builder.add(
        new_words,
        use_cases,
        pronounce,
        back_inline
    )
    builder.adjust(2)
    
    return builder.as_markup()


def get_card_navigation(word_id, current: int = 0, total: int = 0):
    builder = InlineKeyboardBuilder()
    
    if current > 0:
        builder.button(
            text="Предыдущая ⬅️",
            callback_data=WordCardQuizCallback(
                word_id=word_id,
                direction=0 
            )
        )
    else:
        builder.button(
            text="⬅️ Начало",
            callback_data=WordCardQuizCallback(
                word_id=word_id,
                direction=0
            )
        )

    builder.button(
        text="Следующая ➡️",
        callback_data=WordCardQuizCallback(
            word_id=word_id
        )
    )

    builder.add(
        vocab_menu_inline,
        main_menu_inline
    )
    builder.adjust(2)

    return builder.as_markup()


def get_word_card(word: WordCardDTO | None = None, current: int = 0, total: int = 0):
    builder = InlineKeyboardBuilder()
    text = f"<b>Карточки для изучения закончились</b>\nДождись новых или переходи к другим секциям, удачи!"

    if word:
        progress = f"🔢 Карточка {current + 1} из {total}\n"
        progress_bar = "".join(["🟩" if i < current else "🟦" for i in range(total)])
        if total > 1:
            text = f"{progress}{progress_bar}\n\n"

        rand_int = random.randint(0, 1)
        text += ( f"🇬🇧 <b>{word.word_text.upper()}</b> <code>[{word.transcription}]</code>\n"
        + f"🇷🇺 <b>{word.translation}</b>\n\n"
        + f"🧠 <b>Context:</b>\n"
        + f" — <i>{word.examples['en'][rand_int].replace(word.word_text, f'<b>{word.word_text}</b>')}</i>\n"
        + f"({word.examples['ru'][rand_int]})\n\n"
        + f"💡 <b>Tip:</b> {word.tip['en']}\n({word.tip['ru']})"
        )

        kb = get_card_navigation(word.word_id, current=current, total=total)
        return text, kb
    
    builder.add(
        vocab_menu_inline,
        main_menu_inline
    )
    builder.adjust(2)

    return text, builder.as_markup()

def get_translation_card(word: WordCardDTO | None = None, current: int = 0, total: int = 0):
    builder = InlineKeyboardBuilder()
    text = f"<b>Переводные карточки для изучения закончились</b>\nДождись новых или переходи к другим секциям, удачи!"

    if word:
        progress = f"🔢 Карточка {current + 1} из {total}\n"
        progress_bar = "".join(["🟩" if i < current else "🟦" for i in range(total)])
        if total > 1:
            text = f"{progress}{progress_bar}\n\n"

        direction = random.randint(0, 1)
        if direction:
            text += f"🇬🇧 <b>Как переводится слово?</b>\n\n🔹 <b>{word.word_text}</b>\n<i>({word.transcription})</i>"
            correct_ans = word.translation
            wrong_answers = word.distractors.get("ru") 
        else:
            text += f"🇷🇺 <b>Выбери верный перевод:</b>\n\n🔹 <b>{word.translation.capitalize()}</b>"
            correct_ans = word.word_text
            wrong_answers = word.distractors.get("en") 

        text_callback = [(correct_ans, 1)] + [(wrong_answer, 0) for wrong_answer in wrong_answers[:3]]
        random.shuffle(text_callback)

        for kb_text, callback in text_callback:
            builder.button(
                text=kb_text,
                callback_data=TranslateQuizCallback(
                    word_id=word.word_id,
                    is_correct=callback,
                    translation=correct_ans if not callback else None
                ) 
            )

    builder.add(
        vocab_menu_inline,
        main_menu_inline
    )
    builder.adjust(2)

    return text, builder.as_markup()
