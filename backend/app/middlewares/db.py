from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database.base import async_session
from app.database.repo.user import UserRepo
from app.database.repo.vocabulary import VocabularyRepo

from app.core.services.words_learning import WordsLearningService
from app.core.clients import GeminiClient
from app.core.services.words_tutor import AITutorService

from app.config import config
# from app.database.repo.quiz import QuizRepo

class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Создаем сессию
        async with async_session() as session:
            # Инициализируем репозитории
            user_repo = UserRepo(session)
            vocab_repo = VocabularyRepo(session)
            
            gemini_client = GeminiClient(api_key=config.GEMINI_API_KEY.get_secret_value())
            ai_tutor = AITutorService(gemini_client)
            
            # Прокидываем их в data (теперь они доступны в хендлере как аргументы)
            data["user_repo"] = user_repo
            data["words_service"] = WordsLearningService(vocab_repo, ai_tutor)
            

            data["ai_tutor"] = ai_tutor
            # data["quiz_repo"] = quiz_repo
            
            # Вызываем хендлер
            result = await handler(event, data)
            
            # Сессия закроется сама при выходе из with
            return result