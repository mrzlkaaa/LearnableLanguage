from datetime import datetime, time
from sqlalchemy import BigInteger, String, Integer, ForeignKey, JSON, Text, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

# ----------------------
# 1. ПРОФИЛЬ И НАСТРОЙКИ
# ----------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32))
    full_name: Mapped[str] = mapped_column(String(64))
    
    # Текущий уровень (определяется входным тестом, меняется динамически)
    # None, A1, A2, B1, B2, C1
    level: Mapped[str] = mapped_column(String(5), default="B2")
    
    # Настройки активности (JSON, чтобы гибко добавлять новые фичи)
    # Пример: {
    #   "active_hours_start": 9, 
    #   "active_hours_end": 21, 
    #   "frequency": "medium", (3 раза в день)
    #   "timezone": "UTC+3"
    # }
    settings: Mapped[dict] = mapped_column(JSON, default={})
    
    # Дата регистрации
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    # Связь с прогрессом
    vocabulary: Mapped[list["UserWord"]] = relationship(back_populates="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    

# ----------------------
# 2. СЛОВАРЬ И SRS (Vocabulary Micro-Block)
# ----------------------

class Word(Base):
    """Глобальный словарь слов (контент)"""
    __tablename__ = "words"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(50), index=True)  # само слово
    translation: Mapped[str] = mapped_column(String(100))
    transcription: Mapped[str | None] = mapped_column(String(50))
    definition: Mapped[list[str]] = mapped_column(JSON)
    
    # Уровень слова (чтобы не давать A1 ученику слова уровня C2)
    cefr_level: Mapped[str] = mapped_column(String(2)) # A1-C2
    
    # Примеры использования (JSON array)
    # ["I love apples.", "He ate an apple."]
    examples: Mapped[list[str]] = mapped_column(JSON)
    use_cases: Mapped[list[str]] = mapped_column(JSON)
    distractors: Mapped[list[str]] = mapped_column(JSON)
    tip: Mapped[list[str]] = mapped_column(JSON)

class UserWord(Base):
    """
    Личный словарь юзера.
    Здесь работает алгоритм SRS (Spaced Repetition System - как Anki).
    """
    __tablename__ = "user_words"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    
    # Статус изучения
    is_learned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # SRS поля (SuperMemo-2 алгоритм или упрощенный)
    box: Mapped[int] = mapped_column(Integer, default=1) # Коробка 1-5
    next_review: Mapped[datetime] = mapped_column(DateTime) # Когда повторять
    last_review: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="vocabulary")
    word: Mapped["Word"] = relationship()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

# ----------------------
# 3. МИКРО-БЛОКИ (Reading / Listening)
# ----------------------

class MicroUnit(Base):
    """
    Короткие тексты или аудио для практики.
    """
    __tablename__ = "micro_units"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Тип: 'reading' (текст), 'listening' (аудио), 'grammar' (теория)
    unit_type: Mapped[str] = mapped_column(String(20))
    
    cefr_level: Mapped[str] = mapped_column(String(2)) # B1, B2...
    
    # Контент:
    # Для Reading: Сам текст
    # Для Listening: file_id из Telegram или URL
    content_payload: Mapped[str] = mapped_column(Text)
    
    # Вопросы к тексту/аудио (JSON)
    # [
    #   {"q": "Who went home?", "options": ["John", "Mary"], "correct": "John"}
    # ]
    quiz_data: Mapped[dict] = mapped_column(JSON)


class PlacementTestQuestion(Base):
    """
    Легковесные вопросы для быстрого определения уровня языка.
    Используются только в сценарии /start -> Onboarding.
    """
    __tablename__ = "placement_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Текст вопроса (короткий, на грамматику или лексику)
    # Пример: "I ____ (be) at home yesterday."
    text: Mapped[str] = mapped_column(String(255))
    
    # Уровень сложности вопроса (CEFR)
    # Важно: это не уровень юзера, а сложность самого вопроса.
    difficulty_level: Mapped[str] = mapped_column(String(2)) # "A1", "A2", "B1", "B2", "C1"

    # Варианты ответов и правильный ключ (JSON)
    # {
    #   "options": ["am", "was", "were", "been"],
    #   "correct_index": 1  (т.е. "was")
    # }
    data: Mapped[dict] = mapped_column(JSON)