from datetime import datetime, timedelta, date, time
from sqlalchemy import select, and_
from app.database.models import UserWord, Word, User
from app.database.base import BaseRepo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, exists, and_, or_
from sqlalchemy.orm import joinedload 

class VocabularyRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user_word(self, user_id: int, word_id: int):
        """Добавляет новое слово в личный словарь (Box 1)"""
        link = UserWord(
            user_id=user_id, 
            word_id=word_id,
            box=1,
            next_review=datetime.now() + timedelta(hours=4)
        )
        self.session.add(link)
        await self.session.commit()
        return link
    
    async def create_global_word(
        self,
        text,
        translation,
        transcription,
        definition,
        level,
        context,
        use_cases,
        distractors,
        tip
    ):
        new_word = Word(
            text=text.lower(), # Всегда сохраняем в нижнем регистре для консистентности
            translation=translation,
            transcription=transcription,
            definition=definition,
            cefr_level=level,
            examples=context,
            use_cases=use_cases,
            distractors=distractors,
            tip=tip

        )
        self.session.add(new_word)
        
        await self.session.commit() 
        return new_word
    

    async def get_today_acquired_words_count(self, user_id: int):
        today_start = datetime.now().combine(datetime.now().date(), time.min)
        
        stmt = select(func.count(UserWord.word_id)).where(
            UserWord.user_id == user_id,
            UserWord.created_at >= today_start # Все слова, добавленные после 00:00
        )

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_user_known_word_ids(self, user_id: int) -> list[int]:
        """Возвращает список ID всех слов, которые юзер уже учит."""
        stmt = select(UserWord.word_id).where(UserWord.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    

    async def get_user_level(self, user_id: int) -> User :
        stmt = select(User.level).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_word(self, user_id: int, word_id: int) -> UserWord | None:
        """Получаем связь юзер-слово, чтобы узнать текущий Box."""
        stmt = select(UserWord).where(
            UserWord.user_id == user_id,
            UserWord.word_id == word_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_words_for_review(
        self,
        user_id: int
    ):
        #* review only -> box > 1
        #* If user fails any word it drop back to box = 1
        #* So now the words classifies as a NEW
        now = datetime.now()
        stmt = (
            select(UserWord)
            .where(UserWord.user_id == user_id)
            .where(UserWord.box > 1)
            .where(UserWord.next_review <= now)
            .order_by(UserWord.next_review.asc())
            .limit(20) #* only 20 words in return to 
            .options(joinedload(UserWord.word)) 
        )

        results = await self.session.execute(stmt)
        results = list(results.scalars().all())

        if len(results) > 0:
            return results
        
        return None
    
    async def get_new_user_words(
        self,
        user_id
    ):
        #* new words only -> box = 1
        #* If user fails any word it drop back to box = 1
        #* So the fetches the word that already added or failed
        #* And NEW only for today to PREVENT global fetch of new words
    
        
        stmt = ( select(UserWord)
            .where(UserWord.user_id == user_id)
            .where(UserWord.box == 1)
            .options(joinedload(UserWord.word))
        )
        results = await self.session.execute(stmt)
        results = list(results.scalars().all())

        if len(results) > 0:
            return results
        
        return None

    async def get_global_word(
        self,
        level,
        exclude_ids
    ):
        #* search among existing words
        stmt = select(Word).where(Word.cefr_level == level)
        
        # Если есть слова для исключения - добавляем фильтр
        if exclude_ids:
            stmt = stmt.where(Word.id.not_in(exclude_ids))
            
        # Сортировка func.random() работает и в SQLite, и в PostgreSQL
        stmt = stmt.order_by(func.random()).limit(1)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_word_duplicate(
        self,
        word_text
    ):
        #* search among existing words
        stmt = select(Word).where(Word.text == word_text)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    
    async def get_word_translation_duplicate(
        self,
        translation
    ):
        #* search among existing words
        stmt = select(Word).where(Word.translation == translation)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def update_user_word(self, user_word: UserWord):
        """
        Просто комитим изменения. 
        Объект user_word уже будет изменен в Сервисе.
        """
        self.session.add(user_word)
        await self.session.commit()



    async def is_word_exists(self, word_text: str) -> bool:
        """
        * Check if word exists in local DataBase
        * Prevent from adding duplicate generated by AI
        """
        # Ищем: есть ли связь UserWord для этого юзера с таким текстом в таблице Word
        stmt = select(
            exists().where(
                and_(
                    func.lower(Word.text) == word_text.lower(),
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    