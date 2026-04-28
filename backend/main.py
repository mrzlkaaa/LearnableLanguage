import asyncio
import logging
import sys

from app.config import config
from app.loader import bot, dp, set_default_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.handlers import setup_routers
from app.utils.logger import setup_logger

# Настройка логирования (как в прошлом примере, для краткости опущу тело функции)
from app.middlewares.db import DbSessionMiddleware
from app.database.base import init_models
from app.core.services.words_supply import WordsSupplyService
from app.core.services.words_tutor import AITutorService
from app.database.repo.vocabulary import VocabularyRepo
from app.core.services.words_tutor import LEVELS
from app.core.services.notifications import NotificationManager
from app.core.services.broadcaster import BroadcasterService
from app.core.services.words_learning import WordsLearningService


scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)

async def setup_words_supply_workers(scheduler, supply_service: WordsSupplyService):
    for level in LEVELS:
        scheduler.add_job(
            supply_service.replenish_buffer, 
            trigger='interval', 
            minutes=15,
            kwargs={
                'level': level,
            },
            id=f"supply_{level}",
            max_instances=1
        )
    

async def setup_mailing_workers(scheduler, notification_manager: NotificationManager):
    
    # ... джобы по пополнению базы ...

    # Ежедневная рассылка новых слов (09:00 MSK = 06:00 UTC)
    scheduler.add_job(
        func=notification_manager.send_daily_new_words,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_words_push",
        replace_existing=True
    )

    # Вечерняя напоминалка (20:00 MSK = 17:00 UTC)
    scheduler.add_job(
        func=notification_manager.send_review_words_reminder,
        trigger="cron",
        hour=20,
        minute=0,
        id="evening_reminder_push",
        replace_existing=True
    )


async def main():
    setup_logger()
    
    await init_models()
    
    
    supply_service = WordsSupplyService(
        AITutorService,
        VocabularyRepo
    )
    await setup_words_supply_workers(scheduler, supply_service)
    
    notification_manager = NotificationManager(
        BroadcasterService(
            bot
        ),
        WordsLearningService

    )
    
    await setup_mailing_workers(scheduler, notification_manager)
    
    scheduler.start()

    # 1. Подключаем корневой роутер
    # Вся логика бота теперь инкапсулирована внутри этой функции
    dp.startup.register(set_default_commands)
    main_router = setup_routers()
    dp.include_router(main_router)
    dp.update.middleware(DbSessionMiddleware())
    
    # 2. Регистрируем startup/shutdown хуки (полезно для БД)
    # dp.startup.register(on_startup) 
    
    logger.info("🚀 Бот запускается...")
    
    # 3. Удаляем вебхук и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # Winloop для Windows (опционально, для скорости), uvloop для Linux
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:

        print("Bot stopped")