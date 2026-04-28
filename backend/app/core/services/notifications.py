from sqlalchemy import select
from app.database.models import User
from app.core.constants.templates import TEMPLATES, NotificationType
from app.core.services.words_learning import WordsLearningService
from app.core.services.broadcaster import BroadcasterService
from app.core.clients import GeminiClient
from app.database.base import async_session
from app.config import config
from app.core.services.words_tutor import AITutorService
from app.database.repo.vocabulary import VocabularyRepo
from app.keyboards.for_notifications import notify_new_words, notify_review_words

class NotificationManager:
    def __init__(
        self, 
        broadcaster: BroadcasterService, 
        words_learning_service: WordsLearningService
    ):
        self.broadcaster = broadcaster
        self.learning = words_learning_service

    async def send_daily_new_words(self):
        """
        Эта функция будет запускаться APScheduler'ом каждое утро (например, в 09:00).
        """
        async with async_session() as session:
            # 1. Выбираем юзеров, у которых включены уведомления (если есть такая настройка)
            # Лучше делать это пачками (LIMIT/OFFSET), если юзеров > 1000
            stmt = select(User).where(User.is_active == True) 
            users = (await session.execute(stmt)).scalars().all()

        tasks = []
        
        for user in users:
            # 2. Пробуем получить новые слова для юзера
            # (Используем ту логику с лимитами, которую писали раньше!)

            #* open the session
            async with async_session() as session:
                learning = self.learning(
                    VocabularyRepo(session),
                    AITutorService(GeminiClient(api_key=config.GEMINI_API_KEY.get_secret_value()))
                )

                #* These words were obtained from global vocabulary but still at box = 1 
                result = await learning.get_new_user_words(user.id)
                text = f"❗️ Самое время вернуться, <b>{len(result)}</b> новых слов ждут тебя!"
                
                words_formatted = "\n".join([
                    f"🔹 <b>{w.word_text}</b> — {w.translation}" 
                    for w in result
                ])
                
                message_text = TEMPLATES[NotificationType.HELLO_WORDS].format(
                    words_list=words_formatted
                )
                if not result:
                    #* return words with spicified limit, so len(result) > 1
                    result = await learning.get_new_global_words(user.id)
                    text = f"✅ Подготовили для тебя <b>{len(result)}</b> новых слов, пора начать изучение!"

                    words_formatted = "\n".join([
                        f"🔹 <b>{w.word_text}</b> — {w.translation}" 
                        for w in result
                    ])
                    
                    message_text = TEMPLATES[NotificationType.HELLO_WORDS].format(
                        words_list=words_formatted
                    )
                    if not result:
                        
                        result = await learning.get_words_for_review(user.id)
                        text = f"❗️ Время повторить, уже <b>{len(result)}</b> слов ждут тебя!"

                        words_formatted = "\n".join([
                            f"🔹 <b>{w.word_text}</b> — {w.translation}" 
                            for w in result
                        ])
                        
                        message_text = TEMPLATES[NotificationType.GENTLE_REMINDER].format(
                            count=len(result)
                        )
                    
                        if not result:
                            print("No words to submit...")
                            continue
            

            # 4. Добавляем в очередь на отправку
            tasks.append({
                "user_id": user.id,
                "text": message_text,
                "kb": notify_new_words()
            })

        # 5. Запускаем массовую рассылку
        if tasks:
            count = await self.broadcaster.broadcast_batch(tasks)
            print(f"📢 Рассылка завершена: {count} юзеров получили новые слова.")


    async def send_review_words_reminder(self):
        """
        Эта функция будет запускаться APScheduler'ом каждое утро (например, в 09:00).
        """
        async with async_session() as session:
            # 1. Выбираем юзеров, у которых включены уведомления (если есть такая настройка)
            # Лучше делать это пачками (LIMIT/OFFSET), если юзеров > 1000
            stmt = select(User).where(User.is_active == True) 
            users = (await session.execute(stmt)).scalars().all()

        tasks = []
        
        for user in users:
            # 2. Пробуем получить новые слова для юзера
            # (Используем ту логику с лимитами, которую писали раньше!)

            #* open the session
            async with async_session() as session:
                learning = self.learning(
                    VocabularyRepo(session),
                    AITutorService(GeminiClient(api_key=config.GEMINI_API_KEY.get_secret_value()))
                )
                        
                result = await learning.get_words_for_review(user.id)
                text = f"❗️ Время повторить, уже <b>{len(result)}</b> слов ждут тебя!"
                
                message_text = TEMPLATES[NotificationType.GENTLE_REMINDER].format(
                    count=len(result)
                )
            
                if not result:
                    print("No words to submit...")
                    continue
            

            # 4. Добавляем в очередь на отправку
            tasks.append({
                "user_id": user.id,
                "text": message_text,
                "kb": notify_review_words()
            })

        # 5. Запускаем массовую рассылку
        if tasks:
            count = await self.broadcaster.broadcast_batch(tasks)
            print(f"📢 Рассылка завершена: {count} юзеров получил напоминание о словах.")