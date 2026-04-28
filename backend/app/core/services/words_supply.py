from sqlalchemy import func, select, desc
from app.database.models import Word, User, UserWord
from app.database.base import async_session
import logging

from app.utils.logger import setup_logger
from app.core.clients import GeminiClient
from app.core.services.words_tutor import AITutorService
from app.database.repo.vocabulary import VocabularyRepo
from app.config import config

setup_logger()
logger = logging.getLogger(__name__)


class WordsSupplyService:
    def __init__(
        self,
        ai_service: AITutorService,
        vocab: VocabularyRepo
    ):
        self.ai_service = ai_service
        self.vocab = vocab

    async def replenish_buffer(self, level: str, target_buffer: int = 20):
        """
        Проверяет, сколько свободных слов этого уровня есть в базе.
        Если меньше target_buffer, генерирует новые.
        """
        async with async_session() as session:
            #* Do requst among Users to get the fattests vocabulry
            uw = (
                select(User, func.count(UserWord.word_id).label("vocab_size"))
                .join(User.vocabulary)
                .join(Word, UserWord.word_id == Word.id)
                .where(Word.cefr_level == level)
                .group_by(User.id)
                .order_by(desc("vocab_size"))
                .limit(1)
            )
            result = await session.execute(uw)
            row = result.first()
            
            current_user_count = 0
            if row:
               #* Now users
               current_user_count = row[1]
            
            w = (
                select(func.count(Word.id).label("vocab_size"))
                .where(Word.cefr_level == level)
                .limit(1)
            )
            result = await session.execute(w)
            row = result.first()
            
            total_words = 0
            if row:
                total_words = row[0]    

            current_count = total_words - current_user_count

            # 2. Проверяем дефицит
        if current_count >= target_buffer:
            print(f"✅ Level {level}: Buffer OK ({current_count}/{target_buffer}). Skipping.")
            return

        needed = target_buffer - current_count
        print(f"⚠️ Level {level}: Low buffer! Generating {needed} words...")

                
        gemini_client = GeminiClient(api_key=config.GEMINI_API_KEY.get_secret_value())
        ai_service = self.ai_service(gemini_client)
            
        for _ in range(needed):
            try:
                ai_word_dto = await ai_service.generate_new_vocabulary(level)
                async with async_session() as session:
                    vocab = self.vocab(session)
                    new_word = await vocab.create_global_word(
                        text=ai_word_dto.text,
                        translation=ai_word_dto.translation,
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
                    logger.info(f"   + Added: {new_word.text}")
            except Exception as e:
                logger.error(f"Ошибка генерации (запроса) нового слова {e}")
        
        