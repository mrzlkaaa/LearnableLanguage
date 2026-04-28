from pydantic import BaseModel, Field
from datetime import datetime

class WordCardDTO(BaseModel):
    """Карточка для отображения пользователю"""
    word_text: str
    translation: str
    transcription: str
    definition: dict
    examples: dict
    use_cases: dict
    distractors: dict
    word_id: int
    tip: dict



class UserWordDTO(BaseModel):
    """Карточка для отображения пользователю"""
    box: int
    is_learned: bool
    next_review: datetime
    last_review: datetime


class GeneratedWordDTO(BaseModel):
    """Структура нового слова, сгенерированного нейросетью"""
    text: str = Field(description="Слово на английском (в начальной форме)")
    translation: str = Field(description="Перевод на русский")
    transcription: str = Field(description="Транскрипция (IPA)")
    definition: list[str] = Field(description="Определения на англ и русском")
    cefr_level: str = Field(description="Уровень (A1, A2, B1, B2, C1, C2)")
    example_en: list[str] = Field(description="Примеры на английском")
    example_ru: list[str] = Field(description="Примеры на русском")
    use_cases: list[str] = Field(description="Примеры с пропусками для use cases")
    distractors_en: list[str] = Field(description="Синонимы en (для отвлечения юзера) к слову")
    distractors_ru: list[str] = Field(description="Синонимы ru (для отвлечения юзера) к слову")
    tip: list[str] = Field(description="Лайфхак для запоминания")


class AIFeedbackDTO(BaseModel):
    """Структура ответа от Gemini после проверки задания"""
    is_correct: bool = Field(description="Успешно ли выполнено задание?")
    grammar_score: int = Field(description="Оценка грамматики от 1 до 5")
    feedback_text: str = Field(description="Текст для пользователя (в стиле BroBot)")
    improved_version: str | None = Field(description="Как бы сказал носитель (опционально)")


