from app.database.repo.vocabulary import VocabularyRepo
from app.database.repo.user import UserRepo
from app.core.dtos import WordCardDTO, UserWordDTO
from app.core.services.words_tutor import AITutorService

from datetime import timedelta, datetime

import logging
from app.utils.logger import setup_logger

# SRS_INTERVALS: { Номер коробки : Время до следующего повторения }
SRS_INTERVALS = {
    1: timedelta(hours=4),    # Если ошибся или только начал -> повтор сегодня же
    2: timedelta(days=1),     # Завтра
    3: timedelta(days=3),     # Через 3 дня
    4: timedelta(days=7),     # Через неделю
    5: timedelta(days=14),    # Через 2 недели
    6: timedelta(days=30),    # Через месяц (Финальный босс)
}

# После 6-го уровня слово считается "Выученным" (is_learned = True)
MAX_BOX_LEVEL = 6

setup_logger()
logger = logging.getLogger(__name__)

class WordsLearningService:
    def __init__(
        self, 
        vocab_repo: VocabularyRepo,
        ai_tutor: AITutorService
        # user_repo: UserRepo
    ):
        self.vocab = vocab_repo
        self.ai_tutor = ai_tutor
        # self.users = user_repo

    async def get_new_global_words(
        self, 
        user_id: int,
        num_words:int = 100
    ) -> list[WordCardDTO] | None:
        words = []
        for _ in range(num_words):
            new_word = await self.get_new_global_word(user_id)
            if new_word:
                words.append(new_word)
        
        if len(words) > 0:
            return words

    async def get_new_global_word(
        self, 
        user_id: int,
        # tried_words: list | None = None #* the words comes from recursion 
    ) -> WordCardDTO | None:
        
        limit = 7

        #* check if there are slots for today
        acquired_today = await self.vocab.get_today_acquired_words_count(user_id)
        if limit - acquired_today == 0:
            return None

        level = await self.vocab.get_user_level(user_id)
        known_word_ids = await self.vocab.get_user_known_word_ids(user_id)
        new_word = await self.vocab.get_global_word(level, known_word_ids)

        if not new_word:
            ai_word_dto = await self.ai_tutor.generate_new_vocabulary(level)
            print(ai_word_dto)

            #! important check if the word exists
            duplicate = await self.vocab.get_word_duplicate(ai_word_dto.text.lower())
            if duplicate:
                return await self.get_new_global_word(user_id)

            translation_duplicate = await self.vocab.get_word_translation_duplicate(ai_word_dto.transcription.lower())
            if translation_duplicate:
                return await self.get_new_global_word(user_id)

            new_word = await self.vocab.create_global_word(
                text=ai_word_dto.text.lower(),
                translation=ai_word_dto.translation.lower(),
                transcription=ai_word_dto.transcription,
                definition={
                    "en": ai_word_dto.definition[0],
                    "ru": ai_word_dto.definition[1]
                },
                level=ai_word_dto.cefr_level,
                context={"en": ai_word_dto.example_en, "ru": ai_word_dto.example_ru},
                use_cases={
                    "uc1": ai_word_dto.use_cases[0], 
                    "uc2": ai_word_dto.use_cases[1],
                    "uc3": ai_word_dto.use_cases[2]
                },
                distractors={
                    "en": ai_word_dto.distractors_en,
                    "ru": ai_word_dto.distractors_ru
                },
                tip={
                    "en": ai_word_dto.tip[0],
                    "ru": ai_word_dto.tip[1]
                }
            )


        # Сразу добавляем в словарь юзера, чтобы не потерять
        await self.vocab.add_user_word(user_id, new_word.id)
        
        return WordCardDTO(
            word_text=new_word.text,
            translation=new_word.translation,
            transcription=new_word.transcription,
            definition=new_word.definition,
            examples=new_word.examples,
            use_cases=new_word.use_cases,
            distractors=new_word.distractors,
            is_new=True,
            word_id=new_word.id,
            tip=new_word.tip
        )

    async def get_words_for_review(
        self, 
        user_id: int
    ):
        results = await self.vocab.get_words_for_review(user_id)
        wcs = []
        if not results:
            return wcs
        
        for user_word in results:
            wcs.append(
                WordCardDTO(
                    word_text=user_word.word.text,
                    translation=user_word.word.translation,
                    transcription=user_word.word.transcription,
                    definition=user_word.word.definition,
                    examples=user_word.word.examples,
                    use_cases=user_word.word.use_cases,
                    distractors=user_word.word.distractors,
                    is_new=True,
                    word_id=user_word.word.id,
                    tip=user_word.word.tip
                )
            )

        return wcs

    async def get_new_user_words(
        self,
        user_id
    ):
        results = await self.vocab.get_new_user_words(user_id)
        wcs = []
        if not results:
            return wcs
        
        for user_word in results:
            wcs.append(
                WordCardDTO(
                    word_text=user_word.word.text,
                    translation=user_word.word.translation,
                    transcription=user_word.word.transcription,
                    definition=user_word.word.definition,
                    examples=user_word.word.examples,
                    use_cases=user_word.word.use_cases,
                    distractors=user_word.word.distractors,
                    is_new=True,
                    word_id=user_word.word.id,
                    tip=user_word.word.tip
                )
            )


        return wcs

    async def get_user_word(
        self,
        user_id: int,
        word_id: int
    ):
        user_word =  await self.vocab.get_user_word(user_id, word_id)
        if user_word:
            return user_word
    
    async def update_user_word_progress(
        self,
        user_id: int,
        word_id: int,
        is_correct: bool
    ):
        user_word = await self.get_user_word(user_id, word_id)
        if user_word:

            now = datetime.now()
            user_word.last_review = now
            
            if is_correct:
                    
                next_box = user_word.box + 1
                
                if next_box >= MAX_BOX_LEVEL:
                    user_word.is_learned = True
                    user_word.box = MAX_BOX_LEVEL
                else:
                    user_word.box = next_box
                    user_word.next_review = now + SRS_INTERVALS.get(next_box)

                if user_word.is_learned:
                    
                    user_word.next_review = now + SRS_INTERVALS.get(MAX_BOX_LEVEL)

            else:
                user_word.box = 1
                user_word.is_learned = False
                user_word.next_review = now - timedelta(minutes=1)

            await self.vocab.update_user_word(user_word)

        return user_word
            

            