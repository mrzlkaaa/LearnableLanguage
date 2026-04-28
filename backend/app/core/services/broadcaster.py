import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest

logger = logging.getLogger(__name__)

class BroadcasterService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_safe(self, user_id: int, text: str, keyboard=None) -> bool:
        """
        Отправляет сообщение одному юзеру с обработкой ошибок.
        Возвращает True, если успешно, False, если не удалось.
        """
        try:
            await self.bot.send_message(user_id, text, reply_markup=keyboard)
            return True
            
        except TelegramRetryAfter as e:
            # Если Телеграм говорит "подожди", мы ждем и пробуем снова (рекурсивно)
            logger.warning(f"Flood limit exceeded. Sleep {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
            return await self.send_safe(user_id, text, keyboard)
            
        except TelegramForbiddenError:
            # Юзер заблокировал бота. В идеале тут надо пометить юзера в БД как inactive
            logger.info(f"User {user_id} blocked the bot.")
            return False
            
        except TelegramBadRequest as e:
            logger.error(f"Bad request for user {user_id}: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unknown error for user {user_id}: {e}")
            return False

    async def broadcast_batch(self, tasks: list[dict]):
        """
        Принимает список задач формата: 
        [{"user_id": 123, "text": "...", "kb": ...}, ...]
        """
        sent_count = 0
        
        for task in tasks:
            success = await self.send_safe(
                user_id=task['user_id'],
                text=task['text'],
                keyboard=task.get('kb')
            )
            if success:
                sent_count += 1
            
            # 🛑 КРИТИЧНО: Искусственная задержка, чтобы не спамить (20 сообщений в секунду)
            await asyncio.sleep(0.05) 
            
        return sent_count